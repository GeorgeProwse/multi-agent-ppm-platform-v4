from __future__ import annotations

import pytest
from common.resilience import (
    CircuitBreakerPolicy,
    CircuitOpenError,
    DependencyResilienceConfig,
    ResilienceMiddleware,
    RetryPolicy,
    TimeoutPolicy,
)
from feature_flags.manager import (
    clear_all_dependency_degraded,
    is_dependency_degraded,
    should_use_degraded_mode,
)


@pytest.mark.asyncio
async def test_circuit_open_half_open_and_close_transition() -> None:
    clear_all_dependency_degraded()
    middleware = ResilienceMiddleware(
        DependencyResilienceConfig(
            dependency="dep_test",
            retry=RetryPolicy(max_attempts=1, initial_backoff_s=0),
            timeout=TimeoutPolicy(timeout_s=1),
            circuit_breaker=CircuitBreakerPolicy(
                failure_threshold=1,
                failure_window_s=60,
                recovery_timeout_s=0.01,
            ),
        )
    )

    async def fail() -> int:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await middleware.execute_async(fail)

    assert is_dependency_degraded("dep_test") is True

    with pytest.raises(CircuitOpenError):
        await middleware.execute_async(lambda: fail())

    await __import__("asyncio").sleep(0.02)

    async def succeed() -> int:
        return 7

    value = await middleware.execute_async(succeed)
    assert value == 7
    assert is_dependency_degraded("dep_test") is False


def test_degraded_mode_activates_from_circuit_open(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_all_dependency_degraded()
    monkeypatch.setenv("ENVIRONMENT", "dev")
    assert should_use_degraded_mode("non_existent_flag", "dep_test") is False

    middleware = ResilienceMiddleware(
        DependencyResilienceConfig(
            dependency="dep_test",
            retry=RetryPolicy(max_attempts=1, initial_backoff_s=0),
            timeout=TimeoutPolicy(timeout_s=1),
            circuit_breaker=CircuitBreakerPolicy(failure_threshold=1),
        )
    )

    with pytest.raises(Exception):
        middleware.execute(lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    assert should_use_degraded_mode("non_existent_flag", "dep_test") is True


def test_metric_counters_increment_on_open_denial() -> None:
    from common import resilience as resilience_module

    middleware = ResilienceMiddleware(
        DependencyResilienceConfig(
            dependency="metric_dep",
            retry=RetryPolicy(max_attempts=1, initial_backoff_s=0),
            timeout=TimeoutPolicy(timeout_s=1),
            circuit_breaker=CircuitBreakerPolicy(failure_threshold=1),
        )
    )

    with pytest.raises(Exception):
        middleware.execute(lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(CircuitOpenError):
        middleware.execute(lambda: 1)

    if resilience_module._open_denials is not None:  # noqa: SLF001
        assert resilience_module._open_denials.labels(dependency="metric_dep")._value.get() >= 1
