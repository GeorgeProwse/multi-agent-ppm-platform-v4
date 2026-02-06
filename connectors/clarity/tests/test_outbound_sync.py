import logging

from fastapi.testclient import TestClient

from connectors.clarity.src.main import app
from connectors.clarity.src.mappers import map_to_clarity


def test_clarity_outbound_sync(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    def mock_send(records, tenant_id, *, include_schema):
        assert tenant_id == "test-tenant"
        assert isinstance(records, list)
        mapped_payload = map_to_clarity(records)
        logging.getLogger("connectors.clarity.src.main").info(
            "Outbound payload for Clarity tenant %s (include_schema=%s): %s",
            tenant_id,
            include_schema,
            mapped_payload,
        )

    monkeypatch.setattr(
        "connectors.clarity.src.main.send_to_external_system", mock_send
    )

    client = TestClient(app)
    payload = {
        "records": [{"id": "xyz", "name": "Clarity Example"}],
        "tenant_id": "test-tenant",
        "live": True,
        "include_schema": False,
    }
    response = client.post("/connectors/clarity/sync/outbound", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert "Outbound payload for Clarity tenant test-tenant" in caplog.text
    assert str(map_to_clarity(response.json()["records"])) in caplog.text
