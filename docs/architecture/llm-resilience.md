# LLM Resilience & Timeout Architecture

This document describes the resilience patterns applied to LLM (Large Language Model)
interactions across the Multi-Agent PPM Platform.

## Overview

All LLM calls flow through `packages/llm/src/llm/client.py` (`LLMGateway`), which
wraps provider-specific clients with layered resilience: timeouts, retries, circuit
breakers, and provider-chain fallback.

## Timeout Budget

| Layer | Default | Env Var | Source |
|---|---|---|---|
| HTTP request timeout | 10 s | `LLM_TIMEOUT` | `packages/llm/src/llm/client.py` |
| Azure OpenAI provider | 10 s | `LLM_TIMEOUT` | `packages/llm/src/providers/azure_openai_provider.py` |

The `LLM_TIMEOUT` environment variable controls the per-request HTTP timeout for all
LLM providers. In production, consider raising this to 30-60 s for complex multi-agent
orchestration chains.

## Retry Policy

Configured per provider via `ResilienceMiddleware`:

| Parameter | Default | Env Override |
|---|---|---|
| Max attempts | 3 | Via config dict `retry_policy.max_attempts` |
| Initial backoff | 0.2 s | Via config dict `retry_policy.initial_backoff_s` |
| Backoff multiplier | 2.0x | Hardcoded in `RetryPolicy` |

Retryable HTTP status codes: `408, 409, 425, 429, 500, 502, 503, 504`.

Non-retryable errors (e.g., 401 auth failures) break the retry chain immediately.

## Circuit Breaker

Configured in `packages/common/src/common/resilience.py`:

| Parameter | Default |
|---|---|
| Failure threshold | 5 failures within window |
| Failure window | 60 s |
| Recovery timeout | 30 s |

**Behaviour:**
1. **Closed** (normal) -- requests pass through; failures are counted.
2. **Open** -- after 5 failures within 60 s, all requests are rejected immediately
   with `CircuitOpenError` for 30 s.
3. **Half-open** -- after 30 s, one probe request is allowed. If it succeeds the
   circuit closes; if it fails the circuit reopens.

State transitions emit Prometheus metrics (`circuit_breaker_state_transitions_total`).

## Provider Chain Fallback

`LLMGateway` supports a provider chain (e.g., `["azure", "openai"]`). On retryable
errors, the gateway falls through to the next provider in the chain. Each provider
maintains its own circuit breaker instance.

## Structured Response Retry

For JSON-structured responses (`structured()` method), the gateway applies up to 2
correction attempts. If the LLM returns invalid JSON, the gateway sends a correction
prompt and retries parsing.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_TIMEOUT` | `10` | HTTP request timeout in seconds |
| `LLM_PROVIDER` | `mock` | Provider name or comma-separated chain |
| `LLM_TEMPERATURE` | `0` | Model temperature (0 = deterministic) |
| `AZURE_OPENAI_ENDPOINT` | -- | Azure OpenAI API endpoint URL |
| `AZURE_OPENAI_API_KEY` | -- | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | -- | Azure OpenAI deployment/model name |
| `AZURE_OPENAI_API_VERSION` | -- | Azure OpenAI API version |

## Production Tuning Recommendations

1. **Increase `LLM_TIMEOUT`** to 30-60 s for agent chains that involve multiple
   sequential LLM calls (e.g., intent routing -> response orchestration -> approval).
2. **Monitor circuit breaker state** via the `circuit_breaker_state_transitions_total`
   Prometheus metric. Alert on repeated open transitions.
3. **Set `LLM_PROVIDER`** to a real provider (e.g., `azure`) -- the default `mock`
   provider is for development/testing only.
4. **Use provider chains** for high-availability (e.g., `azure,openai`) so that
   transient failures on one provider fall through to the backup.
