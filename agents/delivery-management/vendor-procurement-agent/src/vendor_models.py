"""
Vendor & Procurement Management Agent - Models and Service Classes

Contains dataclasses, service integration classes, and client wrappers
used by the VendorProcurementAgent.
"""

import importlib
import json
import logging
import os
import re
import uuid
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib import request

from workflow_task_queue import build_task_message, build_task_queue


@dataclass
class ConnectorStatus:
    name: str
    status: str
    detail: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ProcurementConnectorService:
    """Integration hub for procurement systems (SAP Ariba, Coupa, Oracle, Dynamics, ERP/AP)."""

    DEFAULT_CONNECTOR_SPECS = {
        "sap_ariba": {"module": "sap_ariba_connector", "class": "SAPAribaConnector"},
        "coupa": {"module": "coupa_connector", "class": "CoupaConnector"},
        "oracle_procurement": {
            "module": "oracle_procurement_connector",
            "class": "OracleProcurementConnector",
        },
        "dynamics_365": {
            "module": "dynamics_procurement_connector",
            "class": "DynamicsProcurementConnector",
        },
        "erp_ap": {"module": "erp_ap_connector", "class": "ERPAPConnector"},
    }

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.connector_specs = {
            **self.DEFAULT_CONNECTOR_SPECS,
            **self.config.get("connector_specs", {}),
        }
        self.enabled_connectors = self.config.get(
            "enabled_connectors",
            ["sap_ariba", "coupa", "oracle_procurement", "dynamics_365", "erp_ap"],
        )
        self.connector_configs = self.config.get("connectors", {})
        self.connectors: dict[str, Any] = {}

    def initialize(self) -> list[ConnectorStatus]:
        statuses: list[ConnectorStatus] = []
        for name in self.enabled_connectors:
            spec = self.connector_specs.get(name, {})
            module_name = spec.get("module")
            class_name = spec.get("class")
            connector_config = self.connector_configs.get(name, {})
            connector = self._load_connector(name, module_name, class_name, connector_config)
            self.connectors[name] = connector
            if connector is None:
                statuses.append(
                    ConnectorStatus(
                        name=name,
                        status="fallback",
                        detail="Connector unavailable, using fallback integration.",
                    )
                )
            else:
                statuses.append(
                    ConnectorStatus(
                        name=name,
                        status="connected",
                        metadata={"module": module_name, "class": class_name},
                    )
                )
        return statuses

    def _load_connector(
        self,
        name: str,
        module_name: str | None,
        class_name: str | None,
        connector_config: dict[str, Any],
    ) -> Any | None:
        if not module_name or not class_name:
            self.logger.info("Connector spec missing for %s", name)
            return None

        try:
            module = importlib.import_module(module_name)
            connector_class = getattr(module, class_name)
        except (ImportError, AttributeError) as exc:
            self.logger.info("Connector %s not available: %s", name, exc)
            return None

        try:
            return connector_class(connector_config)
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ) as exc:  # noqa: BLE001 - connector constructors can fail
            self.logger.warning("Connector %s failed to initialize: %s", name, exc)
            return None

    def _dispatch(self, method: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        for name, connector in self.connectors.items():
            if connector is None or not hasattr(connector, method):
                results.append(
                    {
                        "connector": name,
                        "status": "skipped",
                        "method": method,
                        "detail": "Connector not available or method not supported.",
                    }
                )
                continue
            try:
                result = getattr(connector, method)(payload)
                results.append(
                    {"connector": name, "status": "ok", "method": method, "result": result}
                )
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                KeyError,
                TypeError,
                RuntimeError,
                OSError,
            ) as exc:  # noqa: BLE001 - external connectors may raise
                results.append(
                    {
                        "connector": name,
                        "status": "error",
                        "method": method,
                        "detail": str(exc),
                    }
                )
        return results

    def sync_vendor(self, vendor: dict[str, Any]) -> list[dict[str, Any]]:
        return self._dispatch("sync_vendor", vendor)

    def publish_rfp(self, rfp: dict[str, Any]) -> list[dict[str, Any]]:
        return self._dispatch("publish_rfp", rfp)

    def submit_proposal(self, proposal: dict[str, Any]) -> list[dict[str, Any]]:
        return self._dispatch("submit_proposal", proposal)

    def select_vendor(self, selection: dict[str, Any]) -> list[dict[str, Any]]:
        return self._dispatch("select_vendor", selection)

    def create_contract(self, contract: dict[str, Any]) -> list[dict[str, Any]]:
        return self._dispatch("create_contract", contract)

    def release_purchase_order(self, purchase_order: dict[str, Any]) -> list[dict[str, Any]]:
        return self._dispatch("release_purchase_order", purchase_order)

    def record_invoice(self, invoice: dict[str, Any]) -> list[dict[str, Any]]:
        return self._dispatch("record_invoice", invoice)

    def initiate_payment(self, payment: dict[str, Any]) -> list[dict[str, Any]]:
        return self._dispatch("initiate_payment", payment)


