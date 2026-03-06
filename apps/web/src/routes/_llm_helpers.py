"""Shared LLM helpers for feature routes.

Provides a thin wrapper around LLMGateway that all feature routes use
to make real LLM calls, with graceful fallback for environments
where no LLM provider is configured.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger("routes._llm_helpers")

# Lazy-init singleton — avoids import-time failures if deps are missing.
_gateway_instance = None


def _get_llm_gateway():
    """Return a shared LLMGateway instance, created on first call."""
    global _gateway_instance
    if _gateway_instance is not None:
        return _gateway_instance

    try:
        from llm.client import LLMGateway

        provider = os.getenv("LLM_PROVIDER", "mock")
        config: dict[str, Any] = {
            "semantic_cache": {"ttl_seconds": 300},
        }
        if provider == "mock":
            config["demo_mode"] = True
        _gateway_instance = LLMGateway(provider=provider, config=config)
        return _gateway_instance
    except Exception as exc:
        logger.warning("LLMGateway init failed, using fallback: %s", exc)
        return None


async def llm_complete(
    system_prompt: str,
    user_prompt: str,
    *,
    tenant_id: str = "default",
    json_mode: bool = False,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Call the LLM and return the response content string.

    Falls back to an empty string on any provider error so that callers
    can degrade gracefully.
    """
    gateway = _get_llm_gateway()
    if gateway is None:
        return ""
    try:
        response = await gateway.complete(
            system_prompt,
            user_prompt,
            tenant_id=tenant_id,
            json_mode=json_mode,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content
    except Exception as exc:
        logger.warning("llm_complete failed: %s", exc)
        return ""


async def llm_complete_json(
    system_prompt: str,
    user_prompt: str,
    *,
    tenant_id: str = "default",
    temperature: float | None = None,
) -> dict[str, Any]:
    """Call the LLM expecting a JSON response. Returns parsed dict or empty dict."""
    raw = await llm_complete(
        system_prompt,
        user_prompt,
        tenant_id=tenant_id,
        json_mode=True,
        temperature=temperature,
    )
    if not raw:
        return {}
    # Strip markdown fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("llm_complete_json: could not parse response as JSON")
        return {}
