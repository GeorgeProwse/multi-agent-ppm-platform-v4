"""Action handler for generating program roadmaps."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from events import ProgramRoadmapUpdatedEvent
from observability.tracing import get_trace_id

if TYPE_CHECKING:
    from program_management_agent import ProgramManagementAgent


async def handle_generate_roadmap(
    agent: ProgramManagementAgent,
    program_id: str,
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """
    Generate integrated program roadmap.

    Returns roadmap with milestones, dependencies, and timelines.
    """
    agent.logger.info("Generating roadmap for program: %s", program_id)

    program = agent.program_store.get(tenant_id, program_id)
    if not program:
        raise ValueError(f"Program not found: {program_id}")

    constituent_projects = program.get("constituent_projects", [])

    # Query project schedules from Schedule & Planning Agent
    project_schedules = await agent._get_project_schedules(constituent_projects)

    # Query resource allocations for overlap detection
    resource_allocations = await agent._get_resource_allocations(constituent_projects)

    # Identify inter-project dependencies
    dependencies = await agent._identify_dependencies(
        constituent_projects,
        schedules=project_schedules,
        resource_allocations=resource_allocations,
    )

    # Calculate critical path across program
    critical_path = await agent._calculate_program_critical_path(project_schedules, dependencies)

    # Generate milestone timeline
    milestones = await _generate_program_milestones(project_schedules, dependencies)

    # Create roadmap visualization data
    roadmap = {
        "program_id": program_id,
        "milestones": milestones,
        "dependencies": dependencies,
        "critical_path": critical_path,
        "project_timelines": project_schedules,
        "resource_allocations": resource_allocations,
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": datetime.now(timezone.utc).isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    agent.roadmap_store.upsert(tenant_id, program_id, roadmap)
    agent.dependency_store.upsert(
        tenant_id, program_id, {"program_id": program_id, "dependencies": dependencies}
    )
    await agent._create_dependency_graph(program_id, dependencies, tenant_id=tenant_id)
    if agent.db_service:
        await agent.db_service.store("program_roadmaps", program_id, roadmap)
        await agent.db_service.store(
            "program_dependencies",
            program_id,
            {"program_id": program_id, "dependencies": dependencies},
        )

    await _publish_program_roadmap_updated(
        agent,
        roadmap,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
    )

    return roadmap


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _generate_program_milestones(
    schedules: dict[str, Any], dependencies: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Generate program-level milestones."""
    milestones = []
    for project_id, schedule in schedules.items():
        start = schedule.get("start")
        end = schedule.get("end")
        if start:
            milestones.append({"project_id": project_id, "milestone": "Start", "date": start})
        if end:
            milestones.append({"project_id": project_id, "milestone": "Finish", "date": end})
    return milestones


async def _publish_program_roadmap_updated(
    agent: ProgramManagementAgent,
    roadmap: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> None:
    event = ProgramRoadmapUpdatedEvent(
        event_name="program.roadmap.updated",
        event_id=f"evt-{uuid.uuid4().hex}",
        timestamp=datetime.now(timezone.utc),
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        trace_id=get_trace_id(),
        payload={
            "program_id": roadmap.get("program_id", ""),
            "roadmap_id": roadmap.get("program_id", ""),
            "updated_at": datetime.fromisoformat(roadmap.get("generated_at")),
            "milestone_count": len(roadmap.get("milestones", [])),
        },
    )
    await agent.event_bus.publish("program.roadmap.updated", event.model_dump())
