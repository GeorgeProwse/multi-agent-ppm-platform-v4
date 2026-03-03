"""Action handler for aggregating benefits across program projects."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from program_management_agent import ProgramManagementAgent


async def handle_aggregate_benefits(
    agent: ProgramManagementAgent,
    program_id: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """
    Aggregate benefits across program projects.

    Returns consolidated benefits and realized value.
    """
    agent.logger.info("Aggregating benefits for program: %s", program_id)

    program = agent.program_store.get(tenant_id, program_id)
    if not program:
        raise ValueError(f"Program not found: {program_id}")

    constituent_projects = program.get("constituent_projects", [])

    # Query benefits from each project
    project_benefits = await agent._get_project_benefits(constituent_projects)

    # Aggregate financial benefits
    total_benefits = sum(pb.get("total_benefits", 0) for pb in project_benefits.values())
    total_costs = sum(pb.get("total_costs", 0) for pb in project_benefits.values())

    # Calculate program-level ROI
    program_roi = (total_benefits - total_costs) / total_costs if total_costs > 0 else 0

    # Identify overlapping benefits (to avoid double-counting)
    adjusted_benefits = await _adjust_for_overlaps(project_benefits)
    if agent.db_service:
        await agent.db_service.store(
            "program_benefits",
            program_id,
            {
                "program_id": program_id,
                "total_benefits": total_benefits,
                "adjusted_benefits": adjusted_benefits,
                "total_costs": total_costs,
                "program_roi": program_roi,
                "project_benefits": project_benefits,
            },
        )

    return {
        "program_id": program_id,
        "total_benefits": total_benefits,
        "adjusted_benefits": adjusted_benefits,
        "total_costs": total_costs,
        "program_roi": program_roi,
        "project_benefits": project_benefits,
        "benefit_categories": await _categorize_benefits(project_benefits),
        "realization_timeline": await _generate_benefit_timeline(project_benefits),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _adjust_for_overlaps(project_benefits: dict[str, Any]) -> float:
    """Adjust benefits for overlaps to avoid double-counting."""
    total = sum(pb.get("total_benefits", 0) for pb in project_benefits.values())
    if total <= 0:
        return 0.0

    overlap_groups: dict[str, list[str]] = {}
    for project_id, benefit in project_benefits.items():
        breakdown = benefit.get("benefit_breakdown") or benefit.get("benefits") or {}
        overlap_key = (
            breakdown.get("overlap_key")
            or breakdown.get("initiative")
            or benefit.get("overlap_key")
            or benefit.get("initiative")
        )
        if overlap_key:
            overlap_groups.setdefault(str(overlap_key), []).append(project_id)

    if not overlap_groups:
        return total

    penalty = 0.0
    for projects in overlap_groups.values():
        if len(projects) > 1:
            penalty += min(0.25, 0.05 * (len(projects) - 1))

    penalty = min(0.35, penalty)
    return total * (1 - penalty)


async def _categorize_benefits(project_benefits: dict[str, Any]) -> dict[str, float]:
    """Categorize benefits by type."""
    categories = {
        "revenue_increase": 0.0,
        "cost_savings": 0.0,
        "risk_reduction": 0.0,
        "efficiency_gains": 0.0,
    }
    for benefit in project_benefits.values():
        breakdown = benefit.get("benefit_breakdown") or benefit.get("benefits") or {}
        categories["revenue_increase"] += breakdown.get("revenue_increase", 0)
        categories["cost_savings"] += breakdown.get("cost_savings", 0)
        categories["risk_reduction"] += breakdown.get("risk_reduction", 0)
        categories["efficiency_gains"] += breakdown.get("efficiency_gains", 0)
    return categories


async def _generate_benefit_timeline(
    project_benefits: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate benefit realization timeline."""
    return []
