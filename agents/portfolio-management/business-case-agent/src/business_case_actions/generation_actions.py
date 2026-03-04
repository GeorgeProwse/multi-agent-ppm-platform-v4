"""
Business Case Generation Action Handlers

Handlers for:
- generate_business_case
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from business_case_investment_agent import BusinessCaseInvestmentAgent


async def generate_business_case(
    agent: BusinessCaseInvestmentAgent,
    request_data: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """
    Generate a comprehensive business case document.

    Returns business case ID and document structure.
    """
    agent.logger.info("Generating business case")

    business_case_id = await agent._generate_business_case_id()
    template = await agent._select_template(request_data)

    cost_data = await agent._gather_cost_data(request_data)
    benefit_data = await agent._gather_benefit_data(request_data)
    market_data = await agent._gather_market_data(request_data)

    executive_summary = await agent._generate_executive_summary(
        request_data, cost_data, benefit_data
    )
    problem_statement = await agent._generate_problem_statement(request_data)
    proposed_solution = await agent._generate_proposed_solution(request_data)

    financial_analysis = await agent._calculate_financial_metrics(cost_data, benefit_data)
    risks = await agent._identify_risks(request_data)
    implementation_approach = await agent._generate_implementation_approach(request_data)

    business_case = {
        "business_case_id": business_case_id,
        "title": request_data.get("title"),
        "project_type": request_data.get("project_type"),
        "methodology": request_data.get("methodology", "hybrid"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": request_data.get("requester", "unknown"),
        "status": "Draft",
        "demand_id": request_data.get("demand_id", "unknown"),
        "template": template,
        "document": {
            "executive_summary": executive_summary,
            "problem_statement": problem_statement,
            "proposed_solution": proposed_solution,
            "financial_analysis": financial_analysis,
            "market_analysis": market_data,
            "risks_and_mitigations": risks,
            "implementation_approach": implementation_approach,
        },
        "financial_metrics": financial_analysis.get("metrics", {}),
        "metadata": {
            "estimated_cost": cost_data.get("total_cost", 0),
            "estimated_benefits": benefit_data.get("total_benefits", 0),
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    agent.business_case_store.upsert(tenant_id, business_case_id, business_case)
    index_text = (
        f"{business_case.get('title','')} {business_case.get('project_type','')} "
        f"{business_case.get('document', {}).get('executive_summary','')}"
    )
    agent.vector_index.add(business_case_id, index_text, business_case)

    agent.logger.info("Generated business case: %s", business_case_id)

    await agent.notification_service.send(
        {
            "recipient": business_case.get("created_by"),
            "subject": f"Business case {business_case_id} created",
            "body": "A draft business case is ready for review.",
            "metadata": {"business_case_id": business_case_id, "tenant_id": tenant_id},
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    await agent._publish_business_case_created(
        business_case,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
    )

    document_entities: list[dict[str, Any]] = []
    if agent._autonomous_deliverables_enabled():
        document_entities.append(
            agent._build_document_entity(business_case, correlation_id=correlation_id)
        )

    return {
        "business_case_id": business_case_id,
        "status": "Draft",
        "document": business_case["document"],
        "financial_metrics": business_case["financial_metrics"],
        "next_steps": (
            "Review and edit the business case, then run scenario analysis "
            "or generate recommendation."
        ),
        "documents": document_entities,
    }
