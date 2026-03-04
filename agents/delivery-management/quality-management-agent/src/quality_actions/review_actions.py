"""Action handlers for review scheduling."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from quality_models import build_review
from quality_utils import generate_review_id

if TYPE_CHECKING:
    from quality_management_agent import QualityManagementAgent


async def schedule_review(
    agent: QualityManagementAgent,
    review_data: dict[str, Any],
) -> dict[str, Any]:
    """Schedule quality review or audit.  Returns review ID and participants."""
    agent.logger.info("Scheduling review: %s", review_data.get("title"))

    review_id = await generate_review_id()
    review = build_review(review_id, review_data)

    agent.reviews[review_id] = review

    calendar_event = await _schedule_calendar_event(agent, review)
    if calendar_event:
        review["calendar_event"] = calendar_event
    await agent._store_record("quality_reviews", review_id, review)
    await agent._publish_quality_event(
        "quality.review.scheduled",
        payload={
            "review_id": review_id,
            "project_id": review.get("project_id"),
            "scheduled_date": review.get("scheduled_date"),
            "calendar_event": calendar_event,
        },
        tenant_id=review.get("project_id") or "unknown",
        correlation_id=str(uuid.uuid4()),
    )

    return {
        "review_id": review_id,
        "title": review["title"],
        "type": review["type"],
        "scheduled_date": review["scheduled_date"],
        "participants": review["participants"],
        "participant_count": len(review["participants"]),
        "calendar_event": calendar_event,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _schedule_calendar_event(
    agent: QualityManagementAgent, review: dict[str, Any]
) -> dict[str, Any] | None:
    if agent.calendar_client and hasattr(agent.calendar_client, "create_event"):
        response = agent.calendar_client.create_event(review)
        if hasattr(response, "__await__"):
            return await response
        return response
    if agent.calendar_service:
        response = agent.calendar_service.create_event(
            {
                "title": review.get("title") or review.get("review_id"),
                "summary": review.get("title") or review.get("review_id"),
                "scheduled_time": review.get("scheduled_date"),
                "description": review.get("description"),
            }
        )
        return response
    comms_client = (agent.config or {}).get("stakeholder_communications_client")
    if comms_client and hasattr(comms_client, "create_calendar_event"):
        response = comms_client.create_calendar_event(review)
        if hasattr(response, "__await__"):
            return await response
        return response
    calendar_config = agent.integration_config.get("calendar", {})
    provider = calendar_config.get("provider")
    if provider in {"outlook", "google"}:
        return {
            "provider": provider,
            "event_id": f"cal-{review['review_id']}",
            "status": "scheduled",
        }
    return None
