"""Action handler for phase transitions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from orchestration import (
    DurableTask,
    DurableWorkflow,
    OrchestrationContext,
    RetryPolicy,
)

from lifecycle_utils import get_gate_name, get_lifecycle_state, publish_project_transitioned

if TYPE_CHECKING:
    from project_lifecycle_agent import ProjectLifecycleAgent


async def transition_phase(
    agent: ProjectLifecycleAgent,
    project_id: str,
    target_phase: str,
    *,
    tenant_id: str,
    correlation_id: str,
    actor_id: str,
) -> dict[str, Any]:
    """
    Transition project to a new phase.

    Returns transition status and gate evaluation results.
    """
    agent.logger.info("Attempting phase transition for project: %s", project_id)

    lifecycle_state = await get_lifecycle_state(agent, tenant_id, project_id)
    if not lifecycle_state:
        raise ValueError(f"Lifecycle state not found for project: {project_id}")

    current_phase = lifecycle_state.get("current_phase")
    methodology_map = lifecycle_state.get("methodology_map", {})

    # Validate transition is allowed
    allowed_transitions = (
        methodology_map.get("phases", {}).get(current_phase, {}).get("next_phases", [])
    )
    if target_phase not in allowed_transitions:
        return {
            "success": False,
            "reason": f"Invalid transition from {current_phase} to {target_phase}",
            "allowed_transitions": allowed_transitions,
        }

    # Get gate name for this transition
    gate_name_val = await get_gate_name(current_phase, target_phase)

    # Evaluate gate criteria
    from lifecycle_actions.evaluate_gate import evaluate_gate

    gate_evaluation = await evaluate_gate(agent, project_id, gate_name_val, tenant_id=tenant_id)

    # Check if gate criteria are met
    if not gate_evaluation.get("criteria_met"):
        return {
            "success": False,
            "reason": "Gate criteria not met",
            "gate_evaluation": gate_evaluation,
            "missing_criteria": gate_evaluation.get("missing_criteria", []),
            "next_steps": "Complete missing activities or request override",
        }

    # Perform transition
    workflow = DurableWorkflow(
        name="phase_transition",
        tasks=[
            DurableTask(
                name="apply_transition",
                action=lambda ctx: _apply_phase_transition(agent, ctx),
                compensation=lambda ctx, exc: _rollback_phase_transition(agent, ctx, exc),
            ),
            DurableTask(
                name="persist_lifecycle",
                action=lambda ctx: _persist_lifecycle_state(agent, ctx),
            ),
            DurableTask(
                name="publish_phase_change",
                action=lambda ctx: _publish_phase_changed(agent, ctx),
            ),
            DurableTask(
                name="sync_project_state",
                action=lambda ctx: _sync_project_state(agent, ctx),
                retry_policy=RetryPolicy(max_attempts=3),
            ),
        ],
        sleep=agent.orchestrator_sleep,
    )
    context = OrchestrationContext(
        workflow_id=f"phase-{project_id}-{target_phase}",
        tenant_id=tenant_id,
        project_id=project_id,
        correlation_id=correlation_id,
        payload={
            "target_phase": target_phase,
            "gate_name": gate_name_val,
            "actor_id": actor_id,
        },
        metadata={"gate_evaluation": gate_evaluation},
    )
    context = await agent.workflow_engine.run(workflow, context)
    transition_record = context.results["apply_transition"]

    agent.logger.info(
        "Transitioned project %s from %s to %s", project_id, current_phase, target_phase
    )

    return {
        "success": True,
        "project_id": project_id,
        "previous_phase": current_phase,
        "current_phase": target_phase,
        "gate_evaluation": gate_evaluation,
        "transition_record": transition_record,
    }


# ---------------------------------------------------------------------------
# Workflow task functions
# ---------------------------------------------------------------------------


async def _apply_phase_transition(
    agent: ProjectLifecycleAgent, context: OrchestrationContext
) -> dict[str, Any]:
    project_id = context.project_id
    target_phase = context.payload.get("target_phase")
    gate_name = context.payload.get("gate_name")
    actor_id = context.payload.get("actor_id")
    lifecycle_state = await get_lifecycle_state(agent, context.tenant_id, project_id)
    if not lifecycle_state:
        raise ValueError(f"Lifecycle state not found for project: {project_id}")
    current_phase = lifecycle_state.get("current_phase")
    transition_record = {
        "from_phase": current_phase,
        "to_phase": target_phase,
        "gate_name": gate_name,
        "transitioned_at": datetime.now(timezone.utc).isoformat(),
        "transitioned_by": actor_id,
    }
    lifecycle_state["current_phase"] = target_phase
    lifecycle_state["phase_start_date"] = datetime.now(timezone.utc).isoformat()
    lifecycle_state["transitions"].append(transition_record)
    lifecycle_state["gates_passed"].append(gate_name)
    agent.projects[project_id]["current_phase"] = target_phase
    agent.projects[project_id]["phase_history"].append(transition_record)
    agent.lifecycle_store.upsert(context.tenant_id, project_id, lifecycle_state)
    context.metadata["previous_phase"] = current_phase
    return transition_record


async def _rollback_phase_transition(
    agent: ProjectLifecycleAgent, context: OrchestrationContext, _exc: Exception | None
) -> None:
    project_id = context.project_id
    lifecycle_state = await get_lifecycle_state(agent, context.tenant_id, project_id)
    if not lifecycle_state:
        return
    previous_phase = context.metadata.get("previous_phase")
    if previous_phase:
        lifecycle_state["current_phase"] = previous_phase
        lifecycle_state["phase_start_date"] = datetime.now(timezone.utc).isoformat()
        agent.projects[project_id]["current_phase"] = previous_phase
        agent.lifecycle_store.upsert(context.tenant_id, project_id, lifecycle_state)


async def _persist_lifecycle_state(
    agent: ProjectLifecycleAgent, context: OrchestrationContext
) -> dict[str, Any]:
    lifecycle_state = await get_lifecycle_state(agent, context.tenant_id, context.project_id)
    if not lifecycle_state:
        raise ValueError("Lifecycle state not found for persistence")
    return agent.persistence.store_lifecycle_state(
        context.tenant_id, context.project_id, lifecycle_state
    )


async def _publish_phase_changed(
    agent: ProjectLifecycleAgent, context: OrchestrationContext
) -> dict[str, Any]:
    transition_record = context.results.get("apply_transition", {})
    await publish_project_transitioned(
        agent,
        context.project_id,
        transition_record.get("from_phase"),
        transition_record.get("to_phase"),
        transition_record.get("transitioned_by", "system"),
        tenant_id=context.tenant_id,
        correlation_id=context.correlation_id,
    )
    await agent.event_bus.publish(
        "phase.changed",
        {
            "project_id": context.project_id,
            "from_phase": transition_record.get("from_phase"),
            "to_phase": transition_record.get("to_phase"),
            "gate_name": transition_record.get("gate_name"),
        },
    )
    return {"status": "published"}


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
