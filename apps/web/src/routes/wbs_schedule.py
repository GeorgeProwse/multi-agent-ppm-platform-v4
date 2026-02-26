"""WBS, schedule, dependency-map, and program-roadmap routes."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from routes._deps import (
    _demo_mode_enabled,
    _load_demo_dashboard_payload,
    _require_session,
)
from routes._models import (
    DependencyLink,
    DependencyMapResponse,
    DependencyNode,
    ProgramRoadmapResponse,
    RoadmapMilestone,
    RoadmapPhase,
    ScheduleResponse,
    ScheduleTask,
    WbsItem,
    WbsResponse,
    WbsUpdateRequest,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Demo data helpers
# ---------------------------------------------------------------------------

_demo_wbs_cache: dict[str, list[WbsItem]] = {}
_demo_schedule_cache: dict[str, list[ScheduleTask]] = {}


def _get_demo_wbs(project_id: str) -> list[WbsItem]:
    if project_id in _demo_wbs_cache:
        return _demo_wbs_cache[project_id]
    items = [
        WbsItem(id="wbs-1", title="Project Charter", parent_id=None, order=0, owner="PM", status="complete"),
        WbsItem(id="wbs-2", title="Requirements", parent_id=None, order=1, owner="Analyst", status="in_progress"),
        WbsItem(id="wbs-2.1", title="Stakeholder Interviews", parent_id="wbs-2", order=0, owner="Analyst", status="complete"),
        WbsItem(id="wbs-2.2", title="Requirements Document", parent_id="wbs-2", order=1, owner="Analyst", status="in_progress"),
        WbsItem(id="wbs-3", title="Design", parent_id=None, order=2, owner="Architect", status="not_started"),
    ]
    _demo_wbs_cache[project_id] = items
    return items


def _get_demo_schedule(project_id: str) -> list[ScheduleTask]:
    if project_id in _demo_schedule_cache:
        return _demo_schedule_cache[project_id]
    tasks = [
        ScheduleTask(id="task-1", name="Kickoff", start="2025-01-06", end="2025-01-10", progress=100, owner="PM", status="complete"),
        ScheduleTask(id="task-2", name="Discovery", start="2025-01-13", end="2025-02-07", progress=75, dependencies=["task-1"], owner="Analyst", status="in_progress"),
        ScheduleTask(id="task-3", name="Architecture Review", start="2025-02-10", end="2025-02-21", progress=0, dependencies=["task-2"], owner="Architect", status="not_started"),
    ]
    _demo_schedule_cache[project_id] = tasks
    return tasks


def _mock_dependency_map(program_id: str) -> DependencyMapResponse:
    return DependencyMapResponse(
        program_id=program_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        nodes=[
            DependencyNode(id="proj-alpha", label="Project Alpha", type="project", status="in_progress"),
            DependencyNode(id="proj-beta", label="Project Beta", type="project", status="planned"),
            DependencyNode(id="milestone-q2", label="Q2 Gate", type="milestone", status="planned"),
        ],
        links=[
            DependencyLink(source="proj-alpha", target="milestone-q2", kind="hard", critical=True),
            DependencyLink(source="proj-beta", target="milestone-q2", kind="soft"),
        ],
    )


def _mock_program_roadmap(program_id: str) -> ProgramRoadmapResponse:
    return ProgramRoadmapResponse(
        program_id=program_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        phases=[
            RoadmapPhase(id="phase-init", name="Initiation", start="2025-01-01", end="2025-03-31", status="complete", progress=100, owner="PMO"),
            RoadmapPhase(id="phase-plan", name="Planning", start="2025-04-01", end="2025-06-30", status="in_progress", progress=40, owner="PMO"),
        ],
        milestones=[
            RoadmapMilestone(id="ms-kickoff", name="Kickoff", date="2025-01-15", phase_id="phase-init", status="complete"),
            RoadmapMilestone(id="ms-design-review", name="Design Review", date="2025-05-01", phase_id="phase-plan", status="planned"),
        ],
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/api/wbs/{project_id}", response_model=WbsResponse)
async def get_wbs(project_id: str, request: Request) -> WbsResponse:
    _require_session(request)
    items = _get_demo_wbs(project_id)
    return WbsResponse(project_id=project_id, updated_at=datetime.now(timezone.utc).isoformat(), items=items)


@router.patch("/api/wbs/{project_id}", response_model=WbsItem)
async def update_wbs_item(project_id: str, payload: WbsUpdateRequest, request: Request) -> WbsItem:
    _require_session(request)
    if not _demo_mode_enabled():
        raise HTTPException(status_code=403, detail="WBS updates are available in demo mode.")
    items = _get_demo_wbs(project_id)
    updated_item = None
    for item in items:
        if item.id == payload.item_id:
            item.parent_id = payload.parent_id
            item.order = payload.order
            updated_item = item
            break
    if updated_item is None:
        raise HTTPException(status_code=404, detail="WBS item not found.")
    return updated_item


@router.get("/api/schedule/{project_id}", response_model=ScheduleResponse)
async def get_schedule(project_id: str, request: Request) -> ScheduleResponse:
    _require_session(request)
    tasks = _get_demo_schedule(project_id)
    return ScheduleResponse(project_id=project_id, updated_at=datetime.now(timezone.utc).isoformat(), tasks=tasks)


@router.get("/api/dependency-map/{program_id}", response_model=DependencyMapResponse)
async def get_dependency_map(program_id: str, request: Request) -> DependencyMapResponse:
    _require_session(request)
    if _demo_mode_enabled():
        payload = _load_demo_dashboard_payload(f"dependency-map-{program_id}.json") or _load_demo_dashboard_payload("dependency-map.json")
        if payload:
            return DependencyMapResponse(**payload)
    return _mock_dependency_map(program_id)


@router.get("/api/program-roadmap/{program_id}", response_model=ProgramRoadmapResponse)
async def get_program_roadmap(program_id: str, request: Request) -> ProgramRoadmapResponse:
    _require_session(request)
    if _demo_mode_enabled():
        payload = _load_demo_dashboard_payload(f"program-roadmap-{program_id}.json") or _load_demo_dashboard_payload("program-roadmap.json")
        if payload:
            return ProgramRoadmapResponse(**payload)
    return _mock_program_roadmap(program_id)
