"""
Action handler for availability queries:
  - get_availability
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from resource_capacity_agent import ResourceCapacityAgent


async def get_availability(
    agent: ResourceCapacityAgent,
    resource_id: str,
    date_range: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """
    Get resource availability for a date range.

    Returns availability calendar.
    """
    agent.logger.info("Getting availability for resource: %s", resource_id)

    resource = agent.resource_pool.get(resource_id)
    if not resource:
        resource = agent.resource_store.get(tenant_id, resource_id)
        if resource:
            agent.resource_pool[resource_id] = resource
    if not resource:
        raise ValueError(f"Resource not found: {resource_id}")

    calendar = agent.capacity_calendar.get(resource_id, {})
    if not calendar:
        calendar = agent.calendar_store.get(tenant_id, resource_id) or {}
        if calendar:
            agent.capacity_calendar[resource_id] = calendar
    allocations = agent._load_allocations(resource_id)

    start_date_str = date_range.get("start_date")
    end_date_str = date_range.get("end_date")
    assert isinstance(start_date_str, str), "start_date must be a string"
    assert isinstance(end_date_str, str), "end_date must be a string"
    start_date = datetime.fromisoformat(start_date_str)
    end_date = datetime.fromisoformat(end_date_str)

    # Calculate availability for each day in range
    availability_by_day = []
    current_date = start_date

    while current_date <= end_date:
        day_availability = await agent._calculate_day_availability(
            resource_id, current_date, calendar, allocations
        )

        availability_by_day.append(day_availability)
        current_date += timedelta(days=1)

    return {
        "resource_id": resource_id,
        "resource_name": resource.get("name"),
        "date_range": date_range,
        "availability_by_day": availability_by_day,
        "average_availability": (
            sum(d.get("available_hours", 0) for d in availability_by_day)
            / len(availability_by_day)
            if availability_by_day
            else 0
        ),
    }
