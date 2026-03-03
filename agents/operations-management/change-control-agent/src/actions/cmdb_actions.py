"""Action handlers for CMDB operations: register CI, create baseline, track implementation."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from change_configuration_agent import ChangeConfigurationAgent


async def register_ci(
    agent: ChangeConfigurationAgent,
    ci_data: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """Register configuration item in CMDB."""
    agent.logger.info("Registering CI: %s", ci_data.get("name"))

    # Generate CI ID
    ci_id = await generate_ci_id()

    # Create CI entry
    ci = {
        "ci_id": ci_id,
        "name": ci_data.get("name"),
        "type": ci_data.get("type"),  # hardware, software, document, requirement
        "version": ci_data.get("version", "1.0"),
        "owner": ci_data.get("owner"),
        "status": ci_data.get("status", "active"),
        "project_id": ci_data.get("project_id"),
        "relationships": ci_data.get("relationships", []),
        "attributes": ci_data.get("attributes", {}),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_modified": datetime.now(timezone.utc).isoformat(),
    }

    # Store CI
    agent.cmdb[ci_id] = ci
    agent.cmdb_store.upsert(tenant_id, ci_id, ci)

    await agent.db_service.store("configuration_items", ci_id, ci)
    if agent.dependency_graph:
        agent.dependency_graph.load_cmdb(agent.cmdb)

    return {"ci_id": ci_id, "name": ci["name"], "type": ci["type"], "version": ci["version"]}


async def create_baseline(
    agent: ChangeConfigurationAgent, baseline_data: dict[str, Any]
) -> dict[str, Any]:
    """Create configuration baseline."""
    agent.logger.info("Creating baseline: %s", baseline_data.get("description"))

    # Generate baseline ID
    baseline_id = await generate_baseline_id()

    # Snapshot current CI versions
    ci_ids = baseline_data.get("ci_ids", [])
    ci_snapshot = {}
    for ci_id in ci_ids:
        ci = agent.cmdb.get(ci_id)
        if ci:
            ci_snapshot[ci_id] = {
                "name": ci.get("name"),
                "version": ci.get("version"),
                "attributes": ci.get("attributes", {}).copy(),
            }

    # Create baseline
    baseline = {
        "baseline_id": baseline_id,
        "project_id": baseline_data.get("project_id"),
        "description": baseline_data.get("description"),
        "ci_snapshot": ci_snapshot,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": baseline_data.get("created_by", "unknown"),
        "locked": True,
    }

    # Store baseline
    agent.baselines[baseline_id] = baseline

    await agent.db_service.store("baselines", baseline_id, baseline)

    return {
        "baseline_id": baseline_id,
        "description": baseline["description"],
        "ci_count": len(ci_snapshot),
        "created_at": baseline["created_at"],
    }


async def track_change_implementation(
    agent: ChangeConfigurationAgent, change_id: str
) -> dict[str, Any]:
    """Track change implementation progress."""
    agent.logger.info("Tracking implementation for change: %s", change_id)

    change = agent.change_requests.get(change_id)
    if not change:
        raise ValueError(f"Change request not found: {change_id}")

    # Get implementation tasks
    implementation_tasks = await get_implementation_tasks(agent, change_id)

    # Calculate completion percentage
    total_tasks = len(implementation_tasks)
    completed_tasks = sum(1 for t in implementation_tasks if t.get("status") == "completed")
    completion_pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Update change status
    if completion_pct == 100:
        change["status"] = "Implemented"
        change["implemented_at"] = datetime.now(timezone.utc).isoformat()

    return {
        "change_id": change_id,
        "status": change["status"],
        "completion_percentage": completion_pct,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "implementation_tasks": implementation_tasks,
    }


async def query_impacted_cis(
    agent: ChangeConfigurationAgent, ci_ids: Iterable[str]
) -> dict[str, Any]:
    if not agent.dependency_graph:
        return {"status": "unavailable", "impacted_cis": []}
    impacted = agent.dependency_graph.get_impacted(ci_ids)
    return {"status": "ok", "impacted_cis": impacted, "count": len(impacted)}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def generate_ci_id() -> str:
    """Generate unique CI ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"CI-{timestamp}"


async def generate_baseline_id() -> str:
    """Generate unique baseline ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"BL-{timestamp}"


async def get_implementation_tasks(
    agent: ChangeConfigurationAgent, change_id: str
) -> list[dict[str, Any]]:
    """Get implementation tasks for change."""
    if agent.task_management_client:
        return await agent.task_management_client.list_tasks(change_id)
    return []
