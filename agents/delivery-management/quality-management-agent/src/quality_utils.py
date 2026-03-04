"""
Quality Management Agent - Utility functions.

Contains ID generators, scoring helpers, text tokenization,
k-means clustering, classification helpers, and other stateless utilities
extracted from the monolithic QualityManagementAgent class.
"""

from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.common.integration_services import NaiveBayesTextClassifier


# ---------------------------------------------------------------------------
# ID generators
# ---------------------------------------------------------------------------


async def generate_plan_id() -> str:
    """Generate unique quality plan ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"QP-{timestamp}"


async def generate_metric_id() -> str:
    """Generate unique metric ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"QM-{timestamp}"


async def generate_test_case_id() -> str:
    """Generate unique test case ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"TC-{timestamp}"


async def generate_suite_id() -> str:
    """Generate unique test suite ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"TS-{timestamp}"


async def generate_execution_id() -> str:
    """Generate unique execution ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"EX-{timestamp}"


async def generate_defect_id() -> str:
    """Generate unique defect ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"DEF-{timestamp}"


async def generate_review_id() -> str:
    """Generate unique review ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"REV-{timestamp}"


async def generate_audit_id() -> str:
    """Generate unique audit ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"AUD-{timestamp}"


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------


def severity_from_category(category: str) -> str:
    if category in {"security_gap", "data_issue"}:
        return "critical"
    if category in {"performance_issue", "integration_failure"}:
        return "high"
    return "medium"


def root_cause_from_category(category: str) -> str:
    root_cause_map = {
        "ui_defect": "ux_issue",
        "performance_issue": "performance_regression",
        "security_gap": "security_gap",
        "integration_failure": "integration_issue",
        "configuration_error": "configuration_issue",
        "data_issue": "data_quality",
        "requirements_gap": "requirements_gap",
        "code_defect": "code_defect",
    }
    return root_cause_map.get(category, "code_defect")


def build_defect_classifier() -> NaiveBayesTextClassifier:
    from agents.common.integration_services import NaiveBayesTextClassifier

    classifier = NaiveBayesTextClassifier(
        labels=[
            "ui_defect",
            "performance_issue",
            "security_gap",
            "integration_failure",
            "configuration_error",
            "data_issue",
            "requirements_gap",
            "code_defect",
        ]
    )
    classifier.fit(
        [
            ("button alignment layout css styling", "ui_defect"),
            ("page rendering broken ui glitch", "ui_defect"),
            ("slow response timeout latency", "performance_issue"),
            ("memory spike cpu overload", "performance_issue"),
            ("authentication bypass vulnerability", "security_gap"),
            ("permission escalation access control", "security_gap"),
            ("api integration failed endpoint", "integration_failure"),
            ("third party service error response", "integration_failure"),
            ("misconfigured feature flag config", "configuration_error"),
            ("environment variable missing configuration", "configuration_error"),
            ("data corruption incorrect dataset", "data_issue"),
            ("migration lost records data sync", "data_issue"),
            ("missing requirement incorrect expectation", "requirements_gap"),
            ("user story misunderstood acceptance criteria", "requirements_gap"),
            ("null pointer exception crash", "code_defect"),
            ("logic bug incorrect calculation", "code_defect"),
        ]
    )
    return classifier


# ---------------------------------------------------------------------------
# Text / ML helpers
# ---------------------------------------------------------------------------


def tokenize_text(text: str) -> list[str]:
    tokens = ["".join(ch for ch in token.lower() if ch.isalnum()) for token in text.split()]
    return [token for token in tokens if token]


def score_labels(content: str, label_tokens: dict[str, list[str]]) -> dict[str, float]:
    if not label_tokens:
        return {}
    tokens = tokenize_text(content)
    scores: dict[str, float] = {}
    for label, vocab in label_tokens.items():
        if not vocab:
            continue
        vocab_set = set(vocab)
        overlap = sum(1 for token in tokens if token in vocab_set)
        scores[label] = overlap / len(vocab_set)
    return scores


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    total = sum(scores.values())
    if total <= 0:
        return {label: 0.0 for label in scores}
    return {label: value / total for label, value in scores.items()}


def vectorize_defects(
    defects: list[dict[str, Any]],
) -> tuple[list[list[float]], list[str]]:
    texts = []
    for defect in defects:
        text = " ".join(
            value
            for value in [
                defect.get("summary"),
                defect.get("description"),
                defect.get("component"),
                defect.get("root_cause"),
            ]
            if value
        )
        texts.append(text)
    vocab = sorted({token for text in texts for token in tokenize_text(text)})
    vectors = []
    for text in texts:
        tokens = tokenize_text(text)
        vector = [tokens.count(term) for term in vocab]
        vectors.append(vector)
    return vectors, vocab


def euclidean_distance(vector: list[float], centroid: list[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vector, centroid)))


