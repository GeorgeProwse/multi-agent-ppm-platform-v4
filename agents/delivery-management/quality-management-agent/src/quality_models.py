"""
Quality Management Agent - Pydantic / data models and constants.

Contains configuration constants, default metric definitions,
and data-structure helpers used throughout the quality management agent.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# Default configuration constants
DEFAULT_SEVERITY_LEVELS = ["critical", "high", "medium", "low"]
DEFAULT_QUALITY_STANDARDS = ["ISO 9001", "CMMI", "IEEE 829"]
DEFAULT_MIN_TEST_COVERAGE = 0.80
DEFAULT_DEFECT_DENSITY_THRESHOLD = 0.05


def build_quality_plan(
    plan_id: str,
    plan_data: dict[str, Any],
    quality_standards: list[str],
) -> dict[str, Any]:
    """Construct a quality plan dictionary."""
    return {
        "plan_id": plan_id,
        "project_id": plan_data.get("project_id"),
        "methodology": plan_data.get("methodology", "predictive"),
        "objectives": plan_data.get("objectives", []),
        "metrics": plan_data.get("metrics", []),
        "acceptance_criteria": plan_data.get("acceptance_criteria", []),
        "test_strategy": plan_data.get("test_strategy", {}),
        "review_schedule": plan_data.get("review_schedule", []),
        "responsible_roles": plan_data.get("responsible_roles", {}),
        "standards": plan_data.get("standards", quality_standards),
        "status": "Draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": plan_data.get("owner", "unknown"),
    }


def build_test_case(
    test_case_id: str,
    test_case_data: dict[str, Any],
    requirements: list[dict[str, Any]],
) -> dict[str, Any]:
    """Construct a test case dictionary."""
    return {
        "test_case_id": test_case_id,
        "project_id": test_case_data.get("project_id"),
        "name": test_case_data.get("name"),
        "description": test_case_data.get("description"),
        "type": test_case_data.get("type", "functional"),
        "priority": test_case_data.get("priority", "medium"),
        "steps": test_case_data.get("steps", []),
        "expected_results": test_case_data.get("expected_results"),
        "preconditions": test_case_data.get("preconditions", []),
        "requirements": requirements,
        "automation_status": test_case_data.get("automation_status", "manual"),
        "status": "Active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_test_suite(
    suite_id: str,
    suite_data: dict[str, Any],
    valid_test_cases: list[str],
) -> dict[str, Any]:
    """Construct a test suite dictionary."""
    return {
        "suite_id": suite_id,
        "project_id": suite_data.get("project_id"),
        "name": suite_data.get("name"),
        "description": suite_data.get("description"),
        "test_case_ids": valid_test_cases,
        "test_environment": suite_data.get("test_environment"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_defect(
    defect_id: str,
    defect_data: dict[str, Any],
    auto_classification: dict[str, Any],
) -> dict[str, Any]:
    """Construct a defect dictionary."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "defect_id": defect_id,
        "project_id": defect_data.get("project_id"),
        "summary": defect_data.get("summary"),
        "description": defect_data.get("description"),
        "severity": defect_data.get("severity", auto_classification.get("severity")),
        "priority": defect_data.get("priority", auto_classification.get("priority")),
        "category": auto_classification.get("category"),
        "component": defect_data.get("component"),
        "test_case_id": defect_data.get("test_case_id"),
        "steps_to_reproduce": defect_data.get("steps_to_reproduce", []),
        "expected_behavior": defect_data.get("expected_behavior"),
        "actual_behavior": defect_data.get("actual_behavior"),
        "environment": defect_data.get("environment"),
        "attachments": defect_data.get("attachments", []),
        "assigned_to": None,
        "root_cause": auto_classification.get("root_cause"),
        "status": "Open",
        "resolution": None,
        "logged_at": now,
        "logged_by": defect_data.get("logged_by", "unknown"),
        "status_history": [{"status": "Open", "timestamp": now}],
    }


def build_review(
    review_id: str,
    review_data: dict[str, Any],
) -> dict[str, Any]:
    """Construct a review dictionary."""
    return {
        "review_id": review_id,
        "project_id": review_data.get("project_id"),
        "type": review_data.get("type", "peer_review"),
        "title": review_data.get("title"),
        "scope": review_data.get("scope"),
        "participants": review_data.get("participants", []),
        "scheduled_date": review_data.get("scheduled_date"),
        "agenda": review_data.get("agenda", []),
        "artifacts": review_data.get("artifacts", []),
        "findings": [],
        "action_items": [],
        "status": "Scheduled",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_audit(
    audit_id: str,
    audit_data: dict[str, Any],
    audit_checks: list[dict[str, Any]],
    audit_score: float,
    findings: list[dict[str, Any]],
    recommendations: list[str],
) -> dict[str, Any]:
    """Construct an audit dictionary."""
    return {
        "audit_id": audit_id,
        "project_id": audit_data.get("project_id"),
        "title": audit_data.get("title"),
        "type": audit_data.get("type", "process_audit"),
        "auditor": audit_data.get("auditor"),
        "audit_date": datetime.now(timezone.utc).isoformat(),
        "checklist": audit_data.get("checklist", []),
        "checks_performed": audit_checks,
        "audit_score": audit_score,
        "findings": findings,
        "recommendations": recommendations,
        "status": "Completed",
        "report": audit_data.get("report"),
    }
