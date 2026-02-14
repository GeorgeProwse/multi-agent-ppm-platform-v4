import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

pytest.importorskip("email_validator")

import main  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUTH_DEV_MODE", "true")
    monkeypatch.setenv("AUTH_DEV_TENANT_ID", "tenant-demo")
    monkeypatch.setenv("ENVIRONMENT", "test")
    return TestClient(main.app)


def test_search_endpoint_returns_demo_results(client, monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    response = client.get("/api/search?q=risk")
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "risk"
    assert payload["total"] == len(payload["results"])
    assert any(result["type"] == "project" for result in payload["results"])


def test_assistant_endpoint_returns_demo_response(client, monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    response = client.post(
        "/api/assistant",
        json={"query": "Which projects have the highest risk exposure?"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "highest risk exposure" in payload["summary"].lower()
    assert payload["items"]


def test_assistant_demo_conversation_endpoint_returns_script(client):
    response = client.get("/api/assistant/demo-conversations/project_intake")
    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"] == "project_intake"
    assert isinstance(payload["messages"], list)
    assert payload["messages"]
    assert payload["messages"][0]["role"] in {"assistant", "user"}


def test_assistant_demo_conversation_endpoint_rejects_unknown_scenario(client):
    response = client.get("/api/assistant/demo-conversations/not_real")
    assert response.status_code == 404
