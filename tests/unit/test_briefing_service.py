"""Tests for briefing generator (Enhancement 5)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

_mod_path = Path(__file__).resolve().parents[2] / "apps" / "web" / "src" / "routes" / "briefings.py"
_spec = importlib.util.spec_from_file_location("briefings", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["briefings"] = _mod
_spec.loader.exec_module(_mod)
_router = _mod.router


def _make_app():
    app = FastAPI()
    app.include_router(_router)
    return app


@pytest.fixture
def client():
    return TestClient(_make_app())


def test_generate_briefing(client):
    resp = client.post(
        "/api/briefings/generate",
        json={
            "portfolio_id": "default",
            "audience": "c_suite",
            "tone": "formal",
            "sections": ["highlights", "risks", "financials"],
            "format": "markdown",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["briefing_id"].startswith("brief-")
    assert "Portfolio Briefing" in data["title"]
    assert len(data["sections"]) == 3
    assert "Key Highlights" in data["content"]


def test_generate_briefing_all_sections(client):
    resp = client.post(
        "/api/briefings/generate",
        json={
            "audience": "board",
            "sections": ["highlights", "risks", "financials", "schedule", "resources", "recommendations"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["sections"]) == 6


def test_briefing_history(client):
    # Generate one first
    client.post("/api/briefings/generate", json={"audience": "pmo"})
    resp = client.get("/api/briefings/history")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_generate_briefing_default_sections(client):
    resp = client.post("/api/briefings/generate", json={})
    assert resp.status_code == 200
    assert len(resp.json()["sections"]) == 6
