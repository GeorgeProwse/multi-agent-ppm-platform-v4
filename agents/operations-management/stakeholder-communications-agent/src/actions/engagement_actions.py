"""Action handler: track_engagement"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from ..stakeholder_utils import (
    calculate_engagement_score,
    calculate_overall_engagement,
    classify_engagement_level,
    prioritize_outreach,
)

if TYPE_CHECKING:
    from ..stakeholder_communications_agent import StakeholderCommunicationsAgent


async def track_engagement(
    agent: StakeholderCommunicationsAgent,
    stakeholder_id: str | None,
) -> dict[str, Any]:
    """Track stakeholder engagement metrics."""
    agent.logger.info("Tracking engagement for stakeholder: %s", stakeholder_id)

    if stakeholder_id:
        stakeholder = agent.stakeholder_register.get(stakeholder_id)
        if not stakeholder:
            raise ValueError(f"Stakeholder not found: {stakeholder_id}")

        metrics = agent.engagement_metrics.get(stakeholder_id, {})

        engagement_score = await calculate_engagement_score(agent, metrics)

        stakeholder["engagement_score"] = engagement_score

        return {
            "stakeholder_id": stakeholder_id,
            "engagement_score": engagement_score,
            "metrics": metrics,
            "engagement_level": await classify_engagement_level(engagement_score),
            "outreach_priority": await prioritize_outreach(engagement_score),
        }
    else:
        overall_engagement = await calculate_overall_engagement(agent)
        return {
            "overall_engagement": overall_engagement,
            "stakeholders_tracked": len(agent.engagement_metrics),
        }
