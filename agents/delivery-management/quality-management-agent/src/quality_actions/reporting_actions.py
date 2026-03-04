"""Action handlers for quality dashboards, reports, and artifact queries."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from quality_utils import generate_openai_narrative

if TYPE_CHECKING:
    from quality_management_agent import QualityManagementAgent


async def get_quality_dashboard(
    agent: QualityManagementAgent,
    project_id: str | None,
    filters: dict[str, Any],
) -> dict[str, Any]:
    """Get quality dashboard data.  Returns dashboard data and visualizations."""
    agent.logger.info("Getting quality dashboard for project: %s", project_id)

    from quality_actions.metric_actions import calculate_metrics

    metrics = await calculate_metrics(agent, project_id) if project_id else {}

    defect_stats = await _get_defect_statistics(agent, project_id, filters)
    test_summary = await _get_test_execution_summary(agent, project_id, filters)
    recent_audits = await _get_recent_audits(agent, project_id, filters)

    return {
        "project_id": project_id,
        "metrics": metrics,
        "defect_statistics": defect_stats,
        "test_summary": test_summary,
        "recent_audits": recent_audits,
        "recommendations": (
            metrics.get("improvement_recommendations", []) if isinstance(metrics, dict) else []
        ),
        "dashboard_generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def generate_quality_report(
    agent: QualityManagementAgent,
    report_type: str,
    filters: dict[str, Any],
) -> dict[str, Any]:
    """Generate quality report.  Returns report data."""
    agent.logger.info("Generating %s quality report", report_type)

    if report_type == "summary":
        report = await _generate_summary_report(agent, filters)
    elif report_type == "defect_analysis":
        report = await _generate_defect_analysis_report(agent, filters)
    elif report_type == "test_coverage":
        report = await _generate_test_coverage_report(agent, filters)
    elif report_type == "audit_summary":
        report = await _generate_audit_summary_report(agent, filters)
    elif report_type == "release_notes":
        report = await _generate_release_notes_report(agent, filters)
    else:
        raise ValueError(f"Unknown report type: {report_type}")

    await agent._publish_quality_event(
        "quality.report.published",
        payload={"report_type": report_type, "filters": filters},
        tenant_id=filters.get("tenant_id", "unknown"),
        correlation_id=str(uuid.uuid4()),
    )
    return report


async def query_quality_artifacts(
    agent: QualityManagementAgent,
    filters: dict[str, Any],
    *,
    tenant_id: str,
) -> dict[str, Any]:
    artifact_type = filters.get("type")
    records: list[dict[str, Any]] = []
    store_map = {
        "plans": agent.quality_plan_store,
        "test_cases": agent.test_case_store,
        "defects": agent.defect_store,
        "audits": agent.audit_store,
        "requirement_links": agent.requirement_link_store,
        "coverage_trends": agent.coverage_trend_store,
    }
    if artifact_type in store_map:
        records = store_map[artifact_type].list(tenant_id)
    else:
        records = (
            agent.quality_plan_store.list(tenant_id)
            + agent.test_case_store.list(tenant_id)
            + agent.defect_store.list(tenant_id)
            + agent.audit_store.list(tenant_id)
        )
    return {"count": len(records), "artifacts": records}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _get_defect_statistics(
    agent: QualityManagementAgent,
    project_id: str | None,
    filters: dict[str, Any],
) -> dict[str, Any]:
    defects = [
        defect
        for defect in agent.defects.values()
        if not project_id or defect.get("project_id") == project_id
    ]
    severity_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for defect in defects:
        severity = defect.get("severity", "unknown")
        status = defect.get("status", "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
    return {"total": len(defects), "by_severity": severity_counts, "by_status": status_counts}


async def _get_test_execution_summary(
    agent: QualityManagementAgent,
    project_id: str | None,
    filters: dict[str, Any],
) -> dict[str, Any]:
    executions = [
        execution
        for execution in agent.test_executions.values()
        if not project_id or execution.get("project_id") == project_id
    ]
    if not executions:
        return {"total_executions": 0, "pass_rate": 0, "coverage": 0}
    total_tests = sum(execution.get("total_tests", 0) for execution in executions)
    passed_tests = sum(execution.get("passed", 0) for execution in executions)
    avg_pass_rate = (passed_tests / total_tests) * 100 if total_tests else 0.0
    latest_execution = max(
        executions,
        key=lambda item: (
            datetime.fromisoformat(item.get("executed_at"))
            if item.get("executed_at")
            else datetime.min
        ),
    )
    return {
        "total_executions": len(executions),
        "pass_rate": avg_pass_rate,
        "coverage": latest_execution.get("code_coverage", 0),
    }


async def _get_recent_audits(
    agent: QualityManagementAgent,
    project_id: str | None,
    filters: dict[str, Any],
) -> list[dict[str, Any]]:
    audits = [
        audit
        for audit in agent.audits.values()
        if not project_id or audit.get("project_id") == project_id
    ]
    audits.sort(
        key=lambda item: (
            datetime.fromisoformat(item.get("audit_date"))
            if item.get("audit_date")
            else datetime.min
        ),
        reverse=True,
    )
    return audits[:5]


async def _generate_summary_report(
    agent: QualityManagementAgent, filters: dict[str, Any]
) -> dict[str, Any]:
    narrative = await generate_openai_narrative(
        "summary", filters, "Summarize overall quality health.", agent.integration_config
    )
    report = {
        "report_type": "summary",
        "data": {"narrative": narrative},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.quality_reports[str(uuid.uuid4())] = report
    return report


async def _generate_defect_analysis_report(
    agent: QualityManagementAgent, filters: dict[str, Any]
) -> dict[str, Any]:
    narrative = await generate_openai_narrative(
        "defect_analysis",
        filters,
        "Analyze defect trends and root causes.",
        agent.integration_config,
    )
    report = {
        "report_type": "defect_analysis",
        "data": {"narrative": narrative},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.quality_reports[str(uuid.uuid4())] = report
    return report


async def _generate_test_coverage_report(
    agent: QualityManagementAgent, filters: dict[str, Any]
) -> dict[str, Any]:
    narrative = await generate_openai_narrative(
        "test_coverage",
        filters,
        "Summarize coverage and automation gaps.",
        agent.integration_config,
    )
    report = {
        "report_type": "test_coverage",
        "data": {"narrative": narrative},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.quality_reports[str(uuid.uuid4())] = report
    return report


async def _generate_audit_summary_report(
    agent: QualityManagementAgent, filters: dict[str, Any]
) -> dict[str, Any]:
    narrative = await generate_openai_narrative(
        "audit_summary",
        filters,
        "Summarize recent audit outcomes.",
        agent.integration_config,
    )
    report = {
        "report_type": "audit_summary",
        "data": {"narrative": narrative},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.quality_reports[str(uuid.uuid4())] = report
    return report


async def _generate_release_notes_report(
    agent: QualityManagementAgent, filters: dict[str, Any]
) -> dict[str, Any]:
    narrative = await generate_openai_narrative(
        "release_notes",
        filters,
        "Draft release notes from test executions, defects, and audits.",
        agent.integration_config,
    )
    report = {
        "report_type": "release_notes",
        "data": {"narrative": narrative},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.quality_reports[str(uuid.uuid4())] = report
    return report
