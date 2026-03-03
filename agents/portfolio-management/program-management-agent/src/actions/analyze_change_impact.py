"""Action handler for analyzing change impact across the program."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from program_management_agent import ProgramManagementAgent


async def handle_analyze_change_impact(
    agent: ProgramManagementAgent,
    program_id: str,
    change: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """
    Analyze impact of changes across the program.

    Returns impact assessment and mitigation options.
    """
    agent.logger.info("Analyzing change impact for program: %s", program_id)

    program = agent.program_store.get(tenant_id, program_id)
    if not program:
        raise ValueError(f"Program not found: {program_id}")

    change_type = change.get("type", "scope")
    affected_project = change.get("project_id")
    change_details = change.get("details", {})

    # Get dependencies for affected project
    dependencies = await agent._get_project_dependencies(program_id, affected_project)  # type: ignore

    # Analyze cascading effects
    cascading_effects = await _analyze_cascading_effects(
        affected_project, dependencies, change_details  # type: ignore
    )

    # Calculate schedule impact
    schedule_impact = await _calculate_schedule_impact(cascading_effects, change_details)

    # Calculate cost impact
    cost_impact = await _calculate_cost_impact(cascading_effects, change_details)

    # Generate mitigation options
    mitigation_options = await _generate_mitigation_options(
        cascading_effects, schedule_impact, cost_impact
    )

    return {
        "program_id": program_id,
        "change_type": change_type,
        "affected_project": affected_project,
        "cascading_effects": cascading_effects,
        "schedule_impact": schedule_impact,
        "cost_impact": cost_impact,
        "mitigation_options": mitigation_options,
        "recommendation": await _select_best_mitigation(mitigation_options),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _analyze_cascading_effects(
    project_id: str, dependencies: list[dict[str, Any]], change_details: dict[str, Any]
) -> list[dict[str, Any]]:
    """Analyze cascading effects of a change."""
    cascading_effects = []
    delay_days = int(change_details.get("delay_days", 5))
    cost_delta = float(change_details.get("cost_delta", 0))

    for dependency in dependencies:
        predecessor = dependency.get("predecessor")
        successor = dependency.get("successor")
        if predecessor == project_id:
            impacted = successor
            direction = "downstream"
        elif successor == project_id:
            impacted = predecessor
            direction = "upstream"
        else:
            continue

        cascading_effects.append(
            {
                "impacted_project_id": impacted,
                "direction": direction,
                "dependency_type": dependency.get("type"),
                "schedule_delay_days": delay_days,
                "cost_delta": cost_delta,
                "shared_resources": dependency.get("shared_resources", []),
            }
        )

    return cascading_effects


async def _calculate_schedule_impact(
    cascading_effects: list[dict[str, Any]], change_details: dict[str, Any]
) -> dict[str, Any]:
    """Calculate schedule impact from changes."""
    return {"delay_days": 0, "affected_milestones": []}


async def _calculate_cost_impact(
    cascading_effects: list[dict[str, Any]], change_details: dict[str, Any]
) -> dict[str, Any]:
    """Calculate cost impact from changes."""
    return {"additional_cost": 0, "affected_budgets": []}


async def _generate_mitigation_options(
    cascading_effects: list[dict[str, Any]],
    schedule_impact: dict[str, Any],
    cost_impact: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate mitigation options."""
    return [
        {
            "option": "Parallelize dependent tasks",
            "schedule_reduction": "5 days",
            "cost": "$10,000",
        },
        {
            "option": "Add resources to critical path",
            "schedule_reduction": "10 days",
            "cost": "$25,000",
        },
        {
            "option": "Accept delay and adjust roadmap",
            "schedule_reduction": "0 days",
            "cost": "$0",
        },
    ]


async def _select_best_mitigation(options: list[dict[str, Any]]) -> str:
    """Select the best mitigation option."""
    if not options:
        return "No mitigation needed"

    def _parse_days(value: str) -> float:
        digits = "".join(ch for ch in value if ch.isdigit() or ch == ".")
        return float(digits) if digits else 0.0

    def _parse_cost(value: str) -> float:
        digits = "".join(ch for ch in value if ch.isdigit() or ch == ".")
        return float(digits) if digits else 0.0

    scored = []
    for option in options:
        reduction = _parse_days(str(option.get("schedule_reduction", "0")))
        cost = _parse_cost(str(option.get("cost", "0")))
        score = reduction - (cost / 10000)
        scored.append((score, option))

    best_option = max(scored, key=lambda item: item[0])[1]
    return best_option.get("option", options[0].get("option", "No mitigation needed"))
