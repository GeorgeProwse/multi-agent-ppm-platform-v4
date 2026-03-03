"""
Resource & Capacity Management Agent - Utility and Helper Functions

Contains helper methods extracted from the ResourceCapacityAgent class.
These are standalone or static-like functions that support action handlers.
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Any


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def month_start(base: datetime, offset: int) -> datetime:
    """Return the first day of the month offset from base."""
    month_index = base.month - 1 + offset
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    return datetime(year, month, 1)


def get_effective_skills(resource: dict[str, Any]) -> list[str]:
    """Get the effective skills for a resource including training-acquired skills."""
    skills = set(resource.get("skills", []) or [])
    training = resource.get("training", {}) if resource else {}
    for skill in training.get("skills", []) or []:
        skills.add(skill)
    for cert in training.get("certifications", []) or []:
        skills.add(cert)
    return list(skills)


def normalize_score(value: Any) -> float:
    """Normalize a score value to a 0.0 - 1.0 range."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.85
    if numeric > 1.0:
        numeric = numeric / 100.0
    return min(1.0, max(0.0, numeric))


def calculate_performance_score_from_records(
    records: list[dict[str, Any]],
    project_context: dict[str, Any],
    analytics_client: Any | None = None,
) -> float:
    """Calculate a weighted performance score from historical records."""
    weights = {
        "on_time_rate": 0.3,
        "quality_score": 0.25,
        "completion_rate": 0.2,
        "customer_satisfaction": 0.15,
        "utilization_rate": 0.1,
    }
    total = 0.0
    metric_totals = {key: 0.0 for key in weights}
    for record in records:
        on_time = normalize_score(record.get("on_time_rate", 0.85))
        quality = normalize_score(record.get("quality_score", 0.85))
        completion = normalize_score(record.get("completion_rate", 0.85))
        satisfaction = normalize_score(record.get("customer_satisfaction", 0.85))
        utilization = normalize_score(record.get("utilization_rate", 0.85))
        total += (
            weights["on_time_rate"] * on_time
            + weights["quality_score"] * quality
            + weights["completion_rate"] * completion
            + weights["customer_satisfaction"] * satisfaction
            + weights["utilization_rate"] * utilization
        )
        metric_totals["on_time_rate"] += on_time
        metric_totals["quality_score"] += quality
        metric_totals["completion_rate"] += completion
        metric_totals["customer_satisfaction"] += satisfaction
        metric_totals["utilization_rate"] += utilization
    average = total / max(len(records), 1)
    context_boost = 0.0
    if project_context.get("priority") == "high":
        context_boost += 0.02
    if analytics_client:
        record_count = max(len(records), 1)
        for metric_name, total_value in metric_totals.items():
            analytics_client.record_metric(
                f"resource.performance.{metric_name}",
                total_value / record_count,
            )
    return min(1.0, max(0.0, average + context_boost))


def has_resource_changed(existing: dict[str, Any], updated: dict[str, Any]) -> bool:
    """Check if a resource profile has changed in any relevant field."""
    fields = [
        "name",
        "role",
        "skills",
        "location",
        "cost_rate",
        "certifications",
        "availability",
        "status",
        "source_system",
    ]
    for field in fields:
        if existing.get(field) != updated.get(field):
            return True
    return False


def calculate_training_load(
    record: dict[str, Any],
    working_hours_per_day: int,
    working_days: list[int],
) -> float:
    """Calculate the training load fraction from a training record."""
    weekly_hours = record.get("weekly_hours")
    total_hours = record.get("total_hours")
    weeks = record.get("weeks", 1)
    if weekly_hours is None and total_hours is not None:
        weekly_hours = float(total_hours) / max(float(weeks or 1), 1.0)
    if weekly_hours is None:
        weekly_hours = 0.0
    total_work_hours = working_hours_per_day * len(working_days)
    return min(max(float(weekly_hours) / max(total_work_hours, 1.0), 0.0), 1.0)


def normalized_skill_match_weights(skill_match_weights: dict[str, Any]) -> dict[str, float]:
    """Normalize skill match weights so they sum to 1.0."""
    weights = {
        "skills": float(skill_match_weights.get("skills", 0.7)),
        "availability": float(skill_match_weights.get("availability", 0.2)),
        "cost": float(skill_match_weights.get("cost", 0.1)),
        "performance": float(skill_match_weights.get("performance", 0.1)),
    }
    total_weight = sum(weights.values()) or 1.0
    return {key: value / total_weight for key, value in weights.items()}
