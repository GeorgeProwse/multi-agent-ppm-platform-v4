import logging

from fastapi.testclient import TestClient

from connectors.planview.src.main import app
from connectors.planview.src.mappers import map_to_planview


def test_planview_outbound_sync(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    def mock_send(records, tenant_id, *, include_schema):
        assert tenant_id == "test-tenant"
        assert isinstance(records, list)
        mapped_payload = map_to_planview(records)
        logging.getLogger("connectors.planview.src.main").info(
            "Outbound payload for Planview tenant %s (include_schema=%s): %s",
            tenant_id,
            include_schema,
            mapped_payload,
        )

    monkeypatch.setattr(
        "connectors.planview.src.main.send_to_external_system", mock_send
    )

    client = TestClient(app)
    payload = {
        "records": [{"id": "abc", "name": "Planview Example"}],
        "tenant_id": "test-tenant",
        "live": True,
        "include_schema": False,
    }
    response = client.post("/connectors/planview/sync/outbound", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert "Outbound payload for Planview tenant test-tenant" in caplog.text
    assert str(map_to_planview(response.json()["records"])) in caplog.text
