"""
Utility classes and services for the Change & Configuration Management Agent.

Contains RepositoryIntegrationService, IaCChangeParser, ChangeWorkflowOrchestrator,
ChangeEventPublisher, DependencyGraphService, ChangeRequestClassifier, and
ApprovalFallbackAgent.
"""

from __future__ import annotations

import importlib.util
import json
import os
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import parse, request

from change_models import PullRequestSummary, RepositoryReference
from event_bus.service_bus import ServiceBusEventBus

from agents.common.connector_integration import (
    DatabaseStorageService,
)
from agents.common.integration_services import NaiveBayesTextClassifier


class RepositoryIntegrationService:
    def __init__(self, logger: Any) -> None:
        self.logger = logger

    def _headers(self, provider: str, extra: dict[str, str] | None = None) -> dict[str, str]:
        provider = provider.lower()
        if provider == "github":
            token = os.getenv("GITHUB_TOKEN")
            if token:
                headers = {"Authorization": f"token {token}"}
                if extra:
                    headers.update(extra)
                return headers
        if provider == "gitlab":
            token = os.getenv("GITLAB_TOKEN")
            if token:
                headers = {"PRIVATE-TOKEN": token}
                if extra:
                    headers.update(extra)
                return headers
        if provider in {"azure", "azure_repos", "azure_devops"}:
            token = os.getenv("AZURE_DEVOPS_TOKEN")
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                if extra:
                    headers.update(extra)
                return headers
        return {}

    def _request(
        self,
        method: str,
        url: str,
        provider: str,
        *,
        parse_json: bool = True,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        headers = self._headers(provider, extra=extra_headers)
        if not headers:
            self.logger.warning("No auth token configured for %s", provider)
            return {"status": "unauthenticated", "url": url}
        try:
            req = request.Request(url, method=method, headers=headers)
            with request.urlopen(req, timeout=10) as response:
                payload = response.read().decode("utf-8")
                if not parse_json:
                    return {"status": "ok", "data": payload}
                return {"status": "ok", "data": json.loads(payload)}
        except (OSError, json.JSONDecodeError) as exc:
            self.logger.warning("Repository request failed: %s", exc)
            return {"status": "error", "error": str(exc)}

    def fetch_repository_data(self, reference: RepositoryReference) -> dict[str, Any]:
        provider = reference.provider.lower()
        if provider == "github":
            url = f"https://api.github.com/repos/{reference.repo}"
        elif provider == "gitlab":
            project_id = parse.quote(reference.repo, safe="")
            url = f"https://gitlab.com/api/v4/projects/{project_id}"
        else:
            url = f"https://dev.azure.com/{reference.repo}/_apis/git/repositories?api-version=7.1"
        return self._request("GET", url, provider)

    def fetch_pull_request_status(self, reference: RepositoryReference) -> dict[str, Any]:
        if not reference.pull_request_id:
            return {"status": "missing_pr"}
        provider = reference.provider.lower()
        if provider == "github":
            url = f"https://api.github.com/repos/{reference.repo}/pulls/{reference.pull_request_id}"
        elif provider == "gitlab":
            project_id = parse.quote(reference.repo, safe="")
            url = (
                f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/"
                f"{reference.pull_request_id}"
            )
        else:
            url = (
                f"https://dev.azure.com/{reference.repo}/_apis/git/pullrequests/"
                f"{reference.pull_request_id}?api-version=7.1"
            )
        return self._request("GET", url, provider)

    def list_pull_requests(
        self, reference: RepositoryReference, state: str = "open"
    ) -> PullRequestSummary:
        provider = reference.provider.lower()
        if provider == "github":
            url = f"https://api.github.com/repos/{reference.repo}/pulls?state={state}"
        elif provider == "gitlab":
            project_id = parse.quote(reference.repo, safe="")
            url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests?state={state}"
        else:
            url = (
                f"https://dev.azure.com/{reference.repo}/_apis/git/pullrequests"
                f"?searchCriteria.status={state}&api-version=7.1"
            )
        response = self._request("GET", url, provider)
        data = response.get("data") if response.get("status") == "ok" else []
        if provider in {"azure", "azure_repos", "azure_devops"} and isinstance(data, dict):
            data = data.get("value", [])
        return PullRequestSummary(
            provider=provider, repo=reference.repo, status=response["status"], data=data
        )

    def fetch_pull_request_diff(self, reference: RepositoryReference) -> dict[str, Any]:
        if not reference.pull_request_id:
            return {"status": "missing_pr"}
        provider = reference.provider.lower()
        if provider == "github":
            url = f"https://api.github.com/repos/{reference.repo}/pulls/{reference.pull_request_id}"
            return self._request(
                "GET",
                url,
                provider,
                parse_json=False,
                extra_headers={"Accept": "application/vnd.github.v3.diff"},
            )
        if provider == "gitlab":
            project_id = parse.quote(reference.repo, safe="")
            url = (
                f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/"
                f"{reference.pull_request_id}/changes"
            )
            return self._request("GET", url, provider)
        url = (
            f"https://dev.azure.com/{reference.repo}/_apis/git/pullrequests/"
            f"{reference.pull_request_id}/changes?api-version=7.1"
        )
        return self._request("GET", url, provider)

    def fetch_commit_diff(self, reference: RepositoryReference) -> dict[str, Any]:
        if not reference.commit_id:
            return {"status": "missing_commit"}
        provider = reference.provider.lower()
        if provider == "github":
            url = f"https://api.github.com/repos/{reference.repo}/commits/{reference.commit_id}"
        elif provider == "gitlab":
            project_id = parse.quote(reference.repo, safe="")
            url = (
                f"https://gitlab.com/api/v4/projects/{project_id}/repository/commits/"
                f"{reference.commit_id}"
            )
        else:
            url = (
                f"https://dev.azure.com/{reference.repo}/_apis/git/repositories/"
                f"commits/{reference.commit_id}?api-version=7.1"
            )
        return self._request("GET", url, provider)


class IaCChangeParser:
    def __init__(self, logger: Any) -> None:
        self.logger = logger

    def parse_files(self, file_paths: Iterable[Path]) -> list[dict[str, Any]]:
        resources: list[dict[str, Any]] = []
        for file_path in file_paths:
            if not file_path.exists():
                continue
            if file_path.suffix in {".tf", ".tfvars"}:
                resources.extend(self._parse_terraform(file_path))
            elif file_path.suffix in {".json"}:
                resources.extend(self._parse_arm(file_path))
            elif file_path.suffix in {".bicep"}:
                resources.extend(self._parse_bicep(file_path))
        return resources

    def parse_repository(self, repo_root: Path) -> list[dict[str, Any]]:
        if not repo_root.exists():
            return []
        candidate_files: list[Path] = []
        for extension in ("*.tf", "*.tfvars", "*.json", "*.bicep"):
            candidate_files.extend(repo_root.rglob(extension))
        return self.parse_files(candidate_files)

    def _parse_terraform(self, file_path: Path) -> list[dict[str, Any]]:
        resources: list[dict[str, Any]] = []
        spec = importlib.util.find_spec("terraform_config_inspect")
        if spec:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            tf_module = module.Module.load(str(file_path.parent))
            for resource_type, blocks in tf_module.resources.items():
                for resource_name in blocks:
                    resources.append(
                        {
                            "resource_type": resource_type,
                            "resource_name": resource_name,
                            "source": str(file_path),
                        }
                    )
            return resources

        content = file_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("resource "):
                parts = line.replace("resource", "").replace('"', "").split()
                if len(parts) >= 2:
                    resources.append(
                        {
                            "resource_type": parts[0],
                            "resource_name": parts[1],
                            "source": str(file_path),
                        }
                    )
        return resources

    def _parse_arm(self, file_path: Path) -> list[dict[str, Any]]:
        resources: list[dict[str, Any]] = []
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return resources
        for resource in payload.get("resources", []):
            resources.append(
                {
                    "resource_type": resource.get("type"),
                    "resource_name": resource.get("name"),
                    "source": str(file_path),
                }
            )
        return resources

    def _parse_bicep(self, file_path: Path) -> list[dict[str, Any]]:
        resources: list[dict[str, Any]] = []
        content = file_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("resource "):
                parts = line.replace("resource", "").replace("'", "").replace('"', "").split()
                if len(parts) >= 2:
                    resources.append(
                        {
                            "resource_type": parts[1],
                            "resource_name": parts[0],
                            "source": str(file_path),
                        }
                    )
        return resources


class ChangeWorkflowOrchestrator:
    def __init__(
        self,
        db_service: DatabaseStorageService,
        orchestrator: str,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.db_service = db_service
        self.orchestrator = orchestrator
        self.config = config or {}

    def _orchestrator_endpoint(self) -> str | None:
        if self.orchestrator == "durable_functions":
            return self.config.get("durable_functions_url") or os.getenv("DURABLE_FUNCTIONS_URL")
        if self.orchestrator == "logic_apps":
            return self.config.get("logic_apps_url") or os.getenv("LOGIC_APPS_URL")
        return None

    def _call_orchestrator(self, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = self._orchestrator_endpoint()
        if not endpoint:
            return {"status": "unconfigured"}
        try:
            body = json.dumps(payload).encode("utf-8")
            req = request.Request(endpoint, data=body, method="POST")
            req.add_header("Content-Type", "application/json")
            with request.urlopen(req, timeout=10) as response:
                return {"status": "submitted", "data": response.read().decode("utf-8")}
        except OSError as exc:
            return {"status": "error", "error": str(exc)}

    async def create_workflow(self, change_id: str, tenant_id: str) -> dict[str, Any]:
        workflow = {
            "change_id": change_id,
            "tenant_id": tenant_id,
            "orchestrator": self.orchestrator,
            "tasks": [
                {"name": "peer_review", "status": "pending"},
                {"name": "automated_checks", "status": "pending"},
                {"name": "final_approval", "status": "pending"},
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        workflow["orchestrator_status"] = self._call_orchestrator(workflow)
        await self.db_service.store("change_workflows", change_id, workflow)
        return workflow


class ChangeEventPublisher:
    def __init__(self, config: dict[str, Any], logger: Any) -> None:
        self.logger = logger
        connection_string = config.get("connection_string") or os.getenv(
            "SERVICE_BUS_CONNECTION_STRING"
        )
        topic_name = config.get("topic_name", "ppm-events")
        self._event_bus = (
            ServiceBusEventBus(connection_string=connection_string, topic_name=topic_name)
            if connection_string
            else None
        )
        self._published_ids: set[str] = set()
        self._event_log: list[dict[str, Any]] = []

    async def publish_event(self, topic: str, payload: dict[str, Any]) -> None:
        event_id = payload.get("event_id")
        if event_id and event_id in self._published_ids:
            self.logger.info("Skipping duplicate event: %s", event_id)
            return
        if event_id:
            self._published_ids.add(event_id)
        self._event_log.append({"topic": topic, "payload": payload})
        if self._event_bus:
            await self._event_bus.publish(topic, payload)

    def get_event_log(self) -> list[dict[str, Any]]:
        return list(self._event_log)


class DependencyGraphService:
    def __init__(self, logger: Any, config: dict[str, Any] | None = None) -> None:
        self.logger = logger
        self.config = config or {}
        self._adjacency: dict[str, list[str]] = {}
        self._driver = None
        if importlib.util.find_spec("neo4j"):
            uri = self.config.get("uri")
            user = self.config.get("username")
            password = self.config.get("password")
            if uri and user and password:
                from neo4j import GraphDatabase

                self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def load_cmdb(self, cmdb: dict[str, Any]) -> None:
        adjacency: dict[str, list[str]] = {}
        for ci_id, ci in cmdb.items():
            adjacency.setdefault(ci_id, [])
            for rel in ci.get("relationships", []):
                target_id = rel.get("target_ci_id")
                if target_id:
                    adjacency[ci_id].append(target_id)
        if self._driver:
            self._sync_cmdb_graph(cmdb)
        self._adjacency = adjacency

    def _sync_cmdb_graph(self, cmdb: dict[str, Any]) -> None:
        if not self._driver:
            return
        with self._driver.session() as session:
            for ci_id, ci in cmdb.items():
                session.run(
                    "MERGE (c:CI {ci_id: $ci_id}) "
                    "SET c.name = $name, c.type = $type, c.status = $status",
                    ci_id=ci_id,
                    name=ci.get("name"),
                    type=ci.get("type"),
                    status=ci.get("status"),
                )
                for rel in ci.get("relationships", []):
                    target_id = rel.get("target_ci_id")
                    if not target_id:
                        continue
                    session.run(
                        "MERGE (source:CI {ci_id: $source_id}) "
                        "MERGE (target:CI {ci_id: $target_id}) "
                        "MERGE (source)-[:DEPENDS_ON]->(target)",
                        source_id=ci_id,
                        target_id=target_id,
                    )

    def get_impacted(self, ci_ids: Iterable[str]) -> list[str]:
        if self._driver:
            return self._get_impacted_from_graph(ci_ids)
        visited: set[str] = set()
        queue = list(ci_ids)
        impacted: set[str] = set()
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for neighbor in self._adjacency.get(current, []):
                impacted.add(neighbor)
                if neighbor not in visited:
                    queue.append(neighbor)
        return sorted(impacted)

    def _get_impacted_from_graph(self, ci_ids: Iterable[str]) -> list[str]:
        if not self._driver:
            return []
        impacted: set[str] = set()
        with self._driver.session() as session:
            for ci_id in ci_ids:
                result = session.run(
                    "MATCH (n:CI {ci_id: $ci_id})-[:DEPENDS_ON*]->(impacted) "
                    "RETURN impacted.ci_id",
                    ci_id=ci_id,
                )
                impacted.update(record[0] for record in result)
        return sorted(impacted)

    def root_cause(self, ci_id: str) -> list[str]:
        if not self._driver:
            return [ci_id]
        with self._driver.session() as session:
            result = session.run(
                "MATCH (n {ci_id: $ci_id})<-[:DEPENDS_ON*]-(root) RETURN root.ci_id",
                ci_id=ci_id,
            )
            return [record[0] for record in result]


class ChangeRequestClassifier:
    def __init__(self, labels: list[str]) -> None:
        self.labels = labels
        self.model = NaiveBayesTextClassifier(labels=labels)

    def train(self, samples: list[tuple[str, str]]) -> None:
        self.model.fit(samples)

    def predict(self, text: str) -> tuple[str, dict[str, float]]:
        return self.model.predict(text)


class ApprovalFallbackAgent:
    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"approval_id": "approval-fallback", "status": "pending"}
