from __future__ import annotations

import sys
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SERVICE_ROOT / "src" / "main.py"

spec = spec_from_file_location("audit_log_main", MODULE_PATH)
module = module_from_spec(spec)
assert spec and spec.loader
sys.path.insert(0, str(SERVICE_ROOT / "src"))
sys.modules[spec.name] = module
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["service"] == "audit-log"


def test_ingest_and_fetch_event(monkeypatch) -> None:
    storage_path = (
        Path(__file__).resolve().parents[3]
        / "services"
        / "audit-log"
        / "storage"
        / "immutable"
    )
    if storage_path.exists():
        for path in storage_path.glob("*.enc"):
            path.unlink()
    monkeypatch.setenv("AUDIT_LOG_ENCRYPTION_KEY", "Y2hhbmdlLW1lLW5vdC1wcm9kLWsxMjM0NTY3ODkwMTIzNDU2Nzg5MA==")
    monkeypatch.setenv("AUDIT_WORM_LOCAL_PATH", str(storage_path))

    payload = {
        "id": "evt-123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": "tenant-alpha",
        "actor": {"id": "user-1", "type": "user", "roles": ["auditor"]},
        "action": "project.create",
        "resource": {"id": "proj-9", "type": "project"},
        "outcome": "success",
        "classification": "internal",
        "metadata": {"ip": "127.0.0.1"},
        "trace_id": "trace-1",
        "correlation_id": "corr-1",
    }

    response = client.post("/audit/events", json=payload)
    assert response.status_code == 200
    assert response.json()["event"]["id"] == "evt-123"

    fetch = client.get("/audit/events/evt-123")
    assert fetch.status_code == 200
    assert fetch.json()["action"] == "project.create"

    assert storage_path.exists()
    encrypted_files = list(storage_path.glob("*.enc"))
    assert encrypted_files
