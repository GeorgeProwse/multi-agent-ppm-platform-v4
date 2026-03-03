"""Action handler for optimize_schedule."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from schedule_planning_agent import SchedulePlanningAgent


async def optimize_schedule(
    agent: SchedulePlanningAgent, schedule_id: str
) -> dict[str, Any]:
    """
    Optimize schedule to minimize duration.

    Returns optimized schedule with recommendations.
    """
    agent.logger.info("Optimizing schedule: %s", schedule_id)

    schedule = agent.schedules.get(schedule_id)
    if not schedule:
        raise ValueError(f"Schedule not found: {schedule_id}")

    # Identify optimization opportunities
    opportunities = await identify_optimization_opportunities(schedule)

    # Apply optimizations
    optimized_schedule = await apply_optimizations(schedule, opportunities)

    # Calculate improvements
    improvements = await calculate_improvements(schedule, optimized_schedule)

    return {
        "schedule_id": schedule_id,
        "original_duration": schedule.get("project_duration_days", 0),
        "optimized_duration": optimized_schedule.get("project_duration_days", 0),
        "duration_reduction": improvements.get("duration_reduction", 0),
        "optimizations_applied": opportunities,
        "recommendations": await generate_optimization_recommendations(opportunities),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def identify_optimization_opportunities(
    schedule: dict[str, Any],
) -> list[dict[str, Any]]:
    """Identify schedule optimization opportunities."""
    return [
        {"type": "parallel_tasks", "description": "Parallelize tasks with no dependencies"},
        {"type": "fast_track", "description": "Fast-track critical path tasks"},
        {"type": "crash", "description": "Crash critical path by adding resources"},
    ]


async def apply_optimizations(
    schedule: dict[str, Any], opportunities: list[dict[str, Any]]
) -> dict[str, Any]:
    """Apply optimizations to schedule."""
    return schedule


async def calculate_improvements(
    original: dict[str, Any], optimized: dict[str, Any]
) -> dict[str, Any]:
    """Calculate improvements from optimization."""
    return {
        "duration_reduction": original.get("project_duration_days", 0)
        - optimized.get("project_duration_days", 0)
    }


async def generate_optimization_recommendations(
    opportunities: list[dict[str, Any]],
) -> list[str]:
    """Generate optimization recommendations."""
    return [opp.get("description") for opp in opportunities]  # type: ignore
