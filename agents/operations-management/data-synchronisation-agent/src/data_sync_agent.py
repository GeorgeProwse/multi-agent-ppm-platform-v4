"""
Data Synchronization & Consistency Agent

Purpose:
Ensures that data flowing through the PPM platform and across integrated systems remains
consistent, up-to-date and accurate through master data management and event-driven synchronization.

Specification: agents/operations-management/data-synchronisation-agent/README.md
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common.bootstrap import ensure_monorepo_paths  # noqa: E402

ensure_monorepo_paths()

import httpx  # noqa: E402
import yaml  # noqa: E402
from observability.metrics import build_business_workflow_metrics  # noqa: E402
from observability.tracing import get_trace_id  # noqa: E402
from security.lineage import mask_lineage_payload  # noqa: E402

from agents.common.connector_integration import ConnectorWriteGate, DatabaseStorageService, _ensure_connector_paths  # noqa: E402
from agents.runtime import BaseAgent  # noqa: E402
from agents.runtime.src.audit import build_audit_event, emit_audit_event  # noqa: E402
from agents.runtime.src.event_bus import EventBus, ServiceBusEventBus  # noqa: E402
from agents.runtime.src.state_store import TenantStateStore  # noqa: E402
from jsonschema import ValidationError, validate  # noqa: E402
from feature_flags import is_feature_enabled  # noqa: E402

from sync_models import InMemorySecretContext, SecretContext  # noqa: E402
from sync_utils import (  # noqa: E402
    apply_transformations,
    get_transformation_rules,
    validate_transformation_rule,
)
from actions import (  # noqa: E402
    apply_conflict_resolution,
    detect_update_conflicts,
    enqueue_retry,
    governed_connector_write,
    handle_create_master_record,
    handle_define_mapping,
    handle_detect_conflicts,
    handle_detect_duplicates,
    handle_get_dashboard,
    handle_get_master_record,
    handle_get_metrics,
    handle_get_quality_report,
    handle_get_retry_queue,
    handle_get_schema,
    handle_get_sync_status,
    handle_merge_duplicates,
    handle_process_retry_queue,
    handle_register_schema,
    handle_reprocess_retry,
    handle_resolve_conflict,
    handle_run_sync,
    handle_sync_data,
    handle_update_master_record,
    handle_validate_data,
    record_conflicts,
    record_quality_metrics,
)

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.cosmos import CosmosClient
    from azure.eventgrid import EventGridPublisherClient
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    from azure.mgmt.datafactory import DataFactoryManagementClient
    from azure.monitor.ingestion import LogsIngestionClient
    from azure.servicebus import ServiceBusMessage
    from azure.servicebus.aio import ServiceBusClient
except ImportError:  # pragma: no cover - optional dependencies
    AzureKeyCredential = None
    CosmosClient = None
    EventGridPublisherClient = None
    DefaultAzureCredential = None
    SecretClient = None
    DataFactoryManagementClient = None
    LogsIngestionClient = None
    ServiceBusMessage = None
    ServiceBusClient = None

try:
    import azure.functions as azure_functions
except ImportError:  # pragma: no cover - optional dependencies
    azure_functions = None

try:
    from sqlalchemy import create_engine
except ImportError:  # pragma: no cover - optional dependencies
    create_engine = None


class DataSyncAgent(BaseAgent):
    """
    Data Synchronization & Consistency Agent - Manages data synchronization across systems.

    Key Capabilities:
    - Master data management (MDM)
    - Data mapping and transformation
    - Event-driven synchronization
    - Conflict detection and resolution
    - Duplicate detection and merging
    - Data quality and validation
    - Audit and lineage tracking
    - Synchronization monitoring
    """

    def __init__(self, agent_id: str = "data-synchronisation-agent", config: dict[str, Any] | None = None):
        super().__init__(agent_id, config)

        self.secret_context: SecretContext = (
            config.get("secret_context")
            if config and config.get("secret_context")
            else InMemorySecretContext(config.get("secrets") if config else None)
        )

        # Configuration parameters
        self.sync_latency_sla_seconds = config.get("sync_latency_sla_seconds", 60) if config else 60
        self.duplicate_confidence_threshold = (
            config.get("duplicate_confidence_threshold", 0.85) if config else 0.85
        )
        self.conflict_resolution_strategy = (
            config.get("conflict_resolution_strategy", "last_write_wins")
            if config
            else "last_write_wins"
        )
        self.authoritative_sources = config.get("authoritative_sources", {}) if config else {}
        self.sync_event_webhook_url = config.get("sync_event_webhook_url") if config else None
        self.sync_event_webhook_timeout = (
            config.get("sync_event_webhook_timeout", 5.0) if config else 5.0
        )
        self.transformation_rules = config.get("transformation_rules", []) if config else []
        self.transformation_schema = {
            "type": "object",
            "properties": {
                "entity_type": {"type": "string"},
                "source_system": {"type": "string"},
                "field_mappings": {"type": "object", "additionalProperties": {"type": "string"}},
                "defaults": {"type": "object"},
                "transformations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "operation": {"type": "string"},
                            "value": {},
                        },
                        "required": ["field", "operation"],
                    },
                },
            },
            "required": ["entity_type", "field_mappings"],
        }

        master_store_path = (
            Path(config.get("master_record_store_path", "data/master_records.json"))
            if config
            else Path("data/master_records.json")
        )
        sync_event_store_path = (
            Path(config.get("sync_event_store_path", "data/sync_events.json"))
            if config
            else Path("data/sync_events.json")
        )
        lineage_store_path = (
            Path(config.get("sync_lineage_store_path", "data/lineage/sync_lineage.json"))
            if config
            else Path("data/lineage/sync_lineage.json")
        )

        environment = os.getenv("ENVIRONMENT", "dev")
        duplicate_resolution_flag = is_feature_enabled(
            "duplicate_resolution", environment=environment, default=False
        )
        self.duplicate_resolution_enabled = (
            config.get("duplicate_resolution_enabled", duplicate_resolution_flag)
            if config
            else duplicate_resolution_flag
        )
        audit_store_path = (
            Path(config.get("sync_audit_store_path", "data/sync_audit_events.json"))
            if config
            else Path("data/sync_audit_events.json")
        )
        self.master_record_store = TenantStateStore(master_store_path)
        self.sync_event_store = TenantStateStore(sync_event_store_path)
        self.sync_lineage_store = TenantStateStore(lineage_store_path)
        self.sync_audit_store = TenantStateStore(audit_store_path)

        # Data stores (will be replaced with database)
        self.master_records = {}  # type: ignore
        self.mapping_rules = {}  # type: ignore
        self.sync_events = {}  # type: ignore
        self.conflicts = {}  # type: ignore
        self.duplicates = {}  # type: ignore
        self.audit_records = {}  # type: ignore
        self.db_service: DatabaseStorageService | None = None
        self.write_gate = ConnectorWriteGate(config or {})
        self.event_bus: EventBus | None = None
        self.service_bus_client: Any | None = None
        self.service_bus_queue_sender: Any | None = None
        self.service_bus_topic_sender: Any | None = None
        self.service_bus_topic_name = os.getenv("AZURE_SERVICE_BUS_TOPIC_NAME", "ppm-events")
        self.service_bus_queue_name = os.getenv("AZURE_SERVICE_BUS_QUEUE_NAME", "ppm-sync-queue")
        self.event_grid_client: Any | None = None
        self.sql_engine: Any | None = None
        self.cosmos_client: Any | None = None
        self.data_factory_client: Any | None = None
        self.data_factory_pipelines: list[str] = []
        self.function_app: Any | None = None
        self.function_names: list[str] = []
        self.data_factory_resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.data_factory_name = os.getenv("AZURE_DATA_FACTORY_NAME")
        self.function_base_url = os.getenv("AZURE_FUNCTION_BASE_URL")
        self.function_key = os.getenv("AZURE_FUNCTION_KEY")
        self.validation_rules: dict[str, list[dict[str, Any]]] = {}
        self.quality_thresholds: dict[str, float] = {}
        self.schema_registry: dict[str, dict[str, Any]] = {}
        self.schema_versions: dict[str, list[dict[str, Any]]] = {}
        self.schema_registry_store = TenantStateStore(
            Path(
                config.get("schema_registry_store_path", "data/schema_registry.json")
                if config
                else "data/schema_registry.json"
            )
        )
        self.seen_record_hashes: dict[str, set[str]] = {}
        self.latency_records: list[dict[str, Any]] = []
        self.quality_records: list[dict[str, Any]] = []
        self.sync_logs: list[dict[str, Any]] = []
        self.sync_state_store = TenantStateStore(
            Path(
                config.get("sync_state_store_path", "data/sync_state.json")
                if config
                else "data/sync_state.json"
            )
        )
        self.retry_queue_store = TenantStateStore(
            Path(
                config.get("retry_queue_store_path", "data/sync_retry_queue.json")
                if config
                else "data/sync_retry_queue.json"
            )
        )
        self.max_retry_attempts = config.get("max_retry_attempts", 3) if config else 3
        self.log_analytics_client: Any | None = None
        self.connectors: dict[str, Any] = {}
        self._sync_business_metrics = build_business_workflow_metrics(
            "data-sync-agent", "connector_sync"
        )

    # ------------------------------------------------------------------
    # Settings helper
    # ------------------------------------------------------------------

    def _get_setting(self, key: str, default: str | None = None) -> str | None:
        secret_value = self.secret_context.get(key)
        if secret_value is not None:
            return secret_value
        return os.getenv(key, default)

    # ------------------------------------------------------------------
    # Lifecycle methods
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Initialize data sync infrastructure and integrations."""
        await super().initialize()
        self.logger.info("Initializing Data Synchronization & Consistency Agent...")

        self.validation_rules = self._load_validation_rules()
        self.quality_thresholds = self._load_quality_thresholds()
        self.schema_registry, self.schema_versions = self._load_schema_registry()
        self.transformation_rules = self._load_mapping_rules()
        self.data_factory_pipelines, self.function_names = self._load_pipeline_config()

        await self._initialize_key_vault_secrets()
        await self._initialize_connectors()
        await self._initialize_service_bus()
        await self._initialize_event_grid()
        await self._initialize_datastores()
        await self._initialize_data_factory()
        await self._initialize_functions()
        await self._initialize_monitoring()

        db_config = self.config.get("database_storage", {}) if self.config else {}
        self.db_service = DatabaseStorageService(db_config)
        self.logger.info("Database Storage Service initialized")

        self.logger.info("Data Synchronization & Consistency Agent initialized")

    async def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data based on the requested action."""
        action = input_data.get("action", "")
        if not action:
            self.logger.warning("No action specified")
            return False
        valid_actions = [
            "sync_data", "run_sync", "create_master_record", "update_master_record",
            "detect_conflicts", "resolve_conflict", "detect_duplicates", "merge_duplicates",
            "validate_data", "define_mapping", "get_sync_status", "get_master_record",
            "metrics", "get_schema", "register_schema", "get_quality_report",
            "process_retries", "reprocess_retry", "get_retry_queue", "get_dashboard",
        ]
        if action not in valid_actions:
            self.logger.warning("Invalid action: %s", action)
            return False
        if action == "sync_data":
            if "entity_type" not in input_data or "data" not in input_data:
                self.logger.warning("Missing entity_type or data for sync")
                return False
        return True

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self.logger.info("Cleaning up Data Synchronization & Consistency Agent...")
        if self.event_bus and hasattr(self.event_bus, "stop"):
            await self.event_bus.stop()
        if self.service_bus_queue_sender and hasattr(self.service_bus_queue_sender, "close"):
            await self.service_bus_queue_sender.close()
        if self.service_bus_topic_sender and hasattr(self.service_bus_topic_sender, "close"):
            await self.service_bus_topic_sender.close()
        if self.service_bus_client and hasattr(self.service_bus_client, "close"):
            await self.service_bus_client.close()
        if self.sql_engine and hasattr(self.sql_engine, "dispose"):
            self.sql_engine.dispose()
        if self.cosmos_client and hasattr(self.cosmos_client, "close"):
            self.cosmos_client.close()
        if self.log_analytics_client and hasattr(self.log_analytics_client, "close"):
            await self.log_analytics_client.close()

    def get_capabilities(self) -> list[str]:
        """Return list of agent capabilities."""
        return [
            "master_data_management", "event_driven_sync", "data_mapping",
            "data_transformation", "conflict_detection", "conflict_resolution",
            "duplicate_detection", "duplicate_merging", "data_validation",
            "data_quality", "sync_monitoring", "audit_logging", "fuzzy_matching",
        ]

    # ------------------------------------------------------------------
    # Process routing (delegates to action modules)
    # ------------------------------------------------------------------

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process data synchronization requests.

        Args:
            input_data: {
                "action": "sync_data" | "create_master_record" | "update_master_record" |
                          "detect_conflicts" | "resolve_conflict" | "detect_duplicates" |
                          "merge_duplicates" | "validate_data" | "define_mapping" |
                          "get_sync_status" | "get_master_record",
                "entity_type": Type of entity (project, resource, vendor, etc.),
                "data": Entity data,
                "source_system": Source system identifier,
                "master_id": Master record ID,
                "conflict_id": Conflict identifier,
                "mapping": Mapping rule definition,
                "filters": Query filters
            }

        Returns:
            Response based on action:
            - sync_data: Sync status and master record ID
            - create_master_record: Master record ID
            - update_master_record: Update confirmation
            - detect_conflicts: Detected conflicts
            - resolve_conflict: Resolution result
            - detect_duplicates: Duplicate candidates
            - merge_duplicates: Merge result
            - validate_data: Validation results
            - define_mapping: Mapping rule ID
            - get_sync_status: Synchronization status
            - get_master_record: Master record data
        """
        action = input_data.get("action", "get_sync_status")
        tenant_id = (
            input_data.get("tenant_id")
            or input_data.get("context", {}).get("tenant_id")
            or "default"
        )
        correlation_id = input_data.get("context", {}).get("correlation_id") or input_data.get(
            "correlation_id"
        )

        if action == "sync_data":
            return await self._sync_data(
                tenant_id,
                input_data.get("entity_type"),  # type: ignore
                input_data.get("data"),  # type: ignore
                input_data.get("source_system"),  # type: ignore
            )
        if action == "run_sync":
            return await self._run_sync(
                tenant_id=tenant_id,
                entity_type=input_data.get("entity_type"),  # type: ignore
                source_system=input_data.get("source_system"),  # type: ignore
                mode=input_data.get("mode", "incremental"),
                filters=input_data.get("filters", {}),
            )
        elif action == "create_master_record":
            return await self._create_master_record(
                tenant_id, input_data.get("entity_type"), input_data.get("data")  # type: ignore
            )
        elif action == "update_master_record":
            return await self._update_master_record(
                tenant_id,
                input_data.get("master_id"),
                input_data.get("data"),
                input_data.get("source_system"),  # type: ignore
            )
        elif action == "detect_conflicts":
            return await self._detect_conflicts(input_data.get("master_id"))  # type: ignore
        elif action == "resolve_conflict":
            return await self._resolve_conflict(
                input_data.get("conflict_id"), input_data.get("resolution")  # type: ignore
            )
        elif action == "detect_duplicates":
            return await self._detect_duplicates(input_data.get("entity_type"))  # type: ignore
        elif action == "merge_duplicates":
            return await self._merge_duplicates(
                input_data.get("master_ids", []),
                input_data.get("primary_id"),  # type: ignore
                decision=input_data.get("decision"),
                reviewer_id=input_data.get("reviewer_id"),
                comments=input_data.get("comments"),
                tenant_id=tenant_id,
                correlation_id=correlation_id,
            )
        elif action == "validate_data":
            return await self._validate_data(input_data.get("entity_type"), input_data.get("data"))  # type: ignore
        elif action == "define_mapping":
            return await self._define_mapping(input_data.get("mapping", {}))
        elif action == "get_sync_status":
            return await self._get_sync_status(input_data.get("filters", {}))
        elif action == "get_master_record":
            return await self._get_master_record(
                tenant_id, input_data.get("master_id")  # type: ignore
            )
        elif action == "metrics":
            return await self._get_metrics(tenant_id)
        elif action == "get_schema":
            return await self._get_schema(input_data.get("entity_type"))  # type: ignore
        elif action == "register_schema":
            return await self._register_schema(
                tenant_id=tenant_id,
                entity_type=input_data.get("entity_type"),
                schema=input_data.get("schema", {}),
                version=input_data.get("version"),
            )
        elif action == "get_quality_report":
            return await self._get_quality_report(tenant_id, input_data.get("entity_type"))
        elif action == "process_retries":
            return await self._process_retry_queue(tenant_id)
        elif action == "reprocess_retry":
            return await self._reprocess_retry(tenant_id, input_data.get("retry_id"))
        elif action == "get_retry_queue":
            return await self._get_retry_queue(tenant_id)
        elif action == "get_dashboard":
            return await self._get_dashboard(tenant_id)
        else:
            raise ValueError(f"Unknown action: {action}")

    # ------------------------------------------------------------------
    # Delegate methods (preserve original method signatures on the class)
    # ------------------------------------------------------------------

    async def _sync_data(self, tenant_id: str, entity_type: str, data: dict[str, Any], source_system: str) -> dict[str, Any]:
        return await handle_sync_data(self, tenant_id, entity_type, data, source_system)

    async def _run_sync(self, tenant_id: str, entity_type: str, source_system: str, mode: str = "incremental", filters: dict[str, Any] | None = None) -> dict[str, Any]:
        return await handle_run_sync(self, tenant_id, entity_type, source_system, mode, filters)

    async def _create_master_record(self, tenant_id: str, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        return await handle_create_master_record(self, tenant_id, entity_type, data)

    async def _update_master_record(self, tenant_id: str, master_id: str, data: dict[str, Any], source_system: str) -> dict[str, Any]:
        return await handle_update_master_record(self, tenant_id, master_id, data, source_system)

    async def _detect_conflicts(self, master_id: str) -> dict[str, Any]:
        return await handle_detect_conflicts(self, master_id)

    async def _resolve_conflict(self, conflict_id: str, resolution: dict[str, Any]) -> dict[str, Any]:
        return await handle_resolve_conflict(self, conflict_id, resolution)

    async def _detect_duplicates(self, entity_type: str) -> dict[str, Any]:
        return await handle_detect_duplicates(self, entity_type)

    async def _merge_duplicates(self, master_ids: list[str], primary_id: str, *, decision: str | None = None, reviewer_id: str | None = None, comments: str | None = None, tenant_id: str | None = None, correlation_id: str | None = None) -> dict[str, Any]:
        return await handle_merge_duplicates(self, master_ids, primary_id, decision=decision, reviewer_id=reviewer_id, comments=comments, tenant_id=tenant_id, correlation_id=correlation_id)

    async def _validate_data(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        return await handle_validate_data(self, entity_type, data)

    async def _define_mapping(self, mapping_config: dict[str, Any]) -> dict[str, Any]:
        return await handle_define_mapping(self, mapping_config)

    async def _get_sync_status(self, filters: dict[str, Any]) -> dict[str, Any]:
        return await handle_get_sync_status(self, filters)

    async def _get_metrics(self, tenant_id: str) -> dict[str, Any]:
        return await handle_get_metrics(self, tenant_id)

    async def _get_master_record(self, tenant_id: str, master_id: str) -> dict[str, Any]:
        return await handle_get_master_record(self, tenant_id, master_id)

    async def _get_schema(self, entity_type: str | None) -> dict[str, Any]:
        return await handle_get_schema(self, entity_type)

    async def _register_schema(self, tenant_id: str, entity_type: str | None, schema: dict[str, Any], version: str | None = None) -> dict[str, Any]:
        return await handle_register_schema(self, tenant_id, entity_type, schema, version)

    async def _get_quality_report(self, tenant_id: str, entity_type: str | None) -> dict[str, Any]:
        return await handle_get_quality_report(self, tenant_id, entity_type)

    async def _process_retry_queue(self, tenant_id: str) -> dict[str, Any]:
        return await handle_process_retry_queue(self, tenant_id)

    async def _reprocess_retry(self, tenant_id: str, retry_id: str | None) -> dict[str, Any]:
        return await handle_reprocess_retry(self, tenant_id, retry_id)

    async def _get_retry_queue(self, tenant_id: str) -> dict[str, Any]:
        return await handle_get_retry_queue(self, tenant_id)

    async def _get_dashboard(self, tenant_id: str) -> dict[str, Any]:
        return await handle_get_dashboard(self, tenant_id)

    async def _detect_update_conflicts(self, master_record: dict[str, Any], new_data: dict[str, Any], source_system: str) -> list[dict[str, Any]]:
        return await detect_update_conflicts(self, master_record, new_data, source_system)

    async def _record_conflicts(self, master_id: str, conflicts: list[dict[str, Any]]) -> str:
        return await record_conflicts(self, master_id, conflicts)

    async def _apply_conflict_resolution(self, master_record: dict[str, Any], new_data: dict[str, Any], conflicts: list[dict[str, Any]]) -> dict[str, Any]:
        return await apply_conflict_resolution(self, master_record, new_data, conflicts)

    async def _enqueue_retry(self, tenant_id: str, entity_type: str, data: dict[str, Any], source_system: str, reason: str) -> None:
        return await enqueue_retry(self, tenant_id, entity_type, data, source_system, reason)

    async def _record_quality_metrics(self, tenant_id: str, entity_type: str, source_system: str, validation_result: dict[str, Any]) -> None:
        return await record_quality_metrics(self, tenant_id, entity_type, source_system, validation_result)

    async def governed_connector_write(self, connector_id: str, resource_type: str, payloads: list[dict[str, Any]], *, approval_required: bool = False, approval_status: str | None = None, dry_run: bool = False, tenant_id: str = "") -> dict[str, Any]:
        return await governed_connector_write(self, connector_id, resource_type, payloads, approval_required=approval_required, approval_status=approval_status, dry_run=dry_run, tenant_id=tenant_id)

    # ------------------------------------------------------------------
    # Internal infrastructure methods (kept on the class)
    # ------------------------------------------------------------------

    def _record_connector_sync_metrics(self, *, tenant_id: str, source_system: str, sync_mode: str, outcome: str, started: datetime) -> None:
        attributes = {
            "service.name": "data-sync-agent",
            "tenant.id": tenant_id,
            "trace.id": get_trace_id() or "unavailable",
            "workflow": "connector_sync",
            "connector": source_system,
            "mode": sync_mode,
            "outcome": outcome,
        }
        self._sync_business_metrics.executions_total.add(1, attributes)
        self._sync_business_metrics.execution_duration_seconds.record(
            max((datetime.now(timezone.utc) - started).total_seconds(), 0.0),
            attributes,
        )

    async def _map_to_canonical(self, entity_type: str, data: dict[str, Any], source_system: str) -> dict[str, Any]:
        rules = [
            rule for rule in self.transformation_rules
            if rule.get("entity_type") == entity_type and rule.get("source_system") == source_system
        ]
        if not rules:
            return data
        mapped = data.copy()
        for rule in rules:
            if not validate_transformation_rule(rule, self.transformation_schema, self.logger):
                continue
            field_mappings = rule.get("field_mappings", {})
            mapped_payload: dict[str, Any] = {}
            for source_field, target_field in field_mappings.items():
                if source_field in mapped:
                    mapped_payload[target_field] = mapped.get(source_field)
            defaults = rule.get("defaults", {})
            for key, value in defaults.items():
                mapped_payload.setdefault(key, value)
            mapped = mapped_payload
        return mapped

    async def _transform_data(self, entity_type: str, data: dict[str, Any], source_system: str) -> dict[str, Any]:
        applicable_rules = get_transformation_rules(self.transformation_rules, entity_type, source_system)
        if not applicable_rules:
            return data
        transformed = data.copy()
        for rule in applicable_rules:
            if not validate_transformation_rule(rule, self.transformation_schema, self.logger):
                continue
            field_mappings = rule.get("field_mappings", {})
            mapped_payload: dict[str, Any] = {}
            has_mapping = False
            for source_field, target_field in field_mappings.items():
                if source_field in transformed:
                    mapped_payload[target_field] = transformed.get(source_field)
                    has_mapping = True
            defaults = rule.get("defaults", {})
            for key, value in defaults.items():
                mapped_payload.setdefault(key, value)
            if has_mapping:
                transformed = mapped_payload
            transformations = rule.get("transformations", [])
            transformed = apply_transformations(transformed, transformations)
        return transformed

    async def _find_existing_master(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any] | None:
        for master_id, record in self.master_records.items():
            if record.get("entity_type") == entity_type and record.get("data", {}).get("id") == data.get("id"):
                return record  # type: ignore
        return None

    async def _generate_master_id(self, entity_type: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"MASTER-{entity_type.upper()}-{timestamp}"

    async def _generate_mapping_id(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"MAP-{timestamp}"

    async def _record_sync_event(self, tenant_id: str, entity_type: str, master_id: str, source_system: str, status: str) -> str:
        event_id = f"EVENT-{len(self.sync_events) + 1}"
        event_record = {
            "event_id": event_id, "entity_type": entity_type, "master_id": master_id,
            "source_system": source_system, "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.sync_events[event_id] = event_record
        self.sync_event_store.upsert(tenant_id, event_id, event_record)
        await self._store_record("sync_events", event_id, event_record)
        return event_id

    async def _record_sync_lineage(self, tenant_id: str, entity_type: str, master_id: str, source_system: str, payload: dict[str, Any]) -> None:
        lineage_id = f"LINEAGE-{len(self.sync_events) + 1}"
        lineage_record = {
            "lineage_id": lineage_id, "entity_type": entity_type, "master_id": master_id,
            "source_system": source_system, "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        masked_lineage = mask_lineage_payload(lineage_record)
        self.sync_lineage_store.upsert(tenant_id, lineage_id, masked_lineage)
        await self._emit_lineage_event(tenant_id, entity_type, master_id, source_system, payload)

    async def _record_sync_metrics(self, tenant_id: str, entity_type: str, source_system: str, latency_seconds: float, started_at: datetime, finished_at: datetime) -> None:
        record = {
            "tenant_id": tenant_id, "entity_type": entity_type, "source_system": source_system,
            "latency_seconds": latency_seconds,
            "started_at": started_at.isoformat(), "finished_at": finished_at.isoformat(),
        }
        self.latency_records.append(record)
        await self._ingest_latency_metric(record)

    async def _record_sync_log(self, tenant_id: str, entity_type: str, source_system: str, status: str, mode: str, started_at: datetime, finished_at: datetime | None = None, master_id: str | None = None, details: dict[str, Any] | None = None) -> None:
        log_record = {
            "log_id": f"SYNCLOG-{len(self.sync_logs) + 1}",
            "tenant_id": tenant_id, "entity_type": entity_type,
            "source_system": source_system, "status": status, "mode": mode,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat() if finished_at else None,
            "master_id": master_id, "details": details or {},
        }
        self.sync_logs.append(log_record)
        await self._store_record("sync_logs", log_record["log_id"], log_record)

    async def _emit_audit_event(self, tenant_id: str, action: str, resource_id: str, resource_type: str, metadata: dict[str, Any]) -> None:
        audit_event = build_audit_event(
            tenant_id=tenant_id, action=action, outcome="success",
            actor_id=self.agent_id, actor_type="service", actor_roles=[],
            resource_id=resource_id, resource_type=resource_type,
            metadata=metadata, trace_id=get_trace_id(),
        )
        self.audit_records[audit_event["id"]] = audit_event
        self.sync_audit_store.upsert(tenant_id, audit_event["id"], audit_event)
        emit_audit_event(audit_event)

    async def _store_record(self, table: str, record_id: str, payload: dict[str, Any]) -> None:
        if not self.db_service:
            return
        await self.db_service.store(table, record_id, payload)

    # ------------------------------------------------------------------
    # Event publishing
    # ------------------------------------------------------------------

    async def _publish_event(self, topic: str, payload: dict[str, Any]) -> None:
        if self.event_bus:
            await self.event_bus.publish(topic, payload)
        await self._publish_service_bus_message(topic, payload)
        await self._publish_event_grid_event(topic, payload)

    async def _publish_service_bus_message(self, topic: str, payload: dict[str, Any]) -> None:
        if not self.service_bus_client or not ServiceBusMessage:
            return
        message = ServiceBusMessage(json.dumps({"topic": topic, "payload": payload, "published_at": datetime.now(timezone.utc).isoformat()}, default=str))
        if self.service_bus_topic_sender:
            try:  # pragma: no cover - network dependent
                async with self.service_bus_topic_sender:
                    await self.service_bus_topic_sender.send_messages(message)
            except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
                self.logger.warning("service_bus_topic_publish_failed", extra={"error": str(exc)})
        if self.service_bus_queue_sender:
            try:  # pragma: no cover - network dependent
                async with self.service_bus_queue_sender:
                    await self.service_bus_queue_sender.send_messages(message)
            except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
                self.logger.warning("service_bus_queue_publish_failed", extra={"error": str(exc)})

    async def _publish_event_grid_event(self, topic: str, payload: dict[str, Any]) -> None:
        if not self.event_grid_client:
            return
        event = {
            "id": str(uuid.uuid4()), "subject": f"data-sync/{topic}", "eventType": topic,
            "eventTime": datetime.now(timezone.utc).isoformat() + "Z", "dataVersion": "1.0", "data": payload,
        }
        try:  # pragma: no cover - network dependent
            await self.event_grid_client.send([event])
        except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
            self.logger.warning("event_grid_publish_failed", extra={"error": str(exc)})

    async def _publish_sync_event(self, tenant_id: str, entity_type: str, master_id: str, source_system: str, payload: dict[str, Any]) -> None:
        self.logger.info("sync_event_published", extra={"tenant_id": tenant_id, "entity_type": entity_type, "master_id": master_id, "source_system": source_system})
        if not self.sync_event_webhook_url:
            return
        webhook_payload = {"tenant_id": tenant_id, "entity_type": entity_type, "master_id": master_id, "source_system": source_system, "payload": payload, "timestamp": datetime.now(timezone.utc).isoformat()}
        try:
            async with httpx.AsyncClient(timeout=self.sync_event_webhook_timeout) as client:
                await client.post(self.sync_event_webhook_url, json=webhook_payload)
        except httpx.RequestError:
            self.logger.warning("sync_event_webhook_unavailable", extra={"url": self.sync_event_webhook_url})

    async def _emit_lineage_event(self, tenant_id: str, entity_type: str, master_id: str, source_system: str, payload: dict[str, Any]) -> None:
        base_url = self._get_setting("DATA_LINEAGE_SERVICE_URL")
        if not base_url:
            return
        token = self._get_setting("DATA_LINEAGE_SERVICE_TOKEN")
        headers = {"X-Tenant-ID": tenant_id}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        lineage_payload = {
            "tenant_id": tenant_id, "connector": "data-sync-agent",
            "source": {"system": source_system, "object": entity_type, "record_id": payload.get("id")},
            "target": {"schema": entity_type, "record_id": master_id},
            "transformations": [f"{source_system}.{entity_type} -> {entity_type}"],
            "entity_type": entity_type, "entity_payload": payload, "classification": "internal",
        }
        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
                await client.post("/lineage/events", json=lineage_payload, headers=headers)
        except httpx.RequestError:
            self.logger.warning("lineage_service_unavailable", extra={"base_url": base_url})

    # ------------------------------------------------------------------
    # ETL / Azure integration
    # ------------------------------------------------------------------

    async def _run_etl_workflows(self, tenant_id: str, entity_type: str, payload: dict[str, Any], source_system: str) -> None:
        await self._trigger_data_factory_pipelines(tenant_id=tenant_id, entity_type=entity_type, payload=payload, source_system=source_system)
        await self._invoke_transformation_functions(tenant_id=tenant_id, entity_type=entity_type, payload=payload, source_system=source_system)

    async def _trigger_data_factory_pipelines(self, tenant_id: str, entity_type: str, payload: dict[str, Any], source_system: str) -> None:
        if not self.data_factory_client:
            return
        if not self.data_factory_resource_group or not self.data_factory_name:
            return
        for pipeline_name in self.data_factory_pipelines:
            try:  # pragma: no cover - network dependent
                self.data_factory_client.pipelines.create_run(
                    resource_group_name=self.data_factory_resource_group, factory_name=self.data_factory_name,
                    pipeline_name=pipeline_name,
                    parameters={"tenant_id": tenant_id, "entity_type": entity_type, "source_system": source_system, "payload": payload},
                )
            except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
                self.logger.warning("data_factory_pipeline_trigger_failed", extra={"pipeline": pipeline_name, "error": str(exc)})

    async def _invoke_transformation_functions(self, tenant_id: str, entity_type: str, payload: dict[str, Any], source_system: str) -> None:
        if not self.function_names or not self.function_base_url:
            return
        headers = {"Content-Type": "application/json"}
        if self.function_key:
            headers["x-functions-key"] = self.function_key
        for function_name in self.function_names:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        f"{self.function_base_url.rstrip('/')}/api/{function_name}",
                        json={"tenant_id": tenant_id, "entity_type": entity_type, "source_system": source_system, "payload": payload},
                        headers=headers,
                    )
            except httpx.RequestError:
                self.logger.warning("function_invocation_failed", extra={"function": function_name})

    async def _ingest_latency_metric(self, record: dict[str, Any]) -> None:
        if not self.log_analytics_client:
            return
        rule_id = self._get_setting("LOG_ANALYTICS_RULE_ID")
        stream_name = self._get_setting("LOG_ANALYTICS_STREAM_NAME", "DataSyncLatency") or "DataSyncLatency"
        if not rule_id:
            return
        try:
            await self.log_analytics_client.upload(rule_id=rule_id, stream_name=stream_name, logs=[record])
        except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
            self.logger.warning("log_analytics_upload_failed", extra={"error": str(exc)})

    async def _ingest_quality_metric(self, record: dict[str, Any]) -> None:
        if not self.log_analytics_client:
            return
        rule_id = self._get_setting("LOG_ANALYTICS_RULE_ID")
        stream_name = self._get_setting("LOG_ANALYTICS_QUALITY_STREAM_NAME", "DataQualityMetrics") or "DataQualityMetrics"
        if not rule_id:
            return
        try:
            await self.log_analytics_client.upload(rule_id=rule_id, stream_name=stream_name, logs=[record])
        except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
            self.logger.warning("log_analytics_quality_upload_failed", extra={"error": str(exc)})

    # ------------------------------------------------------------------
    # Config loaders
    # ------------------------------------------------------------------

    def _load_validation_rules(self) -> dict[str, list[dict[str, Any]]]:
        rules_path = (
            Path(self.config.get("validation_rules_path", "ops/config/agents/data-synchronisation-agent/validation_rules.yaml"))
            if self.config else Path("ops/config/agents/data-synchronisation-agent/validation_rules.yaml")
        )
        if not rules_path.exists():
            return {}
        try:
            with rules_path.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
        except (OSError, yaml.YAMLError) as exc:
            self.logger.warning("validation_rules_load_failed", extra={"error": str(exc)})
            return {}
        return {key: value if isinstance(value, list) else [] for key, value in payload.items()}

    def _load_quality_thresholds(self) -> dict[str, float | dict[str, float]]:
        thresholds_path = (
            Path(self.config.get("quality_thresholds_path", "ops/config/agents/data-synchronisation-agent/quality_thresholds.yaml"))
            if self.config else Path("ops/config/agents/data-synchronisation-agent/quality_thresholds.yaml")
        )
        if not thresholds_path.exists():
            return {}
        try:
            with thresholds_path.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
        except (OSError, yaml.YAMLError) as exc:
            self.logger.warning("quality_thresholds_load_failed", extra={"error": str(exc)})
            return {}
        thresholds: dict[str, float | dict[str, float]] = {}
        for key, value in payload.items():
            if isinstance(value, (int, float)):
                thresholds[key] = float(value)
            elif isinstance(value, dict):
                thresholds[key] = {metric: float(metric_value) for metric, metric_value in value.items() if isinstance(metric_value, (int, float))}
        return thresholds

    def _load_schema_registry(self) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
        registry_path = (
            Path(self.config.get("schema_registry_path", "ops/config/agents/data-synchronisation-agent/schema_registry.yaml"))
            if self.config else Path("ops/config/agents/data-synchronisation-agent/schema_registry.yaml")
        )
        if not registry_path.exists():
            return {}, {}
        try:
            with registry_path.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
        except (OSError, yaml.YAMLError) as exc:
            self.logger.warning("schema_registry_load_failed", extra={"error": str(exc)})
            return {}, {}
        registry: dict[str, dict[str, Any]] = {}
        versions: dict[str, list[dict[str, Any]]] = {}
        for entry in payload.get("entities", []):
            if not isinstance(entry, dict):
                continue
            entity_type = entry.get("name")
            schema = entry.get("schema")
            version = entry.get("version", "1.0")
            if entity_type and isinstance(schema, dict):
                registry[entity_type] = schema
                versions.setdefault(entity_type, []).append({"version": version, "schema": schema})
        return registry, versions

    def _load_mapping_rules(self) -> list[dict[str, Any]]:
        mapping_path = (
            Path(self.config.get("mapping_rules_path", "ops/config/agents/data-synchronisation-agent/mapping_rules.yaml"))
            if self.config else Path("ops/config/agents/data-synchronisation-agent/mapping_rules.yaml")
        )
        if not mapping_path.exists():
            return []
        try:
            with mapping_path.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
        except (OSError, yaml.YAMLError) as exc:
            self.logger.warning("mapping_rules_load_failed", extra={"error": str(exc)})
            return []
        mappings = payload.get("mappings", [])
        if not isinstance(mappings, list):
            return []
        return [entry for entry in mappings if isinstance(entry, dict)]

    def _load_pipeline_config(self) -> tuple[list[str], list[str]]:
        config_path = (
            Path(self.config.get("pipeline_config_path", "ops/config/agents/data-synchronisation-agent/pipelines.yaml"))
            if self.config else Path("ops/config/agents/data-synchronisation-agent/pipelines.yaml")
        )
        if not config_path.exists():
            return [], []
        try:
            with config_path.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
        except (OSError, yaml.YAMLError) as exc:
            self.logger.warning("pipeline_config_load_failed", extra={"error": str(exc)})
            return [], []
        pipelines = [entry.get("name") for entry in payload.get("pipelines", []) if isinstance(entry, dict) and entry.get("name")]
        functions = [entry.get("name") for entry in payload.get("functions", []) if isinstance(entry, dict) and entry.get("name")]
        return pipelines, functions

    # ------------------------------------------------------------------
    # Azure initialization
    # ------------------------------------------------------------------

    async def _initialize_key_vault_secrets(self) -> None:
        key_vault_url = self._get_setting("AZURE_KEY_VAULT_URL")
        if not key_vault_url or not DefaultAzureCredential or not SecretClient:
            return
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_url, credential=credential)
        secret_names = [
            "PLANVIEW_CLIENT_ID", "PLANVIEW_CLIENT_SECRET", "PLANVIEW_REFRESH_TOKEN", "PLANVIEW_INSTANCE_URL",
            "SAP_USERNAME", "SAP_PASSWORD", "SAP_URL",
            "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_INSTANCE_URL",
            "WORKDAY_CLIENT_ID", "WORKDAY_CLIENT_SECRET", "WORKDAY_REFRESH_TOKEN", "WORKDAY_API_URL",
        ]
        loaded_secrets: dict[str, str] = {}
        for secret_name in secret_names:
            if self._get_setting(secret_name):
                continue
            try:
                secret = client.get_secret(secret_name)
            except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
                self.logger.warning("keyvault_secret_unavailable", extra={"secret": secret_name, "error": str(exc)})
                continue
            if secret and secret.value:
                loaded_secrets[secret_name] = secret.value
        if loaded_secrets:
            self.secret_context.set_many(loaded_secrets)

    async def _initialize_connectors(self) -> None:
        _ensure_connector_paths()
        try:
            from azure_devops_connector import AzureDevOpsConnector
            from base_connector import ConnectorCategory, ConnectorConfig
            from jira_connector import JiraConnector
            from planview_connector import PlanviewConnector
            from sap_connector import SapConnector
            from smartsheet_connector import SmartsheetConnector
            from workday_connector import WorkdayConnector
        except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:
            self.logger.warning("connector_import_failed", extra={"error": str(exc)})
            return

        self.connectors: dict[str, Any] = {}
        self._sync_business_metrics = build_business_workflow_metrics("data-sync-agent", "connector_sync")
        for connector_spec in [
            ("planview", "Planview", "PPM", "PLANVIEW_INSTANCE_URL", PlanviewConnector),
            ("sap", "SAP", "ERP", "SAP_URL", SapConnector),
            ("jira", "Jira", "PM", "JIRA_INSTANCE_URL", JiraConnector),
            ("workday", "Workday", "HRIS", "WORKDAY_API_URL", WorkdayConnector),
            ("smartsheet", "Smartsheet", "PM", "SMARTSHEET_API_URL", SmartsheetConnector),
            ("azure_devops", "Azure DevOps", "PM", "AZURE_DEVOPS_ORG_URL", AzureDevOpsConnector),
        ]:
            cid, cname, cat_name, url_key, cls = connector_spec
            try:
                cat = getattr(ConnectorCategory, cat_name)
                cfg = ConnectorConfig(connector_id=cid, name=cname, category=cat, instance_url=self._get_setting(url_key, "") or "")
                self.connectors[cid] = cls(cfg)
            except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:
                self.logger.warning(f"{cid}_connector_failed", extra={"error": str(exc)})

    async def _initialize_service_bus(self) -> None:
        if self.config and self.config.get("event_bus"):
            self.event_bus = self.config["event_bus"]
        connection_string = self._get_setting("AZURE_SERVICE_BUS_CONNECTION_STRING")
        if not connection_string:
            return
        self.event_bus = ServiceBusEventBus(connection_string=connection_string, topic_name=self.service_bus_topic_name)
        if ServiceBusClient is None:
            return
        self.service_bus_client = ServiceBusClient.from_connection_string(connection_string)
        try:
            self.service_bus_queue_sender = self.service_bus_client.get_queue_sender(queue_name=self.service_bus_queue_name)
            self.service_bus_topic_sender = self.service_bus_client.get_topic_sender(topic_name=self.service_bus_topic_name)
        except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
            self.logger.warning("service_bus_sender_unavailable", extra={"error": str(exc)})

    async def _initialize_event_grid(self) -> None:
        endpoint = self._get_setting("EVENT_GRID_ENDPOINT")
        key = self._get_setting("EVENT_GRID_KEY")
        if not endpoint or not key or not EventGridPublisherClient or not AzureKeyCredential:
            return
        self.event_grid_client = EventGridPublisherClient(endpoint, AzureKeyCredential(key))

    async def _initialize_datastores(self) -> None:
        sql_connection_string = self._get_setting("SQL_CONNECTION_STRING")
        if sql_connection_string and create_engine:
            self.sql_engine = create_engine(sql_connection_string)
        cosmos_endpoint = self._get_setting("COSMOS_ENDPOINT")
        cosmos_key = self._get_setting("COSMOS_KEY")
        if cosmos_endpoint and cosmos_key and CosmosClient:
            self.cosmos_client = CosmosClient(cosmos_endpoint, credential=cosmos_key)

    async def _initialize_data_factory(self) -> None:
        if not DataFactoryManagementClient or not DefaultAzureCredential:
            return
        subscription_id = self._get_setting("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            return
        credential = DefaultAzureCredential()
        self.data_factory_client = DataFactoryManagementClient(credential, subscription_id)
        resource_group = self.data_factory_resource_group
        factory_name = self.data_factory_name
        if resource_group and factory_name and self.data_factory_pipelines:
            for pipeline_name in self.data_factory_pipelines:
                try:  # pragma: no cover - network dependent
                    self.data_factory_client.pipelines.get(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name)
                except (ConnectionError, TimeoutError, ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:  # pragma: no cover - network dependent
                    self.logger.warning("data_factory_pipeline_unavailable", extra={"pipeline": pipeline_name, "error": str(exc)})

    async def _initialize_functions(self) -> None:
        if not azure_functions:
            return
        self.function_app = azure_functions.FunctionApp()
        if not self.function_names:
            return
        if not self.function_base_url:
            self.logger.info("function_base_url_missing", extra={"configured_functions": self.function_names})

    async def _initialize_monitoring(self) -> None:
        endpoint = self._get_setting("LOG_ANALYTICS_ENDPOINT")
        if not endpoint or not LogsIngestionClient or not DefaultAzureCredential:
            return
        credential = DefaultAzureCredential()
        self.log_analytics_client = LogsIngestionClient(endpoint=endpoint, credential=credential)
