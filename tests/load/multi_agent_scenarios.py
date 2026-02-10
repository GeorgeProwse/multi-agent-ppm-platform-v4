from __future__ import annotations

import os
from collections.abc import Callable
from urllib.parse import urljoin

import httpx

from ops.tools.load_testing.runner import LoadScenario


def _build_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    auth_token = os.getenv("PERFORMANCE_AUTH_TOKEN")
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    tenant_id = os.getenv("PERFORMANCE_TENANT_ID")
    if tenant_id:
        headers["X-Tenant-ID"] = tenant_id
    return headers


def _build_step_request(base_url: str, timeout: float, step: dict) -> tuple[str, Callable[[], int]]:
    target_url = step["target_url"]
    request_url = (
        target_url
        if target_url.startswith("http")
        else urljoin(base_url.rstrip("/") + "/", target_url)
    )
    method = str(step.get("method", "GET")).upper()
    payload = step.get("payload")
    headers = _build_headers()

    def _request() -> int:
        try:
            response = httpx.request(
                method,
                request_url,
                timeout=timeout,
                headers=headers,
                json=payload,
            )
            return response.status_code
        except httpx.RequestError:
            return 599

    return step["name"], _request


def build_multi_agent_flow_scenario(profile: dict) -> LoadScenario:
    base_url = os.getenv(
        "PERFORMANCE_BASE_URL",
        profile.get("base_url") or "https://staging.api.ppm-platform.com",
    )
    timeout = float(profile.get("timeout_s", 10.0))
    steps = profile.get("flow_steps")
    if not steps:
        steps = [
            {
                "name": profile.get("name", "default"),
                "target_url": profile.get("target_url", "/v1/health"),
                "method": profile.get("method", "GET"),
                "payload": profile.get("payload"),
            }
        ]
    flow_step_fns = [_build_step_request(base_url, timeout, step) for step in steps]
    return LoadScenario(
        name=profile["name"],
        total_requests=int(profile["total_requests"]),
        concurrency=int(profile["concurrency"]),
        flow_step_fns=flow_step_fns,
    )
