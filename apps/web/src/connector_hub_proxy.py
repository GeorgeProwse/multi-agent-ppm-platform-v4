from __future__ import annotations

import os
from typing import Any

import httpx


class ConnectorHubClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url or os.getenv("CONNECTOR_HUB_URL", "http://connector-hub:8080")
        self.timeout = timeout
        self.transport = transport

    async def list_connectors(self, headers: dict[str, str]) -> httpx.Response:
        return await self._request("GET", "/connectors", headers=headers)

    async def create_connector(
        self, payload: dict[str, Any], headers: dict[str, str]
    ) -> httpx.Response:
        return await self._request("POST", "/connectors", headers=headers, json=payload)

    async def update_connector(
        self, connector_id: str, payload: dict[str, Any], headers: dict[str, str]
    ) -> httpx.Response:
        return await self._request(
            "PATCH", f"/connectors/{connector_id}", headers=headers, json=payload
        )

    async def get_connector_health(
        self, connector_id: str, headers: dict[str, str]
    ) -> httpx.Response:
        return await self._request("GET", f"/connectors/{connector_id}/health", headers=headers)

    async def _request(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, transport=self.transport
        ) as client:
            return await client.request(method, path, headers=headers, json=json)
