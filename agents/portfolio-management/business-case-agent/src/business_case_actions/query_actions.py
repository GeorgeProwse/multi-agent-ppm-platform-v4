"""
Business Case Query Action Handlers

Handlers for:
- get_business_case
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from business_case_investment_agent import BusinessCaseInvestmentAgent


async def get_business_case(
    agent: BusinessCaseInvestmentAgent,
    business_case_id: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """Retrieve a business case by ID."""
    business_case = agent.business_case_store.get(tenant_id, business_case_id)
    if not business_case:
        raise ValueError(f"Business case not found: {business_case_id}")
    return business_case  # type: ignore
