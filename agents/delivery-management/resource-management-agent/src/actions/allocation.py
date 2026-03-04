"""
Action handler for resource allocation:
  - allocate_resource
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from resource_capacity_agent import ResourceCapacityAgent


async def allocate_resource(
    agent: ResourceCapacityAgent,
    allocation_data: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """
    Allocate a resource to a project/task.

    Returns allocation ID and updated capacity.
    """
    agent.logger.info("Allocating resource")

    # Generate unique allocation ID
    allocation_id = await agent._generate_allocation_id()

    resource_id = allocation_data.get("resource_id")
    project_id = allocation_data.get("project_id")
    start_date = allocation_data.get("start_date")
    end_date = allocation_data.get("end_date")
    allocation_percentage = allocation_data.get("allocation_percentage", 100)

    assert isinstance(resource_id, str), "resource_id must be a string"
    assert isinstance(start_date, str), "start_date must be a string"
    assert isinstance(end_date, str), "end_date must be a string"

    lock_key = f"resource_allocation_lock:{resource_id}"
    lock_acquired = await agent._acquire_lock(lock_key, ttl_seconds=15)
    if not lock_acquired:
        raise RuntimeError("Allocation is already being processed for this resource.")

    try:
        validation = await agent._validate_allocation(
            resource_id, start_date, end_date, allocation_percentage
        )

        if not validation.get("valid"):
            raise ValueError(f"Invalid allocation: {validation.get('reason')}")

        allocation = {
            "allocation_id": allocation_id,
            "resource_id": resource_id,
            "project_id": project_id,
            "start_date": start_date,
            "end_date": end_date,
            "allocation_percentage": allocation_percentage,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if resource_id not in agent.allocations:
            agent.allocations[resource_id] = []
        agent.allocations[resource_id].append(allocation)
        agent.allocation_store.upsert(tenant_id, allocation_id, allocation)
        agent.repository.upsert_capacity_allocation(allocation)
        if agent.redis_client:
            agent.redis_client.set(
                f"allocation:{allocation_id}", json.dumps(allocation), ex=3600
            )
            agent.redis_client.rpush(
                f"resource_allocations:{resource_id}", json.dumps(allocation)
            )

        await agent._update_resource_availability(resource_id)

        await agent._publish_allocation_event(
            allocation, tenant_id=tenant_id, correlation_id=correlation_id
        )
        await agent._publish_resource_event("resource.allocation.created", allocation)

        agent.logger.info("Created allocation: %s", allocation_id)

        return allocation
    finally:
        await agent._release_lock(lock_key)
