"""Tests for predictive analytics engine (Enhancement 2)."""

from __future__ import annotations

from predictive import (
    HealthPredictor,
    MonteCarloSimulator,
    ResourceBottleneckDetector,
    TrendForecaster,
)


def test_monte_carlo_basic():
    simulator = MonteCarloSimulator()
    result = simulator.simulate(
        {"project_id": "test", "estimated_duration_days": 100, "estimated_cost": 200000},
        iterations=500,
    )
    assert result.project_id == "test"
    assert result.iterations == 500
    assert result.p10_completion_days < result.p50_completion_days < result.p90_completion_days
    assert 0 <= result.on_time_probability <= 1
    assert 0 <= result.on_budget_probability <= 1


def test_trend_forecaster():
    forecaster = TrendForecaster()
    result = forecaster.forecast([10, 20, 30, 40, 50], periods=3)
    assert result.periods == 3
    assert len(result.forecast_values) == 3
    assert len(result.confidence_lower) == 3
    assert len(result.confidence_upper) == 3
    # Trend is upward, so forecasts should be >50
    assert all(v > 50 for v in result.forecast_values)


def test_trend_forecaster_single_point():
    forecaster = TrendForecaster()
    result = forecaster.forecast([42], periods=2)
    assert len(result.forecast_values) == 2


def test_health_predictor():
    predictor = HealthPredictor()
    result = predictor.predict_health(
        "proj-1",
        "Test Project",
        {"risk": 0.3, "schedule": 0.8, "budget": 0.7, "resource": 0.6, "trend_decay": 0.01},
    )
    assert result.project_id == "proj-1"
    assert 0 <= result.current_health_score <= 1
    assert result.trend == "stable"


def test_health_predictor_declining():
    predictor = HealthPredictor()
    result = predictor.predict_health(
        "proj-2", "Declining", {"risk": 0.8, "schedule": 0.3, "budget": 0.3, "resource": 0.2, "trend_decay": 0.05}
    )
    assert result.trend == "declining"
    assert result.predicted_health_90d <= result.current_health_score


def test_bottleneck_detector():
    detector = ResourceBottleneckDetector()
    allocs = [
        {"skill_area": "Python", "demand": 15, "capacity": 10},
        {"skill_area": "Go", "demand": 3, "capacity": 10},
    ]
    bottlenecks = detector.detect(allocs)
    assert len(bottlenecks) == 1
    assert bottlenecks[0].skill_area == "Python"
    assert bottlenecks[0].demand_capacity_ratio > 1.0


def test_bottleneck_detector_no_bottleneck():
    detector = ResourceBottleneckDetector()
    allocs = [{"skill_area": "Rust", "demand": 2, "capacity": 10}]
    assert detector.detect(allocs) == []
