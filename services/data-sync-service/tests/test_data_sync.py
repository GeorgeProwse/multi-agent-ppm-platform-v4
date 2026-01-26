from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SERVICE_ROOT / "src" / "main.py"

spec = spec_from_file_location("data_sync_main", MODULE_PATH)
module = module_from_spec(spec)
assert spec and spec.loader
sys.path.insert(0, str(SERVICE_ROOT / "src"))
sys.modules[spec.name] = module
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_run_sync_creates_status(monkeypatch, tmp_path) -> None:
    status_path = tmp_path / "status.json"
    monkeypatch.setenv("DATA_SYNC_STATUS_PATH", str(status_path))

    response = client.post("/sync/run", json={"connector": "jira", "dry_run": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"

    status_response = client.get(f"/sync/status/{payload['job_id']}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "queued"
