"""Databricks Monte Carlo simulation helpers."""

from __future__ import annotations

import random
from collections.abc import Callable, Iterable
from dataclasses import dataclass


@dataclass
class SimulationResult:
    iterations: int
    results: list[float]
    percentiles: dict[int, float]
    statistics: dict[str, float]


class DatabricksMonteCarloClient:
    """Client wrapper for Databricks-based Monte Carlo simulations."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def simulate(
        self,
        iterations: int,
        sampler: Callable[[int, random.Random], float],
        percentiles: Iterable[int] = (50, 80, 90, 95),
        rng: random.Random | None = None,
    ) -> SimulationResult:
        rng = rng or random.Random(self.seed)
        results: list[float] = []
        for i in range(iterations):
            results.append(float(sampler(i, rng)))

        pct_values = {p: self._percentile(results, p) for p in percentiles}
        stats = {
            "min": min(results) if results else 0.0,
            "max": max(results) if results else 0.0,
            "mean": sum(results) / len(results) if results else 0.0,
        }
        return SimulationResult(
            iterations=iterations,
            results=results,
            percentiles=pct_values,
            statistics=stats,
        )

    def _percentile(self, data: list[float], percentile: int) -> float:
        if not data:
            return 0.0
        ordered = sorted(data)
        index = int(len(ordered) * percentile / 100)
        return ordered[min(index, len(ordered) - 1)]


__all__ = ["DatabricksMonteCarloClient", "SimulationResult"]
