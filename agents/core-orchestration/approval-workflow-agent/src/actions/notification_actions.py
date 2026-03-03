"""
Notification subscription action handlers for the Approval Workflow Agent.

Handles subscribe, unsubscribe, update preferences, and record interaction actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from actions.notification_delivery import merge_preferences, record_interaction_metric

if TYPE_CHECKING:
    from approval_workflow_agent import ApprovalWorkflowAgent


async def handle_notification_action(
    agent: ApprovalWorkflowAgent, action: str, input_data: dict[str, Any]
) -> dict[str, Any]:
    tenant_id = input_data.get("tenant_id") or input_data.get("context", {}).get(
        "tenant_id", "unknown"
    )
    recipient = input_data.get("recipient") or input_data.get("user_id")
    if action == "subscribe_notifications":
        preferences = input_data.get("preferences", {})
        if recipient:
            existing = agent.notification_store.get_preferences(tenant_id, recipient) or {}
            merged = merge_preferences(existing, preferences)
            agent.notification_store.upsert_preferences(tenant_id, recipient, merged)
            return {"status": "subscribed", "recipient": recipient, "preferences": merged}
        return {"status": "failed", "reason": "recipient_required"}
    if action == "unsubscribe_notifications":
        if recipient:
            agent.notification_store.delete_preferences(tenant_id, recipient)
            return {"status": "unsubscribed", "recipient": recipient}
        return {"status": "failed", "reason": "recipient_required"}
    if action == "update_notification_preferences":
        if recipient:
            preferences = input_data.get("preferences", {})
            agent.notification_store.upsert_preferences(tenant_id, recipient, preferences)
            return {"status": "updated", "recipient": recipient, "preferences": preferences}
        return {"status": "failed", "reason": "recipient_required"}
    if action == "record_notification_interaction":
        approval_id = input_data.get("approval_id")
        interaction = input_data.get("interaction")
        if not recipient or not approval_id or not interaction:
            return {"status": "failed", "reason": "missing_fields"}
        record_interaction_metric(
            agent,
            tenant_id=tenant_id,
            recipient=recipient,
            approval_id=approval_id,
            interaction=interaction,
        )
        return {
            "status": "recorded",
            "approval_id": approval_id,
            "recipient": recipient,
            "interaction": interaction,
        }
    return {"status": "failed", "reason": "unsupported_action"}