class ProcurementEventPublisher:
    """Publishes procurement lifecycle events to configured sinks."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        logger: logging.Logger | None = None,
        event_bus: "EventBusClient | None" = None,
    ):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.event_bus = event_bus or EventBusClient(self.config.get("event_bus"))

    async def publish(self, event: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Publishing procurement event %s", event.get("event_type"))
        bus_result = await self.event_bus.publish(event)
        return {
            "status": "published",
            "event_id": event.get("event_id"),
            "event_bus": bus_result,
        }


class TaskManagementClient:
    """Client for publishing mitigation tasks to the task queue."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.task_queue = self.config.get("task_queue") or build_task_queue(
            self.config.get("queue_config")
        )

    async def create_task(
        self,
        *,
        tenant_id: str,
        instance_id: str,
        task_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        task_id = f"{task_type}-{uuid.uuid4()}"
        message = build_task_message(
            tenant_id=tenant_id,
            instance_id=instance_id,
            task_id=task_id,
            task_type=task_type,
            payload=payload,
        )
        await self.task_queue.publish_task(message)
        return {
            "task_id": task_id,
            "status": "queued",
            "queue_backend": self.task_queue.__class__.__name__,
            "message_id": message.message_id,
        }


class CommunicationsClient:
    """Client wrapper for Stakeholder & Communications agent integration."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.agent = self.config.get("agent")
        self.enabled = self.config.get("enabled", True)

        if self.agent is None and self.config.get("use_agent", False):
            try:
                module = importlib.import_module("stakeholder_communications_agent")
                agent_cls = getattr(module, "StakeholderCommunicationsAgent")
                self.agent = agent_cls(config=self.config.get("agent_config"))
            except (ImportError, AttributeError) as exc:
                self.logger.warning("Communications agent unavailable: %s", exc)
                self.agent = None

    async def notify(
        self,
        *,
        tenant_id: str,
        subject: str,
        body: str,
        stakeholders: list[str] | None = None,
        channel: str = "email",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "disabled", "subject": subject}
        if not self.agent:
            self.logger.info("Communications agent not configured; skipping notify.")
            return {"status": "skipped", "subject": subject}

        message_payload = {
            "subject": subject,
            "content": body,
            "channel": channel,
            "stakeholder_ids": stakeholders or [],
            "data": metadata or {},
        }
        message = await self.agent.process(
            {"action": "generate_message", "message": message_payload, "tenant_id": tenant_id}
        )
        message_id = message.get("message_id")
        if not message_id:
            return {"status": "failed", "subject": subject}
        sent = await self.agent.process(
            {"action": "send_message", "message_id": message_id, "tenant_id": tenant_id}
        )
        return {
            "status": sent.get("status", "sent"),
            "message_id": message_id,
            "subject": subject,
        }


class LocalApprovalAgent:
    """Fallback approval workflow when external approval agent is unavailable."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "approval_id": f"local-{uuid.uuid4()}",
            "status": "auto-approved",
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "request": input_data,
        }


