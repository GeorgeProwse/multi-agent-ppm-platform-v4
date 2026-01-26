from __future__ import annotations

import json
from pathlib import Path


def test_api_gateway_contract_snapshot() -> None:
    from api.main import app

    snapshot_path = Path(__file__).resolve().parent / "api-gateway-openapi.json"
    current = app.openapi()

    snapshot = json.loads(snapshot_path.read_text())
    assert current == snapshot, "API contract changed; update snapshot if intentional."
