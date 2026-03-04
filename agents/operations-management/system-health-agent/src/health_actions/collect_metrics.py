"""Action handlers for metric collection."""

from __future__ import annotations

import statistics
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from health_integrations import emit_event_hub_event
from health_utils import generate_metric_id, parse_time_range
from observability.tracing import start_agent_span

if TYPE_CHECKING:
    from system_health_agent import SystemHealthAgent


async def collect_metrics(
    agent: SystemHealthAgent, tenant_id: str, service_name: str, metrics_data: dict[str, Any]
) -> dict[str, Any]:
    """Collect metrics from service.  Returns collection confirmation."""
    agent.logger.info("Collecting metrics for service: %s", service_name)
    if agent._kpi_handles:
        agent._kpi_handles.requests.add(1, {"service": service_name, "tenant": tenant_id})

    with start_agent_span(
        agent.agent_id, attributes={"service.name": service_name, "tenant.id": tenant_id}
    ):
        timestamp = datetime.now(timezone.utc).isoformat()
        metric_id = await generate_metric_id()

        metric_record = {
            "metric_id": metric_id,
            "tenant_id": tenant_id,
            "service_name": service_name,
            "timestamp": timestamp,
            "metrics": metrics_data,
            "collected_at": timestamp,
        }

        agent.metrics[metric_id] = metric_record

        alerts_triggered = await agent._check_metric_thresholds(
            tenant_id, service_name, metrics_data
        )

    await emit_event_hub_event(
        agent,
        {
            "type": "metric",
            "metric_id": metric_id,
            "tenant_id": tenant_id,
            "service_name": service_name,
            "metrics": metrics_data,
            "timestamp": timestamp,
            "event_hub_partitions": agent.event_hub_partitions,
            "event_hub_throughput_units": agent.event_hub_throughput_units,
        },
    )

    return {
        "metric_id": metric_id,
        "service_name": service_name,
        "metrics_collected": len(metrics_data),
        "timestamp": timestamp,
        "alerts_triggered": alerts_triggered,
    }


async def collect_platform_metrics(
    agent: SystemHealthAgent, tenant_id: str, targets: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Collect infrastructure metrics (CPU, memory, disk, network) across services."""
    from health_integrations import scrape_prometheus_target

    agent.logger.info("Collecting platform infrastructure metrics")
    if targets is not None:
        target_list = targets
    else:
        target_list = (agent.prometheus_scrape_targets or []) + (agent.monitor_resource_ids or [])

    collected: dict[str, dict[str, Any]] = {}
    for target in target_list:
        service_name = target.get("name") or target.get("service") or target.get("id")
        if not service_name:
            continue
        if target.get("resource_id"):
            metrics_data = await agent._query_azure_resource_metrics(target["resource_id"])
        else:
            metrics_data = await scrape_prometheus_target(target)
        if metrics_data.get("error"):
            collected[service_name] = metrics_data
            continue
        await collect_metrics(agent, tenant_id, service_name, metrics_data)
        collected[service_name] = metrics_data

    return {
        "services": collected,
        "total_services": len(collected),
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


async def collect_application_metrics(
    agent: SystemHealthAgent, tenant_id: str, time_range: dict[str, Any]
) -> dict[str, Any]:
    """Collect application-level metrics from analytics events."""
    agent.logger.info("Collecting application metrics from analytics module")
    start_time, _ = parse_time_range(time_range)
    records = agent.analytics_client.list_records(since=start_time)

    aggregated: dict[str, dict[str, list[float]]] = {}
    for record in records:
        svc_name = (
            record.metadata.get("service_name")
            or record.metadata.get("service")
            or record.metadata.get("agent_id")
            or record.metadata.get("agent")
            or (record.name.split(".")[0] if "." in record.name else "platform")
        )
        aggregated.setdefault(svc_name, {})
        aggregated[svc_name].setdefault(record.category, []).append(record.value)

    summarized: dict[str, dict[str, Any]] = {}
    for svc_name, categories in aggregated.items():
        metrics_data: dict[str, Any] = {}
        if categories.get("metric"):
            metrics_data["request_latency_ms"] = statistics.mean(categories["metric"])
        if categories.get("error_rate"):
            metrics_data["error_rate"] = statistics.mean(categories["error_rate"])
        if categories.get("anomaly"):
            metrics_data["anomaly_score"] = statistics.mean(categories["anomaly"])
        if metrics_data:
            await collect_metrics(agent, tenant_id, svc_name, metrics_data)
            summarized[svc_name] = metrics_data

    return {
        "services": summarized,
        "records_processed": len(records),
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }
