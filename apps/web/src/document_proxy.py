from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import Request


def build_forward_headers(request: Request, session: dict[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    access_token = session.get("access_token")
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            headers["Authorization"] = auth_header
    tenant_id = session.get("tenant_id")
    if tenant_id:
        headers["X-Tenant-ID"] = tenant_id
    dev_user = request.headers.get("X-Dev-User")
    if dev_user:
        headers["X-Dev-User"] = dev_user
    return headers


class DocumentServiceClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url or os.getenv(
            "DOCUMENT_SERVICE_URL", "http://document-service:8080"
        )
        self.timeout = timeout
        self.transport = transport

    async def create_document(
        self, payload: dict[str, Any], headers: dict[str, str]
    ) -> httpx.Response:
        return await self._request("POST", "/documents", headers=headers, json=payload)

    async def list_documents(self, headers: dict[str, str]) -> httpx.Response:
        return await self._request("GET", "/documents", headers=headers)

    async def get_document(self, document_id: str, headers: dict[str, str]) -> httpx.Response:
        return await self._request("GET", f"/documents/{document_id}", headers=headers)

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
