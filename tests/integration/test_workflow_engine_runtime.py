from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from fastapi.testclient import TestClient


def _load_app():
    module_path = Path(__file__).resolve().parents[2] / "apps" / "workflow-engine" / "src" / "main.py"
    spec = spec_from_file_location("workflow_engine_main", module_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.app


def test_workflow_persistence(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "workflow.db"
    monkeypatch.setenv("WORKFLOW_DB_PATH", str(db_path))

    app = _load_app()
    client = TestClient(app)

    response = client.post(
        "/workflows/start",
        json={
            "workflow_id": "intake-triage",
            "tenant_id": "tenant-alpha",
            "classification": "internal",
            "payload": {"request": "run"},
            "actor": {"id": "user-123", "type": "user", "roles": ["portfolio_admin"]},
        },
    )
    assert response.status_code == 200
    run_id = response.json()["run_id"]

    fetch = client.get(f"/workflows/{run_id}")
    assert fetch.status_code == 200
    assert fetch.json()["run_id"] == run_id