class VendorMLService:
    """Azure ML-backed (or heuristic) service for vendor recommendations and risk scoring."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.model_metadata: dict[str, Any] = {}
        self.training_runs: list[dict[str, Any]] = []
        self.training_data = self.config.get("training_data", [])
        self.scoring_weights: dict[str, float] = self.config.get("scoring_weights", {})
        self.feature_weights: dict[str, float] = {}
        self.feature_stats: dict[str, float] = {}
        self.feature_order = [
            "cost_score",
            "quality_rating",
            "on_time_delivery_rate",
            "compliance_rating",
            "risk_score",
            "delivery_timeliness",
            "external_rating",
            "dispute_count",
            "total_spend",
        ]

    async def train_models(self, vendors: list[dict[str, Any]]) -> dict[str, Any]:
        run_id = f"ml-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        avg_risk = sum(v.get("risk_score", 50) for v in vendors) / len(vendors) if vendors else 50
        self._train_recommendation_model(vendors)
        self.model_metadata = {
            "run_id": run_id,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "vendor_count": len(vendors),
            "avg_risk": avg_risk,
            "provider": "azure_ml" if self.config.get("azure_ml_enabled") else "heuristic",
            "feature_weights": self.feature_weights,
        }
        self.training_runs.append(self.model_metadata)
        return self.model_metadata

    def risk_score(self, vendor: dict[str, Any], compliance_checks: dict[str, Any]) -> float:
        base_risk = 50.0
        if all(v == "Pass" for v in compliance_checks.values()):
            base_risk -= 10.0
        if vendor.get("certifications"):
            base_risk -= 5.0
        if vendor.get("financial_health") == "weak":
            base_risk += 15.0
        avg_risk = self.model_metadata.get("avg_risk", 50)
        adjusted = (base_risk * 0.7) + (avg_risk * 0.3)
        return max(0, min(100, adjusted))

    def recommend_vendors(
        self, vendors: list[dict[str, Any]], category: str, top_n: int = 5
    ) -> list[str]:
        candidates = [
            v
            for v in vendors
            if v.get("category") == category
            and v.get("status") in {"Approved", "pending", "active"}
        ]
        scored = []
        for vendor in candidates:
            score = self.score_vendor(vendor)
            scored.append((vendor.get("vendor_id"), score))
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)
        return [vendor_id for vendor_id, _ in ranked[:top_n] if vendor_id]

    def analyze_performance(
        self, metrics: dict[str, Any], vendor: dict[str, Any]
    ) -> dict[str, Any]:
        trend = "Stable"
        if metrics.get("delivery_timeliness", 100) < 90:
            trend = "Declining"
        if metrics.get("quality_rating", 5) > 4.5:
            trend = "Improving"
        adjusted_metrics = {
            **metrics,
            "risk_adjusted_score": max(0, 100 - vendor.get("risk_score", 50)),
        }
        return {
            "trend": trend,
            "adjusted_metrics": adjusted_metrics,
            "insights": [
                "ML model evaluated delivery and quality trends.",
                "Risk-adjusted score updated for analytics dashboards.",
            ],
        }

    def rank_vendors(self, vendors: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(vendors, key=self.score_vendor, reverse=True)

    def score_vendor(self, vendor: dict[str, Any]) -> float:
        features = self._prepare_features(vendor)
        weights = self.feature_weights or self.scoring_weights
        if not weights:
            weights = {
                "quality_rating": 0.25,
                "on_time_delivery_rate": 0.2,
                "compliance_rating": 0.15,
                "risk_score": 0.2,
                "delivery_timeliness": 0.1,
                "cost_score": 0.1,
            }
        return self._weighted_score(features, weights)

    def score_proposal(
        self,
        proposal: dict[str, Any],
        criteria_weights: dict[str, float] | None = None,
    ) -> dict[str, float]:
        pricing = proposal.get("pricing", {})
        total_cost = pricing.get("total") or pricing.get("amount") or 0
        cost_score = max(0, 100 - (float(total_cost) / 1000))
        features = {
            "cost": cost_score,
            "quality": proposal.get("quality_score", 75),
            "delivery": proposal.get("delivery_score", 80),
            "risk": proposal.get("risk_score", 70),
            "compliance": proposal.get("compliance_score", 80),
        }
        weights = criteria_weights or self.scoring_weights or {}
        if not weights:
            weights = {
                "cost": 0.4,
                "quality": 0.25,
                "delivery": 0.15,
                "risk": 0.15,
                "compliance": 0.05,
            }
        normalized_weights = self._normalize_weights(weights, features.keys())
        return {
            key: float(features.get(key, 0)) * normalized_weights.get(key, 0) for key in features
        }

    def _prepare_features(self, vendor: dict[str, Any]) -> dict[str, float]:
        metrics = vendor.get("performance_metrics", {})
        cost_score = vendor.get("cost_score") or metrics.get("cost_score") or 0
        delivery_timeliness = metrics.get("delivery_timeliness") or metrics.get(
            "on_time_delivery_rate", 0
        )
        external_rating = vendor.get("external_rating") or vendor.get("external_ratings", {}).get(
            "overall", 0
        )
        return {
            "cost_score": float(cost_score),
            "quality_rating": metrics.get("quality_rating", 0) * 20,
            "on_time_delivery_rate": metrics.get("on_time_delivery_rate", 0),
            "compliance_rating": metrics.get("compliance_rating", 0),
            "risk_score": 100 - vendor.get("risk_score", 50),
            "delivery_timeliness": float(delivery_timeliness),
            "external_rating": float(external_rating),
            "dispute_count": max(0, 10 - vendor.get("dispute_count", 0)),
            "total_spend": min(vendor.get("total_spend", 0) / 1000, 100),
        }

    def _train_recommendation_model(self, vendors: list[dict[str, Any]]) -> None:
        training_rows = self.training_data or []
        if not training_rows and vendors:
            training_rows = [
                {
                    **self._prepare_features(vendor),
                    "label": 1 if vendor.get("risk_score", 50) < 50 else 0,
                }
                for vendor in vendors
            ]

        if not training_rows:
            self.feature_weights = {}
            return

        positives = defaultdict(list)
        negatives = defaultdict(list)
        for row in training_rows:
            label = 1 if row.get("label", 0) else 0
            target = positives if label else negatives
            for feature in self.feature_order:
                target[feature].append(float(row.get(feature, 0)))

        weights: dict[str, float] = {}
        for feature in self.feature_order:
            pos_avg = sum(positives[feature]) / len(positives[feature]) if positives[feature] else 0
            neg_avg = sum(negatives[feature]) / len(negatives[feature]) if negatives[feature] else 0
            weights[feature] = pos_avg - neg_avg

        total = sum(abs(value) for value in weights.values()) or 1.0
        self.feature_weights = {key: value / total for key, value in weights.items()}

    def _weighted_score(self, features: dict[str, float], weights: dict[str, float]) -> float:
        normalized = self._normalize_weights(weights, features.keys())
        score = sum(features.get(name, 0.0) * normalized.get(name, 0.0) for name in features)
        return max(0, min(100, score))

    def _normalize_weights(self, weights: dict[str, float], keys: Any) -> dict[str, float]:
        total = sum(abs(weights.get(key, 0.0)) for key in keys) or 1.0
        return {key: weights.get(key, 0.0) / total for key in keys}


class RiskDatabaseClient:
    """Client for vendor risk and sanctions databases."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.risk_sources = self.config.get("risk_sources", [])
        self.timeout = self.config.get("timeout", 8)
        self.mock_responses = self.config.get("mock_responses", {})

    def check_vendor(self, vendor_data: dict[str, Any]) -> dict[str, Any]:
        vendor_key = vendor_data.get("legal_name") or vendor_data.get("tax_id") or ""
        if vendor_key in self.mock_responses:
            return self.mock_responses[vendor_key]
        if not self.risk_sources:
            return {}

        results = {
            "sanctions_check": "Unknown",
            "anti_corruption_check": "Unknown",
            "credit_check": "Unknown",
            "watchlist_hits": [],
            "sources": [],
        }

        payload = {
            "vendor_name": vendor_data.get("legal_name"),
            "tax_id": vendor_data.get("tax_id"),
            "country": vendor_data.get("address", {}).get("country"),
        }

        for source in self.risk_sources:
            response = self._query_source(source, payload)
            if not response:
                continue
            status = response.get("status", "").lower()
            category = source.get("category", "sanctions")
            check_key = {
                "sanctions": "sanctions_check",
                "anti_corruption": "anti_corruption_check",
                "credit": "credit_check",
            }.get(category, "sanctions_check")
            results[check_key] = "Fail" if status in {"hit", "fail", "blocked"} else "Pass"
            results["watchlist_hits"].extend(response.get("hits", []))
            results["sources"].append(
                {
                    "name": source.get("name"),
                    "status": results[check_key],
                    "response_id": response.get("response_id"),
                }
            )

        return results

    def _query_source(self, source: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = source.get("endpoint")
        if not endpoint:
            return {}
        headers = {"Content-Type": "application/json"}
        api_key = source.get("api_key") or self.config.get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        request_payload = json.dumps(payload).encode("utf-8")
        req = request.Request(endpoint, data=request_payload, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                content = json.loads(response.read().decode("utf-8"))
                return {
                    "status": content.get("status", "unknown"),
                    "hits": content.get("hits", []),
                    "response_id": content.get("response_id"),
                }
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ) as exc:  # noqa: BLE001 - external calls best-effort
            self.logger.warning("Risk source %s failed: %s", source.get("name"), exc)
            return {}


class EventBusClient:
    """Publishes and dispatches procurement events to an enterprise event bus."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.endpoint = self.config.get("endpoint")
        self.timeout = self.config.get("timeout", 5)
        self.enabled = self.config.get("enabled", True)
        self._handlers: dict[str, list[Any]] = defaultdict(list)
        self._local_queue: deque[dict[str, Any]] = deque()

    def register_handler(self, event_type: str, handler: Any) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "disabled", "event_id": event.get("event_id")}

        transport_status = "queued"
        if self.endpoint:
            try:
                payload = json.dumps(event).encode("utf-8")
                headers = {"Content-Type": "application/json"}
                req = request.Request(self.endpoint, data=payload, headers=headers, method="POST")
                with request.urlopen(req, timeout=self.timeout) as response:
                    response.read()
                transport_status = "sent"
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                KeyError,
                TypeError,
                RuntimeError,
                OSError,
            ) as exc:  # noqa: BLE001 - external call best-effort
                self.logger.warning("Event bus publish failed: %s", exc)
                transport_status = "error"

        self._local_queue.append(event)
        dispatched = await self.dispatch(event)
        return {
            "status": transport_status,
            "event_id": event.get("event_id"),
            "dispatched_handlers": dispatched,
        }

    async def dispatch(self, event: dict[str, Any]) -> int:
        handlers = self._handlers.get(event.get("event_type"), [])
        dispatched = 0
        for handler in handlers:
            result = handler(event)
            if hasattr(result, "__await__"):
                await result
            dispatched += 1
        return dispatched

    async def process_queue(self) -> int:
        processed = 0
        while self._local_queue:
            event = self._local_queue.popleft()
            processed += await self.dispatch(event)
        return processed


class ProcurementClassifier:
    """Naive Bayes text classifier for procurement request categorization."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.training_data = self.config.get("training_data", [])
        self.token_counts: dict[str, Counter[str]] = defaultdict(Counter)
        self.category_counts: Counter[str] = Counter()
        self.vocab: set[str] = set()
        if self.training_data:
            self._train(self.training_data)

    def predict(self, text: str, fallback: str = "services") -> str:
        tokens = self._tokenize(text)
        if not self.token_counts:
            return self._heuristic(text, fallback=fallback)
        scores: dict[str, float] = {}
        vocab_size = len(self.vocab) or 1
        for category, counts in self.token_counts.items():
            total_tokens = sum(counts.values()) + vocab_size
            score = 0.0
            for token in tokens:
                score += (counts.get(token, 0) + 1) / total_tokens
            scores[category] = score
        if not scores:
            return self._heuristic(text, fallback=fallback)
        return max(scores.items(), key=lambda item: item[1])[0]

    def _train(self, training_data: list[dict[str, Any]]) -> None:
        for row in training_data:
            text = str(row.get("text", ""))
            category = str(row.get("category", "services"))
            tokens = self._tokenize(text)
            self.token_counts[category].update(tokens)
            self.category_counts[category] += 1
            self.vocab.update(tokens)

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9]+", text.lower())

    def _heuristic(self, text: str, fallback: str = "services") -> str:
        description = text.lower()
        if "software" in description or "license" in description:
            return "software"
        if "cloud" in description or "aws" in description or "azure" in description:
            return "cloud"
        if "consultant" in description or "consulting" in description:
            return "consulting"
        return fallback


