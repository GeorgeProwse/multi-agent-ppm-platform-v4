"""Action handler for gate overrides."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from lifecycle_utils import get_lifecycle_state

if TYPE_CHECKING:
    from project_lifecycle_agent import ProjectLifecycleAgent


async def override_gate(
    agent: ProjectLifecycleAgent,
    project_id: str,
    gate_name: str,
    override_reason: str,
    *,
    tenant_id: str,
    correlation_id: str,
    requester: str,
) -> dict[str, Any]:
    """
    Override a gate that doesn't meet criteria.

    Returns override confirmation and audit record.
    """
    agent.logger.info("Overriding gate '%s' for project: %s", gate_name, project_id)

    # Evaluate gate first to document what's being overridden
    from lifecycle_actions.evaluate_gate import evaluate_gate

    gate_evaluation = await evaluate_gate(agent, project_id, gate_name, tenant_id=tenant_id)

    approval_response = await _request_override_approval(
        agent,
        project_id=project_id,
        gate_name=gate_name,
        override_reason=override_reason,
        gate_evaluation=gate_evaluation,
        requester=requester,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
    )

    # Create override record
    override_record = {
        "project_id": project_id,
        "gate_name": gate_name,
        "gate_evaluation": gate_evaluation,
        "override_reason": override_reason,
        "overridden_by": requester,
        "overridden_at": datetime.now(timezone.utc).isoformat(),
        "approval_id": approval_response.get("approval_id"),
        "approval_status": approval_response.get("status"),
    }

    # Mark gate as passed despite not meeting criteria
    lifecycle_state = await get_lifecycle_state(agent, tenant_id, project_id)
    if lifecycle_state and approval_response.get("status") == "approved":
        lifecycle_state["gates_passed"].append(f"{gate_name} (OVERRIDDEN)")
        agent.lifecycle_store.upsert(tenant_id, project_id, lifecycle_state)

    await agent.event_bus.publish("gate.overridden", override_record)
    await agent.external_sync.sync_gate_decision(
        project_id, gate_name, {"override": True, **override_record}
    )
    await agent.notification_service.notify_gate_decision(
        {"project_id": project_id, "gate_name": gate_name, "event": "gate.overridden"}
    )

    agent.logger.warning("Gate override recorded for %s: %s", project_id, gate_name)

    return {
        "success": approval_response.get("status") == "approved",
        "override_record": override_record,
        "warning": "Gate criteria were not met. Override has been recorded for audit.",
        "approval": approval_response,
    }


async def _request_override_approval(
    agent: ProjectLifecycleAgent,
    *,
    project_id: str,
    gate_name: str,
    override_reason: str,
    gate_evaluation: dict[str, Any],
    requester: str,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    if not agent.approval_agent:
        return {"status": "skipped", "reason": "approval_agent_not_configured"}
    response = await agent.approval_agent.process(
        {
            "request_type": "phase_gate",
            "request_id": f"{project_id}:{gate_name}:override",
            "requester": requester,
            "details": {
                "project_id": project_id,
                "gate_name": gate_name,
                "override_reason": override_reason,
                "gate_evaluation": gate_evaluation,
            },
            "tenant_id": tenant_id,
            "correlation_id": correlation_id,
            "context": {"tenant_id": tenant_id, "correlation_id": correlation_id},
        }
    )
    return response
