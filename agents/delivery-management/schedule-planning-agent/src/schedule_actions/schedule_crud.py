"""Action handlers for update_schedule and get_schedule."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from schedule_utils import (
    get_schedule_state,
    persist_schedule,
    publish_schedule_updated,
)

if TYPE_CHECKING:
    from schedule_planning_agent import SchedulePlanningAgent


async def update_schedule(
    agent: SchedulePlanningAgent,
    schedule_id: str,
    updates: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """Update schedule details and persist to canonical storage."""
    agent.logger.info("Updating schedule: %s", schedule_id)
    schedule = await get_schedule_state(agent, tenant_id, schedule_id)
    if not schedule:
        raise ValueError(f"Schedule not found: {schedule_id}")

    allowed_updates = {
        "tasks",
        "dependencies",
        "milestones",
        "status",
        "start_date",
        "end_date",
        "project_duration_days",
        "resource_assignments",
    }
    for key, value in updates.items():
        if key in allowed_updates:
            schedule[key] = value

    schedule["updated_at"] = datetime.now(timezone.utc).isoformat()
    if "dependencies" in updates:
        agent.dependencies[schedule_id] = schedule.get("dependencies", [])
    if "milestones" in updates:
        agent.milestones[schedule_id] = schedule.get("milestones", [])

    agent.schedules[schedule_id] = schedule
    agent.schedule_store.upsert(tenant_id, schedule_id, schedule)
    if agent.enable_persistence:
        await persist_schedule(agent, schedule)
    await publish_schedule_updated(agent, schedule, "schedule.updated")
    await publish_schedule_updated(agent, schedule, "schedule.change.applied")

    return {
        "schedule_id": schedule_id,
        "status": schedule.get("status"),
        "updated_at": schedule.get("updated_at"),
    }


async def get_schedule(
    agent: SchedulePlanningAgent, schedule_id: str, *, tenant_id: str
) -> dict[str, Any]:
    """Retrieve schedule by ID."""
    schedule = await get_schedule_state(agent, tenant_id, schedule_id)
    if not schedule:
        raise ValueError(f"Schedule not found: {schedule_id}")
    return schedule  # type: ignore
