"""
Release & Deployment Agent - Shared type aliases and protocols.

This module defines the typing Protocol that action handlers use to access
agent state and services without creating a circular import back to the
main agent module.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ReleaseAgentProtocol(Protocol):
    """Structural typing contract that action handler functions depend on.

    Every attribute / helper listed here is provided by
    ``ReleaseDeploymentAgent`` at runtime.  Action modules receive the agent
    instance typed as ``ReleaseAgentProtocol`` so they never import the
    concrete class and therefore cannot create circular-import problems.
    """

    # -- logging --
    logger: logging.Logger

    # -- configuration scalars --
    environments: list[str]
    auto_rollback_threshold: float
    deployment_window_hours: int
    approval_environments: list[str]
    enforce_readiness_gates: bool
    auto_rollback_on_anomaly: bool

    # -- data stores (in-memory dicts) --
    releases: dict[str, Any]
    deployment_plans: dict[str, Any]
    environments_inventory: dict[str, Any]
    release_notes: dict[str, Any]
    deployment_metrics: dict[str, Any]
    environment_allocations: dict[str, dict[str, Any]]
    deployment_logs: dict[str, list[dict[str, Any]]]
    deployment_artifacts: dict[str, list[dict[str, Any]]]
    readiness_assessments: dict[str, dict[str, Any]]
    deployment_history: list[dict[str, Any]]

    # -- tenant state stores --
    release_store: Any
    deployment_plan_store: Any

    # -- integration services --
    db_service: Any
    doc_publishing_service: Any
    calendar_service: Any

    # -- optional agent collaborators --
    quality_agent: Any
    change_agent: Any
    risk_agent: Any
    compliance_agent: Any
    schedule_agent: Any
    schedule_agent_action: str | None
    approval_agent: Any

    # -- optional external clients --
    azure_devops_client: Any
    github_actions_client: Any
    durable_functions_client: Any
    azure_policy_client: Any
    openai_client: Any
    environment_reservation_client: Any
    configuration_management_client: Any
    tracking_clients: list[Any]
    version_control_client: Any
    monitoring_client: Any
    analytics_client: Any
    event_bus: Any

    # -- paths --
    rollback_scripts_path: Path
