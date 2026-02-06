import logging

from fastapi.testclient import TestClient

from connectors.sap.src.main import app
from connectors.sap.src.mappers import map_to_sap


def test_sap_outbound_sync(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    def mock_send(records, tenant_id, *, include_schema):
        assert tenant_id == "test-tenant"
        assert isinstance(records, list)
        mapped_payload = map_to_sap(records)
        logging.getLogger("connectors.sap.src.main").info(
            "Outbound payload for SAP tenant %s (include_schema=%s): %s",
            tenant_id,
            include_schema,
            mapped_payload,
        )

    monkeypatch.setattr(
        "connectors.sap.src.main.send_to_external_system", mock_send
    )

    client = TestClient(app)
    payload = {
        "records": [{"id": "123", "name": "Example"}],
        "tenant_id": "test-tenant",
        "live": True,
        "include_schema": False,
    }
    response = client.post("/connectors/sap/sync/outbound", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert "Outbound payload for SAP tenant test-tenant" in caplog.text
    assert str(map_to_sap(response.json()["records"])) in caplog.text
