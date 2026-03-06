"""Tests for security posture endpoints (Enhancement 9)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import router directly to avoid routes/__init__.py triggering unrelated imports.
_mod_path = Path(__file__).resolve().parents[2] / "apps" / "web" / "src" / "routes" / "security_posture.py"
_spec = importlib.util.spec_from_file_location("security_posture", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["security_posture"] = _mod
_spec.loader.exec_module(_mod)
_router = _mod.router


def _make_app():
    app = FastAPI()
    app.include_router(_router)
    return app


@pytest.fixture
def client():
    return TestClient(_make_app())


def test_security_posture(client):
    resp = client.get("/api/security/posture")
    assert resp.status_code == 200
    data = resp.json()
    assert "posture_score" in data
    assert 0 <= data["posture_score"] <= 100
    assert "compliance_checks" in data


def test_list_policies(client):
    resp = client.get("/api/security/policies")
    assert resp.status_code == 200
    policies = resp.json()
    assert len(policies) > 0
    assert all("policy_id" in p for p in policies)


def test_test_policy(client):
    resp = client.post(
        "/api/security/policies/test",
        json={
            "policy": {
                "policy_id": "test-pol",
                "name": "Test",
                "description": "test",
                "effect": "deny",
                "subjects": {},
                "resources": {},
                "actions": ["read"],
                "conditions": [{"field": "subject.role", "operator": "equals", "value": "admin"}],
                "enabled": True,
            },
            "context": {"subject": {"role": "admin"}},
        },
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == "deny"


def test_classification_stats(client):
    resp = client.get("/api/security/classification-stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "public" in data
    assert "restricted" in data