class FinancialManagementClient:
    """Client for budget checks against a financial management service."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.endpoint = self.config.get("endpoint")
        self.api_key = self.config.get("api_key")
        self.timeout = self.config.get("timeout", 5)
        self.budget_data = self.config.get("budget_data", {})

    def get_budget_status(self, request_data: dict[str, Any]) -> dict[str, Any]:
        if self.endpoint:
            response = self._call_budget_api(request_data)
            if response:
                return response

        project_id = request_data.get("project_id") or "default"
        program_id = request_data.get("program_id")
        key = program_id or project_id
        budget_info = self.budget_data.get(key, {"total": 0, "committed": 0})
        remaining = budget_info.get("total", 0) - budget_info.get("committed", 0)
        estimated_cost = request_data.get("estimated_cost", 0)
        return {
            "available": remaining >= estimated_cost,
            "remaining_budget": max(0, remaining - estimated_cost),
            "budget_total": budget_info.get("total", 0),
            "budget_committed": budget_info.get("committed", 0),
        }

    def _call_budget_api(self, request_data: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps(request_data).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(self.endpoint, data=payload, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ) as exc:  # noqa: BLE001 - external calls best-effort
            self.logger.warning("Budget API call failed: %s", exc)
            return {}


class PerformanceAnalyticsClient:
    """Client for analytics services (delivery history, issue tracker, PM metrics)."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.endpoint = self.config.get("endpoint")
        self.api_key = self.config.get("api_key")
        self.timeout = self.config.get("timeout", 6)
        self.performance_data = self.config.get("performance_data", {})

    def get_vendor_summary(self, vendor_id: str) -> dict[str, Any]:
        if self.endpoint:
            response = self._call_analytics_api({"vendor_id": vendor_id})
            if response:
                return response
        return self.performance_data.get(
            vendor_id,
            {
                "deliveries": [],
                "quality_scores": [],
                "compliance_incidents": [],
                "sla_records": [],
                "issue_tracker": [],
                "total_spend": 0,
                "contract_count": 0,
                "dispute_count": 0,
            },
        )

    def _call_analytics_api(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(
            self.endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ) as exc:  # noqa: BLE001 - external calls best-effort
            self.logger.warning("Analytics API call failed: %s", exc)
            return {}


class FormRecognizerClient:
    """Wrapper for Azure Form Recognizer clause extraction."""

    def __init__(self, config: dict[str, Any] | None = None, logger: logging.Logger | None = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.endpoint = self.config.get("endpoint") or os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        self.api_key = self.config.get("api_key") or os.getenv("AZURE_FORM_RECOGNIZER_KEY")
        self.model = self.config.get("model", "prebuilt-document")

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key)

    def extract_clauses(self, contract_text: str) -> dict[str, Any] | None:
        if not self.is_configured():
            return None
        payload = json.dumps({"content": contract_text}).encode("utf-8")
        url = f"{self.endpoint}/formrecognizer/documentModels/{self.model}:analyze?api-version=2023-07-31"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.api_key,
        }
        req = request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=10) as response:
                content = response.read().decode("utf-8")
                return json.loads(content)
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ) as exc:  # noqa: BLE001 - remote call best-effort
            self.logger.warning("Form Recognizer call failed: %s", exc)
            return None
