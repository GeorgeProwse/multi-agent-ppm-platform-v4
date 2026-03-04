"""Action handler: update_communication_preferences"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..stakeholder_utils import load_stakeholder

if TYPE_CHECKING:
    from ..stakeholder_communications_agent import StakeholderCommunicationsAgent


async def update_communication_preferences(
    agent: StakeholderCommunicationsAgent,
    tenant_id: str,
    stakeholder_id: str | None,
    preferences: dict[str, Any],
) -> dict[str, Any]:
    if not stakeholder_id:
        raise ValueError("stakeholder_id is required")
    stakeholder = load_stakeholder(agent, tenant_id, stakeholder_id)
    if not stakeholder:
        raise ValueError(f"Stakeholder not found: {stakeholder_id}")
    stakeholder["communication_preferences"] = preferences
    if preferences.get("preferred_channels"):
        stakeholder["preferred_channels"] = preferences["preferred_channels"]
    if "opt_out" in preferences:
        stakeholder["opt_out"] = bool(preferences["opt_out"])
    agent.stakeholder_store.upsert(tenant_id, stakeholder_id, stakeholder.copy())
    return {
        "stakeholder_id": stakeholder_id,
        "preferences": stakeholder.get("communication_preferences", {}),
        "preferred_channels": stakeholder.get("preferred_channels", []),
    }
