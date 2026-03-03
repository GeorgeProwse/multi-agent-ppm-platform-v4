"""Action handler: classify_stakeholder"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from ..stakeholder_utils import determine_engagement_strategy, load_stakeholder

if TYPE_CHECKING:
    from ..stakeholder_communications_agent import StakeholderCommunicationsAgent


async def classify_stakeholder(
    agent: StakeholderCommunicationsAgent,
    tenant_id: str,
    stakeholder_id: str,
) -> dict[str, Any]:
    """Classify stakeholder using power-interest matrix."""
    agent.logger.info("Classifying stakeholder: %s", stakeholder_id)

    stakeholder = load_stakeholder(agent, tenant_id, stakeholder_id)
    if not stakeholder:
        raise ValueError(f"Stakeholder not found: {stakeholder_id}")

    influence = stakeholder.get("influence", "medium")
    interest = stakeholder.get("interest", "medium")

    engagement_strategy = await determine_engagement_strategy(influence, interest)

    stakeholder["engagement_strategy"] = engagement_strategy
    agent.stakeholder_store.upsert(tenant_id, stakeholder_id, stakeholder.copy())

    return {
        "stakeholder_id": stakeholder_id,
        "influence": influence,
        "interest": interest,
        "engagement_strategy": engagement_strategy,
        "recommended_frequency": engagement_strategy.get("frequency"),
    }
