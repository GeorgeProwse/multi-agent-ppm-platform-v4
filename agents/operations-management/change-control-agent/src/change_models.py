"""
Data models for the Change & Configuration Management Agent.

Contains dataclasses for repository references, pull request summaries,
impact training samples, and the ChangeImpactModel for ML-based predictions.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass
class RepositoryReference:
    provider: str
    repo: str
    pull_request_id: str | None = None
    commit_id: str | None = None


@dataclass
class PullRequestSummary:
    provider: str
    repo: str
    status: str
    data: list[dict[str, Any]]


@dataclass
class ImpactTrainingSample:
    complexity: float
    historical_failure_rate: float
    affected_services: int
    risk_category: str
    success_probability: float


class ChangeImpactModel:
    def __init__(self) -> None:
        self._weights = {
            "complexity": 0.4,
            "failure_rate": 0.3,
            "services": 0.2,
            "risk_modifier": 0.1,
        }
        self._risk_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        self._trained = False
        self._coefficients: list[float] | None = None

    def _feature_vector(self, features: dict[str, Any]) -> list[float]:
        complexity = float(features.get("complexity", 1.0))
        failure_rate = float(features.get("historical_failure_rate", 0.1))
        affected_services = float(features.get("affected_services", 1))
        risk_category = str(features.get("risk_category", "medium")).lower()
        risk_modifier = self._risk_map.get(risk_category, 0.5)
        return [1.0, complexity, failure_rate, affected_services, risk_modifier]

    def _invert_matrix(self, matrix: list[list[float]]) -> list[list[float]] | None:
        size = len(matrix)
        identity = [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
        augmented = [row + identity_row for row, identity_row in zip(matrix, identity)]
        for i in range(size):
            pivot = augmented[i][i]
            if abs(pivot) < 1e-8:
                for j in range(i + 1, size):
                    if abs(augmented[j][i]) > 1e-8:
                        augmented[i], augmented[j] = augmented[j], augmented[i]
                        pivot = augmented[i][i]
                        break
            if abs(pivot) < 1e-8:
                return None
            scale = 1.0 / pivot
            augmented[i] = [value * scale for value in augmented[i]]
            for j in range(size):
                if j == i:
                    continue
                factor = augmented[j][i]
                augmented[j] = [augmented[j][k] - factor * augmented[i][k] for k in range(size * 2)]
        return [row[size:] for row in augmented]

    def _fit_linear(self, samples: Sequence[ImpactTrainingSample]) -> None:
        if len(samples) < 2:
            return
        x_rows = [
            self._feature_vector(
                {
                    "complexity": sample.complexity,
                    "historical_failure_rate": sample.historical_failure_rate,
                    "affected_services": sample.affected_services,
                    "risk_category": sample.risk_category,
                }
            )
            for sample in samples
        ]
        y_values = [sample.success_probability for sample in samples]
        features = len(x_rows[0])
        xtx = [[0.0 for _ in range(features)] for _ in range(features)]
        xty = [0.0 for _ in range(features)]
        for row, target in zip(x_rows, y_values):
            for i in range(features):
                xty[i] += row[i] * target
                for j in range(features):
                    xtx[i][j] += row[i] * row[j]
        inverse = self._invert_matrix(xtx)
        if not inverse:
            return
        coefficients = [0.0 for _ in range(features)]
        for i in range(features):
            coefficients[i] = sum(inverse[i][j] * xty[j] for j in range(features))
        self._coefficients = coefficients

    def train(self, samples: Iterable[ImpactTrainingSample]) -> None:
        samples_list = list(samples)
        if not samples_list:
            return
        avg_failure = sum(sample.historical_failure_rate for sample in samples_list) / len(
            samples_list
        )
        self._weights["failure_rate"] = 0.3 + min(0.2, avg_failure)
        self._fit_linear(samples_list)
        self._trained = True

    def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        vector = self._feature_vector(features)
        risk_category = str(features.get("risk_category", "medium")).lower()
        if self._coefficients:
            raw_success = sum(weight * value for weight, value in zip(self._coefficients, vector))
            success_probability = max(0.05, min(0.95, raw_success))
            score = max(0.5, (1.0 - success_probability) * 5)
        else:
            complexity = float(features.get("complexity", 1.0))
            failure_rate = float(features.get("historical_failure_rate", 0.1))
            affected_services = float(features.get("affected_services", 1))
            risk_modifier = self._risk_map.get(risk_category, 0.5)
            score = (
                complexity * self._weights["complexity"]
                + failure_rate * self._weights["failure_rate"]
                + affected_services * self._weights["services"]
                + risk_modifier * self._weights["risk_modifier"]
            )
            success_probability = max(0.05, min(0.95, 1.0 - score / 5))
        return {
            "impact_score": round(score, 2),
            "success_probability": round(success_probability, 2),
            "risk_category": risk_category,
            "model_trained": self._trained,
        }
