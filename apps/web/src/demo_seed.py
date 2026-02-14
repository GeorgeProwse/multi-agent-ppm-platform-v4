from __future__ import annotations

from pathlib import Path
from typing import Any

from knowledge_store import KnowledgeStore
from methodologies import get_methodology_map
from spreadsheet_models import ColumnCreate, RowCreate, SheetCreate
from spreadsheet_store import SpreadsheetStore
from timeline_models import MilestoneCreate
from timeline_store import TimelineStore
from tree_models import NodeType, TreeNodeCreate, TreeNodeRef
from tree_store import TreeStore
from workspace_state_store import WorkspaceStateStore

DEMO_TENANT_ID = "demo-tenant"
DEMO_PROJECTS: dict[str, str] = {
    "demo-predictive": "predictive",
    "demo-adaptive": "adaptive",
    "demo-hybrid": "hybrid",
}


def _seed_workspace_state(workspace_state_store: WorkspaceStateStore, project_id: str, methodology: str) -> None:
    methodology_map = get_methodology_map(methodology)
    stages = methodology_map.get("stages", [])
    first_stage = stages[0] if stages else {}
    first_activity = (first_stage.get("activities") or [{}])[0]

    completion: dict[str, bool] = {}
    all_activities: list[dict[str, Any]] = []
    for stage in stages:
        all_activities.extend(stage.get("activities", []))
    all_activities.extend(methodology_map.get("monitoring", []))

    for index, activity in enumerate(all_activities):
        activity_id = activity.get("id")
        if not activity_id:
            continue
        completion[activity_id] = index % 3 == 0

    workspace_state_store.update_selection(
        DEMO_TENANT_ID,
        project_id,
        {
            "methodology": methodology,
            "current_stage_id": first_stage.get("id"),
            "current_activity_id": first_activity.get("id"),
            "activity_completion": completion,
            "current_canvas_tab": "document",
        },
    )


def _seed_sheet(spreadsheet_store: SpreadsheetStore, project_id: str) -> str:
    existing = spreadsheet_store.list_sheets(DEMO_TENANT_ID, project_id)
    if existing:
        return existing[0].sheet_id

    sheet = spreadsheet_store.create_sheet(
        DEMO_TENANT_ID,
        project_id,
        SheetCreate(
            name="RAID Register",
            columns=[
                ColumnCreate(name="Type", type="text", required=True),
                ColumnCreate(name="Title", type="text", required=True),
                ColumnCreate(name="Owner", type="text", required=True),
                ColumnCreate(name="Status", type="text", required=True),
            ],
        ),
    )
    column_ids = {column.name: column.column_id for column in sheet.columns}
    spreadsheet_store.add_row(
        DEMO_TENANT_ID,
        project_id,
        sheet.sheet_id,
        RowCreate(
            values={
                column_ids["Type"]: "Risk",
                column_ids["Title"]: "Vendor delivery dependency",
                column_ids["Owner"]: "PMO",
                column_ids["Status"]: "Mitigating",
            }
        ),
    )
    return sheet.sheet_id


def _seed_timeline(timeline_store: TimelineStore, project_id: str) -> str:
    milestones = timeline_store.list_milestones(DEMO_TENANT_ID, project_id)
    if milestones:
        return milestones[0].milestone_id
    milestone = timeline_store.create_milestone(
        DEMO_TENANT_ID,
        project_id,
        MilestoneCreate(title="Gate Review", date="2026-03-15", status="planned", owner="PMO"),
    )
    return milestone.milestone_id


def _seed_tree_artifacts(tree_store: TreeStore, project_id: str, sheet_id: str, milestone_id: str) -> None:
    nodes = tree_store.list_nodes(DEMO_TENANT_ID, project_id)
    if nodes:
        return
    root = tree_store.create_node(
        DEMO_TENANT_ID,
        project_id,
        TreeNodeCreate(type=NodeType.folder, title="Seeded Artifacts", parent_id=None),
    )
    tree_store.create_node(
        DEMO_TENANT_ID,
        project_id,
        TreeNodeCreate(
            type=NodeType.document,
            parent_id=root.node_id,
            title="Business Case",
            ref=TreeNodeRef(document_id=f"{project_id}-business-case"),
        ),
    )
    tree_store.create_node(
        DEMO_TENANT_ID,
        project_id,
        TreeNodeCreate(
            type=NodeType.sheet,
            parent_id=root.node_id,
            title="RAID Register",
            ref=TreeNodeRef(sheet_id=sheet_id),
        ),
    )
    tree_store.create_node(
        DEMO_TENANT_ID,
        project_id,
        TreeNodeCreate(
            type=NodeType.milestone,
            parent_id=root.node_id,
            title="Milestones",
            ref=TreeNodeRef(milestone_id=milestone_id),
        ),
    )


def _seed_knowledge(knowledge_store: KnowledgeStore, project_id: str, methodology: str) -> None:
    lessons = knowledge_store.list_lessons(project_id=project_id)
    if lessons:
        return
    knowledge_store.create_lesson(
        project_id=project_id,
        stage_id=f"{methodology}-monitoring",
        stage_name="Monitoring & Controlling",
        title=f"{methodology.title()} delivery checkpoint",
        description="Weekly control-tower review captured from seeded demo scenario.",
        tags=["demo", methodology],
        topics=["monitoring", "governance"],
    )


def seed_demo_data(
    *,
    workspace_state_store: WorkspaceStateStore,
    spreadsheet_store: SpreadsheetStore,
    timeline_store: TimelineStore,
    tree_store: TreeStore,
    knowledge_db_path: Path,
) -> None:
    knowledge_store = KnowledgeStore(knowledge_db_path)
    for project_id, methodology in DEMO_PROJECTS.items():
        _seed_workspace_state(workspace_state_store, project_id, methodology)
        sheet_id = _seed_sheet(spreadsheet_store, project_id)
        milestone_id = _seed_timeline(timeline_store, project_id)
        _seed_tree_artifacts(tree_store, project_id, sheet_id, milestone_id)
        _seed_knowledge(knowledge_store, project_id, methodology)
