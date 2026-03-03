"""Action handlers for program approval and decision recording."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from program_management_agent import ProgramManagementAgent


async def handle_submit_program_for_approval(
    agent: ProgramManagementAgent,
    program_id: str,
    *,
    decision_payload: dict[str, Any],
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """Submit a program for approval via the approval workflow agent."""
    if not agent.approval_agent and agent.approval_agent_enabled:
        from approval_workflow_agent import ApprovalWorkflowAgent

        agent.approval_agent = ApprovalWorkflowAgent(config=agent.approval_agent_config)
    if not agent.approval_agent:
        return {"status": "skipped", "reason": "approval_agent_not_configured"}

    approval = await agent.approval_agent.process(
        {
            "request_type": "program_optimization",
            "request_id": program_id,
            "requester": decision_payload.get("requester", "system"),
            "details": decision_payload,
            "tenant_id": tenant_id,
            "correlation_id": correlation_id,
            "context": {"tenant_id": tenant_id, "correlation_id": correlation_id},
        }
    )
    if agent.db_service:
        await agent.db_service.store(
            "program_approvals",
            program_id,
            {"program_id": program_id, "approval": approval},
        )
    return approval


async def handle_record_program_decision(
    agent: ProgramManagementAgent,
    program_id: str,
    *,
    decision: dict[str, Any],
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """Record a governance decision for a program."""
    program = agent.program_store.get(tenant_id, program_id) or {}
    decision_entry = {
        "decision_id": str(uuid.uuid4()),
        "program_id": program_id,
        "decision": decision,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    program.setdefault("decision_log", []).append(decision_entry)
    agent.program_store.upsert(tenant_id, program_id, program)
    if agent.db_service:
        await agent.db_service.store(
            "program_decisions", decision_entry["decision_id"], decision_entry
        )

    await agent.event_bus.publish(
        "program.decision.recorded",
        {
            "program_id": program_id,
            "tenant_id": tenant_id,
            "decision": decision_entry,
            "correlation_id": correlation_id,
        },
    )
    return {"status": "recorded", "decision": decision_entry}
