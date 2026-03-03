"""Action handlers for CI/CD webhooks and post-change monitoring."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from urllib import request

from actions.submit_change import publish_event

if TYPE_CHECKING:
    from change_configuration_agent import ChangeConfigurationAgent


async def handle_cicd_webhook(
    agent: ChangeConfigurationAgent, payload: dict[str, Any]
) -> dict[str, Any]:
    """Handle CI/CD webhook payloads and update change status."""
    change_id = payload.get("change_id")
    if not change_id:
        return {"status": "ignored", "reason": "missing_change_id"}
    change = agent.change_requests.get(change_id)
    if not change:
        return {"status": "ignored", "reason": "unknown_change_id"}
    deployment_status = payload.get("deployment_status", "unknown")
    change["deployment_status"] = deployment_status
    if deployment_status in {"succeeded", "failed"}:
        change["status"] = "Implemented" if deployment_status == "succeeded" else "Failed"
        change["implemented_at"] = (
            datetime.now(timezone.utc).isoformat()
            if deployment_status == "succeeded"
            else change.get("implemented_at")
        )
    await agent.db_service.store("change_requests", change_id, change)
    await publish_event(
        agent,
        "change.deployment",
        {
            "event_id": f"change.deployment:{change_id}:{deployment_status}",
            "change_id": change_id,
            "deployment_status": deployment_status,
        },
    )
    return {"status": "updated", "change_id": change_id, "deployment_status": deployment_status}


async def monitor_change(
    agent: ChangeConfigurationAgent,
    change_id: str | None,
    window_minutes: int,
) -> dict[str, Any]:
    if not change_id:
        raise ValueError("change_id is required")
    change = agent.change_requests.get(change_id)
    if not change:
        raise ValueError(f"Change request not found: {change_id}")
    if not agent.monitoring_endpoint:
        return {"change_id": change_id, "status": "skipped", "reason": "no_monitoring_endpoint"}
    payload = {"change_id": change_id, "window_minutes": window_minutes}
    try:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(agent.monitoring_endpoint, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        with request.urlopen(req, timeout=10) as response:
            metrics = response.read().decode("utf-8")
        change["monitoring_metrics"] = metrics
        await agent.db_service.store("change_requests", change_id, change)
        await publish_event(
            agent,
            "change.monitoring",
            {"event_id": f"change.monitoring:{change_id}", "metrics": metrics},
        )
        return {"change_id": change_id, "status": "ok", "metrics": metrics}
    except OSError as exc:
        return {"change_id": change_id, "status": "error", "error": str(exc)}


async def subscribe_cicd_webhooks(
    agent: ChangeConfigurationAgent,
    subscriptions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not subscriptions:
        return []
    stored_subscriptions: list[dict[str, Any]] = []
    for subscription in subscriptions:
        subscription_id = subscription.get("id") or f"cicd-{uuid.uuid4()}"
        payload = {
            "subscription_id": subscription_id,
            "tool": subscription.get("tool"),
            "endpoint": subscription.get("endpoint"),
            "events": subscription.get("events", ["deployment"]),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await agent.db_service.store("cicd_subscriptions", subscription_id, payload)
        stored_subscriptions.append(payload)
    return stored_subscriptions
