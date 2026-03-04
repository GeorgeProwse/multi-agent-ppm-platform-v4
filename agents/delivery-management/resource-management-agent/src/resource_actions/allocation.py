"""Action handlers: add_resource, update_resource, delete_resource, request_resource,
approve_request, allocate_resource."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from resource_actions.helpers import (
    apply_training_record,
    determine_approver,
    store_canonical_profile,
    update_resource_availability,
    validate_allocation,
)

if TYPE_CHECKING:
    from resource_capacity_agent import ResourceCapacityAgent


async def handle_add_resource(
    agent: ResourceCapacityAgent,
    resource_data: dict[str, Any],
    *,
    tenant_id: str,
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
    training_metadata: dict[str, Any] = {}

    # Create resource profile
    resource_profile: dict[str, Any] = {
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
        training_metadata = await apply_training_record(agent, resource_id, training_record)
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

    validation = await agent._validate_resource_record(resource_profile, tenant_id=tenant_id)

    # Store resource
    agent.resource_pool[resource_id] = resource_profile
    agent.resource_store.upsert(tenant_id, resource_id, resource_profile)
    canonical_profile = dict(resource_profile)
    canonical_profile.update({"employee_id": resource_id, "source_system": "agent"})
    await store_canonical_profile(agent, resource_id, canonical_profile, resource_profile)
    await agent._index_skills()
    await agent._publish_resource_event("resource.added", resource_profile)

    agent.logger.info("Added resource: %s", resource_id)

    return {
        "resource_id": resource_id,
        "profile": resource_profile,
        "status": "active",
        "data_quality": validation,
    }


async def handle_update_resource(
    agent: ResourceCapacityAgent,
    resource_data: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """Update resource details in the pool."""
    resource_id = resource_data.get("resource_id")
    assert isinstance(resource_id, str), "resource_id must be a string"
    existing = agent.resource_pool.get(resource_id)
    if not existing:
        return await handle_add_resource(agent, resource_data, tenant_id=tenant_id)

    updated = {**existing, **{k: v for k, v in resource_data.items() if v is not None}}
    updated["updated_at"] = datetime.now(timezone.utc).isoformat()
    agent.resource_pool[resource_id] = updated
    agent.resource_store.upsert(tenant_id, resource_id, updated)
    canonical_profile = dict(updated)
    canonical_profile.update({"employee_id": resource_id, "source_system": "agent"})
    await store_canonical_profile(agent, resource_id, canonical_profile, updated)
    await agent._index_skills()
    await agent._publish_resource_event("resource.updated", updated)
    return {"resource_id": resource_id, "profile": updated, "status": updated.get("status")}


async def handle_delete_resource(
    agent: ResourceCapacityAgent,
    resource_id: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """Delete (deactivate) a resource from the pool."""
    if resource_id not in agent.resource_pool:
        return {"resource_id": resource_id, "status": "NotFound"}
    await agent._deactivate_resource(resource_id, reason="manual_delete")
    if agent.db_service:
        await agent.db_service.delete("resource_profiles", resource_id)
    agent.repository.delete_employee_profile(resource_id)
    return {"resource_id": resource_id, "status": "Inactive"}


async def handle_request_resource(
    agent: ResourceCapacityAgent,
    request_data: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """
    Submit a resource request.

    Returns request ID and recommended resources.
    """
    agent.logger.info("Processing resource request")

    # Generate unique request ID
    request_id = await agent._generate_request_id()

    project_id = request_data.get("project_id")
    required_skills = request_data.get("required_skills", [])
    start_date = request_data.get("start_date")
    end_date = request_data.get("end_date")
    effort = request_data.get("effort", 1.0)  # FTE

    assert isinstance(start_date, str), "start_date must be a string"
    assert isinstance(end_date, str), "end_date must be a string"

    # Match skills and find candidates
    from resource_actions.reporting import handle_match_skills

    candidates = await handle_match_skills(agent, required_skills, {"project_id": project_id})

    # Check availability for each candidate
    available_candidates = []
    for candidate in candidates.get("candidates", []):
        availability = await agent._check_availability(
            candidate["resource_id"], start_date, end_date, effort
        )
        if availability.get("is_available"):
            candidate["availability_windows"] = availability.get("windows", [])
            available_candidates.append(candidate)

    # Create request record
    request = {
        "request_id": request_id,
        "project_id": project_id,
        "project_role": request_data.get("project_role"),
        "project_roles": request_data.get("project_roles", []),
        "required_skills": required_skills,
        "start_date": start_date,
        "end_date": end_date,
        "effort": effort,
        "requested_by": request_data.get("requested_by", "unknown"),
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "status": "Pending",
        "recommended_candidates": available_candidates,
    }

    # Store request
    agent.demand_requests[request_id] = request

    # Route to approver
    approver = await determine_approver(agent, request)
    approval_payload: dict[str, Any] = {}
    if agent.approval_client:
        approval_payload = await agent.approval_client.request_approval(
            request,
            tenant_id=tenant_id,
            correlation_id=request_id,
            approver_hint=approver,
        )
        request["approval_id"] = approval_payload.get("approval_id")
        request["approval_status"] = approval_payload.get("status")

    if agent.db_service:
        await agent.db_service.store("resource_requests", request_id, request)
    await agent._publish_resource_event("resource.request.created", request)
    await agent._notify_requester(request)

    agent.logger.info("Created resource request: %s", request_id)

    return {
        "request_id": request_id,
        "status": "Pending",
        "recommended_candidates": available_candidates,
        "approver": approver,
        "approval": approval_payload,
        "next_steps": f"Request routed to {approver} for approval",
    }


async def handle_approve_request(
    agent: ResourceCapacityAgent,
    request_id: str,
    approval_decision: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """
    Approve or reject a resource request.

    Returns approval status and allocation if approved.
    """
    agent.logger.info("Processing approval for request: %s", request_id)

    request = agent.demand_requests.get(request_id)
    if not request:
        raise ValueError(f"Request not found: {request_id}")

    approved = approval_decision.get("approved", False)
    selected_resource = approval_decision.get("selected_resource_id")
    comments = approval_decision.get("comments", "")
    approver_id = approval_decision.get("approver_id", "unknown")
    approval_id = request.get("approval_id")
    if approval_id and agent.approval_client:
        await agent.approval_client.record_decision(
            approval_id,
            decision="approved" if approved else "rejected",
            approver_id=approver_id,
            comments=comments,
            tenant_id=tenant_id,
            correlation_id=request_id,
        )

    if approved and selected_resource:
        # Create allocation
        allocation = await handle_allocate_resource(
            agent,
            {
                "resource_id": selected_resource,
                "project_id": request.get("project_id"),
                "start_date": request.get("start_date"),
                "end_date": request.get("end_date"),
                "allocation_percentage": request.get("effort", 1.0) * 100,
            },
            tenant_id=tenant_id,
            correlation_id=request_id,
        )

        request["status"] = "Approved"
        request["approved_at"] = datetime.now(timezone.utc).isoformat()
        request["allocated_resource"] = selected_resource
        request["allocation_id"] = allocation.get("allocation_id")

        # Notify Schedule & Planning Agent
        await agent._publish_resource_event("resource.request.approved", request)
        await agent._notify_requester(request)
        await agent._notify_project_manager(request)

        return {
            "request_id": request_id,
            "status": "Approved",
            "allocation": allocation,
            "comments": comments,
        }
    else:
        request["status"] = "Rejected"
        request["rejected_at"] = datetime.now(timezone.utc).isoformat()
        request["rejection_reason"] = comments

        await agent._publish_resource_event("resource.request.rejected", request)
        await agent._notify_requester(request)

        return {"request_id": request_id, "status": "Rejected", "rejection_reason": comments}


async def handle_allocate_resource(
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
        validation = await validate_allocation(
            agent, resource_id, start_date, end_date, allocation_percentage
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

        await update_resource_availability(agent, resource_id)

        await agent._publish_allocation_event(
            allocation, tenant_id=tenant_id, correlation_id=correlation_id
        )
        await agent._publish_resource_event("resource.allocation.created", allocation)

        agent.logger.info("Created allocation: %s", allocation_id)

        return allocation
    finally:
        await agent._release_lock(lock_key)
