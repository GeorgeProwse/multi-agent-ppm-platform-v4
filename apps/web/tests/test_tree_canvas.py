import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import main  # noqa: E402
from tree_store import TreeStore  # noqa: E402
from workspace_state_store import WorkspaceStateStore  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTH_DEV_MODE", "true")
    monkeypatch.setenv("ENVIRONMENT", "test")
    main.tree_store = TreeStore(tmp_path / "trees.json")
    main.workspace_state_store = WorkspaceStateStore(tmp_path / "workspace_state.json")
    return TestClient(main.app)


def _set_tenant(monkeypatch, tenant_id: str) -> None:
    monkeypatch.setenv("AUTH_DEV_TENANT_ID", tenant_id)


def test_create_list_update_delete_nodes(client, monkeypatch):
    _set_tenant(monkeypatch, "tenant-a")
    folder_response = client.post(
        "/api/tree/demo-1/nodes",
        json={"type": "folder", "title": "Artifacts"},
    )
    assert folder_response.status_code == 200
    folder = folder_response.json()

    doc_response = client.post(
        "/api/tree/demo-1/nodes",
        json={
            "type": "document",
            "title": "Charter",
            "parent_id": folder["node_id"],
            "ref": {"document_id": "doc-1"},
        },
    )
    assert doc_response.status_code == 200
    document = doc_response.json()

    list_response = client.get("/api/tree/demo-1")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload["project_id"] == "demo-1"
    assert len(payload["nodes"]) == 2

    update_response = client.patch(
        f"/api/tree/demo-1/nodes/{document['node_id']}",
        json={"title": "Updated Charter"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Charter"

    delete_response = client.delete(f"/api/tree/demo-1/nodes/{folder['node_id']}")
    assert delete_response.status_code == 200
    delete_payload = delete_response.json()
    assert delete_payload["deleted"] is True
    assert delete_payload["deleted_count"] == 2

    list_response = client.get("/api/tree/demo-1")
    assert list_response.status_code == 200
    assert list_response.json()["nodes"] == []


def test_move_node_changes_parent(client, monkeypatch):
    _set_tenant(monkeypatch, "tenant-a")
    parent_a = client.post(
        "/api/tree/demo-1/nodes",
        json={"type": "folder", "title": "Phase 1"},
    ).json()
    parent_b = client.post(
        "/api/tree/demo-1/nodes",
        json={"type": "folder", "title": "Phase 2"},
    ).json()
    note = client.post(
        "/api/tree/demo-1/nodes",
        json={
            "type": "note",
            "title": "Reminder",
            "parent_id": parent_a["node_id"],
            "ref": {"text": "Check dependencies"},
        },
    ).json()

    move_response = client.post(
        f"/api/tree/demo-1/nodes/{note['node_id']}/move",
        json={"new_parent_id": parent_b["node_id"], "new_sort_order": 2},
    )
    assert move_response.status_code == 200
    moved = move_response.json()
    assert moved["parent_id"] == parent_b["node_id"]
    assert moved["sort_order"] == 2


def test_validation_rejects_wrong_ref_for_type(client, monkeypatch):
    _set_tenant(monkeypatch, "tenant-a")
    response = client.post(
        "/api/tree/demo-1/nodes",
        json={"type": "document", "title": "Bad", "ref": {"sheet_id": "s-1"}},
    )
    assert response.status_code == 422


def test_tenant_isolation(client, monkeypatch):
    _set_tenant(monkeypatch, "tenant-a")
    response = client.post(
        "/api/tree/demo-1/nodes",
        json={"type": "folder", "title": "Tenant A"},
    )
    assert response.status_code == 200

    _set_tenant(monkeypatch, "tenant-b")
    list_response = client.get("/api/tree/demo-1")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload["tenant_id"] == "tenant-b"
    assert payload["nodes"] == []


def test_open_ref_persists_and_drives_tab_switch(client, monkeypatch):
    _set_tenant(monkeypatch, "tenant-a")
    response = client.post(
        "/api/workspace/demo-1/select",
        json={
            "current_stage_id": None,
            "current_activity_id": None,
            "current_canvas_tab": "document",
            "methodology": None,
            "open_ref": {"document_id": "doc-99"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["current_canvas_tab"] == "document"
    assert payload["last_opened_document_id"] == "doc-99"
