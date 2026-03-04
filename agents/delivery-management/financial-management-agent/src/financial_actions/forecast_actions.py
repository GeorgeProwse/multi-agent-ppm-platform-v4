"""Action handlers for financial forecasting."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from financial_utils import calculate_confidence_interval

if TYPE_CHECKING:
    from financial_management_agent import FinancialManagementAgent


async def generate_forecast(
    agent: FinancialManagementAgent,
    project_id: str,
    time_period: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """Generate rolling forecast using AI-driven models.

    Returns forecast data and projections.
    """
    agent.logger.info("Generating forecast for project: %s", project_id)

    # Get historical spending data
    historical_data = await agent._get_historical_spending(project_id)

    # Get resource allocation plans
    resource_plans = await agent._get_resource_plans(project_id)

    # Get schedule progress
    schedule_progress = await agent._get_schedule_progress(project_id)

    # Run forecasting model
    forecast = await agent._run_forecasting_model(
        historical_data, resource_plans, schedule_progress
    )

    # Calculate Estimate at Completion (EAC)
    eac = await agent._calculate_eac(project_id, forecast, tenant_id=tenant_id)

    # Store forecast
    agent.forecasts[project_id] = {
        "forecast_data": forecast,
        "eac": eac,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "time_period": time_period,
    }
    agent.forecast_store.upsert(tenant_id, project_id, agent.forecasts[project_id])

    await agent.db_service.store("forecasts", project_id, agent.forecasts[project_id])

    await agent._publish_financial_event(
        "finance.forecast.generated",
        {
            "project_id": project_id,
            "eac": eac,
            "time_period": time_period,
            "generated_at": agent.forecasts[project_id]["generated_at"],
        },
    )

    return {
        "project_id": project_id,
        "forecast": forecast,
        "eac": eac,
        "variance_from_baseline": await agent._calculate_forecast_variance(
            project_id, eac, tenant_id=tenant_id
        ),
        "confidence_interval": calculate_confidence_interval(
            forecast.get("monthly_forecast", [])
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def generate_financial_variants(
    agent: FinancialManagementAgent,
    project_id: str,
    scenarios: list[dict[str, Any]],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """Generate scenario variants for financial outcomes."""
    agent.logger.info("Generating financial variants for project: %s", project_id)
    baseline_metrics = await agent._get_project_financial_summary(
        project_id, tenant_id=tenant_id
    )

    async def _build_scenario(
        baseline: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        scenario = dict(baseline)
        budget_baseline = float(baseline.get("budget_baseline", 0) or 0)
        actual_cost = float(baseline.get("actual_cost", 0) or 0)
        forecast_eac = float(baseline.get("forecast_eac", 0) or 0)

        budget_delta = float(params.get("budget_delta", 0) or 0)
        actual_delta = float(params.get("actual_cost_delta", 0) or 0)
        forecast_delta = float(params.get("forecast_eac_delta", 0) or 0)

        budget_multiplier = params.get("budget_multiplier")
        actual_multiplier = params.get("actual_cost_multiplier")
        forecast_multiplier = params.get("forecast_eac_multiplier")

        budget_baseline = budget_baseline + budget_delta
        if budget_multiplier:
            budget_baseline *= float(budget_multiplier)

        actual_cost = actual_cost + actual_delta
        if actual_multiplier:
            actual_cost *= float(actual_multiplier)

        forecast_eac = forecast_eac + forecast_delta
        if forecast_multiplier:
            forecast_eac *= float(forecast_multiplier)

        cpi = float(baseline.get("cost_performance_index", 1.0) or 1.0)
        spi = float(baseline.get("schedule_performance_index", 1.0) or 1.0)
        cpi += float(params.get("cost_performance_index_delta", 0) or 0)
        spi += float(params.get("schedule_performance_index_delta", 0) or 0)

        scenario.update(
            {
                "budget_baseline": max(budget_baseline, 0),
                "actual_cost": max(actual_cost, 0),
                "forecast_eac": max(forecast_eac, 0),
                "cost_performance_index": max(cpi, 0),
                "schedule_performance_index": max(spi, 0),
                "variance_at_completion": forecast_eac - budget_baseline,
                "performance_status": await agent._assess_performance_status(cpi, spi),
                "scenario_notes": params.get("notes"),
                "scenario_adjustments": params,
            }
        )
        return scenario

    async def _compare(baseline: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
        return {
            "budget_variance": scenario.get("budget_baseline", 0)
            - baseline.get("budget_baseline", 0),
            "actual_cost_variance": scenario.get("actual_cost", 0)
            - baseline.get("actual_cost", 0),
            "forecast_variance": scenario.get("forecast_eac", 0)
            - baseline.get("forecast_eac", 0),
            "variance_at_completion_delta": scenario.get("variance_at_completion", 0)
            - baseline.get("variance_at_completion", 0),
            "cpi_delta": scenario.get("cost_performance_index", 1.0)
            - baseline.get("cost_performance_index", 1.0),
            "spi_delta": scenario.get("schedule_performance_index", 1.0)
            - baseline.get("schedule_performance_index", 1.0),
        }

    results: list[dict[str, Any]] = []
    for index, variant in enumerate(scenarios):
        scenario_params = variant.get("params") or variant
        scenario_name = variant.get("name") or f"Scenario {index + 1}"
        scenario_id = variant.get("scenario_id") or f"{project_id}-scenario-{index + 1}"
        output = await agent.scenario_engine.run_metric_scenario(
            baseline_metrics=baseline_metrics,
            scenario_params=scenario_params,
            scenario_metrics_builder=_build_scenario,
            comparison_builder=_compare,
        )
        results.append(
            {
                "scenario_id": scenario_id,
                "name": scenario_name,
                "params": scenario_params,
                "metrics": output["scenario_metrics"],
                "comparison": output["comparison"],
            }
        )

    forecast_values = [result["metrics"].get("forecast_eac", 0) for result in results]
    summary = {
        "baseline_forecast": baseline_metrics.get("forecast_eac", 0),
        "best_case": min(forecast_values) if forecast_values else 0,
        "worst_case": max(forecast_values) if forecast_values else 0,
        "average": sum(forecast_values) / len(forecast_values) if forecast_values else 0,
    }

    return {
        "project_id": project_id,
        "baseline_metrics": baseline_metrics,
        "scenarios": results,
        "forecast_summary": summary,
    }
