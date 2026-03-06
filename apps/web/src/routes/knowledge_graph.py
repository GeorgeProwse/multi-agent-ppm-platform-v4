"""Knowledge graph and AI recommendations API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(tags=["knowledge-graph"])


class GraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # lesson, risk, decision, project, entity
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    edge_type: str  # relates_to, caused_by, mitigated_by, learned_from


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class Pattern(BaseModel):
    pattern_id: str
    title: str
    description: str
    occurrences: int
    affected_projects: list[str]
    severity: str  # low, medium, high


class Recommendation(BaseModel):
    recommendation_id: str
    title: str
    description: str
    priority: str  # critical, important, informational
    source_lesson_id: str
    source_lesson_title: str
    actionable_text: str


class RecommendationRequest(BaseModel):
    project_id: str
    context_type: str = "general"
    context_id: str = ""


_DEMO_NODES = [
    GraphNode(id="lesson-001", label="Vendor SLA must be enforced weekly", node_type="lesson", metadata={"project": "proj-alpha", "date": "2025-06-15"}),
    GraphNode(id="lesson-002", label="Early stakeholder engagement reduces scope creep", node_type="lesson", metadata={"project": "proj-beta", "date": "2025-09-01"}),
    GraphNode(id="lesson-003", label="Automated testing saves 30% QA effort", node_type="lesson", metadata={"project": "proj-gamma", "date": "2025-11-20"}),
    GraphNode(id="risk-001", label="Vendor delivery delay", node_type="risk", metadata={"severity": "high", "status": "active"}),
    GraphNode(id="risk-002", label="Resource shortage", node_type="risk", metadata={"severity": "medium", "status": "mitigated"}),
    GraphNode(id="risk-003", label="Scope creep", node_type="risk", metadata={"severity": "high", "status": "active"}),
    GraphNode(id="decision-001", label="Adopted microservices architecture", node_type="decision", metadata={"date": "2025-03-01"}),
    GraphNode(id="decision-002", label="Selected Azure over AWS", node_type="decision", metadata={"date": "2025-04-15"}),
    GraphNode(id="proj-alpha", label="Project Alpha", node_type="project", metadata={"status": "active"}),
    GraphNode(id="proj-beta", label="Project Beta", node_type="project", metadata={"status": "active"}),
    GraphNode(id="proj-gamma", label="Project Gamma", node_type="project", metadata={"status": "completed"}),
]

_DEMO_EDGES = [
    GraphEdge(source="lesson-001", target="risk-001", edge_type="mitigated_by"),
    GraphEdge(source="lesson-002", target="risk-003", edge_type="mitigated_by"),
    GraphEdge(source="lesson-001", target="proj-alpha", edge_type="learned_from"),
    GraphEdge(source="lesson-002", target="proj-beta", edge_type="learned_from"),
    GraphEdge(source="lesson-003", target="proj-gamma", edge_type="learned_from"),
    GraphEdge(source="risk-001", target="proj-alpha", edge_type="relates_to"),
    GraphEdge(source="risk-002", target="proj-beta", edge_type="relates_to"),
    GraphEdge(source="risk-003", target="proj-beta", edge_type="relates_to"),
    GraphEdge(source="decision-001", target="proj-alpha", edge_type="relates_to"),
    GraphEdge(source="decision-002", target="proj-alpha", edge_type="relates_to"),
    GraphEdge(source="decision-001", target="lesson-003", edge_type="caused_by"),
]

_DEMO_PATTERNS = [
    Pattern(
        pattern_id="pat-001",
        title="Vendor Delays Correlate with Missing SLA Enforcement",
        description="3 projects experienced vendor delivery delays when weekly SLA reviews were not conducted.",
        occurrences=3,
        affected_projects=["proj-alpha", "proj-delta", "proj-epsilon"],
        severity="high",
    ),
    Pattern(
        pattern_id="pat-002",
        title="Scope Creep in Projects Without Early Stakeholder Engagement",
        description="Projects that skipped inception stakeholder workshops had 40% higher scope change rates.",
        occurrences=4,
        affected_projects=["proj-beta", "proj-delta", "proj-zeta", "proj-eta"],
        severity="medium",
    ),
]

_DEMO_RECOMMENDATIONS = [
    Recommendation(
        recommendation_id="rec-001",
        title="Implement Weekly Vendor SLA Reviews",
        description="Based on past lessons, projects with external vendors should conduct weekly SLA compliance reviews.",
        priority="critical",
        source_lesson_id="lesson-001",
        source_lesson_title="Vendor SLA must be enforced weekly",
        actionable_text="Add a recurring 'Vendor SLA Review' task to Sprint ceremonies. Assign to procurement lead.",
    ),
    Recommendation(
        recommendation_id="rec-002",
        title="Conduct Stakeholder Alignment Workshop",
        description="Historical data shows that early stakeholder engagement reduces scope creep by 40%.",
        priority="important",
        source_lesson_id="lesson-002",
        source_lesson_title="Early stakeholder engagement reduces scope creep",
        actionable_text="Schedule a 2-hour stakeholder alignment workshop within the first 2 weeks of the project.",
    ),
    Recommendation(
        recommendation_id="rec-003",
        title="Invest in Test Automation",
        description="Similar projects achieved 30% QA efficiency gains through automated testing.",
        priority="informational",
        source_lesson_id="lesson-003",
        source_lesson_title="Automated testing saves 30% QA effort",
        actionable_text="Allocate 15% of sprint capacity to building automated test coverage in the first 3 sprints.",
    ),
]


@router.get("/api/knowledge/graph")
async def get_knowledge_graph(
    scope: str = Query(default="portfolio"),
    id: str = Query(default="default"),
) -> GraphData:
    return GraphData(nodes=_DEMO_NODES, edges=_DEMO_EDGES)


@router.get("/api/knowledge/patterns")
async def get_patterns(
    scope: str = Query(default="portfolio"),
    id: str = Query(default="default"),
) -> list[Pattern]:
    return _DEMO_PATTERNS


@router.post("/api/knowledge/recommendations")
async def get_recommendations(request: RecommendationRequest) -> list[Recommendation]:
    return _DEMO_RECOMMENDATIONS


@router.get("/api/knowledge/stats")
async def get_graph_stats() -> dict[str, Any]:
    node_types: dict[str, int] = {}
    for node in _DEMO_NODES:
        node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
    return {
        "total_nodes": len(_DEMO_NODES),
        "total_edges": len(_DEMO_EDGES),
        "node_types": node_types,
        "density": round(len(_DEMO_EDGES) / max(len(_DEMO_NODES) * (len(_DEMO_NODES) - 1) / 2, 1), 3),
    }
