import pytest
from resource_capacity_agent import ResourceCapacityAgent
from datetime import datetime, timedelta


class EventCollector:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    async def publish(self, topic: str, payload: dict) -> None:
        self.events.append((topic, payload))


def build_agent_config(tmp_path, **overrides):
    return {
        "event_bus": EventCollector(),
        "resource_store_path": tmp_path / "resources.json",
        "allocation_store_path": tmp_path / "allocations.json",
        **overrides,
    }


@pytest.mark.asyncio
async def test_resource_allocation_persistence_and_events(tmp_path):
    event_bus = EventCollector()
    agent = ResourceCapacityAgent(config=build_agent_config(tmp_path, event_bus=event_bus))
    await agent.initialize()

    add_response = await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-a",
            "resource": {
                "resource_id": "res-1",
                "name": "Avery",
                "role": "Engineer",
                "skills": ["python"],
                "location": "Remote",
            },
        }
    )
    assert add_response["data_quality"]["is_valid"] is True

    allocation_response = await agent.process(
        {
            "action": "allocate_resource",
            "tenant_id": "tenant-a",
            "correlation_id": "corr-1",
            "allocation": {
                "resource_id": "res-1",
                "project_id": "proj-1",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "allocation_percentage": 50,
            },
        }
    )

    assert allocation_response["allocation_id"]
    assert any(topic == "resource.allocation.created" for topic, _ in event_bus.events)


@pytest.mark.asyncio
async def test_resource_capacity_resource_pool(tmp_path):
    agent = ResourceCapacityAgent(config=build_agent_config(tmp_path))
    await agent.initialize()

    response = await agent.process({"action": "get_resource_pool", "tenant_id": "tenant-a"})

    assert "resources" in response


@pytest.mark.asyncio
async def test_resource_capacity_validation_rejects_invalid_action(tmp_path):
    agent = ResourceCapacityAgent(config=build_agent_config(tmp_path))
    await agent.initialize()

    valid = await agent.validate_input({"action": "invalid"})

    assert valid is False


@pytest.mark.asyncio
async def test_resource_capacity_validation_rejects_missing_fields(tmp_path):
    agent = ResourceCapacityAgent(config=build_agent_config(tmp_path))
    await agent.initialize()

    valid = await agent.validate_input(
        {"action": "add_resource", "resource": {"resource_id": "res-1"}}
    )

    assert valid is False


@pytest.mark.asyncio
async def test_resource_capacity_skill_matching(tmp_path):
    agent = ResourceCapacityAgent(
        config=build_agent_config(tmp_path, skill_matching_threshold=0.0)
    )
    await agent.initialize()

    await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-a",
            "resource": {
                "resource_id": "res-1",
                "name": "Avery",
                "role": "Engineer",
                "skills": ["python", "ml"],
                "location": "Remote",
            },
        }
    )
    await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-a",
            "resource": {
                "resource_id": "res-2",
                "name": "Jordan",
                "role": "Engineer",
                "skills": ["java"],
                "location": "Remote",
            },
        }
    )

    response = await agent.process(
        {"action": "match_skills", "skills_required": ["python"], "project_context": {}}
    )

    assert response["candidates"][0]["resource_id"] == "res-1"


@pytest.mark.asyncio
async def test_resource_capacity_forecasting(tmp_path):
    agent = ResourceCapacityAgent(
        config=build_agent_config(tmp_path, forecast_horizon_months=3)
    )
    await agent.initialize()

    await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-a",
            "resource": {
                "resource_id": "res-forecast",
                "name": "Taylor",
                "role": "Analyst",
                "skills": ["planning"],
                "location": "Remote",
            },
        }
    )

    now = datetime.utcnow()
    agent.allocations["res-forecast"] = [
        {
            "allocation_id": "alloc-1",
            "resource_id": "res-forecast",
            "project_id": "proj-1",
            "start_date": (now - timedelta(days=45)).date().isoformat(),
            "end_date": (now - timedelta(days=15)).date().isoformat(),
            "allocation_percentage": 50,
            "status": "Active",
        }
    ]

    forecast = await agent.process({"action": "forecast_capacity", "filters": {"history_months": 3}})

    assert len(forecast["future_capacity"]) == 3
    assert len(forecast["future_demand"]) == 3


@pytest.mark.asyncio
async def test_resource_capacity_conflict_detection(tmp_path):
    agent = ResourceCapacityAgent(config=build_agent_config(tmp_path))
    await agent.initialize()

    await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-a",
            "resource": {
                "resource_id": "res-conflict",
                "name": "Alex",
                "role": "Engineer",
                "skills": ["python"],
                "location": "Remote",
            },
        }
    )

    agent.allocations["res-conflict"] = [
        {
            "allocation_id": "alloc-a",
            "resource_id": "res-conflict",
            "project_id": "proj-1",
            "start_date": "2024-01-01",
            "end_date": "2024-02-01",
            "allocation_percentage": 60,
            "status": "Active",
        },
        {
            "allocation_id": "alloc-b",
            "resource_id": "res-conflict",
            "project_id": "proj-2",
            "start_date": "2024-01-15",
            "end_date": "2024-02-15",
            "allocation_percentage": 60,
            "status": "Active",
        },
    ]

    conflicts = await agent.process({"action": "identify_conflicts", "filters": {}})

    assert conflicts["total_conflicts"] == 1


@pytest.mark.asyncio
async def test_resource_capacity_enforces_allocation_constraints(tmp_path):
    agent = ResourceCapacityAgent(
        config=build_agent_config(
            tmp_path,
            max_concurrent_allocations=1,
            enforce_allocation_constraints=True,
        )
    )
    await agent.initialize()

    await agent.process(
        {
            "action": "add_resource",
            "tenant_id": "tenant-a",
            "resource": {
                "resource_id": "res-constraint",
                "name": "Jamie",
                "role": "Engineer",
                "skills": ["python"],
                "location": "Remote",
            },
        }
    )

    agent.allocations["res-constraint"] = [
        {
            "allocation_id": "alloc-1",
            "resource_id": "res-constraint",
            "project_id": "proj-1",
            "start_date": "2024-01-01",
            "end_date": "2024-02-01",
            "allocation_percentage": 50,
            "status": "Active",
        }
    ]

    with pytest.raises(ValueError, match="Allocation exceeds maximum concurrent allocation"):
        await agent.process(
            {
                "action": "allocate_resource",
                "tenant_id": "tenant-a",
                "allocation": {
                    "resource_id": "res-constraint",
                    "project_id": "proj-2",
                    "start_date": "2024-01-15",
                    "end_date": "2024-02-15",
                    "allocation_percentage": 25,
                },
            }
        )
