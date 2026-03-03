"""
Compliance & Regulatory Agent

Purpose:
Ensures projects, programs and portfolios adhere to internal policies, external regulations
and industry standards. Manages compliance requirements, monitors adherence, and facilitates
audits and evidence collection.

Specification: agents/delivery-management/compliance-governance-agent/README.md
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from observability.tracing import get_trace_id

import requests
from tools.runtime_paths import bootstrap_runtime_paths

bootstrap_runtime_paths()

from llm.client import LLMGateway  # noqa: E402

from agents.common.connector_integration import (  # noqa: E402
    DatabaseStorageService,
    DocumentManagementService,
    DocumentMetadata,
    GRCIntegrationService,
    NotificationService,
)
from agents.runtime import BaseAgent, ServiceBusEventBus, get_event_bus  # noqa: E402
from agents.runtime.src.audit import build_audit_event, emit_audit_event  # noqa: E402
from agents.runtime.src.policy import (  # noqa: E402
    evaluate_compliance_controls,
    evaluate_policy_bundle,
    load_default_policy_bundle,
)
from agents.runtime.src.state_store import TenantStateStore  # noqa: E402

# -- Extracted modules -------------------------------------------------------
from compliance_models import ComplianceRuleEngine  # noqa: E402
from compliance_utils import (  # noqa: E402
    extract_effective_date,
    extract_obligations_from_text,
)
from actions import (  # noqa: E402
    handle_add_regulation,
    handle_assess_compliance,
    handle_conduct_audit,
    handle_define_control,
    handle_generate_compliance_report,
    handle_get_compliance_dashboard,
    handle_get_evidence,
    handle_get_report,
    handle_list_evidence,
    handle_list_reports,
    handle_manage_policy,
    handle_map_controls_to_project,
    handle_monitor_regulations,
    handle_monitor_regulatory_changes,
    handle_prepare_audit,
    handle_upload_evidence,
    handle_verify_release_compliance,
)

# Re-export models so existing ``from compliance_regulatory_agent import …`` still works.
from compliance_models import (  # noqa: E402, F401
    ComplianceRuleEngine as ComplianceRuleEngine,
    ControlRequirement as ControlRequirement,
    EvidenceSnapshot as EvidenceSnapshot,
    RegulatoryFramework as RegulatoryFramework,
)


class ComplianceRegulatoryAgent(BaseAgent):
    """
    Compliance & Regulatory Agent - Ensures adherence to policies and regulations.

    Key Capabilities:
    - Regulatory requirement management
    - Control library and mapping
    - Compliance assessment and gap analysis
    - Control assignment and testing
    - Policy management and versioning
    - Audit preparation and management
    - Compliance dashboards and reporting
    - Regulatory change monitoring
    """

    def __init__(self, agent_id: str = "compliance-governance-agent", config: dict[str, Any] | None = None):
        super().__init__(agent_id, config)

        # Configuration parameters
        self.regulations = (
            config.get(
                "regulations", ["Privacy Act 1988", "APRA CPS 234", "ISO 27001", "ASD ISM", "PSPF"]
            )
            if config
            else ["Privacy Act 1988", "APRA CPS 234", "ISO 27001", "ASD ISM", "PSPF"]
        )
        self.enable_regulatory_monitoring = (
            config.get("enable_regulatory_monitoring", False) if config else False
        )
        self.regulatory_search_keywords = (
            config.get(
                "regulatory_search_keywords",
                ["law", "regulation", "standard", "guidance", "compliance update"],
            )
            if config
            else ["law", "regulation", "standard", "guidance", "compliance update"]
        )
        self.regulatory_search_result_limit = (
            int(config.get("regulatory_search_result_limit", 5)) if config else 5
        )

        self.control_test_frequencies = (
            config.get(
                "control_test_frequencies",
                {
                    "critical": "monthly",
                    "high": "quarterly",
                    "medium": "semi-annually",
                    "low": "annually",
                },
            )
            if config
            else {
                "critical": "monthly",
                "high": "quarterly",
                "medium": "semi-annually",
                "low": "annually",
            }
        )

        evidence_store_path = (
            Path(config.get("evidence_store_path", "data/compliance_evidence.json"))
            if config
            else Path("data/compliance_evidence.json")
        )
        self.evidence_store = TenantStateStore(evidence_store_path)

        self.event_bus = config.get("event_bus") if config else None
        if self.event_bus is None:
            service_bus_connection = (
                config.get("service_bus_connection_string")
                if config
                else os.getenv("SERVICE_BUS_CONNECTION_STRING")
            )
            if service_bus_connection:
                try:
                    self.event_bus = ServiceBusEventBus(connection_string=service_bus_connection)
                except RuntimeError as exc:
                    self.logger.warning(
                        "Service bus event bus unavailable, falling back to in-memory",
                        extra={"error": str(exc)},
                    )
                    self.event_bus = get_event_bus()
            else:
                self.event_bus = get_event_bus()

        self.notification_service = NotificationService(
            config.get("notifications") if config else None
        )
        self.agent_clients = config.get("agent_clients", {}) if config else {}
        self.rule_engine = ComplianceRuleEngine()

        # Data stores (will be replaced with database)
        self.regulation_library: dict[str, Any] = {}
        self.control_registry: dict[str, Any] = {}
        self.compliance_mappings: dict[str, Any] = {}
        self.policies: dict[str, Any] = {}
        self.audits: dict[str, Any] = {}
        self.evidence: dict[str, Any] = {}
        self.regulatory_changes: dict[str, Any] = {}
        self.control_embeddings: dict[str, dict[str, float]] = {}
        self.compliance_reports: dict[str, Any] = {}
        self.compliance_alerts: list[dict[str, Any]] = []
        self.compliance_schemas: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Initialize database connections, GRC integrations, and AI models."""
        await super().initialize()
        self.logger.info("Initializing Compliance & Regulatory Agent...")

        doc_config = self.config.get("document_management", {}) if self.config else {}
        self.document_service = DocumentManagementService(doc_config)
        self.logger.info("Document Management Service initialized")

        grc_config = self.config.get("grc_integration", {}) if self.config else {}
        self.grc_service = GRCIntegrationService(grc_config)
        self.logger.info("GRC Integration Service initialized")

        db_config = self.config.get("database_storage", {}) if self.config else {}
        self.db_service = DatabaseStorageService(db_config)
        self.logger.info("Database Storage Service initialized")

        await self._seed_regulatory_frameworks()
        await self._define_compliance_schemas()

        if self.event_bus and hasattr(self.event_bus, "subscribe"):
            for topic in [
                "release.deployed",
                "deployment.completed",
                "config.changed",
                "quality.test.completed",
                "risk.updated",
                "security.alert",
                "incident.created",
                "change.requested",
            ]:
                self.event_bus.subscribe(
                    topic, self._handle_compliance_event  # type: ignore[arg-type]
                )

        self.logger.info("Compliance & Regulatory Agent initialized")

    async def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data based on the requested action."""
        action = input_data.get("action", "")
        if not action:
            self.logger.warning("No action specified")
            return False

        valid_actions = [
            "add_regulation",
            "define_control",
            "map_controls_to_project",
            "assess_compliance",
            "test_control",
            "manage_policy",
            "prepare_audit",
            "conduct_audit",
            "upload_evidence",
            "monitor_regulatory_changes",
            "get_compliance_dashboard",
            "generate_compliance_report",
            "verify_release_compliance",
            "list_evidence",
            "get_evidence",
            "list_reports",
            "get_report",
        ]

        if action not in valid_actions:
            self.logger.warning("Invalid action: %s", action)
            return False

        if action == "define_control":
            control_data = input_data.get("control", {})
            required_fields = ["description", "regulation", "owner"]
            for field in required_fields:
                if field not in control_data:
                    self.logger.warning("Missing required field: %s", field)
                    return False

        return True

    # ------------------------------------------------------------------
    # Process dispatcher
    # ------------------------------------------------------------------

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process compliance and regulatory requests.

        Delegates to action-specific handlers in the ``actions`` package.
        """
        action = input_data.get("action", "get_compliance_dashboard")
        context = input_data.get("context", {})
        tenant_id = context.get("tenant_id") or input_data.get("tenant_id") or "unknown"
        correlation_id = (
            context.get("correlation_id") or input_data.get("correlation_id") or str(uuid.uuid4())
        )

        compliance_decision = evaluate_compliance_controls(
            {
                "personal_data": input_data.get("personal_data", {}),
                "consent": input_data.get("consent", {}),
            }
        )
        if compliance_decision.decision == "deny":
            emit_audit_event(
                build_audit_event(
                    tenant_id=tenant_id,
                    action="compliance.data_processing.denied",
                    outcome="denied",
                    actor_id=self.agent_id,
                    actor_type="service",
                    actor_roles=[],
                    resource_id=input_data.get("project_id") or "unknown",
                    resource_type="compliance_processing",
                    metadata={"reasons": list(compliance_decision.reasons)},
                    legal_basis="consent",
                    retention_period="P3Y",
                    trace_id=get_trace_id(),
                    correlation_id=correlation_id,
                )
            )
            return {
                "status": "error",
                "error": "Consent is required before processing personal data.",
                "reasons": list(compliance_decision.reasons),
            }

        input_data["personal_data"] = compliance_decision.sanitized_payload.get("personal_data", {})
        emit_audit_event(
            build_audit_event(
                tenant_id=tenant_id,
                action="compliance.data_processing.allowed",
                outcome="success",
                actor_id=self.agent_id,
                actor_type="service",
                actor_roles=[],
                resource_id=input_data.get("project_id") or "unknown",
                resource_type="compliance_processing",
                metadata={
                    "masked_fields": list(compliance_decision.masked_fields),
                    "reasons": list(compliance_decision.reasons),
                },
                legal_basis="consent",
                retention_period="P3Y",
                trace_id=get_trace_id(),
                correlation_id=correlation_id,
            )
        )

        if action == "add_regulation":
            return await handle_add_regulation(self, input_data.get("regulation", {}))

        elif action == "define_control":
            return await handle_define_control(self, input_data.get("control", {}))

        elif action == "map_controls_to_project":
            return await handle_map_controls_to_project(
                self,
                input_data.get("project_id"),  # type: ignore
                input_data.get("mapping", {}),
                tenant_id=tenant_id,
                correlation_id=correlation_id,
            )

        elif action == "assess_compliance":
            return await handle_assess_compliance(
                self, input_data.get("project_id"), input_data.get("assessment", {})  # type: ignore
            )

        elif action == "test_control":
            from actions.test_control import handle_test_control

            return await handle_test_control(
                self, input_data.get("control_id"), input_data.get("test", {})  # type: ignore
            )

        elif action == "manage_policy":
            return await handle_manage_policy(self, input_data.get("policy", {}))

        elif action == "prepare_audit":
            return await handle_prepare_audit(self, input_data.get("audit", {}))

        elif action == "conduct_audit":
            return await handle_conduct_audit(self, input_data.get("audit_id"))  # type: ignore

        elif action == "upload_evidence":
            return await handle_upload_evidence(
                self,
                input_data.get("control_id"),  # type: ignore
                input_data.get("evidence", {}),
                tenant_id=tenant_id,
                correlation_id=correlation_id,
            )

        elif action == "monitor_regulatory_changes":
            return await handle_monitor_regulatory_changes(
                self,
                domain=input_data.get("domain"),
                region=input_data.get("region"),
                tenant_id=tenant_id,
                correlation_id=correlation_id,
            )

        elif action == "get_compliance_dashboard":
            return await handle_get_compliance_dashboard(
                self,
                input_data.get("project_id"),
                input_data.get("portfolio_id"),
                domain=input_data.get("domain"),
                region=input_data.get("region"),
            )

        elif action == "generate_compliance_report":
            return await handle_generate_compliance_report(
                self, input_data.get("report_type", "summary"), input_data.get("filters", {})
            )

        elif action == "verify_release_compliance":
            return await handle_verify_release_compliance(
                self,
                input_data.get("release_id"),
                input_data.get("release", {}),
            )
        elif action == "list_evidence":
            return await handle_list_evidence(self, input_data.get("filters", {}))
        elif action == "get_evidence":
            return await handle_get_evidence(self, input_data.get("evidence_id"))
        elif action == "list_reports":
            return await handle_list_reports(self, input_data.get("filters", {}))
        elif action == "get_report":
            return await handle_get_report(self, input_data.get("report_id"))

        else:
            raise ValueError(f"Unknown action: {action}")

    # ------------------------------------------------------------------
    # Public API kept on the class for backward-compat
    # ------------------------------------------------------------------

    async def monitor_regulations(
        self,
        domain: str,
        region: str | None,
        *,
        llm_client: LLMGateway | None = None,
        result_limit: int | None = None,
    ) -> dict[str, Any]:
        """Monitor external sources for new or changing regulations."""
        return await handle_monitor_regulations(
            self, domain, region, llm_client=llm_client, result_limit=result_limit
        )

    # Thin wrapper so action modules can call ``agent._map_controls_to_project``
    async def _map_controls_to_project(
        self,
        project_id: str,
        mapping_data: dict[str, Any],
        *,
        tenant_id: str,
        correlation_id: str,
    ) -> dict[str, Any]:
        return await handle_map_controls_to_project(
            self, project_id, mapping_data, tenant_id=tenant_id, correlation_id=correlation_id
        )

    # ------------------------------------------------------------------
    # Shared internal helpers (used by multiple action modules)
    # ------------------------------------------------------------------

    async def _publish_event(self, topic: str, payload: dict[str, Any]) -> None:
        if not self.event_bus:
            return
        await self.event_bus.publish(topic, payload)

    async def _notify_stakeholders(self, *, subject: str, message: str) -> list[dict[str, Any]]:
        stakeholders = self.config.get("stakeholders", []) if self.config else []
        recipients = [
            s.get("email") for s in stakeholders if isinstance(s, dict) and s.get("email")
        ]
        if not recipients:
            recipients = [self.config.get("default_stakeholder_email", "compliance@example.com")]
        results = []
        for recipient in recipients:
            result = await self.notification_service.send_email(
                to=recipient, subject=subject, body=message, metadata={"category": "compliance"}
            )
            results.append(result)
        return results

    async def _create_stakeholder_tasks(
        self, updates: list[dict[str, Any]], tenant_id: str
    ) -> list[dict[str, Any]]:
        stakeholders = self.config.get("stakeholders", []) if self.config else []
        recipients = [
            s.get("email") for s in stakeholders if isinstance(s, dict) and s.get("email")
        ]
        if not recipients:
            recipients = [self.config.get("default_stakeholder_email", "compliance@example.com")]
        tasks = []
        for update in updates:
            task_id = f"TASK-{uuid.uuid4().hex[:8]}"
            task = {
                "task_id": task_id,
                "tenant_id": tenant_id,
                "title": f"Review regulatory update: {update.get('regulation', 'Update')}",
                "description": update.get("description"),
                "regulation": update.get("regulation"),
                "effective_date": update.get("effective_date"),
                "assigned_to": recipients,
                "status": "open",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_url": update.get("source_url"),
            }
            tasks.append(task)
            await self.db_service.store("compliance_tasks", task_id, task)
            await self._publish_event("compliance.task.created", task)
        return tasks

    async def _evaluate_control_mapping_policy(
        self,
        *,
        project_id: str,
        mapping: dict[str, Any],
        tenant_id: str,
        correlation_id: str,
    ) -> dict[str, Any]:
        policy_bundle = {
            "metadata": {
                "version": self.get_config("policy_version", "1.0.0"),
                "owner": self.get_config("policy_owner", self.agent_id),
                "name": mapping.get("mapping_id", project_id),
            },
            "project_id": project_id,
            "control_count": len(mapping.get("applicable_controls", [])),
            "regulation_count": len(mapping.get("applicable_regulations", [])),
        }
        decision = evaluate_policy_bundle(policy_bundle, load_default_policy_bundle())
        outcome = "denied" if decision.decision == "deny" else "success"
        audit_event = build_audit_event(
            tenant_id=tenant_id,
            action="compliance.control_mapping.policy.checked",
            outcome=outcome,
            actor_id=self.agent_id,
            actor_type="service",
            actor_roles=[],
            resource_id=project_id,
            resource_type="compliance_mapping",
            metadata={"decision": decision.decision, "reasons": decision.reasons},
            trace_id=get_trace_id(),
            correlation_id=correlation_id,
        )
        emit_audit_event(audit_event)
        return {"decision": decision.decision, "reasons": decision.reasons}

    async def _extract_regulation_metadata(self, regulation_data: dict[str, Any]) -> dict[str, Any]:
        text = regulation_data.get("text") or ""
        document_url = regulation_data.get("document_url")
        document_content = regulation_data.get("document_content")

        extracted_text = text
        metadata: dict[str, Any] = {}
        if document_url or document_content:
            document_result = await self._analyze_document_intelligence(
                document_url=document_url, document_content=document_content
            )
            extracted_text = document_result.get("content") or extracted_text
            metadata["document_intelligence"] = document_result

        text_analytics_result = await self._analyze_text_analytics(extracted_text)
        metadata["text_analytics"] = text_analytics_result

        obligations = extract_obligations_from_text(
            extracted_text, text_analytics_result.get("key_phrases", [])
        )
        effective_date = extract_effective_date(text_analytics_result.get("entities", []))

        return {"obligations": obligations, "effective_date": effective_date, "metadata": metadata}

    async def _analyze_text_analytics(self, text: str) -> dict[str, Any]:
        endpoint = self.config.get("text_analytics_endpoint") if self.config else None
        api_key = self.config.get("text_analytics_key") if self.config else None
        endpoint = endpoint or os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
        api_key = api_key or os.getenv("AZURE_TEXT_ANALYTICS_KEY")
        if not endpoint or not api_key or not text:
            return {"key_phrases": [], "entities": []}

        text_payload = {"documents": [{"id": "1", "language": "en", "text": text[:5000]}]}
        headers = {"Ocp-Apim-Subscription-Key": api_key, "Content-Type": "application/json"}

        async def _post(path: str) -> dict[str, Any]:
            response = await asyncio.to_thread(
                requests.post,
                f"{endpoint.rstrip('/')}/{path}",
                headers=headers,
                json=text_payload,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()

        try:
            key_phrases_response = await _post("text/analytics/v3.1/keyPhrases")
            entities_response = await _post("text/analytics/v3.1/entities/recognition/general")
        except requests.RequestException as exc:
            self.logger.warning("Text analytics failed", extra={"error": str(exc)})
            return {"key_phrases": [], "entities": []}

        key_phrases = (
            key_phrases_response.get("documents", [{}])[0].get("keyPhrases", [])
            if isinstance(key_phrases_response, dict)
            else []
        )
        entities = (
            entities_response.get("documents", [{}])[0].get("entities", [])
            if isinstance(entities_response, dict)
            else []
        )
        return {"key_phrases": key_phrases, "entities": entities}

    async def _analyze_document_intelligence(
        self,
        *,
        document_url: str | None,
        document_content: str | bytes | None,
    ) -> dict[str, Any]:
        endpoint = self.config.get("document_intelligence_endpoint") if self.config else None
        api_key = self.config.get("document_intelligence_key") if self.config else None
        endpoint = endpoint or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        api_key = api_key or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        if not endpoint or not api_key or (not document_url and not document_content):
            return {"content": ""}

        headers = {"Ocp-Apim-Subscription-Key": api_key}
        analyze_url = (
            f"{endpoint.rstrip('/')}/formrecognizer/documentModels/prebuilt-layout:analyze"
        )
        params = {"api-version": "2023-07-31"}

        if document_url:
            request_body = {"urlSource": document_url}
            headers["Content-Type"] = "application/json"
            response = await asyncio.to_thread(
                requests.post, analyze_url, params=params, headers=headers,
                json=request_body, timeout=15,
            )
        else:
            if isinstance(document_content, str):
                document_bytes = document_content.encode("utf-8")
            else:
                document_bytes = document_content
            headers["Content-Type"] = "application/octet-stream"
            response = await asyncio.to_thread(
                requests.post, analyze_url, params=params, headers=headers,
                data=document_bytes, timeout=15,
            )

        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            self.logger.warning("Document intelligence call failed", extra={"error": str(exc)})
            return {"content": ""}

        operation_location = response.headers.get("operation-location")
        if not operation_location:
            return {"content": ""}

        try:
            result_response = await asyncio.to_thread(
                requests.get, operation_location,
                headers={"Ocp-Apim-Subscription-Key": api_key}, timeout=15,
            )
            result_response.raise_for_status()
            result_payload = result_response.json()
        except (requests.RequestException, ValueError) as exc:
            self.logger.warning("Document intelligence result failed", extra={"error": str(exc)})
            return {"content": ""}

        content = result_payload.get("analyzeResult", {}).get("content", "")
        return {"content": content, "raw": result_payload}

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    async def _handle_compliance_event(self, event: dict[str, Any]) -> None:
        project_id = event.get("project_id")
        if not project_id:
            return
        assessment = await handle_assess_compliance(
            self,
            project_id,
            {
                "tenant_id": event.get("tenant_id", "unknown"),
                "correlation_id": event.get("correlation_id", str(uuid.uuid4())),
                "mapping": event.get("mapping", {}),
            },
        )
        if assessment.get("gaps"):
            recommendations = [
                {"control_id": gap.get("control_id"), "recommendation": gap.get("remediation")}
                for gap in assessment.get("gaps", [])
            ]
            alert = {
                "alert_id": f"ALERT-{uuid.uuid4().hex[:8]}",
                "project_id": project_id,
                "gaps": assessment.get("gaps", []),
                "compliance_score": assessment.get("compliance_score", 0),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "trigger": event.get("event_type") or event.get("type"),
                "recommendations": recommendations,
            }
            self.compliance_alerts.append(alert)
            await self.db_service.store("compliance_alerts", alert["alert_id"], alert)
            await self._publish_event("compliance.alert.raised", alert)

    # ------------------------------------------------------------------
    # Seed data & schema definitions
    # ------------------------------------------------------------------

    async def _seed_regulatory_frameworks(self) -> None:
        if self.regulation_library or self.control_registry:
            return
        if self.config and not self.config.get("seed_frameworks", True):
            return

        frameworks = {
            "REG-ISO-27001": {
                "name": "ISO 27001",
                "description": "Information security management system requirements.",
                "jurisdiction": ["global"],
                "industry": ["technology", "finance", "healthcare", "public"],
                "data_sensitivity": ["medium", "high"],
                "effective_date": "2022-10-25",
                "related_controls": [],
                "applicability_rules": {
                    "applies_to_all": True,
                    "jurisdiction_filter": ["global"],
                    "industry_filter": [],
                    "data_sensitivity_filter": ["medium", "high"],
                },
            },
            "REG-SOC-2": {
                "name": "SOC 2",
                "description": "Trust Services Criteria for service organizations.",
                "jurisdiction": ["global"],
                "industry": ["technology", "services", "saas"],
                "data_sensitivity": ["medium", "high"],
                "effective_date": "2017-05-01",
                "related_controls": [],
                "applicability_rules": {
                    "applies_to_all": False,
                    "jurisdiction_filter": [],
                    "industry_filter": ["technology", "services", "saas"],
                    "data_sensitivity_filter": ["medium", "high"],
                },
            },
            "REG-PRIVACY-ACT-AU": {
                "name": "Privacy Act 1988 (Cth)",
                "description": "Australian Privacy Act 1988 including the Australian Privacy Principles (APPs).",
                "jurisdiction": ["au"],
                "industry": [],
                "data_sensitivity": ["high"],
                "effective_date": "1988-12-21",
                "related_controls": [],
                "applicability_rules": {
                    "applies_to_all": False,
                    "jurisdiction_filter": ["au"],
                    "industry_filter": [],
                    "data_sensitivity_filter": ["high"],
                },
            },
        }

        controls = [
            {"control_id": "CTL-ISO-01", "description": "Maintain an information security policy approved by management.", "regulation": "REG-ISO-27001", "control_type": "preventive", "owner": "security", "requirements": ["implemented", "evidence"], "test_frequency": "annually"},
            {"control_id": "CTL-ISO-02", "description": "Perform regular risk assessments and document mitigations.", "regulation": "REG-ISO-27001", "control_type": "detective", "owner": "risk", "requirements": ["implemented", "risk_mitigation", "evidence"], "test_frequency": "quarterly"},
            {"control_id": "CTL-SOC2-01", "description": "Monitor system availability and incident response.", "regulation": "REG-SOC-2", "control_type": "detective", "owner": "operations", "requirements": ["implemented", "quality_tests", "evidence"], "test_frequency": "quarterly"},
            {"control_id": "CTL-SOC2-02", "description": "Maintain audit logs for changes and access.", "regulation": "REG-SOC-2", "control_type": "preventive", "owner": "security", "requirements": ["implemented", "audit_logs", "evidence"], "test_frequency": "monthly"},
            {"control_id": "CTL-PRIVACY-AU-01", "description": "Conduct privacy impact assessments for personal information under APP obligations.", "regulation": "REG-PRIVACY-ACT-AU", "control_type": "preventive", "owner": "privacy", "requirements": ["implemented", "data_privacy", "evidence"], "test_frequency": "annually"},
            {"control_id": "CTL-PRIVACY-AU-02", "description": "Ensure APP access and correction requests are tracked and fulfilled within statutory timelines.", "regulation": "REG-PRIVACY-ACT-AU", "control_type": "detective", "owner": "privacy", "requirements": ["implemented", "quality_tests", "evidence"], "test_frequency": "quarterly"},
        ]

        for regulation_id, regulation in frameworks.items():
            regulation["regulation_id"] = regulation_id
            regulation["created_at"] = datetime.now(timezone.utc).isoformat()
            self.regulation_library[regulation_id] = regulation
            await self.db_service.store("regulations", regulation_id, regulation)

        for control in controls:
            control_id = control["control_id"]
            control_payload = {
                **control,
                "evidence_requirements": control.get("evidence_requirements", []),
                "status": "Active",
                "last_test_date": None,
                "last_test_result": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self.control_registry[control_id] = control_payload
            regulation_id = control_payload.get("regulation")
            if regulation_id in self.regulation_library:
                self.regulation_library[regulation_id]["related_controls"].append(control_id)
            await self.db_service.store("controls", control_id, control_payload)

    async def _define_compliance_schemas(self) -> None:
        schemas = {
            "regulatory_frameworks": {"framework_id": "string", "name": "string", "description": "string", "jurisdiction": "list[string]", "industry": "list[string]", "data_sensitivity": "list[string]", "effective_date": "string", "applicability_rules": "json"},
            "control_requirements": {"control_id": "string", "regulation_id": "string", "description": "string", "owner": "string", "control_type": "string", "requirements": "list[string]", "evidence_requirements": "list[string]", "test_frequency": "string"},
            "control_mappings": {"mapping_id": "string", "project_id": "string", "industry": "string", "geography": "string", "data_sensitivity": "string", "control_ids": "list[string]", "created_at": "string"},
            "compliance_evidence": {"evidence_id": "string", "control_id": "string", "project_id": "string", "source_agent": "string", "metadata": "json", "created_at": "string"},
            "compliance_reports": {"report_id": "string", "report_type": "string", "framework": "string", "generated_at": "string", "report_url": "string"},
        }
        self.compliance_schemas = schemas
        for schema_id, schema in schemas.items():
            await self.db_service.store("compliance_schema", schema_id, schema)

    # ------------------------------------------------------------------
    # Cleanup & capabilities
    # ------------------------------------------------------------------

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self.logger.info("Cleaning up Compliance & Regulatory Agent...")
        self.logger.info("Compliance & Regulatory Agent cleanup complete")

    def get_capabilities(self) -> list[str]:
        """Return list of agent capabilities."""
        return [
            "regulation_management",
            "regulation_parsing",
            "control_definition",
            "control_library_management",
            "compliance_mapping",
            "compliance_assessment",
            "gap_analysis",
            "control_testing",
            "policy_management",
            "policy_versioning",
            "audit_preparation",
            "audit_management",
            "evidence_management",
            "regulatory_change_monitoring",
            "compliance_dashboards",
            "compliance_reporting",
            "automated_control_testing",
            "external_regulatory_monitoring",
            "compliance_alerting",
            "compliance_release_verification",
        ]
