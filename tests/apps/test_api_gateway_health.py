import importlib.util

import pytest
from fastapi.testclient import TestClient


def _slowapi_available() -> bool:
    return importlib.util.find_spec("slowapi") is not None


@pytest.mark.skipif(not _slowapi_available(), reason="slowapi is not installed")
def test_healthz():
    from api.main import app

    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
