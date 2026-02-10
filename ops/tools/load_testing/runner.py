from __future__ import annotations

import json
import os
import statistics
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoadScenario:
    name: str
    request_fn: Callable[[], int] | None = None
    total_requests: int = 1
    concurrency: int = 1
    flow_step_fns: list[tuple[str, Callable[[], int]]] | None = None


@dataclass(frozen=True)
class LoadSla:
    max_avg_latency_s: float
    max_p95_latency_s: float
    max_error_rate: float
    min_requests_per_s: float | None = None


@dataclass(frozen=True)
class LoadScenarioResult:
    name: str
    durations_s: list[float]
    error_count: int
    total_duration_s: float
    step_durations_s: dict[str, list[float]]
    step_error_count: dict[str, int]

    @property
    def average_latency_s(self) -> float:
        return statistics.mean(self.durations_s) if self.durations_s else 0.0

    @property
    def p95_latency_s(self) -> float:
        if not self.durations_s:
            return 0.0
        ordered = sorted(self.durations_s)
        index = max(int(len(ordered) * 0.95) - 1, 0)
        return ordered[index]

    @property
    def error_rate(self) -> float:
        total = len(self.durations_s)
        return self.error_count / total if total else 0.0

    @property
    def requests_per_s(self) -> float:
        if self.total_duration_s <= 0:
            return 0.0
        return len(self.durations_s) / self.total_duration_s

    @property
    def step_average_latency_s(self) -> dict[str, float]:
        return {
            name: (statistics.mean(durations) if durations else 0.0)
            for name, durations in self.step_durations_s.items()
        }

    @property
    def step_p95_latency_s(self) -> dict[str, float]:
        percentiles: dict[str, float] = {}
        for name, durations in self.step_durations_s.items():
            if not durations:
                percentiles[name] = 0.0
                continue
            ordered = sorted(durations)
            index = max(int(len(ordered) * 0.95) - 1, 0)
            percentiles[name] = ordered[index]
        return percentiles

    @property
    def step_error_rate(self) -> dict[str, float]:
        total = len(self.durations_s)
        return {
            name: (errors / total if total else 0.0)
            for name, errors in self.step_error_count.items()
        }


def run_load_scenario(scenario: LoadScenario) -> LoadScenarioResult:
    durations: list[float] = []
    errors = 0
    step_durations: dict[str, list[float]] = {}
    step_errors: dict[str, int] = {}

    if scenario.flow_step_fns:
        step_fns = scenario.flow_step_fns
    elif scenario.request_fn:
        step_fns = [(scenario.name, scenario.request_fn)]
    else:
        raise ValueError("LoadScenario must define request_fn or flow_step_fns")

    for step_name, _ in step_fns:
        step_durations[step_name] = []
        step_errors[step_name] = 0

    def _invoke() -> tuple[float, bool, list[tuple[str, float, bool]]]:
        flow_start = time.perf_counter()
        flow_failed = False
        invocation_steps: list[tuple[str, float, bool]] = []

        for step_name, request_fn in step_fns:
            start = time.perf_counter()
            status = request_fn()
            duration = time.perf_counter() - start
            step_failed = status >= 400
            if step_failed:
                flow_failed = True
            invocation_steps.append((step_name, duration, step_failed))

        flow_duration = time.perf_counter() - flow_start
        return flow_duration, flow_failed, invocation_steps

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=scenario.concurrency) as executor:
        futures = [executor.submit(_invoke) for _ in range(scenario.total_requests)]
        for future in as_completed(futures):
            flow_duration, flow_failed, invocation_steps = future.result()
            durations.append(flow_duration)
            if flow_failed:
                errors += 1
            for step_name, step_duration, step_failed in invocation_steps:
                step_durations[step_name].append(step_duration)
                if step_failed:
                    step_errors[step_name] += 1
    total_duration = time.perf_counter() - start

    return LoadScenarioResult(
        name=scenario.name,
        durations_s=durations,
        error_count=errors,
        total_duration_s=total_duration,
        step_durations_s=step_durations,
        step_error_count=step_errors,
    )


def load_profile(path: Path) -> dict:
    payload = json.loads(path.read_text())
    if isinstance(payload, list):
        if not payload:
            return {}
        target_name = os.getenv("LOAD_TARGET")
        if target_name:
            for entry in payload:
                if entry.get("name") == target_name:
                    payload = entry
                    break
            else:
                payload = payload[0]
        else:
            payload = payload[0]
    elif isinstance(payload, dict) and "targets" in payload:
        targets = payload.get("targets") or []
        target_name = os.getenv("LOAD_TARGET")
        selected = None
        if target_name:
            selected = next((entry for entry in targets if entry.get("name") == target_name), None)
        payload = selected or (targets[0] if targets else {})
    profiles = payload.get("profiles")
    if not profiles:
        return payload
    profile_name = os.getenv("LOAD_PROFILE", "ci")
    selected = profiles.get(profile_name) or profiles.get("ci")
    if not selected:
        return payload
    merged = {key: value for key, value in payload.items() if key != "profiles"}
    merged.update(selected)
    return merged


def assert_sla(result: LoadScenarioResult, sla: LoadSla) -> None:
    if result.average_latency_s > sla.max_avg_latency_s:
        raise AssertionError(
            f"Average latency {result.average_latency_s:.3f}s exceeds SLA "
            f"{sla.max_avg_latency_s:.3f}s"
        )
    if result.p95_latency_s > sla.max_p95_latency_s:
        raise AssertionError(
            f"P95 latency {result.p95_latency_s:.3f}s exceeds SLA " f"{sla.max_p95_latency_s:.3f}s"
        )
    if result.error_rate > sla.max_error_rate:
        raise AssertionError(
            f"Error rate {result.error_rate:.2%} exceeds SLA " f"{sla.max_error_rate:.2%}"
        )
    if sla.min_requests_per_s is not None and result.requests_per_s < sla.min_requests_per_s:
        raise AssertionError(
            f"Throughput {result.requests_per_s:.2f} rps below SLA "
            f"{sla.min_requests_per_s:.2f} rps"
        )
