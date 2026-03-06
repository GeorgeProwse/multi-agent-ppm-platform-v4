"""Predictive analytics API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from predictive import (
    HealthPredictor,
    MonteCarloSimulator,
    ResourceBottleneckDetector,
    TrendForecaster,
)
from predictive_models import (
    BottleneckPrediction,
    HealthPrediction,
    RiskHeatmapCell,
    ScenarioComparison,
    SimulationResult,
)

router = APIRouter(prefix="/v1/predictive", tags=["predictive"])

_simulator = MonteCarloSimulator()
_forecaster = TrendForecaster()
_health_predictor = HealthPredictor()
_bottleneck_detector = ResourceBottleneckDetector()


class MonteCarloRequest(BaseModel):
    project_data: dict[str, Any]
    iterations: int = 1000


class ScenarioComparisonRequest(BaseModel):
    scenarios: list[dict[str, Any]] = Field(min_length=2)


# --- Demo data helpers ---

_DEMO_PROJECTS = [
    {"project_id": "proj-alpha", "project_name": "Project Alpha", "risk": 0.3, "schedule": 0.8, "budget": 0.7, "resource": 0.6, "trend_decay": 0.01},
    {"project_id": "proj-beta", "project_name": "Project Beta", "risk": 0.7, "schedule": 0.4, "budget": 0.5, "resource": 0.3, "trend_decay": 0.05},
    {"project_id": "proj-gamma", "project_name": "Project Gamma", "risk": 0.2, "schedule": 0.9, "budget": 0.85, "resource": 0.9, "trend_decay": -0.02},
    {"project_id": "proj-delta", "project_name": "Project Delta", "risk": 0.5, "schedule": 0.6, "budget": 0.6, "resource": 0.5, "trend_decay": 0.03},
]

_RISK_CATEGORIES = ["Technical", "Schedule", "Budget", "Resource", "Compliance", "Vendor"]


@router.get("/health-forecast")
async def health_forecast(
    portfolio_id: str = Query(default="default"),
) -> list[HealthPrediction]:
    return [
        _health_predictor.predict_health(p["project_id"], p["project_name"], p)
        for p in _DEMO_PROJECTS
    ]


@router.get("/risk-heatmap")
async def risk_heatmap(
    portfolio_id: str = Query(default="default"),
) -> list[RiskHeatmapCell]:
    import random as _rng

    cells: list[RiskHeatmapCell] = []
    for proj in _DEMO_PROJECTS:
        for cat in _RISK_CATEGORIES:
            cells.append(
                RiskHeatmapCell(
                    project_id=proj["project_id"],
                    project_name=proj["project_name"],
                    risk_category=cat,
                    risk_score=round(_rng.uniform(0.1, 0.9), 2),
                    trend=_rng.choice(["up", "stable", "down"]),
                )
            )
    return cells


@router.post("/monte-carlo")
async def monte_carlo(request: MonteCarloRequest) -> SimulationResult:
    return _simulator.simulate(request.project_data, request.iterations)


@router.get("/resource-bottlenecks")
async def resource_bottlenecks(
    portfolio_id: str = Query(default="default"),
) -> list[BottleneckPrediction]:
    demo_allocations = [
        {"skill_area": "Python", "demand": 12, "capacity": 10},
        {"skill_area": "React", "demand": 8, "capacity": 6},
        {"skill_area": "DevOps", "demand": 5, "capacity": 7},
        {"skill_area": "Data Science", "demand": 4, "capacity": 3},
    ]
    return _bottleneck_detector.detect(demo_allocations)


@router.post("/scenario-comparison")
async def scenario_comparison(
    request: ScenarioComparisonRequest,
) -> list[ScenarioComparison]:
    results: list[ScenarioComparison] = []
    for i, scenario in enumerate(request.scenarios):
        results.append(
            ScenarioComparison(
                scenario_id=scenario.get("id", f"scenario-{i+1}"),
                scenario_name=scenario.get("name", f"Scenario {i+1}"),
                total_cost=float(scenario.get("total_cost", 500000 + i * 100000)),
                total_duration_days=float(scenario.get("duration_days", 180 + i * 30)),
                risk_score=float(scenario.get("risk_score", 0.3 + i * 0.1)),
                resource_utilization=float(scenario.get("utilization", 0.75 + i * 0.05)),
                npv=float(scenario.get("npv", 200000 - i * 50000)),
                roi_percentage=float(scenario.get("roi", 25 - i * 5)),
            )
        )
    return results
