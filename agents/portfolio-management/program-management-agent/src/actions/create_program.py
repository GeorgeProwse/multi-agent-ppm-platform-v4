"""Action handlers for creating and retrieving programs."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from events import ProgramCreatedEvent
from observability.tracing import get_trace_id

if TYPE_CHECKING:
    from program_management_agent import ProgramManagementAgent


async def handle_create_program(
    agent: ProgramManagementAgent,
    program_data: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """
    Create a new program structure.

    Returns program ID and initial structure.
    """
    agent.logger.info("Creating new program")

    # Generate unique program ID
    program_id = f"PROG-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    # Extract program details
    name = program_data.get("name")
    description = program_data.get("description")
    strategic_objectives = program_data.get("strategic_objectives", [])
    constituent_projects = program_data.get("constituent_projects", [])
    methodology = program_data.get("methodology", "hybrid")

    # Create program structure
    program = {
        "program_id": program_id,
        "name": name,
        "description": description,
        "strategic_objectives": strategic_objectives,
        "constituent_projects": constituent_projects,
        "methodology": methodology,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": program_data.get("created_by", "unknown"),
        "status": "Planning",
        "portfolio_id": program_data.get("portfolio_id", "unknown"),
        "metadata": {
            "project_count": len(constituent_projects),
            "dependencies_identified": 0,
            "synergies_found": 0,
        },
    }

    agent.program_store.upsert(tenant_id, program_id, program)
    if agent.db_service:
        await agent.db_service.store("programs", program_id, program)
    await _sync_work_management_mappings(agent, program_id, program)

    agent.logger.info("Created program: %s", program_id)

    await _publish_program_created(
        agent,
        program,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
    )

    return {
        "program_id": program_id,
        "name": name,
        "status": "Planning",
        "constituent_projects": constituent_projects,
        "next_steps": "Generate roadmap and identify dependencies",
    }


async def handle_get_program(
    agent: ProgramManagementAgent,
    program_id: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """Retrieve a program by ID."""
    program = agent.program_store.get(tenant_id, program_id)
    if not program:
        raise ValueError(f"Program not found: {program_id}")
    return program  # type: ignore


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _publish_program_created(
    agent: ProgramManagementAgent,
    program: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> None:
    event = ProgramCreatedEvent(
        event_name="program.created",
        event_id=f"evt-{uuid.uuid4().hex}",
        timestamp=datetime.now(timezone.utc),
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        trace_id=get_trace_id(),
        payload={
            "program_id": program.get("program_id", ""),
            "name": program.get("name", ""),
            "portfolio_id": program.get("portfolio_id", "unknown"),
            "created_at": datetime.fromisoformat(program.get("created_at")),
            "owner": program.get("created_by", "unknown"),
        },
    )
    await agent.event_bus.publish("program.created", event.model_dump())


async def _sync_work_management_mappings(
    agent: ProgramManagementAgent,
    program_id: str,
    program: dict[str, Any],
) -> None:
    mappings: list[dict[str, Any]] = []
    if agent.jira_base_url and agent.jira_api_token:
        mappings.extend(await _fetch_jira_mappings(agent, program_id, program))
    if agent.azure_devops_org_url and agent.azure_devops_pat:
        mappings.extend(await _fetch_azure_devops_mappings(agent, program_id, program))
    if not mappings:
        return
    if agent.mapping_container:
        for mapping in mappings:
            await agent.mapping_container.upsert_item(mapping)


async def _fetch_jira_mappings(
    agent: ProgramManagementAgent,
    program_id: str,
    program: dict[str, Any],
) -> list[dict[str, Any]]:
    import httpx

    headers = {"Authorization": f"Bearer {agent.jira_api_token}"}
    url = f"{agent.jira_base_url}/rest/api/3/project/search"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json().get("values", [])
    mappings = []
    for project in projects:
        mappings.append(
            {
                "id": f"jira:{project.get('id')}",
                "system": "jira",
                "program_id": program_id,
                "project_id": project.get("id"),
                "project_key": project.get("key"),
                "project_name": project.get("name"),
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return mappings


async def _fetch_azure_devops_mappings(
    agent: ProgramManagementAgent,
    program_id: str,
    program: dict[str, Any],
) -> list[dict[str, Any]]:
    import base64

    import httpx

    token = base64.b64encode(f":{agent.azure_devops_pat}".encode()).decode("utf-8")
    headers = {"Authorization": f"Basic {token}"}
    url = f"{agent.azure_devops_org_url}/_apis/projects?api-version=7.0"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json().get("value", [])
    mappings = []
    for project in projects:
        mappings.append(
            {
                "id": f"azure-devops:{project.get('id')}",
                "system": "azure_devops",
                "program_id": program_id,
                "project_id": project.get("id"),
                "project_name": project.get("name"),
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return mappings
