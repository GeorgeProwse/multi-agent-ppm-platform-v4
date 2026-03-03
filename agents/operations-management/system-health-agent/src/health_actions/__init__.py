"""Action handlers for the System Health & Monitoring Agent."""

from health_actions.alert_management import (
    acknowledge_alert,
    check_metric_thresholds,
    create_alert,
    get_alerts,
)
from health_actions.anomaly_detection import apply_anomaly_detection, detect_anomalies
from health_actions.capacity_planning import (
    forecast_capacity,
    get_capacity_recommendations,
)
from health_actions.check_health import (
    check_all_services_health,
    check_health,
    get_environment_health,
    get_health_endpoints,
    get_system_status,
)
from health_actions.collect_metrics import (
    collect_application_metrics,
    collect_metrics,
    collect_platform_metrics,
)
from health_actions.dashboard_reporting import (
    get_deployment_baseline,
    get_deployment_metrics,
    get_grafana_dashboard,
    get_health_dashboard,
    get_metrics,
    get_postmortem_report,
    query_historical_metrics,
)
from health_actions.incident_management import (
    analyze_root_cause,
    create_incident,
    resolve_incident,
)

__all__ = [
    "acknowledge_alert",
    "analyze_root_cause",
    "apply_anomaly_detection",
    "check_all_services_health",
    "check_health",
    "check_metric_thresholds",
    "collect_application_metrics",
    "collect_metrics",
    "collect_platform_metrics",
    "create_alert",
    "create_incident",
    "detect_anomalies",
    "forecast_capacity",
    "get_alerts",
    "get_capacity_recommendations",
    "get_deployment_baseline",
    "get_deployment_metrics",
    "get_environment_health",
    "get_grafana_dashboard",
    "get_health_dashboard",
    "get_health_endpoints",
    "get_metrics",
    "get_postmortem_report",
    "get_system_status",
    "query_historical_metrics",
    "resolve_incident",
]
