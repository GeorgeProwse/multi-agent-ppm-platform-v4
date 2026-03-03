"""
Escalation scheduling and notification logic for the Approval Workflow Agent.

Handles scheduling escalation timers and sending escalation notifications
based on risk and criticality levels.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from actions.notification_delivery import (
    build_notification_context,
    dispatch_notification,
    persist_notification,
    resolve_notification_preferences,
)

if TYPE_CHECKING:
    from approval_workflow_agent import ApprovalWorkflowAgent


async def schedule_escalations(
    agent: ApprovalWorkflowAgent,
    *,
    tenant_id: str,
    approval_chain: dict[str, Any],
    approvers: list[str],
    details: dict[str, Any],
    risk_score: str,
    criticality_level: str,
    escalation_timeout_hours: float,
) -> None:
    """Schedule escalation notifications based on the configured policy."""
    delay_seconds = int(escalation_timeout_hours * 3600)

    if not approvers:
        return

    scheduled_at = datetime.now(timezone.utc)
    escalation_at = scheduled_at + timedelta(seconds=delay_seconds)
    agent.escalation_timers[approval_chain["id"]] = {
        "scheduled_at": scheduled_at.isoformat(),
        "escalation_at": escalation_at.isoformat(),
        "timeout_hours": escalation_timeout_hours,
        "risk_score": risk_score,
        "criticality_level": criticality_level,
    }

    async def escalation_task() -> None:
        await asyncio.sleep(delay_seconds)
        await send_escalation_notifications(
            agent,
            tenant_id=tenant_id,
            approval_chain=approval_chain,
            approvers=approvers,
            details=details,
            risk_score=risk_score,
            criticality_level=criticality_level,
            escalation_timeout_hours=escalation_timeout_hours,
        )
        agent.escalation_timers[approval_chain["id"]]["last_escalated_at"] = datetime.now(
            timezone.utc
        ).isoformat()
        agent._emit_audit_event(
            tenant_id=tenant_id,
            correlation_id=str(uuid.uuid4()),
            action="approval.escalated",
            outcome="success",
            resource_id=approval_chain["id"],
            metadata={
                "risk_score": risk_score,
                "criticality_level": criticality_level,
                "escalation_timeout_hours": escalation_timeout_hours,
            },
        )

    task = asyncio.create_task(escalation_task())
    agent.escalation_timers[approval_chain["id"]]["task"] = task
    agent.logger.info("Escalation scheduled for approval %s", approval_chain["id"])


async def send_escalation_notifications(
    agent: ApprovalWorkflowAgent,
    *,
    tenant_id: str,
    approval_chain: dict[str, Any],
    approvers: list[str],
    details: dict[str, Any],
    risk_score: str,
    criticality_level: str,
    escalation_timeout_hours: float,
) -> None:
    for approver in approvers:
        context = build_notification_context(
            tenant_id=tenant_id,
            approval_chain=approval_chain,
            approver=approver,
            details=details,
        )
        context.update(
            {
                "risk_score": risk_score,
                "criticality_level": criticality_level,
                "escalation_timeout_hours": escalation_timeout_hours,
            }
        )
        preferences = resolve_notification_preferences(
            agent,
            tenant_id=tenant_id,
            approver=approver,
            approval_chain=approval_chain,
        )
        locale = preferences.get("locale", agent.template_engine.default_locale)
        accessible_format = preferences.get("accessible_format", "text_only")
        subject = agent.template_engine.render("approval_escalation_subject", locale, context)
        body, html_body = agent.template_engine.render_accessible(
            template_key="approval_escalation_body",
            locale=locale,
            context=context,
            accessible_format=accessible_format,
        )
        chat_message = agent.template_engine.render("approval_escalation_chat", locale, context)
        push_message = agent.template_engine.render("approval_escalation_push", locale, context)
        notification = {
            "to": approver,
            "subject": subject,
            "body": body,
            "deadline": approval_chain["deadline"],
            "approval_id": approval_chain["id"],
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "channels": preferences.get("channels", {}),
            "delivery": preferences.get("delivery", "immediate"),
            "locale": locale,
            "accessible_format": accessible_format,
            "type": "escalation",
            "risk_score": risk_score,
            "criticality_level": criticality_level,
        }
        await dispatch_notification(
            agent,
            tenant_id=tenant_id,
            recipient=approver,
            notification=notification,
            subject=subject,
            body=body,
            chat_message=chat_message,
            push_message=push_message,
            html_body=html_body,
            preferences=preferences,
        )
        agent.notifications.append(notification)
        persist_notification(agent, tenant_id, approval_chain["id"], notification)
