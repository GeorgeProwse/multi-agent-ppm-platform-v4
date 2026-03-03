"""Action handler for coordinating resource allocation across projects."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from program_utils import flatten_resource_allocations

if TYPE_CHECKING:
    from program_management_agent import ProgramManagementAgent


async def handle_coordinate_resources(
    agent: ProgramManagementAgent,
    program_id: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """
    Coordinate resource allocation across projects.

    Returns resource allocation recommendations and conflict resolution.
    """
    agent.logger.info("Coordinating resources for program: %s", program_id)

    program = agent.program_store.get(tenant_id, program_id)
    if not program:
        raise ValueError(f"Program not found: {program_id}")

    constituent_projects = program.get("constituent_projects", [])

    # Query resource allocations from Resource Management Agent
    resource_allocations = await agent._get_resource_allocations(constituent_projects)

    # Identify resource conflicts
    conflicts = await _identify_resource_conflicts(resource_allocations)

    # Generate optimization recommendations
    recommendations = await _optimize_resource_allocation(resource_allocations, conflicts)

    # Calculate utilization across program
    utilization = await _calculate_program_utilization(resource_allocations)

    return {
        "program_id": program_id,
        "resource_allocations": resource_allocations,
        "conflicts": conflicts,
        "recommendations": recommendations,
        "utilization": utilization,
        "shared_resources": await _identify_shared_resources(resource_allocations),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _identify_resource_conflicts(
    allocations: dict[str, Any],
) -> list[dict[str, Any]]:
    """Identify resource allocation conflicts."""
    resource_usage: dict[str, list[str]] = {}
    for project_id, allocation in allocations.items():
        for resource in flatten_resource_allocations(allocation):
            resource_usage.setdefault(resource, []).append(project_id)

    conflicts = []
    for resource, projects in resource_usage.items():
        if len(projects) > 1:
            conflicts.append(
                {
                    "resource": resource,
                    "projects": projects,
                    "severity": "high" if len(projects) >= 3 else "medium",
                }
            )
    return conflicts


async def _optimize_resource_allocation(
    allocations: dict[str, Any], conflicts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Generate resource optimization recommendations."""
    recommendations: list[dict[str, Any]] = []
    for conflict in conflicts:
        projects = conflict.get("projects", [])
        recommendations.append(
            {
                "resource": conflict.get("resource"),
                "action": "stagger_assignments",
                "projects": projects,
                "rationale": "Reduce simultaneous contention for shared resources",
            }
        )
        recommendations.append(
            {
                "resource": conflict.get("resource"),
                "action": "augment_capacity",
                "projects": projects,
                "rationale": "Consider adding temporary capacity or contractors",
            }
        )
    if not conflicts:
        recommendations.append(
            {
                "action": "maintain_allocation",
                "rationale": "Resource usage appears balanced across projects",
            }
        )
    return recommendations


async def _calculate_program_utilization(allocations: dict[str, Any]) -> float:
    """Calculate average utilization across program."""
    if not allocations:
        return 0.0
    resource_usage: dict[str, int] = {}
    for allocation in allocations.values():
        resources = flatten_resource_allocations(allocation)
        for resource in resources:
            resource_usage[resource] = resource_usage.get(resource, 0) + 1
    shared_resources = sum(1 for count in resource_usage.values() if count > 1)
    utilization = shared_resources / max(1, len(resource_usage))
    return round(min(1.0, 0.5 + utilization * 0.5), 2)


async def _identify_shared_resources(allocations: dict[str, Any]) -> list[dict[str, Any]]:
    """Identify resources shared across multiple projects."""
    resource_usage: dict[str, list[str]] = {}
    for project_id, allocation in allocations.items():
        for resource in flatten_resource_allocations(allocation):
            resource_usage.setdefault(resource, []).append(project_id)

    return [
        {"resource": resource, "projects": projects}
        for resource, projects in resource_usage.items()
        if len(projects) > 1
    ]
