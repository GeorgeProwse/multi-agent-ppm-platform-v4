import sys
import types

import pytest
from pydantic import BaseModel


events_stub = types.ModuleType("events")


class _Event(BaseModel):
    event_name: str
    event_id: str
    timestamp: object
    tenant_id: str
    correlation_id: str
    trace_id: str | None = None
    payload: dict


events_stub.CharterCreatedEvent = _Event
events_stub.WbsCreatedEvent = _Event
events_stub.ScopeChangeEvent = _Event
sys.modules["events"] = events_stub

from project_definition_agent import ProjectDefinitionAgent


class EventCollector:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    async def publish(self, topic: str, payload: dict) -> None:
        self.events.append((topic, payload))


@pytest.mark.asyncio
async def test_project_definition_charter_and_wbs_structure_and_events(tmp_path) -> None:
    event_bus = EventCollector()
    agent = ProjectDefinitionAgent(
        config={
            "event_bus": event_bus,
            "charter_store_path": tmp_path / "charters.json",
            "wbs_store_path": tmp_path / "wbs.json",
        }
    )
    await agent.initialize()

    charter = await agent.process(
        {
            "action": "generate_charter",
            "tenant_id": "tenant-a",
            "charter_data": {
                "title": "Project Helios",
                "description": "Launch customer analytics platform",
                "project_type": "delivery",
                "methodology": "hybrid",
            },
        }
    )

    project_id = charter["project_id"]
    assert charter["charter_id"]
    assert charter["document"].keys() >= {
        "executive_summary",
        "objectives",
        "scope_overview",
        "success_criteria",
    }

    wbs = await agent.process(
        {
            "action": "generate_wbs",
            "tenant_id": "tenant-a",
            "project_id": project_id,
            "scope_statement": {"phase_1": {"name": "Discovery"}},
        }
    )
    assert wbs["wbs_id"]
    assert isinstance(wbs["structure"], dict)
    assert any(topic == "charter.created" for topic, _ in event_bus.events)
    assert any(topic == "wbs.created" for topic, _ in event_bus.events)


@pytest.mark.asyncio
async def test_project_definition_scope_baseline_snapshot(tmp_path) -> None:
    event_bus = EventCollector()
    agent = ProjectDefinitionAgent(
        config={
            "event_bus": event_bus,
            "charter_store_path": tmp_path / "charters.json",
            "wbs_store_path": tmp_path / "wbs.json",
        }
    )
    await agent.initialize()

    charter = await agent.process(
        {
            "action": "generate_charter",
            "tenant_id": "tenant-a",
            "charter_data": {
                "title": "Project Nova",
                "description": "Improve onboarding",
                "project_type": "delivery",
                "methodology": "agile",
            },
        }
    )
    project_id = charter["project_id"]

    await agent.process(
        {
            "action": "generate_wbs",
            "tenant_id": "tenant-a",
            "project_id": project_id,
            "scope_statement": {"phase_1": {"name": "Design"}},
        }
    )
    await agent.process(
        {
            "action": "manage_requirements",
            "project_id": project_id,
            "requirements": [{"text": "System shall support SSO."}],
        }
    )

    baseline = await agent.process({"action": "manage_scope_baseline", "project_id": project_id})

    assert project_id in baseline["baseline_id"]
    assert baseline["status"] == "Locked"
    assert any(topic == "scope.baseline.locked" for topic, _ in event_bus.events)
