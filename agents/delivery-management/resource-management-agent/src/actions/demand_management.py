"""
Action handlers for demand management:
  - request_resource
  - approve_request
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from resource_capacity_agent import ResourceCapacityAgent


async def request_resource(
    agent: ResourceCapacityAgent, request_data: dict[str, Any], *, tenant_id: str
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
    candidates = await agent._match_skills(required_skills, {"project_id": project_id})

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
    approver = await agent._determine_approver(request)
    approval_payload = {}
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


async def approve_request(
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
        allocation = await agent._allocate_resource(
            {
                "resource_id": selected_resource,
                "project_id": request.get("project_id"),
                "start_date": request.get("start_date"),
                "end_date": request.get("end_date"),
                "allocation_percentage": request.get("effort", 1.0) * 100,
            }
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
