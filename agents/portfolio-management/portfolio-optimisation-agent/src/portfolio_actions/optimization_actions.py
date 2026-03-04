"""
Portfolio Optimization Action Handlers

Handlers for:
- optimize_portfolio
- rebalance_portfolio
"""

from __future__ import annotations

import math
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from portfolio_utils import (
    apply_alignment_constraint,
    apply_risk_appetite,
    calculate_investment_mix,
    calculate_portfolio_metrics,
    calculate_rebalancing_impact,
    suggest_rebalancing_actions,
)

if TYPE_CHECKING:
    from portfolio_strategy_agent import PortfolioStrategyAgent


async def optimize_portfolio(
    agent: PortfolioStrategyAgent,
    projects: list[dict[str, Any]],
    constraints: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """
    Run capacity-constrained optimization to maximize portfolio value.

    Uses multi-objective optimization to balance value, risk, and resource constraints.
    """
    agent.logger.info("Optimizing portfolio with %s projects", len(projects))

    budget_ceiling = constraints.get("budget_ceiling", float("inf"))
    resource_capacity = constraints.get("resource_capacity", {})
    min_compliance_spend = constraints.get("min_compliance_spend", 0)
    risk_appetite = constraints.get("risk_appetite", 0.6)
    min_alignment_score = constraints.get("min_alignment_score", 0.3)
    optimization_method = constraints.get("optimization_method", "integer_programming")
    risk_aversion = constraints.get("risk_aversion", 0.5)
    objective_weights = constraints.get("objective_weights", {})
    discount_rate = constraints.get("discount_rate", agent.get_config("discount_rate", 0.08))

    enriched_projects = await agent._enrich_projects_with_financials(
        projects, tenant_id=tenant_id, correlation_id=correlation_id
    )

    prioritization = await agent._prioritize_portfolio(
        enriched_projects,
        agent.default_weights,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        portfolio_id=None,
        cycle="optimization",
    )
    ranked_projects = prioritization["ranked_projects"]

    scored_projects = []
    for project_data in ranked_projects:
        project = next(
            (p for p in enriched_projects if p.get("project_id") == project_data["project_id"]),
            None,
        )
        if not project:
            continue
        project_cost = float(project.get("estimated_cost", project.get("cost", 0)))
        expected_value = float(
            project.get("expected_value")
            or agent._calculate_project_value(project, discount_rate=discount_rate)
            or 0
        )
        roi_score = await agent._score_roi(project)
        risk_score = await agent._score_risk(project)
        alignment_score = project_data.get("scores", {}).get(
            "strategic_alignment", project_data["overall_score"]
        )
        weighted_score = (
            alignment_score * objective_weights.get("strategic_alignment", 0.4)
            + roi_score * objective_weights.get("roi", 0.3)
            + risk_score * objective_weights.get("risk", 0.3)
        )
        value = expected_value * max(0.1, weighted_score)
        scored_projects.append(
            {
                "project_id": project["project_id"],
                "project_name": project.get("name"),
                "score": project_data["overall_score"],
                "cost": project_cost,
                "expected_value": expected_value,
                "value": value,
                "category": project.get("category", "operations"),
                "resource_requirements": project.get("resource_requirements", {}),
                "risk_score": risk_score,
                "alignment_score": alignment_score,
                "roi_score": roi_score,
            }
        )

    if not math.isfinite(budget_ceiling):
        budget_ceiling = sum(item["cost"] for item in scored_projects)

    selected_projects = await agent._select_optimized_projects(
        scored_projects,
        budget_ceiling=budget_ceiling,
        min_compliance_spend=min_compliance_spend,
        resource_capacity=resource_capacity,
        method=optimization_method,
        risk_aversion=risk_aversion,
        objective_weights=objective_weights,
    )
    selected_projects = apply_alignment_constraint(selected_projects, min_alignment_score)
    selected_projects = apply_risk_appetite(selected_projects, risk_appetite)
    total_cost = sum(item["cost"] for item in selected_projects)
    total_value = sum(item["expected_value"] for item in selected_projects)

    portfolio_metrics = calculate_portfolio_metrics(selected_projects)

    optimization_record = {
        "optimization_id": f"OPT-{uuid.uuid4().hex}",
        "selected_projects": selected_projects,
        "total_projects": len(selected_projects),
        "total_cost": total_cost,
        "total_value": total_value,
        "budget_utilization": total_cost / budget_ceiling if budget_ceiling > 0 else 0,
        "portfolio_metrics": portfolio_metrics,
        "constraints_applied": constraints,
        "optimization_method": optimization_method,
        "discount_rate": discount_rate,
        "optimized_at": datetime.now(timezone.utc).isoformat(),
    }
    if agent.db_service:
        await agent.db_service.store(
            "portfolio_optimization",
            optimization_record["optimization_id"],
            optimization_record,
        )
        await agent.db_service.store(
            "portfolio_decision_log",
            optimization_record["optimization_id"],
            {
                "portfolio_id": optimization_record["optimization_id"],
                "decision_type": "optimization",
                "details": optimization_record,
                "recorded_at": optimization_record["optimized_at"],
            },
        )
    await agent.event_bus.publish(
        "portfolio.optimized",
        {
            "portfolio_id": optimization_record["optimization_id"],
            "tenant_id": tenant_id,
            "optimization": optimization_record,
            "correlation_id": correlation_id,
        },
    )
    if constraints.get("submit_for_approval"):
        from portfolio_actions.status_actions import submit_portfolio_for_approval

        approval = await submit_portfolio_for_approval(
            agent,
            optimization_record["optimization_id"],
            decision_payload={"optimization": optimization_record},
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )
        optimization_record["approval"] = approval
    return optimization_record


async def rebalance_portfolio(
    agent: PortfolioStrategyAgent,
    portfolio_id: str | None = None,
    tenant_id: str = "",
    correlation_id: str = "",
) -> dict[str, Any]:
    """
    Analyze current portfolio and recommend rebalancing actions.

    Returns recommendations to align with target investment mix.
    """
    agent.logger.info("Rebalancing portfolio: %s", portfolio_id)

    current_portfolio = await agent._get_current_portfolio(portfolio_id)
    current_mix = calculate_investment_mix(current_portfolio)

    gaps = {}
    for category, target_pct in agent.target_mix.items():
        current_pct = current_mix.get(category, 0)
        gaps[category] = target_pct - current_pct

    recommendations = []
    for category, gap in gaps.items():
        if abs(gap) > 0.05:
            action = "increase" if gap > 0 else "decrease"
            recommendations.append(
                {
                    "category": category,
                    "action": action,
                    "current_percentage": current_mix.get(category, 0),
                    "target_percentage": agent.target_mix[category],
                    "gap_percentage": gap,
                    "suggested_actions": suggest_rebalancing_actions(category, gap),
                }
            )

    impact = calculate_rebalancing_impact(recommendations)
    await agent._publish_event(
        "portfolio.rebalanced",
        {
            "portfolio_id": portfolio_id,
            "gaps": gaps,
            "recommendations": recommendations,
            "impact": impact,
            "rebalanced_at": datetime.now(timezone.utc).isoformat(),
        },
        tenant_id=tenant_id,
        correlation_id=correlation_id,
    )

    return {
        "portfolio_id": portfolio_id,
        "current_mix": current_mix,
        "target_mix": agent.target_mix,
        "gaps": gaps,
        "recommendations": recommendations,
        "impact": impact,
        "rebalanced_at": datetime.now(timezone.utc).isoformat(),
    }
