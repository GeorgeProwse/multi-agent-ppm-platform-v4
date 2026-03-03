"""
System Health & Monitoring Agent

Purpose:
Ensures the operational reliability, performance and availability of the PPM platform through
comprehensive monitoring, alerting, and proactive maintenance.

Specification: agents/operations-management/system-health-agent/README.md
"""

import asyncio
import importlib.util
import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
from observability.metrics import build_kpi_handles, configure_metrics
from observability.tracing import configure_tracing, start_agent_span

from agents.runtime import BaseAgent, get_event_bus
from agents.runtime.src.state_store import TenantStateStore
from integrations.services.integration.analytics import AnalyticsClient

# ---------------------------------------------------------------------------
# Lazy Azure / optional-dependency imports (unchanged from original)
# ---------------------------------------------------------------------------


def _safe_find_spec(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


_HAS_AZURE = _safe_find_spec("azure")
_HAS_AZURE_MONITOR_OPENTELEMETRY = _HAS_AZURE and (_safe_find_spec("azure.monitor.opentelemetry"))
if _HAS_AZURE_MONITOR_OPENTELEMETRY:
    from azure.monitor.opentelemetry import configure_azure_monitor as _configure_azure_monitor
else:
    _configure_azure_monitor = None

_HAS_OTEL_AZURE_EXPORTER = _safe_find_spec("opentelemetry.exporter.azuremonitor")
if _HAS_OTEL_AZURE_EXPORTER:
    from opentelemetry.exporter.azuremonitor import (
        AzureMonitorLogExporter,
        AzureMonitorMetricExporter,
        AzureMonitorTraceExporter,
    )
else:
    AzureMonitorLogExporter = None
    AzureMonitorMetricExporter = None
    AzureMonitorTraceExporter = None

_HAS_AZURE_MONITOR_QUERY = _HAS_AZURE and (_safe_find_spec("azure.monitor.query"))
if _HAS_AZURE_MONITOR_QUERY:
    from azure.monitor.query import LogsQueryClient, LogsQueryStatus, MetricsQueryClient
else:
    LogsQueryClient = None
    LogsQueryStatus = None
    MetricsQueryClient = None

_HAS_ANOMALY_DETECTOR = _HAS_AZURE and (_safe_find_spec("azure.ai.anomalydetector"))
if _HAS_ANOMALY_DETECTOR:
    from azure.ai.anomalydetector import AnomalyDetectorClient
    from azure.ai.anomalydetector.models import TimeSeriesPoint
    from azure.core.credentials import AzureKeyCredential
else:
    AnomalyDetectorClient = None
    TimeSeriesPoint = None
    AzureKeyCredential = None

_HAS_AZURE_EVENTHUB = _HAS_AZURE and _safe_find_spec("azure.eventhub")
if _HAS_AZURE_EVENTHUB:
    from azure.eventhub import EventData, EventHubProducerClient
else:
    EventData = None
    EventHubProducerClient = None

_HAS_AZURE_AUTOMATION = _HAS_AZURE and _safe_find_spec("azure.mgmt.automation")
if _HAS_AZURE_AUTOMATION:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.automation import AutomationClient
    from azure.mgmt.automation.models import JobCreateParameters, RunbookAssociationProperty
else:
    AutomationClient = None
    JobCreateParameters = None
    RunbookAssociationProperty = None

_HAS_PROMETHEUS = _safe_find_spec("prometheus_client")
if _HAS_PROMETHEUS:
    from prometheus_client import CollectorRegistry, Counter, Gauge, start_http_server
else:
    CollectorRegistry = None
    Counter = None
    Gauge = None
    start_http_server = None

# ---------------------------------------------------------------------------
# Action handler imports (delegated modules)
# ---------------------------------------------------------------------------
from actions import (
    acknowledge_alert,
    analyze_root_cause,
    apply_anomaly_detection,
    check_all_services_health,
    check_health,
    check_metric_thresholds,
    collect_application_metrics,
    collect_metrics,
    collect_platform_metrics,
    create_alert,
    create_incident,
    detect_anomalies,
    forecast_capacity,
    get_alerts,
    get_capacity_recommendations,
    get_deployment_baseline,
    get_deployment_metrics,
    get_environment_health,
    get_grafana_dashboard,
    get_health_dashboard,
    get_health_endpoints,
    get_metrics,
    get_postmortem_report,
    get_system_status,
    query_historical_metrics,
    resolve_incident,
)
from health_utils import (
    load_health_endpoints,
    load_monitor_resource_ids,
    load_prometheus_scrape_targets,
    parse_prometheus_metrics,
    parse_time_range,
    sanitize_text,
)


class SystemHealthAgent(BaseAgent):
    """
    System Health & Monitoring Agent - Monitors platform health and performance.

    Key Capabilities:
    - Resource monitoring (compute, memory, storage, network)
    - Application and agent monitoring
    - Log and trace collection
    - Alerting and incident management
    - Anomaly detection and predictive maintenance
    - Dashboarding and reporting
    - Root cause analysis and diagnostics
    - Capacity planning and scaling recommendations
    """

    def __init__(self, agent_id: str = "system-health-agent", config: dict[str, Any] | None = None):
        super().__init__(agent_id, config)

        # Configuration parameters
        self.alert_threshold_error_rate = (
            config.get("alert_threshold_error_rate", 0.05) if config else 0.05
        )
        self.alert_threshold_response_time_ms = (
            config.get("alert_threshold_response_time_ms", 1000) if config else 1000
        )
        self.metrics_retention_days = config.get("metrics_retention_days", 90) if config else 90
        self.monitor_workspace_id = (
            config.get("monitor_workspace_id")
            if config and config.get("monitor_workspace_id")
            else os.getenv("MONITOR_WORKSPACE_ID")
        )
        self.app_insights_instrumentation_key = (
            config.get("appinsights_instrumentation_key")
            if config and config.get("appinsights_instrumentation_key")
            else os.getenv("APPINSIGHTS_INSTRUMENTATION_KEY")
        )
        self.app_insights_resource_id = (
            config.get("appinsights_resource_id")
            if config and config.get("appinsights_resource_id")
            else os.getenv("APPINSIGHTS_RESOURCE_ID")
        )
        self.azure_monitor_connection_string = (
            config.get("azure_monitor_connection_string")
            if config and config.get("azure_monitor_connection_string")
            else os.getenv("AZURE_MONITOR_CONNECTION_STRING")
        )
        if not self.azure_monitor_connection_string and self.app_insights_instrumentation_key:
            self.azure_monitor_connection_string = (
                f"InstrumentationKey={self.app_insights_instrumentation_key}"
            )
        self.event_hub_connection_string = (
            config.get("event_hub_connection_string")
            if config and config.get("event_hub_connection_string")
            else os.getenv("EVENT_HUB_CONNECTION_STRING")
        )
        self.event_hub_name = (
            config.get("event_hub_name")
            if config and config.get("event_hub_name")
            else os.getenv("EVENT_HUB_NAME")
        )
        self.event_hub_partitions = int(
            config.get("event_hub_partitions", os.getenv("EVENT_HUB_PARTITIONS", "4"))
            if config
            else os.getenv("EVENT_HUB_PARTITIONS", "4")
        )
        self.event_hub_throughput_units = int(
            config.get("event_hub_throughput_units", os.getenv("EVENT_HUB_THROUGHPUT_UNITS", "1"))
            if config
            else os.getenv("EVENT_HUB_THROUGHPUT_UNITS", "1")
        )
        self.pagerduty_webhook_url = (
            config.get("pagerduty_webhook_url")
            if config and config.get("pagerduty_webhook_url")
            else os.getenv("PAGERDUTY_WEBHOOK_URL")
        )
        self.opsgenie_webhook_url = (
            config.get("opsgenie_webhook_url")
            if config and config.get("opsgenie_webhook_url")
            else os.getenv("OPSGENIE_WEBHOOK_URL")
        )
        self.scaling_webhook_url = (
            config.get("scaling_webhook_url")
            if config and config.get("scaling_webhook_url")
            else os.getenv("SCALING_WEBHOOK_URL")
        )
        self.automation_webhook_url = (
            config.get("automation_webhook_url")
            if config and config.get("automation_webhook_url")
            else os.getenv("AUTOMATION_WEBHOOK_URL")
        )
        self.automation_subscription_id = (
            config.get("automation_subscription_id")
            if config and config.get("automation_subscription_id")
            else os.getenv("AUTOMATION_SUBSCRIPTION_ID")
        )
        self.automation_resource_group = (
            config.get("automation_resource_group")
            if config and config.get("automation_resource_group")
            else os.getenv("AUTOMATION_RESOURCE_GROUP")
        )
        self.automation_account_name = (
            config.get("automation_account_name")
            if config and config.get("automation_account_name")
            else os.getenv("AUTOMATION_ACCOUNT_NAME")
        )
        self.automation_runbook_name = (
            config.get("automation_runbook_name")
            if config and config.get("automation_runbook_name")
            else os.getenv("AUTOMATION_RUNBOOK_NAME")
        )
        self.scaling_thresholds = {
            "cpu": float(
                config.get("scaling_threshold_cpu", os.getenv("SCALING_THRESHOLD_CPU", "0.8"))
                if config
                else os.getenv("SCALING_THRESHOLD_CPU", "0.8")
            ),
            "memory": float(
                config.get("scaling_threshold_memory", os.getenv("SCALING_THRESHOLD_MEMORY", "0.8"))
                if config
                else os.getenv("SCALING_THRESHOLD_MEMORY", "0.8")
            ),
            "queue_depth": float(
                config.get(
                    "scaling_threshold_queue_depth",
                    os.getenv("SCALING_THRESHOLD_QUEUE_DEPTH", "1000"),
                )
                if config
                else os.getenv("SCALING_THRESHOLD_QUEUE_DEPTH", "1000")
            ),
        }
        self.servicenow_instance_url = (
            config.get("servicenow_instance_url")
            if config and config.get("servicenow_instance_url")
            else os.getenv("SERVICENOW_INSTANCE_URL")
        )
        self.servicenow_username = (
            config.get("servicenow_username")
            if config and config.get("servicenow_username")
            else os.getenv("SERVICENOW_USERNAME")
        )
        self.servicenow_password = (
            config.get("servicenow_password")
            if config and config.get("servicenow_password")
            else os.getenv("SERVICENOW_PASSWORD")
        )
        self.servicenow_token = (
            config.get("servicenow_token")
            if config and config.get("servicenow_token")
            else os.getenv("SERVICENOW_TOKEN")
        )
        self.anomaly_detector_endpoint = (
            config.get("anomaly_detector_endpoint")
            if config and config.get("anomaly_detector_endpoint")
            else os.getenv("ANOMALY_DETECTOR_ENDPOINT")
        )
        self.anomaly_detector_key = (
            config.get("anomaly_detector_key")
            if config and config.get("anomaly_detector_key")
            else os.getenv("ANOMALY_DETECTOR_KEY")
        )
        self.health_endpoints = (
            config.get("health_endpoints") if config and config.get("health_endpoints") else None
        ) or load_health_endpoints(self.logger)
        self.health_probe_interval_seconds = int(
            config.get(
                "health_probe_interval_seconds",
                os.getenv("HEALTH_PROBE_INTERVAL_SECONDS", "60"),
            )
            if config
            else os.getenv("HEALTH_PROBE_INTERVAL_SECONDS", "60")
        )
        self.metrics_port = int(
            config.get("metrics_port", os.getenv("PROMETHEUS_METRICS_PORT", "0"))
            if config
            else os.getenv("PROMETHEUS_METRICS_PORT", "0")
        )
        self.prometheus_scrape_targets = (
            config.get("prometheus_scrape_targets")
            if config and config.get("prometheus_scrape_targets")
            else load_prometheus_scrape_targets(self.logger)
        )
        self.monitor_resource_ids = (
            config.get("monitor_resource_ids")
            if config and config.get("monitor_resource_ids")
            else load_monitor_resource_ids(self.logger)
        )

        alert_store_path = (
            Path(config.get("alert_store_path", "data/alerts.json"))
            if config
            else Path("data/alerts.json")
        )
        incident_store_path = (
            Path(config.get("incident_store_path", "data/incidents.json"))
            if config
            else Path("data/incidents.json")
        )
        self.alert_store = TenantStateStore(alert_store_path)
        self.incident_store = TenantStateStore(incident_store_path)

        # Data stores (will be replaced with database)
        self.metrics = {}  # type: ignore
        self.alerts = {}  # type: ignore
        self.incidents = {}  # type: ignore
        self.health_checks = {}  # type: ignore
        self.anomalies = {}  # type: ignore
        self._kpi_handles = None
        self._logs_query_client = None
        self._metrics_query_client = None
        self._event_hub_producer = None
        self._automation_client = None
        self._health_probe_task: asyncio.Task | None = None
        self._prometheus_registry = None
        self._prometheus_metrics: dict[str, Any] = {}
        self._azure_monitor_configured = False
        self._alert_rules: list[dict[str, Any]] = []
        self._pii_patterns = {
            "email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "phone": re.compile(r"\+?\d[\d\s().-]{7,}\d"),
        }
        self.analytics_client = config.get("analytics_client") if config else None
        if not self.analytics_client:
            self.analytics_client = AnalyticsClient()
        self.event_bus = config.get("event_bus") if config else None
        if self.event_bus is None:
            try:
                self.event_bus = get_event_bus()
            except ValueError:
                self.event_bus = None
        self.grafana_datasource = (
            config.get("grafana_datasource", os.getenv("GRAFANA_DATASOURCE", "Prometheus"))
            if config
            else os.getenv("GRAFANA_DATASOURCE", "Prometheus")
        )
        self.grafana_folder = (
            config.get("grafana_folder", os.getenv("GRAFANA_FOLDER", "System Health"))
            if config
            else os.getenv("GRAFANA_FOLDER", "System Health")
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Initialize monitoring infrastructure and integrations."""
        await super().initialize()
        self.logger.info("Initializing System Health & Monitoring Agent...")

        configure_tracing(self.agent_id)
        try:
            configure_metrics(self.agent_id)
        except ValueError:
            pass
        try:
            self._kpi_handles = build_kpi_handles(self.agent_id)
        except ValueError:
            self._kpi_handles = {}
        await self._initialize_azure_monitoring()
        await self._configure_opentelemetry_exporters()
        await self._initialize_event_hub()
        await self._initialize_automation_client()
        await self._initialize_prometheus_metrics()
        await self._configure_alert_rules()
        await self._initialize_health_probes()

        self.logger.info("System Health & Monitoring Agent initialized")

    async def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data based on the requested action."""
        action = input_data.get("action", "")

        if not action:
            self.logger.warning("No action specified")
            return False

        valid_actions = [
            "collect_metrics",
            "collect_platform_metrics",
            "collect_application_metrics",
            "check_health",
            "create_alert",
            "detect_anomalies",
            "create_incident",
            "analyze_root_cause",
            "get_system_status",
            "get_metrics",
            "get_alerts",
            "get_capacity_recommendations",
            "get_health_endpoints",
            "query_historical_metrics",
            "forecast_capacity",
            "acknowledge_alert",
            "resolve_incident",
            "get_health_dashboard",
            "get_postmortem_report",
            "get_environment_health",
            "get_grafana_dashboard",
        ]

        if action not in valid_actions:
            self.logger.warning("Invalid action: %s", action)
            return False

        return True

    # ------------------------------------------------------------------
    # Process routing (delegates to extracted action modules)
    # ------------------------------------------------------------------

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process system health and monitoring requests.

        Args:
            input_data: {
                "action": "collect_metrics" | "check_health" | "create_alert" |
                          "detect_anomalies" | "create_incident" | "analyze_root_cause" |
                          "get_system_status" | "get_metrics" | "get_alerts" |
                          "get_capacity_recommendations" | "acknowledge_alert" | "resolve_incident",
                "service_name": Service or agent name,
                "metrics": Metrics data to collect,
                "alert": Alert configuration,
                "incident": Incident details,
                "time_range": Time range for queries,
                "alert_id": Alert identifier,
                "incident_id": Incident identifier,
                "filters": Query filters
            }

        Returns:
            Response based on action:
            - collect_metrics: Collection confirmation
            - check_health: Health status for all services
            - create_alert: Alert ID and configuration
            - detect_anomalies: Detected anomalies
            - create_incident: Incident ID and details
            - analyze_root_cause: Root cause analysis
            - get_system_status: Overall system health
            - get_metrics: Metric values
            - get_alerts: Active alerts
            - get_capacity_recommendations: Scaling recommendations
            - acknowledge_alert: Acknowledgment confirmation
            - resolve_incident: Resolution confirmation
        """
        action = input_data.get("action", "get_system_status")
        tenant_id = (
            input_data.get("tenant_id")
            or input_data.get("context", {}).get("tenant_id")
            or "default"
        )

        if action == "collect_metrics":
            return await collect_metrics(
                self,
                tenant_id,
                input_data.get("service_name"),  # type: ignore
                input_data.get("metrics", {}),
            )

        elif action == "collect_platform_metrics":
            return await collect_platform_metrics(self, tenant_id, input_data.get("targets"))

        elif action == "collect_application_metrics":
            return await collect_application_metrics(
                self, tenant_id, input_data.get("time_range", {})
            )

        elif action == "check_health":
            return await check_health(self, input_data.get("service_name"))

        elif action == "create_alert":
            return await create_alert(self, tenant_id, input_data.get("alert", {}))

        elif action == "detect_anomalies":
            return await detect_anomalies(
                self,
                tenant_id,
                input_data.get("service_name"),  # type: ignore
                input_data.get("time_range", {}),
            )

        elif action == "create_incident":
            return await create_incident(self, tenant_id, input_data.get("incident", {}))

        elif action == "analyze_root_cause":
            return await analyze_root_cause(self, input_data.get("incident_id"))  # type: ignore

        elif action == "get_system_status":
            return await get_system_status(self)

        elif action == "get_metrics":
            if input_data.get("deployment_plan"):
                return await get_deployment_metrics(self, input_data["deployment_plan"])
            return await get_metrics(
                self,
                input_data.get("service_name"),  # type: ignore
                input_data.get("metric_name"),  # type: ignore
                input_data.get("time_range", {}),
            )

        elif action == "get_alerts":
            return await get_alerts(self, input_data.get("filters", {}))

        elif action == "get_capacity_recommendations":
            return await get_capacity_recommendations(self, input_data.get("service_name"))

        elif action == "get_health_endpoints":
            return await get_health_endpoints(self)

        elif action == "query_historical_metrics":
            return await query_historical_metrics(
                self,
                input_data.get("service_name"),  # type: ignore
                input_data.get("metric_name"),  # type: ignore
                input_data.get("time_range", {}),
            )

        elif action == "forecast_capacity":
            return await forecast_capacity(self, input_data.get("service_name"))

        elif action == "acknowledge_alert":
            return await acknowledge_alert(
                self,
                tenant_id,
                input_data.get("alert_id"),
                input_data.get("acknowledged_by"),  # type: ignore
            )

        elif action == "resolve_incident":
            return await resolve_incident(
                self,
                tenant_id,
                input_data.get("incident_id"),
                input_data.get("resolution", {}),  # type: ignore
            )

        elif action == "get_health_dashboard":
            return await get_health_dashboard(self, tenant_id, input_data.get("time_range", {}))

        elif action == "get_postmortem_report":
            return await get_postmortem_report(self, tenant_id, input_data.get("time_range", {}))

        elif action == "get_environment_health":
            return await get_environment_health(
                self, input_data.get("environment") or input_data.get("service_name")
            )

        elif action == "get_grafana_dashboard":
            return await get_grafana_dashboard(self)

        else:
            raise ValueError(f"Unknown action: {action}")

    # ------------------------------------------------------------------
    # Internal helpers kept on the class (used by action modules via agent ref)
    # ------------------------------------------------------------------

    async def _check_metric_thresholds(
        self, tenant_id: str, service_name: str, metrics_data: dict[str, Any]
    ) -> list[str]:
        return await check_metric_thresholds(self, tenant_id, service_name, metrics_data)

    async def _get_service_metrics(
        self, service_name: str, time_range: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Get metrics for service in time range."""
        metrics_list: list[dict[str, Any]] = []
        start_time, end_time = parse_time_range(time_range)
        for metric in self.metrics.values():
            if metric.get("service_name") != service_name:
                continue
            timestamp = metric.get("timestamp")
            if timestamp:
                parsed = (
                    datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp
                )
                if parsed < start_time or parsed > end_time:
                    continue
            metrics_list.append(metric)

        query_metrics = await self._query_metrics(service_name, "*", time_range)
        metrics_list.extend(query_metrics)
        return metrics_list

    async def _query_metrics(
        self, service_name: str, metric_name: str, time_range: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Query metrics from store."""
        if not self._logs_query_client:
            return []

        start_time, end_time = parse_time_range(time_range)
        metric_filter = "" if metric_name == "*" else f'| where name == "{metric_name}"'
        query = (
            "customMetrics "
            f'| where cloud_RoleName == "{service_name}" '
            f"{metric_filter} "
            f"| where timestamp between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()})) "
            "| project timestamp, name, value"
            "| order by timestamp asc"
        )
        if self.monitor_workspace_id:
            response = await asyncio.to_thread(
                self._logs_query_client.query_workspace,
                workspace_id=self.monitor_workspace_id,
                query=query,
                timespan=(start_time, end_time),
            )
        elif self.app_insights_resource_id:
            response = await asyncio.to_thread(
                self._logs_query_client.query_resource,
                resource_id=self.app_insights_resource_id,
                query=query,
                timespan=(start_time, end_time),
            )
        else:
            return []
        if response.status != LogsQueryStatus.SUCCESS:
            self.logger.warning("Log Analytics query returned partial results")

        table = response.tables[0] if response.tables else None
        if not table:
            return []

        values = []
        for row in table.rows:
            values.append(
                {
                    "timestamp": row[0],
                    "metric": row[1],
                    "value": row[2],
                }
            )
        return values

    async def _query_azure_resource_metrics(self, resource_id: str) -> dict[str, Any]:
        if not self._metrics_query_client:
            return {"error": "azure_monitor_unavailable"}
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=5)
        metric_names = [
            "Percentage CPU",
            "Available Memory Bytes",
            "Total Memory Bytes",
            "Logical Disk % Free Space",
            "Network In Total",
            "Network Out Total",
        ]
        response = await asyncio.to_thread(
            self._metrics_query_client.query_resource,
            resource_id=resource_id,
            metric_names=metric_names,
            timespan=(start_time, end_time),
        )
        result: dict[str, Any] = {"metrics_source": "azure_monitor"}
        value_lookup: dict[str, float] = {}
        for metric in response.metrics:
            mn = getattr(metric.name, "value", None) or str(metric.name)
            if not metric.timeseries:
                continue
            points = metric.timeseries[0].data
            if not points:
                continue
            latest = next((point for point in reversed(points) if point.average is not None), None)
            if not latest:
                continue
            value_lookup[mn] = float(latest.average)

        cpu_value = value_lookup.get("Percentage CPU")
        if cpu_value is not None:
            result["cpu_usage"] = cpu_value / 100.0
        available_memory = value_lookup.get("Available Memory Bytes")
        total_memory = value_lookup.get("Total Memory Bytes")
        if available_memory is not None and total_memory:
            result["memory_usage"] = (total_memory - available_memory) / total_memory
        elif available_memory is not None:
            result["memory_available_bytes"] = available_memory
        disk_free = value_lookup.get("Logical Disk % Free Space")
        if disk_free is not None:
            result["disk_usage"] = (100.0 - disk_free) / 100.0
        network_in = value_lookup.get("Network In Total")
        if network_in is not None:
            result["network_rx_bytes_total"] = network_in
        network_out = value_lookup.get("Network Out Total")
        if network_out is not None:
            result["network_tx_bytes_total"] = network_out
        return result

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    async def _initialize_azure_monitoring(self) -> None:
        if _HAS_AZURE_MONITOR_QUERY and (
            self.monitor_workspace_id or self.app_insights_resource_id
        ):
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential()
            self._logs_query_client = LogsQueryClient(credential)
            self._metrics_query_client = MetricsQueryClient(credential)
            self.logger.info(
                "Azure Monitor clients configured",
                extra={
                    "workspace_id": self.monitor_workspace_id,
                    "app_insights_resource_id": self.app_insights_resource_id,
                },
            )

    async def _configure_opentelemetry_exporters(self) -> None:
        if self._azure_monitor_configured:
            return
        if not self.azure_monitor_connection_string:
            self.logger.info("Azure Monitor connection string not configured")
            return
        if _configure_azure_monitor:
            _configure_azure_monitor(connection_string=self.azure_monitor_connection_string)
            self._azure_monitor_configured = True
            self.logger.info("Azure Monitor OpenTelemetry configured via SDK")
            return
        if not _HAS_OTEL_AZURE_EXPORTER:
            self.logger.warning("Azure Monitor exporter unavailable")
            return

        from opentelemetry import metrics as otel_metrics
        from opentelemetry import trace
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": self.agent_id})
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(AzureMonitorTraceExporter(self.azure_monitor_connection_string))
        )
        trace.set_tracer_provider(tracer_provider)

        metric_reader = PeriodicExportingMetricReader(
            AzureMonitorMetricExporter(self.azure_monitor_connection_string)
        )
        otel_metrics.set_meter_provider(
            MeterProvider(resource=resource, metric_readers=[metric_reader])
        )

        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(AzureMonitorLogExporter(self.azure_monitor_connection_string))
        )
        handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
        logging.getLogger().addHandler(handler)
        self._azure_monitor_configured = True
        self.logger.info("Azure Monitor exporters configured")

    async def _initialize_event_hub(self) -> None:
        if not (self.event_hub_connection_string and self.event_hub_name):
            return
        if not _HAS_AZURE_EVENTHUB:
            self.logger.warning("Azure Event Hub SDK not available")
            return
        self._event_hub_producer = EventHubProducerClient.from_connection_string(
            conn_str=self.event_hub_connection_string,
            eventhub_name=self.event_hub_name,
        )
        self.logger.info(
            "Event Hub producer initialized",
            extra={
                "event_hub": self.event_hub_name,
                "partitions": self.event_hub_partitions,
                "throughput_units": self.event_hub_throughput_units,
            },
        )

    async def _initialize_automation_client(self) -> None:
        if (
            not _HAS_AZURE_AUTOMATION
            or not self.automation_subscription_id
            or not self.automation_resource_group
            or not self.automation_account_name
        ):
            return
        credential = DefaultAzureCredential()
        self._automation_client = AutomationClient(credential, self.automation_subscription_id)
        self.logger.info(
            "Azure Automation client initialized",
            extra={
                "automation_account": self.automation_account_name,
                "resource_group": self.automation_resource_group,
            },
        )

    async def _initialize_prometheus_metrics(self) -> None:
        if not (_HAS_PROMETHEUS and self.metrics_port and self.metrics_port > 0):
            return
        self._prometheus_registry = CollectorRegistry()
        self._prometheus_metrics["health_status"] = Gauge(
            "service_health_status",
            "Health status of monitored services (1=healthy, 0=degraded)",
            ["service"],
            registry=self._prometheus_registry,
        )
        self._prometheus_metrics["health_latency"] = Gauge(
            "service_health_latency_ms",
            "Latency of health checks in milliseconds",
            ["service"],
            registry=self._prometheus_registry,
        )
        self._prometheus_metrics["health_checks"] = Counter(
            "service_health_checks_total",
            "Total health checks executed",
            ["service"],
            registry=self._prometheus_registry,
        )
        start_http_server(self.metrics_port, registry=self._prometheus_registry)
        self.logger.info("Prometheus metrics endpoint started", extra={"port": self.metrics_port})

    async def _configure_alert_rules(self) -> None:
        self._alert_rules = [
            {
                "name": "error_rate_threshold",
                "metric": "error_rate",
                "threshold": self.alert_threshold_error_rate,
                "severity": "critical",
                "notification_channels": [
                    url for url in [self.pagerduty_webhook_url, self.opsgenie_webhook_url] if url
                ],
            },
            {
                "name": "response_time_threshold",
                "metric": "response_time_ms",
                "threshold": self.alert_threshold_response_time_ms,
                "severity": "warning",
                "notification_channels": [
                    url for url in [self.pagerduty_webhook_url, self.opsgenie_webhook_url] if url
                ],
            },
        ]
        self.logger.info("Alert rules configured", extra={"count": len(self._alert_rules)})

    async def _initialize_health_probes(self) -> None:
        if not self.health_endpoints or self.health_probe_interval_seconds <= 0:
            return
        if self._health_probe_task:
            return
        self._health_probe_task = asyncio.create_task(self._periodic_health_probes())
        self.logger.info(
            "Health probes scheduled",
            extra={"interval": self.health_probe_interval_seconds},
        )

    async def _periodic_health_probes(self) -> None:
        while True:
            try:
                await check_all_services_health(self)
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                KeyError,
                TypeError,
                RuntimeError,
                OSError,
            ) as exc:
                self.logger.warning("Health probe failure", extra={"error": str(exc)})
            await asyncio.sleep(self.health_probe_interval_seconds)

    # ------------------------------------------------------------------
    # Backward-compatible thin wrappers kept on the class so that
    # existing callers (tests, orchestrator) continue to work via
    # ``agent._method_name(...)`` or ``agent.method_name(...)``.
    # ------------------------------------------------------------------

    def _parse_prometheus_metrics(self, payload: str) -> dict[str, Any]:
        return parse_prometheus_metrics(payload)

    async def _apply_anomaly_detection(self, metrics_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return await apply_anomaly_detection(self, metrics_list)

    async def _collect_metrics(self, tenant_id: str, service_name: str, metrics_data: dict[str, Any]) -> dict[str, Any]:
        return await collect_metrics(self, tenant_id, service_name, metrics_data)

    async def _collect_application_metrics(self, tenant_id: str, time_range: dict[str, Any]) -> dict[str, Any]:
        return await collect_application_metrics(self, tenant_id, time_range)

    async def _create_alert(self, tenant_id: str, alert_config: dict[str, Any]) -> dict[str, Any]:
        return await create_alert(self, tenant_id, alert_config)

    async def _create_incident(self, tenant_id: str, incident_data: dict[str, Any]) -> dict[str, Any]:
        return await create_incident(self, tenant_id, incident_data)

    async def _get_system_status(self) -> dict[str, Any]:
        return await get_system_status(self)

    async def _get_environment_health(self, environment: str | None) -> dict[str, Any]:
        return await get_environment_health(self, environment)

    async def _get_deployment_metrics(self, deployment_plan: dict[str, Any]) -> dict[str, Any]:
        return await get_deployment_metrics(self, deployment_plan)

    async def _get_deployment_baseline(self, deployment_plan: dict[str, Any]) -> dict[str, Any]:
        return await get_deployment_baseline(self, deployment_plan)

    async def _emit_event_hub_event(self, payload: dict[str, Any]) -> None:
        from health_integrations import emit_event_hub_event
        await emit_event_hub_event(self, payload)

    async def _create_servicenow_incident(self, incident: dict[str, Any]) -> None:
        from health_integrations import create_servicenow_incident
        await create_servicenow_incident(self, incident)

    def _sanitize_text(self, value: str) -> str:
        return sanitize_text(value)

    # ------------------------------------------------------------------
    # Public convenience methods (called by other agents/orchestrator)
    # ------------------------------------------------------------------

    async def get_metrics(self, deployment_plan: dict[str, Any]) -> dict[str, Any]:
        """Expose monitoring metrics for deployment workflows."""
        return await get_deployment_metrics(self, deployment_plan)

    async def get_baseline(self, deployment_plan: dict[str, Any]) -> dict[str, Any]:
        """Expose baseline metrics for deployment workflows."""
        return await get_deployment_baseline(self, deployment_plan)

    async def get_environment_health(self, environment: str) -> dict[str, Any]:
        """Expose health status for deployment workflows."""
        return await get_environment_health(self, environment)

    # ------------------------------------------------------------------
    # Cleanup & capabilities
    # ------------------------------------------------------------------

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self.logger.info("Cleaning up System Health & Monitoring Agent...")
        if self._health_probe_task:
            self._health_probe_task.cancel()
            self._health_probe_task = None
        if self._event_hub_producer:
            await asyncio.to_thread(self._event_hub_producer.close)
            self._event_hub_producer = None

    def get_capabilities(self) -> list[str]:
        """Return list of agent capabilities."""
        return [
            "resource_monitoring",
            "application_monitoring",
            "log_collection",
            "trace_collection",
            "alerting",
            "incident_management",
            "anomaly_detection",
            "predictive_maintenance",
            "root_cause_analysis",
            "capacity_planning",
            "health_checks",
            "performance_monitoring",
            "dashboard_creation",
            "postmortem_reporting",
            "deployment_health_gate",
            "grafana_dashboard",
            "environment_health_query",
        ]
