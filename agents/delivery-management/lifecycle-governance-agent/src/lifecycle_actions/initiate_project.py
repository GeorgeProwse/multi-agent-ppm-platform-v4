"""Action handler for project initiation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from lifecycle_utils import load_methodology_map
from orchestration import (
    DurableTask,
    DurableWorkflow,
    OrchestrationContext,
    RetryPolicy,
)

if TYPE_CHECKING:
    from project_lifecycle_agent import ProjectLifecycleAgent


async def initiate_project(
    agent: ProjectLifecycleAgent, project_data: dict[str, Any], *, tenant_id: str
) -> dict[str, Any]:
    """
    Initiate a new project and set initial lifecycle state.

    Returns project record and methodology map.
    """
    agent.logger.info("Initiating project")

    project_id = project_data.get("project_id")
    workflow = DurableWorkflow(
        name="project_initiation",
        tasks=[
            DurableTask(
                name="create_records",
                action=lambda ctx: _create_project_record(agent, ctx),
                compensation=lambda ctx, exc: _rollback_project_record(agent, ctx, exc),
            ),
            DurableTask(
                name="persist_methodology",
                action=lambda ctx: _persist_methodology_decision(agent, ctx),
            ),
            DurableTask(
                name="publish_project_initiated",
                action=lambda ctx: _publish_project_initiated(agent, ctx),
                retry_policy=RetryPolicy(max_attempts=3),
            ),
            DurableTask(
                name="sync_project_state",
                action=lambda ctx: _sync_project_state(agent, ctx),
                retry_policy=RetryPolicy(max_attempts=3),
            ),
            DurableTask(
                name="notify_project_initiated",
                action=lambda ctx: _notify_project_initiated(agent, ctx),
            ),
        ],
        sleep=agent.orchestrator_sleep,
    )

    context = OrchestrationContext(
        workflow_id=f"initiate-{project_id}",
        tenant_id=tenant_id,
        project_id=project_id,
        correlation_id=str(uuid.uuid4()),
        payload={"project_data": project_data},
    )
    context = await agent.workflow_engine.run(workflow, context)
    init_payload = context.results["create_records"]

    agent.logger.info("Initiated project: %s", project_id)

    return {
        "project_id": project_id,
        "current_phase": init_payload["methodology_map"]["initial_phase"],
        "methodology": init_payload["methodology"],
        "methodology_map": init_payload["methodology_map"],
        "next_steps": "Generate project charter and complete initiation activities",
    }


# ---------------------------------------------------------------------------
# Workflow task functions
# ---------------------------------------------------------------------------


async def _create_project_record(
    agent: ProjectLifecycleAgent, context: OrchestrationContext
) -> dict[str, Any]:
    from lifecycle_actions.recommend_methodology import recommend_methodology

    project_data = context.payload.get("project_data", {})
    project_id = project_data.get("project_id")
    name = project_data.get("name")
    methodology = project_data.get("methodology", "hybrid")

    recommended_methodology = await recommend_methodology(agent, project_data)
    if methodology != recommended_methodology.get("methodology"):
        agent.logger.warning(
            "Provided methodology differs from recommended",
            extra={
                "provided": methodology,
                "recommended": recommended_methodology.get("methodology"),
            },
        )

    methodology_map = await load_methodology_map(agent, methodology, tenant_id=context.tenant_id)
    project = {
        "project_id": project_id,
        "name": name,
        "methodology": methodology,
        "current_phase": methodology_map["initial_phase"],
        "phase_history": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "Active",
    }
    lifecycle_state = {
        "project_id": project_id,
        "current_phase": methodology_map["initial_phase"],
        "phase_start_date": datetime.now(timezone.utc).isoformat(),
        "methodology_map": methodology_map,
        "transitions": [],
        "gates_passed": [],
        "gates_pending": [],
    }

    agent.projects[project_id] = project
    agent.lifecycle_states[project_id] = lifecycle_state
    agent.lifecycle_store.upsert(context.tenant_id, project_id, lifecycle_state)
    agent.persistence.store_lifecycle_state(context.tenant_id, project_id, lifecycle_state)

    context.results["methodology_decision"] = recommended_methodology
    return {
        "project_id": project_id,
        "project": project,
        "lifecycle_state": lifecycle_state,
        "methodology": methodology,
        "methodology_map": methodology_map,
    }


async def _rollback_project_record(
    agent: ProjectLifecycleAgent, context: OrchestrationContext, _exc: Exception | None
) -> None:
    project_id = context.project_id
    agent.projects.pop(project_id, None)
    agent.lifecycle_states.pop(project_id, None)


async def _persist_methodology_decision(
    agent: ProjectLifecycleAgent, context: OrchestrationContext
) -> dict[str, Any]:
    decision = context.results.get("methodology_decision") or context.payload.get(
        "project_data", {}
    )
    return agent.persistence.store_methodology_decision(
        context.tenant_id, context.project_id, decision
    )


async def _publish_project_initiated(
    agent: ProjectLifecycleAgent, context: OrchestrationContext
) -> dict[str, Any]:
    payload = {
        "project_id": context.project_id,
        "initiated_at": datetime.now(timezone.utc).isoformat(),
        "methodology": context.results.get("create_records", {}).get("methodology"),
    }
    await agent.event_bus.publish("project.initiated", payload)
    return payload


async def _sync_project_state(
    agent: ProjectLifecycleAgent, context: OrchestrationContext
) -> dict[str, Any]:
    state = (
        context.results.get("create_records", {}).get("lifecycle_state")
        or context.payload.get("project_data")
        or context.payload
    )
    results = await agent.external_sync.sync_project_state(context.project_id, state)
    return {"sync_results": [result.__dict__ for result in results]}


async def _notify_project_initiated(
    agent: ProjectLifecycleAgent, context: OrchestrationContext
) -> dict[str, Any]:
    payload = {
        "project_id": context.project_id,
        "event": "project.initiated",
        "methodology": context.results.get("create_records", {}).get("methodology"),
    }
    return await agent.notification_service.notify_project_initiated(payload)
