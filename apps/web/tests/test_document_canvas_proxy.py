import sys
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import main  # noqa: E402
from document_proxy import DocumentServiceClient  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUTH_DEV_MODE", "true")
    monkeypatch.setenv("ENVIRONMENT", "test")
    return TestClient(main.app)


def _set_tenant(monkeypatch, tenant_id: str) -> None:
    monkeypatch.setenv("AUTH_DEV_TENANT_ID", tenant_id)


def _wire_client(monkeypatch, transport: httpx.AsyncBaseTransport) -> None:
    def _client() -> DocumentServiceClient:
        return DocumentServiceClient(base_url="http://document-service:8080", transport=transport)

    monkeypatch.setattr(main, "_document_client", _client)


def test_create_document_success_forwards_headers(client, monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["headers"] = dict(request.headers)
        captured["path"] = request.url.path
        return httpx.Response(
            200,
            json={
                "document_id": "doc-1",
                "name": "Spec",
                "classification": "internal",
                "retention_days": 90,
                "created_at": "2024-01-01T00:00:00Z",
                "retention_until": "2024-03-31T00:00:00Z",
                "metadata": {},
                "advisories": ["log retention"],
                "content": "content",
            },
        )

    transport = httpx.MockTransport(handler)
    _wire_client(monkeypatch, transport)
    _set_tenant(monkeypatch, "tenant-a")

    response = client.post(
        "/api/document-canvas/documents",
        json={
            "name": "Spec",
            "content": "content",
            "classification": "internal",
            "retention_days": 90,
            "metadata": {},
        },
        headers={"X-Dev-User": "tester"},
    )

    assert response.status_code == 200
    assert captured["path"] == "/documents"
    assert captured["headers"]["authorization"] == "Bearer dev-token"
    assert captured["headers"]["x-tenant-id"] == "tenant-a"
    assert captured["headers"]["x-dev-user"] == "tester"


def test_create_document_policy_denied_propagates_reasons(client, monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"detail": {"reasons": ["blocked"]}})

    transport = httpx.MockTransport(handler)
    _wire_client(monkeypatch, transport)
    _set_tenant(monkeypatch, "tenant-a")

    response = client.post(
        "/api/document-canvas/documents",
        json={
            "name": "Spec",
            "content": "content",
            "classification": "restricted",
            "retention_days": 90,
            "metadata": {},
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": {"reasons": ["blocked"]}}


def test_list_documents_tenant_scoped(client, monkeypatch):
    async def handler_tenant_a(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-tenant-id"] == "tenant-a"
        return httpx.Response(200, json=[{"document_id": "doc-a"}])

    transport = httpx.MockTransport(handler_tenant_a)
    _wire_client(monkeypatch, transport)
    _set_tenant(monkeypatch, "tenant-a")

    response = client.get("/api/document-canvas/documents")
    assert response.status_code == 200
    assert response.json() == [{"document_id": "doc-a"}]

    async def handler_tenant_b(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-tenant-id"] == "tenant-b"
        return httpx.Response(200, json=[{"document_id": "doc-b"}])

    transport_b = httpx.MockTransport(handler_tenant_b)
    _wire_client(monkeypatch, transport_b)
    _set_tenant(monkeypatch, "tenant-b")

    response = client.get("/api/document-canvas/documents")
    assert response.status_code == 200
    assert response.json() == [{"document_id": "doc-b"}]


def test_get_document_by_id(client, monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/documents/doc-77"
        return httpx.Response(200, json={"document_id": "doc-77"})

    transport = httpx.MockTransport(handler)
    _wire_client(monkeypatch, transport)
    _set_tenant(monkeypatch, "tenant-a")

    response = client.get("/api/document-canvas/documents/doc-77")
    assert response.status_code == 200
    assert response.json() == {"document_id": "doc-77"}