def kmeans(vectors: list[list[float]], k: int) -> list[dict[str, Any]]:
    if not vectors:
        return []
    centroids = random.sample(vectors, k=k)
    assignments = [0 for _ in vectors]
    for _ in range(5):
        for idx, vector in enumerate(vectors):
            distances = [euclidean_distance(vector, centroid) for centroid in centroids]
            assignments[idx] = distances.index(min(distances))
        new_centroids = [[0.0 for _ in vectors[0]] for _ in range(k)]
        counts = [0 for _ in range(k)]
        for vector, cluster_id in zip(vectors, assignments):
            counts[cluster_id] += 1
            for i, value in enumerate(vector):
                new_centroids[cluster_id][i] += value
        for cluster_id in range(k):
            if counts[cluster_id] == 0:
                continue
            new_centroids[cluster_id] = [
                value / counts[cluster_id] for value in new_centroids[cluster_id]
            ]
        centroids = new_centroids
    clusters = []
    for cluster_id in range(k):
        clusters.append(
            {
                "cluster_id": cluster_id,
                "count": assignments.count(cluster_id),
            }
        )
    return clusters


# ---------------------------------------------------------------------------
# Resource scoring
# ---------------------------------------------------------------------------


def derive_required_skills(defect: dict[str, Any]) -> list[str]:
    component = defect.get("component")
    category = defect.get("root_cause")
    required_skills = [skill for skill in [component, category] if skill]
    if defect.get("severity") == "critical":
        required_skills.append("incident_response")
    return required_skills


def score_resource_candidate(candidate: dict[str, Any], skills: list[str]) -> float:
    candidate_skills = set(candidate.get("skills", []))
    skill_match = sum(1 for skill in skills if skill in candidate_skills)
    availability = float(candidate.get("availability", 0.0))
    return skill_match * 0.7 + availability * 0.3


# ---------------------------------------------------------------------------
# Calculation helpers
# ---------------------------------------------------------------------------


async def calculate_resolution_time(defect: dict[str, Any]) -> float:
    """Calculate defect resolution time in hours."""
    logged_at = datetime.fromisoformat(defect.get("logged_at"))  # type: ignore
    resolved_at = datetime.now(timezone.utc)

    if defect.get("status_history"):
        for entry in reversed(defect["status_history"]):
            if entry.get("status") in ["Resolved", "Closed"]:
                resolved_at = datetime.fromisoformat(entry["timestamp"])
                break

    delta = resolved_at - logged_at
    return delta.total_seconds() / 3600


async def calculate_audit_score(checks: list[dict[str, Any]]) -> float:
    """Calculate audit score."""
    if not checks:
        return 0.0
    passed = sum(1 for c in checks if c.get("result") == "pass")
    return (passed / len(checks)) * 100


async def extract_audit_findings(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract audit findings from checks."""
    findings = []
    for check in checks:
        if check.get("result") == "fail":
            findings.append(
                {
                    "check": check.get("check"),
                    "severity": "high",
                    "description": check.get("notes", "Failed audit check"),
                }
            )
    return findings


async def generate_audit_recommendations(checks: list[dict[str, Any]]) -> list[str]:
    """Generate audit recommendations."""
    recommendations = []
    failed_checks = [c for c in checks if c.get("result") == "fail"]
    if failed_checks:
        recommendations.append("Address failed audit checks immediately")
        recommendations.append("Implement corrective action plan")
    return recommendations


async def import_test_results(execution_data: dict[str, Any]) -> list[dict[str, Any]]:
    raw_results = execution_data.get("test_results")
    if isinstance(raw_results, list):
        results = raw_results
    else:
        raw_json = execution_data.get("test_results_json")
        results = []
        if raw_json:
            data = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
            results = data.get("results", data) if isinstance(data, dict) else data
        else:
            results_path = execution_data.get("test_results_path")
            if results_path:
                content = Path(results_path).read_text()
                data = json.loads(content)
                results = data.get("results", data) if isinstance(data, dict) else data
    if not results or not isinstance(results, list):
        return []
    normalized: list[dict[str, Any]] = []
    project_id = execution_data.get("project_id")
    for result in results:
        status = result.get("result") or result.get("status") or result.get("outcome")
        normalized_status = str(status or "pass").lower()
        if normalized_status in {"passed", "success"}:
            normalized_status = "pass"
        elif normalized_status in {"failed", "error"}:
            normalized_status = "fail"
        normalized.append(
            {
                **result,
                "project_id": result.get("project_id", project_id),
                "result": normalized_status,
            }
        )
    return normalized


async def generate_openai_narrative(
    report_type: str,
    filters: dict[str, Any],
    default_prompt: str,
    integration_config: dict[str, Any],
) -> str:
    """Generate narrative text using Azure OpenAI (simulated)."""
    prompt_prefix = integration_config.get("azure_openai", {}).get("prompt_prefix", "")
    context = {
        "filters": filters,
        "report_type": report_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    summary = f"{default_prompt} Context: {json.dumps(context)}"
    if prompt_prefix:
        summary = f"{prompt_prefix}\n{summary}"
    return summary
