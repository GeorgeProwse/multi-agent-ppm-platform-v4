"""
Action handler for scenario analysis:
  - scenario_analysis
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from resource_capacity_agent import ResourceCapacityAgent


async def scenario_analysis(
    agent: ResourceCapacityAgent, scenario_params: dict[str, Any]
) -> dict[str, Any]:
    """
    Perform what-if scenario analysis.

    Returns scenario comparison metrics.
    """
    agent.logger.info("Running scenario analysis")

    scenario_name = scenario_params.get("scenario_name", "Unnamed Scenario")
    changes = scenario_params.get("changes", {})

    baseline = await agent._create_baseline_scenario()
    scenario_output = await agent.scenario_engine.run_scenario(
        baseline=baseline,
        scenario_params=changes,
        scenario_builder=agent._apply_scenario_changes,
        metrics_builder=agent._calculate_scenario_metrics,
        comparison_builder=agent._compare_scenarios,
        recommendation_builder=agent._generate_scenario_recommendation,
    )

    return {
        "scenario_name": scenario_name,
        "scenario_params": scenario_params,
        "baseline_metrics": scenario_output["baseline_metrics"],
        "scenario_metrics": scenario_output["scenario_metrics"],
        "comparison": scenario_output["comparison"],
        "recommendation": scenario_output.get("recommendation"),
    }
