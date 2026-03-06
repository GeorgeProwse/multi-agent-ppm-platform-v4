"""Methodology-aware project setup wizard API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(tags=["project-setup"])


class ProjectCharacteristics(BaseModel):
    industry: str = "technology"
    team_size: int = 10
    duration_months: int = 6
    risk_level: str = "medium"  # low, medium, high
    regulatory: list[str] = Field(default_factory=list)  # SOX, GDPR, HIPAA, GxP


class MethodologyRecommendation(BaseModel):
    methodology: str  # predictive, adaptive, hybrid
    match_score: float
    rationale: str
    strengths: list[str]


class ProjectTemplate(BaseModel):
    template_id: str
    name: str
    methodology: str
    industry: str
    description: str
    stages: list[dict[str, Any]]
    activity_count: int


class WorkspaceConfig(BaseModel):
    project_id: str
    project_name: str
    methodology: str
    template_id: str
    stages: list[dict[str, Any]]


_TEMPLATES = [
    ProjectTemplate(
        template_id="tmpl-agile-tech",
        name="Agile Software Delivery",
        methodology="adaptive",
        industry="technology",
        description="Iterative software delivery with 2-week sprints, continuous integration, and DevOps practices.",
        stages=[
            {"id": "inception", "name": "Inception", "activities": ["Vision & Scope", "Team Formation", "Backlog Seeding"]},
            {"id": "iteration", "name": "Iteration", "activities": ["Sprint Planning", "Daily Standup", "Sprint Review", "Retrospective"]},
            {"id": "release", "name": "Release", "activities": ["Release Planning", "UAT", "Deployment", "Hypercare"]},
        ],
        activity_count=10,
    ),
    ProjectTemplate(
        template_id="tmpl-waterfall-construct",
        name="Waterfall Construction",
        methodology="predictive",
        industry="construction",
        description="Sequential delivery with formal gates, detailed planning, and regulatory compliance.",
        stages=[
            {"id": "initiate", "name": "Initiate", "activities": ["Project Charter", "Stakeholder Register", "Feasibility Study"]},
            {"id": "plan", "name": "Plan", "activities": ["WBS", "Schedule Baseline", "Cost Baseline", "Risk Register"]},
            {"id": "execute", "name": "Execute", "activities": ["Procurement", "Quality Control", "Status Reporting"]},
            {"id": "close", "name": "Close", "activities": ["Lessons Learned", "Final Deliverable", "Contract Closure"]},
        ],
        activity_count=14,
    ),
    ProjectTemplate(
        template_id="tmpl-hybrid-pharma",
        name="Hybrid Pharma Development",
        methodology="hybrid",
        industry="pharma",
        description="Combines predictive regulatory gates with adaptive research sprints for drug development programs.",
        stages=[
            {"id": "discovery", "name": "Discovery", "activities": ["Research Sprints", "Literature Review", "Hypothesis Validation"]},
            {"id": "preclinical", "name": "Pre-Clinical", "activities": ["Protocol Design", "Lab Testing", "GxP Compliance"]},
            {"id": "clinical", "name": "Clinical Trials", "activities": ["Trial Design", "Patient Enrollment", "Data Collection"]},
            {"id": "submission", "name": "Regulatory Submission", "activities": ["Dossier Preparation", "FDA/EMA Review", "Approval Gate"]},
        ],
        activity_count=12,
    ),
    ProjectTemplate(
        template_id="tmpl-agile-finance",
        name="Agile Financial Systems",
        methodology="adaptive",
        industry="finance",
        description="Agile delivery with SOX compliance gates and automated audit trails.",
        stages=[
            {"id": "inception", "name": "Inception", "activities": ["Compliance Mapping", "Architecture Review", "Backlog"]},
            {"id": "delivery", "name": "Delivery", "activities": ["Sprint Cycles", "SOX Evidence Collection", "Security Review"]},
            {"id": "release", "name": "Release", "activities": ["Audit Gate", "Production Deploy", "Post-Implementation Review"]},
        ],
        activity_count=9,
    ),
]


@router.post("/api/project-setup/recommend-methodology")
async def recommend_methodology(
    characteristics: ProjectCharacteristics,
) -> list[MethodologyRecommendation]:
    recommendations: list[MethodologyRecommendation] = []

    predictive_score = 0.3
    adaptive_score = 0.3
    hybrid_score = 0.4

    if characteristics.risk_level == "high" or characteristics.regulatory:
        predictive_score += 0.3
        hybrid_score += 0.1
    if characteristics.team_size <= 15:
        adaptive_score += 0.2
    if characteristics.duration_months <= 4:
        adaptive_score += 0.15
    if characteristics.duration_months > 12:
        predictive_score += 0.15
    if characteristics.industry in ("pharma", "government"):
        predictive_score += 0.2
        hybrid_score += 0.15
    if characteristics.industry in ("technology", "finance"):
        adaptive_score += 0.2

    total = predictive_score + adaptive_score + hybrid_score
    recommendations = [
        MethodologyRecommendation(
            methodology="predictive",
            match_score=round(predictive_score / total, 2),
            rationale="Structured approach with formal gates, ideal for regulated environments and fixed-scope projects.",
            strengths=["Clear milestones", "Predictable timelines", "Audit-friendly"],
        ),
        MethodologyRecommendation(
            methodology="adaptive",
            match_score=round(adaptive_score / total, 2),
            rationale="Iterative delivery with continuous feedback, ideal for evolving requirements and smaller teams.",
            strengths=["Fast feedback loops", "Flexible scope", "Higher team engagement"],
        ),
        MethodologyRecommendation(
            methodology="hybrid",
            match_score=round(hybrid_score / total, 2),
            rationale="Combines predictive governance with adaptive execution, balancing control with agility.",
            strengths=["Best of both worlds", "Compliance + agility", "Scalable governance"],
        ),
    ]
    recommendations.sort(key=lambda r: r.match_score, reverse=True)
    return recommendations


@router.get("/api/project-setup/templates")
async def list_templates(
    methodology: str = Query(default=""),
    industry: str = Query(default=""),
) -> list[ProjectTemplate]:
    results = _TEMPLATES
    if methodology:
        results = [t for t in results if t.methodology == methodology]
    if industry:
        results = [t for t in results if t.industry == industry]
    return results


@router.post("/api/project-setup/configure-workspace")
async def configure_workspace(
    project_name: str,
    template_id: str,
    customizations: dict[str, Any] = None,
) -> WorkspaceConfig:
    template = next((t for t in _TEMPLATES if t.template_id == template_id), _TEMPLATES[0])
    import uuid

    return WorkspaceConfig(
        project_id=f"proj-{uuid.uuid4().hex[:8]}",
        project_name=project_name,
        methodology=template.methodology,
        template_id=template.template_id,
        stages=template.stages,
    )
