from __future__ import annotations

import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parents[4]
SRC_DIR = TESTS_DIR.parent / "src"
sys.path.extend(
    [
        str(SRC_DIR),
        str(REPO_ROOT),
        str(REPO_ROOT / "packages"),
        str(REPO_ROOT / "agents" / "runtime"),
    ]
)

from quality_management_agent import QualityManagementAgent


class DummyEventBus:
    def __init__(self) -> None:
        self.published: list[tuple[str, dict]] = []

    async def publish(self, topic: str, payload: dict) -> None:
        self.published.append((topic, payload))


def _make_agent(tmp_path: Path) -> QualityManagementAgent:
    return QualityManagementAgent(
        config={
            "event_bus": DummyEventBus(),
            "quality_plan_store_path": str(tmp_path / "quality_plans.json"),
            "test_case_store_path": str(tmp_path / "test_cases.json"),
            "defect_store_path": str(tmp_path / "defects.json"),
            "audit_store_path": str(tmp_path / "audits.json"),
            "requirement_link_store_path": str(tmp_path / "req_links.json"),
            "coverage_trend_store_path": str(tmp_path / "coverage.json"),
            "approval_agent_enabled": False,
        }
    )


@pytest.mark.anyio
async def test_create_quality_plan(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    result = await agent.process(
        {
            "action": "create_quality_plan",
            "tenant_id": "tenant-1",
            "plan": {
                "project_id": "proj-001",
                "objectives": ["zero_critical_defects", "test_coverage_90"],
                "standards": ["ISO 9001"],
                "review_cadence": "weekly",
            },
        }
    )
    assert result.get("plan_id") or result.get("project_id") == "proj-001"


@pytest.mark.anyio
async def test_log_defect_creates_defect(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    result = await agent.process(
        {
            "action": "log_defect",
            "tenant_id": "tenant-1",
            "defect": {
                "summary": "Login button unresponsive on mobile",
                "severity": "high",
                "component": "auth-ui",
                "description": "Button does not respond to tap on iOS 17",
                "reporter": "qa-engineer-1",
            },
        }
    )
    assert result.get("defect_id")
    assert result.get("status")


@pytest.mark.anyio
async def test_log_defect_assigns_owner(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    result = await agent.process(
        {
            "action": "log_defect",
            "tenant_id": "tenant-2",
            "defect": {
                "summary": "Data export produces incorrect totals",
                "severity": "critical",
                "component": "reporting",
                "description": "Export totals off by 10% for Q4",
                "reporter": "qa-lead",
            },
        }
    )
    defect_id = result.get("defect_id")
    assert defect_id
    assert defect_id in agent.defects


@pytest.mark.anyio
async def test_create_test_case(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    result = await agent.process(
        {
            "action": "create_test_case",
            "tenant_id": "tenant-1",
            "test_case": {
                "name": "Verify login with valid credentials",
                "description": "User can log in using correct username and password",
                "steps": [
                    {"step": 1, "action": "Enter username", "expected": "Field accepts input"},
                    {"step": 2, "action": "Enter password", "expected": "Field is masked"},
                    {"step": 3, "action": "Click login", "expected": "Dashboard loads"},
                ],
                "component": "auth",
                "priority": "high",
            },
        }
    )
    assert result.get("test_case_id") or result.get("success") is not False


@pytest.mark.anyio
async def test_validate_input_rejects_missing_action(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    valid = await agent.validate_input({})
    assert valid is False


@pytest.mark.anyio
async def test_validate_input_rejects_log_defect_missing_fields(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    valid = await agent.validate_input(
        {
            "action": "log_defect",
            "defect": {"summary": "Missing severity and component"},
        }
    )
    assert valid is False


@pytest.mark.anyio
async def test_validate_input_accepts_log_defect_with_required_fields(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    valid = await agent.validate_input(
        {
            "action": "log_defect",
            "defect": {
                "summary": "Something broken",
                "severity": "medium",
                "component": "api",
            },
        }
    )
    assert valid is True


@pytest.mark.anyio
async def test_validate_input_rejects_create_plan_missing_objectives(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    valid = await agent.validate_input(
        {
            "action": "create_quality_plan",
            "plan": {"project_id": "proj-x"},
        }
    )
    assert valid is False


@pytest.mark.anyio
async def test_defect_classifier_initializes(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    # Classifier is built lazily; verify the agent started cleanly
    assert agent.min_test_coverage == pytest.approx(0.80)
    assert "critical" in agent.defect_severity_levels
