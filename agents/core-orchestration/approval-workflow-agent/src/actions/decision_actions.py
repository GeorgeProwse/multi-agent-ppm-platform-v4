"""
Decision recording action for the Approval Workflow Agent.

Handles recording approval/rejection decisions with audit trails,
metrics, and event publishing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from actions.notification_delivery import record_response_metric

if TYPE_CHECKING:
    from approval_workflow_agent import ApprovalWorkflowAgent


async def record_decision(
    agent: ApprovalWorkflowAgent,
    *,
    approval_id: str,
    decision: str,
    approver_id: str,
    comments: str | None,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    response_time_seconds = None
    existing = agent.approval_store.get(tenant_id, approval_id)
    if existing:
        created_at = existing.get("details", {}).get("chain", {}).get("created_at")
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at)
                response_time_seconds = (
                    datetime.now(timezone.utc) - created_dt.replace(tzinfo=timezone.utc)
                ).total_seconds()
            except ValueError:
                response_time_seconds = None
    agent.approval_store.update(
        tenant_id,
        approval_id,
        decision,
        {
            "decision": decision,
            "decided_by": approver_id,
            "decided_at": datetime.now(timezone.utc).isoformat(),
            "comments": comments,
            "response_time_seconds": response_time_seconds,
        },
    )
    agent._emit_audit_event(
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        action="approval.decision",
        outcome="success",
        resource_id=approval_id,
        metadata={
            "decision": decision,
            "approver_id": approver_id,
            "comments": comments,
            "risk_score": existing.get("details", {}).get("risk_score") if existing else None,
            "criticality_level": (
                existing.get("details", {}).get("criticality_level") if existing else None
            ),
        },
    )
    if response_time_seconds is not None:
        record_response_metric(
            agent,
            tenant_id=tenant_id,
            approval_id=approval_id,
            approver_id=approver_id,
            response_time_seconds=response_time_seconds,
            decision=decision,
        )
    agent._publish_approval_event(
        event_type="approval.decision",
        tenant_id=tenant_id,
        approval_chain=existing.get("details", {}).get("chain") if existing else {},
        payload={
            "approval_id": approval_id,
            "decision": decision,
            "approver_id": approver_id,
            "comments": comments,
        },
    )
    request_type = existing.get("details", {}).get("request_type") if existing else None
    request_id = existing.get("details", {}).get("request_id") if existing else None
    request_details = existing.get("details", {}).get("request_details") if existing else {}
    if decision == "approved" and request_type == "resource_optimization":
        optimization_id = None
        if isinstance(request_details, dict):
            optimization_id = request_details.get("optimization_id")
        agent._emit_audit_event(
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            action="resource.optimization.approved",
            outcome="success",
            resource_id=request_id or approval_id,
            metadata={
                "approval_id": approval_id,
                "request_id": request_id,
                "optimization_id": optimization_id,
                "approver_id": approver_id,
            },
        )
    if decision in {"approved", "rejected"}:
        agent._publish_approval_event(
            event_type=f"approval.{decision}",
            tenant_id=tenant_id,
            approval_chain=existing.get("details", {}).get("chain") if existing else {},
            payload={
                "approval_id": approval_id,
                "approver_id": approver_id,
                "comments": comments,
            },
        )
    return {
        "approval_id": approval_id,
        "decision": decision,
        "status": decision,
        "metadata": {
            "risk_score": existing.get("details", {}).get("risk_score") if existing else None,
            "criticality_level": (
                existing.get("details", {}).get("criticality_level") if existing else None
            ),
        },
    }
