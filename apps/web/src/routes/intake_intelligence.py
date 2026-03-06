"""Intelligent demand intake — duplicate detection, auto-classification, business case generation."""

from __future__ import annotations

import hashlib
import math
import time
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["intake-intelligence"])

# Simulated demand corpus for duplicate detection
_EXISTING_DEMANDS = [
    {"id": "DEM-001", "title": "Cloud Migration for Finance Module", "description": "Migrate the on-premise finance module to Azure cloud infrastructure", "status": "approved", "category": "strategic"},
    {"id": "DEM-002", "title": "Mobile App for Field Teams", "description": "Build a mobile application for field service teams to report status", "status": "in_review", "category": "operational"},
    {"id": "DEM-003", "title": "GDPR Data Retention Policy Implementation", "description": "Implement automated data retention and deletion policies for GDPR compliance", "status": "approved", "category": "regulatory"},
    {"id": "DEM-004", "title": "HR System Integration", "description": "Integrate Workday HCM with internal resource management system", "status": "completed", "category": "operational"},
    {"id": "DEM-005", "title": "AI-Powered Risk Assessment", "description": "Build an AI model to automatically assess and score project risks", "status": "approved", "category": "strategic"},
]

CLASSIFICATION_CATEGORIES = ["strategic", "operational", "regulatory", "maintenance", "innovation"]


class DuplicateCheckRequest(BaseModel):
    title: str
    description: str


class DuplicateMatch(BaseModel):
    demand_id: str
    title: str
    description: str
    status: str
    similarity_score: float


class ClassifyRequest(BaseModel):
    description: str


class ClassificationResult(BaseModel):
    category: str
    confidence: float
    all_scores: dict[str, float]


class BusinessCaseRequest(BaseModel):
    title: str
    description: str
    category: str = ""


class BusinessCaseSkeleton(BaseModel):
    problem_statement: str
    proposed_solution: str
    expected_benefits: list[str]
    estimated_cost_range: str
    risk_factors: list[str]
    success_criteria: list[str]


def _simple_similarity(text_a: str, text_b: str) -> float:
    """Jaccard similarity on word sets as a lightweight duplicate detector."""
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


@router.post("/api/intake/check-duplicates")
async def check_duplicates(request: DuplicateCheckRequest) -> list[DuplicateMatch]:
    combined = f"{request.title} {request.description}"
    matches: list[DuplicateMatch] = []
    for demand in _EXISTING_DEMANDS:
        existing_text = f"{demand['title']} {demand['description']}"
        score = _simple_similarity(combined, existing_text)
        if score > 0.15:
            matches.append(
                DuplicateMatch(
                    demand_id=demand["id"],
                    title=demand["title"],
                    description=demand["description"],
                    status=demand["status"],
                    similarity_score=round(score, 3),
                )
            )
    matches.sort(key=lambda m: m.similarity_score, reverse=True)
    return matches[:5]


@router.post("/api/intake/auto-classify")
async def auto_classify(request: ClassifyRequest) -> ClassificationResult:
    """Auto-classify a demand description into categories with confidence."""
    text = request.description.lower()
    scores: dict[str, float] = {}

    keyword_map = {
        "strategic": ["transform", "innovate", "competitive", "market", "growth", "ai", "cloud", "digital", "strategy"],
        "operational": ["process", "efficiency", "integrate", "automate", "workflow", "team", "internal", "mobile"],
        "regulatory": ["compliance", "gdpr", "sox", "audit", "regulation", "privacy", "retention", "security", "hipaa"],
        "maintenance": ["fix", "patch", "upgrade", "maintain", "legacy", "debt", "refactor", "bug"],
        "innovation": ["research", "prototype", "experiment", "pilot", "emerging", "ml", "blockchain"],
    }

    for cat, keywords in keyword_map.items():
        matches = sum(1 for kw in keywords if kw in text)
        scores[cat] = round(matches / max(len(keywords), 1), 3)

    best_cat = max(scores, key=lambda k: scores[k])
    confidence = scores[best_cat]
    if confidence < 0.1:
        best_cat = "operational"
        confidence = 0.3

    return ClassificationResult(
        category=best_cat,
        confidence=round(min(confidence * 3, 0.95), 2),
        all_scores=scores,
    )


@router.post("/api/intake/generate-business-case")
async def generate_business_case(request: BusinessCaseRequest) -> BusinessCaseSkeleton:
    """Generate a business case skeleton from demand description."""
    return BusinessCaseSkeleton(
        problem_statement=f"The organization needs to address: {request.description[:200]}",
        proposed_solution=f"Implement a solution for '{request.title}' leveraging the platform's existing agent infrastructure and connector ecosystem.",
        expected_benefits=[
            "Improved operational efficiency by 15-25%",
            "Reduced manual effort through AI-driven automation",
            "Enhanced visibility and decision-making capability",
            "Better alignment with strategic objectives",
        ],
        estimated_cost_range="$50,000 — $250,000 (depending on scope and complexity)",
        risk_factors=[
            "Integration complexity with existing systems",
            "Resource availability for implementation",
            "Change management and user adoption",
            "Technical feasibility of AI components",
        ],
        success_criteria=[
            "Solution deployed and operational within agreed timeline",
            "User adoption rate exceeds 80% within 3 months",
            "Measurable improvement in target KPIs",
            "Stakeholder satisfaction score above 4.0/5.0",
        ],
    )
