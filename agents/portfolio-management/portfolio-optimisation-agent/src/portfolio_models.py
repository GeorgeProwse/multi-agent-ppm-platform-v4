"""
Portfolio Strategy & Optimization Models

Service and infrastructure model classes for the PortfolioStrategyAgent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PortfolioConfig:
    """Configuration model for PortfolioStrategyAgent."""

    criteria_weights: dict[str, float] = field(
        default_factory=lambda: {
            "strategic_alignment": 0.30,
            "roi": 0.25,
            "risk": 0.20,
            "resource_feasibility": 0.15,
            "compliance": 0.10,
        }
    )
    target_mix: dict[str, float] = field(
        default_factory=lambda: {
            "innovation": 0.30,
            "operations": 0.50,
            "compliance": 0.20,
        }
    )
    rebalancing_frequency: str = "quarterly"
    budget_granularity: int = 1000
    embedding_dimensions: int = 128
    discount_rate: float = 0.08
    policy_version: str = "1.0.0"
    approval_agent_enabled: bool = True

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> PortfolioConfig:
        """Create a PortfolioConfig from a raw config dictionary."""
        return cls(
            criteria_weights=config.get(
                "criteria_weights",
                {
                    "strategic_alignment": 0.30,
                    "roi": 0.25,
                    "risk": 0.20,
                    "resource_feasibility": 0.15,
                    "compliance": 0.10,
                },
            ),
            target_mix=config.get(
                "target_mix",
                {"innovation": 0.30, "operations": 0.50, "compliance": 0.20},
            ),
            rebalancing_frequency=config.get("rebalancing_frequency", "quarterly"),
            budget_granularity=config.get("budget_granularity", 1000),
            embedding_dimensions=config.get("embedding_dimensions", 128),
            discount_rate=config.get("discount_rate", 0.08),
            policy_version=config.get("policy_version", "1.0.0"),
            approval_agent_enabled=config.get("approval_agent_enabled", True),
        )


@dataclass
class ProjectScore:
    """Scores computed for a single project during prioritization."""

    project_id: Any
    project_name: str | None
    strategic_alignment: float
    roi: float
    risk: float
    resource_feasibility: float
    compliance: float
    overall_score: float
    recommendation: str
    policy_decision: dict[str, Any] = field(default_factory=dict)
    rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary for JSON output."""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "overall_score": self.overall_score,
            "scores": {
                "strategic_alignment": self.strategic_alignment,
                "roi": self.roi,
                "risk": self.risk,
                "resource_feasibility": self.resource_feasibility,
                "compliance": self.compliance,
            },
            "recommendation": self.recommendation,
            "policy_decision": self.policy_decision,
            "rank": self.rank,
        }


@dataclass
class OptimizationResult:
    """Result of a portfolio optimization run."""

    optimization_id: str
    selected_projects: list[dict[str, Any]]
    total_projects: int
    total_cost: float
    total_value: float
    budget_utilization: float
    portfolio_metrics: dict[str, Any]
    constraints_applied: dict[str, Any]
    optimization_method: str
    discount_rate: float
    optimized_at: str

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary for JSON output."""
        return {
            "optimization_id": self.optimization_id,
            "selected_projects": self.selected_projects,
            "total_projects": self.total_projects,
            "total_cost": self.total_cost,
            "total_value": self.total_value,
            "budget_utilization": self.budget_utilization,
            "portfolio_metrics": self.portfolio_metrics,
            "constraints_applied": self.constraints_applied,
            "optimization_method": self.optimization_method,
            "discount_rate": self.discount_rate,
            "optimized_at": self.optimized_at,
        }


@dataclass
class ScenarioDefinition:
    """Persisted definition of a named portfolio scenario."""

    scenario_id: str
    scenario: dict[str, Any]
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario": self.scenario,
            "updated_at": self.updated_at,
        }
