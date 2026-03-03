"""
Action handlers for resource pool management:
  - add_resource
  - update_resource
  - delete_resource
  - get_resource_pool
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from data_quality.rules import evaluate_quality_rules

if TYPE_CHECKING:
    from resource_capacity_agent import ResourceCapacityAgent


async def add_resource(
    agent: ResourceCapacityAgent, resource_data: dict[str, Any], *, tenant_id: str
) -> dict[str, Any]:
    """
    Add a resource to the pool.

    Returns resource ID and profile.
    """
    agent.logger.info("Adding resource to pool")

    resource_id = resource_data.get("resource_id")
    assert isinstance(resource_id, str), "resource_id must be a string"
    name = resource_data.get("name")
    role = resource_data.get("role")
    skills = resource_data.get("skills", [])
    location = resource_data.get("location", "Unknown")
    cost_rate = resource_data.get("cost_rate", 0.0)
    certifications = resource_data.get("certifications", [])
    training_record = resource_data.get("training_record")
    training_metadata = {}

    # Create resource profile
    resource_profile = {
        "resource_id": resource_id,
        "name": name,
        "role": role,
        "skills": skills,
        "location": location,
        "cost_rate": cost_rate,
        "certifications": certifications,
        "availability": 1.0,  # 100% available by default
        "team_memberships": resource_data.get("team_memberships", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "training": training_metadata,
        "training_load": 0.0,
    }

    agent.resource_pool[resource_id] = resource_profile
    if training_record:
        training_metadata = await agent._apply_training_record(resource_id, training_record)
        resource_profile["training"] = training_metadata
        resource_profile["training_load"] = training_metadata.get("training_load", 0.0)

    # Initialize capacity calendar
    calendar_entry = {
        "resource_id": resource_id,
        "available_hours_per_day": resource_data.get(
            "available_hours_per_day", agent.default_working_hours_per_day
        ),
        "working_days": resource_data.get("working_days", agent.default_working_days),
        "planned_leave": resource_data.get("planned_leave", []),
        "holidays": resource_data.get("holidays", []),
    }
    agent.capacity_calendar[resource_id] = calendar_entry
    agent.calendar_store.upsert(tenant_id, resource_id, calendar_entry)
    await agent._persist_resource_schedule(
        resource_id,
        calendar_entry,
        tenant_id=tenant_id,
        availability=resource_profile.get("availability", 1.0),
    )

    validation = await _validate_resource_record(agent, resource_profile, tenant_id=tenant_id)

    # Store resource
    agent.resource_pool[resource_id] = resource_profile
    agent.resource_store.upsert(tenant_id, resource_id, resource_profile)
    canonical_profile = dict(resource_profile)
    canonical_profile.update(
        {
            "employee_id": resource_id,
            "source_system": "agent",
        }
    )
    await agent._store_canonical_profile(resource_id, canonical_profile, resource_profile)
    await agent._index_skills()
    await agent._publish_resource_event("resource.added", resource_profile)

    agent.logger.info("Added resource: %s", resource_id)

    return {
        "resource_id": resource_id,
        "profile": resource_profile,
        "status": "active",
        "data_quality": validation,
    }


async def update_resource(
    agent: ResourceCapacityAgent, resource_data: dict[str, Any], *, tenant_id: str
) -> dict[str, Any]:
    """Update resource details in the pool."""
    resource_id = resource_data.get("resource_id")
    assert isinstance(resource_id, str), "resource_id must be a string"
    existing = agent.resource_pool.get(resource_id)
    if not existing:
        return await add_resource(agent, resource_data, tenant_id=tenant_id)

    updated = {**existing, **{k: v for k, v in resource_data.items() if v is not None}}
    updated["updated_at"] = datetime.now(timezone.utc).isoformat()
    agent.resource_pool[resource_id] = updated
    agent.resource_store.upsert(tenant_id, resource_id, updated)
    canonical_profile = dict(updated)
    canonical_profile.update({"employee_id": resource_id, "source_system": "agent"})
    await agent._store_canonical_profile(resource_id, canonical_profile, updated)
    await agent._index_skills()
    await agent._publish_resource_event("resource.updated", updated)
    return {"resource_id": resource_id, "profile": updated, "status": updated.get("status")}


async def delete_resource(
    agent: ResourceCapacityAgent, resource_id: str, *, tenant_id: str
) -> dict[str, Any]:
    """Delete (deactivate) a resource from the pool."""
    if resource_id not in agent.resource_pool:
        return {"resource_id": resource_id, "status": "NotFound"}
    await agent._deactivate_resource(resource_id, reason="manual_delete")
    if agent.db_service:
        await agent.db_service.delete("resource_profiles", resource_id)
    agent.repository.delete_employee_profile(resource_id)
    return {"resource_id": resource_id, "status": "Inactive"}


async def get_resource_pool(
    agent: ResourceCapacityAgent, filters: dict[str, Any], *, tenant_id: str
) -> dict[str, Any]:
    """Retrieve resource pool data."""
    role_filter = filters.get("role")
    location_filter = filters.get("location")
    status_filter = filters.get("status", "Active")

    filtered_resources = []

    resources = list(agent.resource_pool.values())
    if not resources:
        resources = agent.resource_store.list(tenant_id)
        for resource in resources:
            resource_id = resource.get("resource_id")
            if resource_id:
                agent.resource_pool[resource_id] = resource

    for resource in resources:
        if role_filter and resource.get("role") != role_filter:
            continue
        if location_filter and resource.get("location") != location_filter:
            continue
        if status_filter and resource.get("status") != status_filter:
            continue

        filtered_resources.append(resource)

    return {
        "total_resources": len(filtered_resources),
        "resources": filtered_resources,
        "filters_applied": filters,
    }


async def _validate_resource_record(
    agent: ResourceCapacityAgent, resource_profile: dict[str, Any], *, tenant_id: str
) -> dict[str, Any]:
    record = {
        "id": resource_profile.get("resource_id"),
        "tenant_id": tenant_id,
        "name": resource_profile.get("name"),
        "role": resource_profile.get("role"),
        "location": resource_profile.get("location"),
        "status": resource_profile.get("status"),
        "created_at": resource_profile.get("created_at"),
        "metadata": {
            "skills": resource_profile.get("skills"),
            "certifications": resource_profile.get("certifications"),
            "availability": resource_profile.get("availability"),
            "cost_rate": resource_profile.get("cost_rate"),
        },
    }
    report = evaluate_quality_rules("resource", record)
    return {
        "is_valid": report.is_valid,
        "issues": [issue.__dict__ for issue in report.issues],
    }
