"""Action handlers for the Continuous Improvement & Process Mining Agent."""

from ci_actions.benchmarking import benchmark_performance, share_best_practices
from ci_actions.conformance import (
    check_conformance,
    detect_bottlenecks,
    detect_deviations,
)
from ci_actions.discovery import discover_process
from ci_actions.improvement import (
    complete_improvement,
    create_improvement,
    get_improvement_backlog,
    get_improvement_history,
    prioritize_improvements,
    track_benefits,
)
from ci_actions.ingest import ingest_analytics_report, ingest_event_log
from ci_actions.insights import (
    get_conformance_report,
    get_kpi_report,
    get_process_insights,
    get_process_model,
    get_recommendations,
)
from ci_actions.root_cause import analyze_root_cause

__all__ = [
    "analyze_root_cause",
    "benchmark_performance",
    "check_conformance",
    "complete_improvement",
    "create_improvement",
    "detect_bottlenecks",
    "detect_deviations",
    "discover_process",
    "get_conformance_report",
    "get_improvement_backlog",
    "get_improvement_history",
    "get_kpi_report",
    "get_process_insights",
    "get_process_model",
    "get_recommendations",
    "ingest_analytics_report",
    "ingest_event_log",
    "prioritize_improvements",
    "share_best_practices",
    "track_benefits",
]
