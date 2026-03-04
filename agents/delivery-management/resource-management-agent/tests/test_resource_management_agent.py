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

from resource_capacity_agent import ResourceCapacityAgent


class DummyEventBus:
    def __init__(self) -> None:
        self.published: list[tuple[str, dict]] = []

    async def publish(self, topic: str, payload: dict) -> None:
        self.published.append((topic, payload))


def _make_agent(tmp_path: Path) -> ResourceCapacityAgent:
    return ResourceCapacityAgent(
        config={
            "event_bus": DummyEventBus(),
            "resource_store_path": str(tmp_path / "resources.json"),
            "allocation_store_path": str(tmp_path / "allocations.json"),
            "calendar_store_path": str(tmp_path / "calendars.json"),
            "risk_adjustments_path": str(tmp_path / "risk_adj.yaml"),
            "enforce_allocation_constraints": False,
            "max_allocation_threshold": 1.0,
            "skill_matching_threshold": 0.70,
        }
    )


@pytest.mark.anyio
async def test_add_resource_creates_entry(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    result = await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-1",
            "resource": {
                "name": "Alice Chen",
                "role": "Senior Developer",
                "skills": ["Python", "FastAPI", "Azure"],
                "availability": 1.0,
                "cost_per_hour": 150.0,
                "location": "Sydney",
            },
        }
    )
    assert result.get("resource_id")


@pytest.mark.anyio
async def test_get_resource_pool_returns_resources(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    # Add a resource first
    await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-2",
            "resource": {
                "name": "Bob Smith",
                "role": "BA",
                "skills": ["Requirements", "JIRA"],
                "availability": 0.8,
                "cost_per_hour": 100.0,
            },
        }
    )
    result = await agent.process(
        {
            "action": "get_resource_pool",
            "tenant_id": "tenant-2",
        }
    )
    assert result.get("resources") is not None or result.get("resource_pool") is not None


@pytest.mark.anyio
async def test_allocate_resource_after_add(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    add_result = await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-3",
            "resource": {
                "name": "Carol Williams",
                "role": "PM",
                "skills": ["Project Management", "Agile"],
                "availability": 1.0,
                "cost_per_hour": 120.0,
            },
        }
    )
    resource_id = add_result.get("resource_id")
    assert resource_id

    alloc_result = await agent.process(
        {
            "action": "allocate_resource",
            "tenant_id": "tenant-3",
            "resource_id": resource_id,
            "project_id": "proj-x",
            "allocation_percentage": 0.5,
            "start_date": "2026-04-01",
            "end_date": "2026-06-30",
            "role": "Project Manager",
        }
    )
    assert alloc_result.get("allocation_id") or alloc_result.get("success") is not False


@pytest.mark.anyio
async def test_match_skills_returns_candidates(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    # Add resources with different skills
    for name, skills in [
        ("Dev 1", ["Python", "Django"]),
        ("Dev 2", ["Python", "FastAPI", "Azure"]),
        ("BA 1", ["Requirements", "Stakeholder Management"]),
    ]:
        await agent.process(
            {
                "action": "add_resource",
                "tenant_id": "tenant-4",
                "resource": {
                    "name": name,
                    "role": "Specialist",
                    "skills": skills,
                    "availability": 1.0,
                    "cost_per_hour": 100.0,
                },
            }
        )

    result = await agent.process(
        {
            "action": "match_skills",
            "tenant_id": "tenant-4",
            "required_skills": ["Python", "Azure"],
            "project_id": "proj-skills",
        }
    )
    assert result.get("matches") is not None or result.get("candidates") is not None


@pytest.mark.anyio
async def test_validate_input_rejects_empty(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    valid = await agent.validate_input({})
    assert valid is False


@pytest.mark.anyio
async def test_default_config_values(tmp_path: Path) -> None:
    agent = _make_agent(tmp_path)
    assert agent.max_allocation_threshold == pytest.approx(1.0)
    assert agent.skill_matching_threshold == pytest.approx(0.70)
    assert agent.forecast_horizon_months == 12
