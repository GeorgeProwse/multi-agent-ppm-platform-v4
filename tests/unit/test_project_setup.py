"""Tests for project setup wizard (Enhancement 7)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

_mod_path = Path(__file__).resolve().parents[2] / "apps" / "web" / "src" / "routes" / "project_setup.py"
_spec = importlib.util.spec_from_file_location("project_setup", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["project_setup"] = _mod
_spec.loader.exec_module(_mod)
_router = _mod.router


def _make_app():
    app = FastAPI()
    app.include_router(_router)
    return app


@pytest.fixture
def client():
    return TestClient(_make_app())


def test_recommend_methodology(client):
    resp = client.post(
        "/api/project-setup/recommend-methodology",
        json={
            "industry": "technology",
            "team_size": 10,
            "duration_months": 6,
            "risk_level": "medium",
        },
    )
    assert resp.status_code == 200
    recs = resp.json()
    assert len(recs) == 3
    methodologies = {r["methodology"] for r in recs}
    assert methodologies == {"predictive", "adaptive", "hybrid"}
    assert all(0 < r["match_score"] < 1 for r in recs)


def test_list_templates_all(client):
    resp = client.get("/api/project-setup/templates")
    assert resp.status_code == 200
    templates = resp.json()
    assert len(templates) >= 3


def test_list_templates_filtered(client):
    resp = client.get("/api/project-setup/templates?methodology=adaptive")
    assert resp.status_code == 200
    templates = resp.json()
    assert all(t["methodology"] == "adaptive" for t in templates)


def test_configure_workspace(client):
    resp = client.post(
        "/api/project-setup/configure-workspace?project_name=My%20New%20Project&template_id=tmpl-agile-tech"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_name"] == "My New Project"
    assert data["project_id"].startswith("proj-")
    assert data["methodology"] == "adaptive"
