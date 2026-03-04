"""
Portfolio Scenario Action Handlers

Handlers for:
- run_scenario_analysis
- compare_scenarios
- upsert_scenario
- get_scenario
- list_scenarios
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from portfolio_utils import (
    apply_scenario_multipliers,
    generate_scenario_comparison,
    identify_trade_offs,
    recommend_best_scenario,
)

if TYPE_CHECKING:
    from portfolio_strategy_agent import PortfolioStrategyAgent


async def run_scenario_analysis(
    agent: PortfolioStrategyAgent,
    scenarios: list[dict[str, Any]],
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """
    Generate alternate portfolios under different scenarios and compare outcomes.

    Returns scenario analysis with trade-off details.
    """
    agent.logger.info("Running scenario analysis for %s scenarios", len(scenarios))

    async def _run_single_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
        scenario_index = len(agent.optimization_scenarios)
        scenario_id = scenario.get("id", f"scenario_{scenario_index}")
        scenario_name = scenario.get("name", f"Scenario {scenario_index + 1}")

        budget_multiplier = scenario.get("budget_multiplier", 1.0)
        capacity_multiplier = scenario.get("capacity_multiplier", 1.0)
        priority_shift = scenario.get("priority_shift", {})
        parameter_multipliers = scenario.get("parameter_multipliers", {})

        base_resource_capacity = scenario.get("resource_capacity", {})
        adjusted_resource_capacity = {
            resource: value * capacity_multiplier
            for resource, value in base_resource_capacity.items()
        }
        adjusted_constraints = {
            "budget_ceiling": scenario.get("budget_ceiling", 1000000) * budget_multiplier,
            "resource_capacity": adjusted_resource_capacity,
            "min_compliance_spend": scenario.get("min_compliance_spend", 0),
            "risk_appetite": scenario.get("risk_appetite", 0.6),
            "min_alignment_score": scenario.get("min_alignment_score", 0.3),
            "optimization_method": scenario.get("optimization_method", "integer_programming"),
            "risk_aversion": scenario.get("risk_aversion", 0.5),
            "objective_weights": scenario.get("objective_weights", {}),
        }

        adjusted_weights = agent.default_weights.copy()
        for criterion, adjustment in priority_shift.items():
            if criterion in adjusted_weights:
                adjusted_weights[criterion] *= adjustment

        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}

        scenario_projects = apply_scenario_multipliers(
            scenario.get("projects", []), parameter_multipliers
        )
        optimization_result = await agent._optimize_portfolio(
            scenario_projects,
            adjusted_constraints,
            tenant_id=scenario.get("tenant_id", tenant_id),
            correlation_id=scenario.get("correlation_id", scenario_id),
        )

        result = {
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "parameters": scenario,
            "results": optimization_result,
            "trade_offs": identify_trade_offs(optimization_result),
        }

        agent.optimization_scenarios[scenario_id] = {
            "name": scenario_name,
            "results": optimization_result,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if agent.db_service:
            await agent.db_service.store(
                "portfolio_scenarios",
                scenario_id,
                {
                    "scenario_id": scenario_id,
                    "scenario_name": scenario_name,
                    "parameters": scenario,
                    "results": optimization_result,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        return result

    scenario_output = await agent.scenario_engine.run_multi_scenarios(
        scenarios=scenarios,
        scenario_runner=_run_single_scenario,
        comparison_builder=generate_scenario_comparison,
    )
    scenario_results = scenario_output["scenarios"]
    comparison = scenario_output["comparison"]

    await agent.event_bus.publish(
        "portfolio.scenario.generated",
        {
            "tenant_id": tenant_id,
            "correlation_id": correlation_id,
            "scenarios": scenario_results,
            "comparison": comparison,
        },
    )

    return {
        "scenarios": scenario_results,
        "comparison": comparison,
        "recommendation": recommend_best_scenario(scenario_results),
    }


async def compare_scenarios(
    agent: PortfolioStrategyAgent,
    scenario_ids: list[str],
) -> dict[str, Any]:
    """Compare multiple scenarios side-by-side."""
    agent.logger.info("Comparing %s scenarios", len(scenario_ids))

    scenarios = []
    for scenario_id in scenario_ids:
        if scenario_id in agent.optimization_scenarios:
            scenarios.append(agent.optimization_scenarios[scenario_id])

    comparison = generate_scenario_comparison(scenarios)
    return {"scenarios": scenarios, "comparison": comparison}


async def upsert_scenario(
    agent: PortfolioStrategyAgent,
    scenario: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """Create or update a named scenario definition."""
    scenario_id = scenario.get("id") or f"scenario_{uuid.uuid4().hex}"
    definition = {
        "scenario_id": scenario_id,
        "scenario": scenario,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.scenario_definitions[scenario_id] = definition
    if agent.db_service:
        await agent.db_service.store(
            "portfolio_scenario_definitions", scenario_id, definition
        )
    await agent.event_bus.publish(
        "portfolio.scenario.updated",
        {
            "scenario_id": scenario_id,
            "tenant_id": tenant_id,
            "correlation_id": correlation_id,
            "scenario": scenario,
        },
    )
    return definition


async def get_scenario(
    agent: PortfolioStrategyAgent,
    scenario_id: str,
) -> dict[str, Any]:
    """Retrieve a scenario definition by ID."""
    if scenario_id in agent.scenario_definitions:
        return agent.scenario_definitions[scenario_id]
    return {"scenario_id": scenario_id, "scenario": {}, "status": "not_found"}


async def list_scenarios(agent: PortfolioStrategyAgent) -> dict[str, Any]:
    """Return all stored scenario definitions."""
    return {"scenarios": list(agent.scenario_definitions.values())}
