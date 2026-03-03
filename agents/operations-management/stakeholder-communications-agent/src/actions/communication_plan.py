"""Action handler: create_communication_plan"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from stakeholder_utils import generate_plan_id

if TYPE_CHECKING:
    from ..stakeholder_communications_agent import StakeholderCommunicationsAgent


async def create_communication_plan(
    agent: StakeholderCommunicationsAgent,
    plan_data: dict[str, Any],
) -> dict[str, Any]:
    """Create communication plan."""
    agent.logger.info("Creating communication plan: %s", plan_data.get("name"))

    plan_id = await generate_plan_id()

    stakeholder_ids = plan_data.get("stakeholder_ids", [])
    valid_stakeholders = [s_id for s_id in stakeholder_ids if s_id in agent.stakeholder_register]

    plan = {
        "plan_id": plan_id,
        "project_id": plan_data.get("project_id"),
        "name": plan_data.get("name"),
        "objectives": plan_data.get("objectives", []),
        "stakeholder_ids": valid_stakeholders,
        "channel": plan_data.get("channel", "email"),
        "frequency": plan_data.get("frequency", "weekly"),
        "schedule": plan_data.get("schedule", []),
        "template_id": plan_data.get("template_id"),
        "status": "Active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    agent.communication_plans[plan_id] = plan

    return {
        "plan_id": plan_id,
        "name": plan["name"],
        "stakeholders": len(valid_stakeholders),
        "channel": plan["channel"],
        "frequency": plan["frequency"],
    }
