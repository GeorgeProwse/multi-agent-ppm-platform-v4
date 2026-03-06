"""Tests for knowledge graph endpoints (Enhancement 10)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

_mod_path = Path(__file__).resolve().parents[2] / "apps" / "web" / "src" / "routes" / "knowledge_graph.py"
_spec = importlib.util.spec_from_file_location("knowledge_graph", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["knowledge_graph"] = _mod
_spec.loader.exec_module(_mod)
_router = _mod.router


def _make_app():
    app = FastAPI()
    app.include_router(_router)
    return app


@pytest.fixture
def client():
    return TestClient(_make_app())


def test_get_graph(client):
    resp = client.get("/api/knowledge/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0


def test_get_patterns(client):
    resp = client.get("/api/knowledge/patterns")
    assert resp.status_code == 200
    patterns = resp.json()
    assert len(patterns) > 0
    assert all("pattern_id" in p for p in patterns)


def test_get_recommendations(client):
    resp = client.post(
        "/api/knowledge/recommendations",
        json={"project_id": "proj-alpha", "context_type": "general"},
    )
    assert resp.status_code == 200
    recs = resp.json()
    assert len(recs) > 0
    assert all("recommendation_id" in r for r in recs)


def test_get_stats(client):
    resp = client.get("/api/knowledge/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_nodes"] > 0
    assert data["total_edges"] > 0
    assert "node_types" in data
