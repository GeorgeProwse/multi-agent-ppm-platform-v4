"""Action handlers for requirement linkage management."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quality_management_agent import QualityManagementAgent


async def link_test_case_requirements(
    agent: "QualityManagementAgent",
    link_data: dict[str, Any],
    *,
    tenant_id: str,
    correlation_id: str,
) -> dict[str, Any]:
    """Create a requirement linkage record for a test case."""
    link_id = f"TRL-{uuid.uuid4().hex[:8]}"
    requirement_ids = list({str(req) for req in link_data.get("requirement_ids", []) if req})
    requirements = await _link_to_requirements(
        agent, requirement_ids, project_id=link_data.get("project_id")
    )
    link_record = {
        "link_id": link_id,
        "project_id": link_data.get("project_id"),
        "test_case_id": link_data.get("test_case_id"),
        "requirements": requirements,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "linked",
    }
    agent.requirement_links[link_id] = link_record
    agent.requirement_link_store.upsert(tenant_id, link_id, link_record)
    await agent._store_record("quality_requirement_links", link_id, link_record)
    await agent._publish_quality_event(
        "quality.requirements.linked",
        payload={
            "link_id": link_id,
            "project_id": link_record.get("project_id"),
            "test_case_id": link_record.get("test_case_id"),
        },
        tenant_id=tenant_id,
        correlation_id=correlation_id,
    )
    return link_record


async def update_test_case_links(
    agent: "QualityManagementAgent",
    link_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """Update a requirement linkage record."""
    link_record = agent.requirement_links.get(link_id)
    if not link_record:
        raise ValueError(f"Requirement link not found: {link_id}")
    if "requirement_ids" in updates:
        requirement_ids = list({str(req) for req in updates.get("requirement_ids", []) if req})
        link_record["requirements"] = await _link_to_requirements(
            agent, requirement_ids, project_id=link_record.get("project_id")
        )
    if "status" in updates:
        link_record["status"] = updates.get("status")
    link_record["updated_at"] = datetime.now(timezone.utc).isoformat()
    agent.requirement_links[link_id] = link_record
    await agent._store_record("quality_requirement_links", link_id, link_record)
    return link_record


async def get_requirement_links(
    agent: "QualityManagementAgent",
    filters: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    """Query requirement linkage records by filters."""
    project_id = filters.get("project_id")
    test_case_id = filters.get("test_case_id")
    requirement_id = filters.get("requirement_id")
    link_records = list(agent.requirement_links.values())
    if not link_records and tenant_id:
        link_records = agent.requirement_link_store.list(tenant_id)
    filtered = []
    for record in link_records:
        if project_id and record.get("project_id") != project_id:
            continue
        if test_case_id and record.get("test_case_id") != test_case_id:
            continue
        if requirement_id:
            requirements = record.get("requirements", [])
            if not any(req.get("requirement_id") == requirement_id for req in requirements):
                continue
        filtered.append(record)
    return {"count": len(filtered), "links": filtered}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _link_to_requirements(
    agent: "QualityManagementAgent",
    requirement_ids: list[str],
    project_id: str | None,
) -> list[dict[str, Any]]:
    if not requirement_ids:
        return []
    requirements = await _fetch_project_requirements(agent, project_id)
    requirement_lookup = {
        str(req.get("requirement_id") or req.get("id")): req for req in requirements
    }
    linked = []
    for req_id in requirement_ids:
        req_record = requirement_lookup.get(str(req_id))
        linked.append(
            {
                "requirement_id": req_id,
                "title": req_record.get("title") if req_record else None,
                "status": "validated" if req_record else "unverified",
            }
        )
    return linked


async def _fetch_project_requirements(
    agent: "QualityManagementAgent", project_id: str | None
) -> list[dict[str, Any]]:
    if not project_id:
        return []
    project_definition_client = (agent.config or {}).get("project_definition_client")
    if project_definition_client and hasattr(project_definition_client, "get_requirements"):
        response = project_definition_client.get_requirements(project_id)
        if hasattr(response, "__await__"):
            response = await response
        requirements = response.get("requirements", []) if isinstance(response, dict) else []
        return requirements
    requirements_config = agent.integration_config.get("project_definition", {}).get(
        "requirements_by_project", {}
    )
    return requirements_config.get(project_id, [])
