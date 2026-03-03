"""Action handlers: track_delivery_event, queue/flush digest notifications"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, TYPE_CHECKING

from ..stakeholder_utils import (
    get_template,
    has_consent,
    load_stakeholder,
    publish_event,
    publish_metrics_event,
    record_communication_history,
    resolve_delivery_channels,
    safe_format_template,
    summarize_report,
)

if TYPE_CHECKING:
    from ..stakeholder_communications_agent import StakeholderCommunicationsAgent


async def track_delivery_event(
    agent: StakeholderCommunicationsAgent,
    tenant_id: str,
    message_id: str | None,
    stakeholder_id: str | None,
    event: dict[str, Any],
) -> dict[str, Any]:
    if not message_id or message_id not in agent.messages:
        raise ValueError("message_id not found")
    if not stakeholder_id:
        raise ValueError("stakeholder_id is required")
    event_type = event.get("type", "delivered")
    message = agent.messages[message_id]
    if stakeholder_id in agent.engagement_metrics:
        metrics = agent.engagement_metrics[stakeholder_id]
        if event_type == "opened":
            metrics["messages_opened"] += 1
        elif event_type == "clicked":
            metrics["messages_clicked"] += 1
        elif event_type == "responded":
            metrics["responses_received"] += 1
    record_communication_history(
        agent,
        {
            "stakeholder_id": stakeholder_id,
            "channel": message.get("channel"),
            "subject": message.get("subject"),
            "status": event_type,
            "content": event.get("details"),
            "metadata": {"message_id": message_id, "event": event},
        },
    )
    publish_event(
        agent,
        f"stakeholder.message.{event_type}",
        {"message_id": message_id, "stakeholder_id": stakeholder_id, "event": event},
    )
    publish_metrics_event(
        agent,
        tenant_id=tenant_id,
        event_type="message_engagement",
        payload={
            "message_id": message_id,
            "stakeholder_id": stakeholder_id,
            "event_type": event_type,
            "event": event,
        },
    )
    return {"message_id": message_id, "stakeholder_id": stakeholder_id, "event": event_type}


async def queue_digest_notifications(
    agent: StakeholderCommunicationsAgent,
    tenant_id: str,
    message: dict[str, Any],
) -> list[dict[str, Any]]:
    queued_entries: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    for personalized in message.get("personalized_messages", []):
        stakeholder_id = personalized.get("stakeholder_id")
        if not stakeholder_id:
            continue
        scheduled_time = personalized.get("scheduled_time")
        if scheduled_time:
            send_after = scheduled_time
        else:
            send_after = (now + timedelta(minutes=agent.digest_window_minutes)).isoformat()
        key = (tenant_id, stakeholder_id)
        entry = {
            "message_id": message.get("message_id"),
            "subject": personalized.get("subject") or message.get("subject"),
            "content": personalized.get("content"),
            "queued_at": now.isoformat(),
            "send_after": send_after,
            "project_id": message.get("project_id"),
        }
        agent.digest_queue.setdefault(key, []).append(entry)
        queued_entries.append({"stakeholder_id": stakeholder_id, "send_after": send_after})
        if len(agent.digest_queue.get(key, [])) >= agent.digest_batch_size:
            await flush_digest_notifications(agent, tenant_id, stakeholder_id)
    return queued_entries


async def flush_digest_notifications(
    agent: StakeholderCommunicationsAgent,
    tenant_id: str,
    stakeholder_id: str | None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    flushed: list[dict[str, Any]] = []
    for (queued_tenant, queued_stakeholder), items in list(agent.digest_queue.items()):
        if queued_tenant != tenant_id:
            continue
        if stakeholder_id and queued_stakeholder != stakeholder_id:
            continue
        due_items = []
        for item in items:
            try:
                send_after = datetime.fromisoformat(item["send_after"])
            except (TypeError, ValueError):
                send_after = now
            if send_after <= now:
                due_items.append(item)
        if not due_items:
            continue
        stakeholder = load_stakeholder(agent, tenant_id, queued_stakeholder)
        if not stakeholder:
            continue
        digest_payload = await _build_digest_payload(agent, stakeholder, due_items)
        digest_message = {
            "subject": digest_payload["subject"],
            "content": digest_payload["body"],
            "channel": "preferred",
            "attachments": [],
        }
        delivery_channels = resolve_delivery_channels(digest_message, stakeholder)
        results = []
        for channel in delivery_channels:
            if not await has_consent(stakeholder, channel):
                results.append({"channel": channel, "status": "skipped_no_consent"})
                continue
            result = await agent._send_via_channel(
                channel,
                stakeholder,
                digest_message,
                digest_payload["body"],
                digest_payload["subject"],
            )
            results.append({"channel": channel, "status": result.get("status")})
            if queued_stakeholder in agent.engagement_metrics:
                agent.engagement_metrics[queued_stakeholder]["messages_sent"] += 1
        agent.digest_queue[(queued_tenant, queued_stakeholder)] = [
            item for item in items if item not in due_items
        ]
        record_communication_history(
            agent,
            {
                "stakeholder_id": queued_stakeholder,
                "channel": ",".join(delivery_channels),
                "subject": digest_payload["subject"],
                "status": "sent",
                "content": digest_payload["body"],
                "metadata": {"digest_items": len(due_items), "results": results},
            },
        )
        flushed.append(
            {
                "stakeholder_id": queued_stakeholder,
                "digest_items": len(due_items),
                "channels": delivery_channels,
            }
        )
    return {"status": "flushed", "digests": flushed}


async def _build_digest_payload(
    agent: StakeholderCommunicationsAgent,
    stakeholder: dict[str, Any],
    items: list[dict[str, Any]],
) -> dict[str, str]:
    digest_items = "\n".join(
        f"- {item.get('subject') or 'Update'}"
        for item in items
        if item.get("subject") or item.get("content")
    )
    summary_source = "\n\n".join(item.get("content", "") for item in items)
    summary = await summarize_report(
        agent,
        summary_source,
        stakeholder.get("role", "general"),
        stakeholder.get("locale") or agent.default_locale,
    )
    template = get_template(
        agent, "digest_update", stakeholder.get("locale") or agent.default_locale
    )
    subject = template.get("subject", "Update digest")
    body_template = template.get("body", "{digest_items}")
    payload = {
        "name": stakeholder.get("name", ""),
        "project_name": stakeholder.get("project_name", "your project"),
        "digest_items": digest_items,
        "summary": summary.get("summary", ""),
    }
    return {
        "subject": safe_format_template(subject, payload),
        "body": safe_format_template(body_template, payload),
    }
