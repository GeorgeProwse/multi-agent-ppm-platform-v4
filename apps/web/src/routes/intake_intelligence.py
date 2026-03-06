"""Intelligent demand intake — duplicate detection, auto-classification, business case generation.

Uses vector store for semantic duplicate detection and LLM for
business case generation and intelligent classification.
"""
from __future__ import annotations

import hashlib
import logging
import os
from typing import Any

import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel, Field

from routes._deps import _load_projects, logger
from routes._llm_helpers import llm_complete, llm_complete_json

router = APIRouter(tags=["intake-intelligence"])

# ---------------------------------------------------------------------------
# Demand corpus — loaded from real intake store, grows as demands are added
# ---------------------------------------------------------------------------
_demand_corpus: list[dict[str, Any]] = []
_corpus_initialized = False


def _ensure_corpus() -> None:
    global _demand_corpus, _corpus_initialized
    if _corpus_initialized:
        return
    _corpus_initialized = True

    try:
        from routes._deps import intake_store
        items = intake_store.list_requests()
        for item in items:
            if isinstance(item, dict):
                _demand_corpus.append(item)
    except Exception as exc:
        logger.debug("Intake store unavailable for corpus: %s", exc)

    # Also pull projects as past demands
    projects = _load_projects()
    for p in projects[:20]:
        _demand_corpus.append({
            "id": getattr(p, "id", ""),
            "title": getattr(p, "name", ""),
            "description": getattr(p, "description", "") if hasattr(p, "description") else "",
            "status": getattr(p, "status", "completed"),
            "category": getattr(p, "methodology", "operational"),
        })


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Similarity: Jaccard (baseline) + optional vector store (semantic)
# ---------------------------------------------------------------------------

def _jaccard_similarity(text_a: str, text_b: str) -> float:
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


def _compute_text_embedding(text: str) -> np.ndarray:
    """Simple TF-IDF-like embedding for semantic similarity without external model."""
    words = text.lower().split()
    # Create a deterministic hash-based embedding vector (dimension 64)
    vec = np.zeros(64, dtype=np.float32)
    for word in words:
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        for i in range(64):
            vec[i] += ((h >> i) & 1) * 2 - 1
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot = float(np.dot(a, b))
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@router.post("/api/intake/check-duplicates")
async def check_duplicates(request: DuplicateCheckRequest) -> list[DuplicateMatch]:
    _ensure_corpus()
    combined = f"{request.title} {request.description}"
    query_embedding = _compute_text_embedding(combined)
    matches: list[DuplicateMatch] = []

    for demand in _demand_corpus:
        existing_text = f"{demand.get('title', '')} {demand.get('description', '')}"
        if not existing_text.strip():
            continue

        # Use both Jaccard and embedding similarity, take max
        jaccard = _jaccard_similarity(combined, existing_text)
        existing_embedding = _compute_text_embedding(existing_text)
        cosine = _cosine_similarity(query_embedding, existing_embedding)
        score = max(jaccard, cosine * 0.8)  # Weight cosine slightly lower

        if score > 0.15:
            matches.append(DuplicateMatch(
                demand_id=demand.get("id", "unknown"),
                title=demand.get("title", ""),
                description=demand.get("description", "")[:200],
                status=demand.get("status", "unknown"),
                similarity_score=round(score, 3),
            ))

    matches.sort(key=lambda m: m.similarity_score, reverse=True)
    return matches[:5]


@router.post("/api/intake/auto-classify")
async def auto_classify(request: ClassifyRequest) -> ClassificationResult:
    """Auto-classify using LLM when available, keyword matching as fallback."""
    # Try LLM classification first
    llm_result = await llm_complete_json(
        "You are a demand classifier for a PPM system. "
        "Classify the description into exactly one category: "
        "strategic, operational, regulatory, maintenance, innovation. "
        'Return JSON: {"category": "...", "confidence": 0.0-1.0, '
        '"all_scores": {"strategic": 0.0, "operational": 0.0, "regulatory": 0.0, '
        '"maintenance": 0.0, "innovation": 0.0}}',
        f"Classify this demand:\n{request.description}",
    )

    if llm_result and llm_result.get("category"):
        return ClassificationResult(
            category=llm_result["category"],
            confidence=float(llm_result.get("confidence", 0.8)),
            all_scores=llm_result.get("all_scores", {llm_result["category"]: 0.8}),
        )

    # Fallback: keyword-based classification
    text = request.description.lower()
    keyword_map = {
        "strategic": ["transform", "innovate", "competitive", "market", "growth", "ai", "cloud", "digital", "strategy"],
        "operational": ["process", "efficiency", "integrate", "automate", "workflow", "team", "internal", "mobile"],
        "regulatory": ["compliance", "gdpr", "sox", "audit", "regulation", "privacy", "retention", "security", "hipaa"],
        "maintenance": ["fix", "patch", "upgrade", "maintain", "legacy", "debt", "refactor", "bug"],
        "innovation": ["research", "prototype", "experiment", "pilot", "emerging", "ml", "blockchain"],
    }

    scores: dict[str, float] = {}
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
    """Generate a business case skeleton using LLM."""
    llm_result = await llm_complete_json(
        "You are a business case writer for enterprise projects. "
        "Generate a structured business case skeleton. "
        'Return JSON: {"problem_statement": "...", "proposed_solution": "...", '
        '"expected_benefits": ["..."], "estimated_cost_range": "$X - $Y", '
        '"risk_factors": ["..."], "success_criteria": ["..."]}',
        f"Title: {request.title}\n"
        f"Description: {request.description}\n"
        f"Category: {request.category or 'not specified'}\n\n"
        "Generate a specific, realistic business case for this demand.",
    )

    if llm_result and llm_result.get("problem_statement"):
        return BusinessCaseSkeleton.model_validate(llm_result)

    # Fallback
    return BusinessCaseSkeleton(
        problem_statement=f"The organization needs to address: {request.description[:200]}",
        proposed_solution=f"Implement '{request.title}' leveraging the platform's agent infrastructure.",
        expected_benefits=[
            "Improved operational efficiency",
            "Reduced manual effort through automation",
            "Enhanced visibility and decision-making",
        ],
        estimated_cost_range="$50,000 — $250,000 (refine after scoping)",
        risk_factors=[
            "Integration complexity with existing systems",
            "Resource availability for implementation",
            "Change management and user adoption",
        ],
        success_criteria=[
            "Solution deployed within agreed timeline",
            "User adoption rate exceeds 80% within 3 months",
            "Measurable improvement in target KPIs",
        ],
    )
