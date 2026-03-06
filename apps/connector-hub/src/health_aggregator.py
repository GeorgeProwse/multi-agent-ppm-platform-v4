"""Connector health aggregation service."""

from __future__ import annotations

from typing import Any

from health_models import (
    ConflictRecord,
    ConnectorHealthRecord,
    DataFreshnessRecord,
)


class ConnectorHealthAggregator:
    """Aggregates health status across all configured connectors."""

    def get_all_status(self, tenant_id: str) -> list[ConnectorHealthRecord]:
        """Return health status for all connectors. Demo data for showcase."""
        return [
            ConnectorHealthRecord(
                connector_id="jira",
                name="Jira Cloud",
                category="project_management",
                status="healthy",
                circuit_state="closed",
                last_sync="2026-03-06T10:30:00Z",
                error_rate_1h=0.02,
                sync_direction="bidirectional",
            ),
            ConnectorHealthRecord(
                connector_id="azure-devops",
                name="Azure DevOps",
                category="project_management",
                status="healthy",
                circuit_state="closed",
                last_sync="2026-03-06T10:28:00Z",
                error_rate_1h=0.0,
                sync_direction="bidirectional",
            ),
            ConnectorHealthRecord(
                connector_id="sap",
                name="SAP S/4HANA",
                category="erp",
                status="degraded",
                circuit_state="half_open",
                last_sync="2026-03-06T09:15:00Z",
                error_rate_1h=0.15,
                sync_direction="inbound",
            ),
            ConnectorHealthRecord(
                connector_id="slack",
                name="Slack",
                category="communication",
                status="healthy",
                circuit_state="closed",
                last_sync="2026-03-06T10:31:00Z",
                error_rate_1h=0.0,
                sync_direction="outbound",
            ),
            ConnectorHealthRecord(
                connector_id="workday",
                name="Workday HCM",
                category="hr",
                status="down",
                circuit_state="open",
                last_sync="2026-03-05T23:00:00Z",
                error_rate_1h=1.0,
                sync_direction="inbound",
            ),
            ConnectorHealthRecord(
                connector_id="servicenow",
                name="ServiceNow",
                category="itsm",
                status="healthy",
                circuit_state="closed",
                last_sync="2026-03-06T10:25:00Z",
                error_rate_1h=0.01,
                sync_direction="bidirectional",
            ),
        ]

    def get_data_freshness(self, tenant_id: str) -> list[DataFreshnessRecord]:
        return [
            DataFreshnessRecord(connector_id="jira", connector_name="Jira Cloud", entity_type="work_item", last_synced_at="2026-03-06T10:30:00Z", record_count=1247, freshness_status="fresh"),
            DataFreshnessRecord(connector_id="jira", connector_name="Jira Cloud", entity_type="project", last_synced_at="2026-03-06T10:30:00Z", record_count=42, freshness_status="fresh"),
            DataFreshnessRecord(connector_id="sap", connector_name="SAP S/4HANA", entity_type="budget", last_synced_at="2026-03-06T09:15:00Z", record_count=89, freshness_status="stale"),
            DataFreshnessRecord(connector_id="sap", connector_name="SAP S/4HANA", entity_type="vendor", last_synced_at="2026-03-06T09:15:00Z", record_count=156, freshness_status="stale"),
            DataFreshnessRecord(connector_id="workday", connector_name="Workday HCM", entity_type="resource", last_synced_at="2026-03-05T23:00:00Z", record_count=312, freshness_status="critical"),
            DataFreshnessRecord(connector_id="servicenow", connector_name="ServiceNow", entity_type="issue", last_synced_at="2026-03-06T10:25:00Z", record_count=567, freshness_status="fresh"),
        ]

    def get_conflict_queue(self, tenant_id: str) -> list[ConflictRecord]:
        return [
            ConflictRecord(
                conflict_id="cf-001",
                connector_id="jira",
                connector_name="Jira Cloud",
                entity_type="work_item",
                entity_id="PROJ-1234",
                source_value="In Progress",
                canonical_value="Active",
                detected_at="2026-03-06T09:45:00Z",
            ),
            ConflictRecord(
                conflict_id="cf-002",
                connector_id="sap",
                connector_name="SAP S/4HANA",
                entity_type="budget",
                entity_id="BUD-2026-Q1",
                source_value="$1,250,000",
                canonical_value="$1,200,000",
                detected_at="2026-03-06T08:30:00Z",
            ),
        ]

    def resolve_conflict(
        self,
        tenant_id: str,
        conflict_id: str,
        strategy: str,
        manual_value: str | None = None,
    ) -> ConflictRecord:
        return ConflictRecord(
            conflict_id=conflict_id,
            connector_id="jira",
            connector_name="Jira Cloud",
            entity_type="work_item",
            entity_id="PROJ-1234",
            source_value="In Progress",
            canonical_value="Active",
            detected_at="2026-03-06T09:45:00Z",
            status="resolved",
            resolution=strategy,
        )
