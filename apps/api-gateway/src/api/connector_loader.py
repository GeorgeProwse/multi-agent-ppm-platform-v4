from __future__ import annotations

import importlib
import logging
from typing import Any

from feature_flags import is_mcp_feature_enabled

from connectors.sdk.src.base_connector import ConnectorConfig
from connectors.sdk.src.connector_registry import (
    get_all_connectors,
    get_connector_definition,
)
from connectors.sdk.src.project_connector_store import ProjectConnectorConfig

logger = logging.getLogger(__name__)

# PascalCase segments that don't follow simple str.capitalize()
_PASCAL_OVERRIDES: dict[str, str] = {
    "iot": "IoT",
    "sharepoint": "SharePoint",
    "servicenow": "ServiceNow",
    "netsuite": "NetSuite",
    "logicgate": "LogicGate",
    "devops": "DevOps",
    "successfactors": "SuccessFactors",
}


def _to_class_name(connector_id: str) -> str:
    """Convert a connector_id like 'azure_devops' to 'AzureDevOpsConnector'."""
    parts = connector_id.split("_")
    return "".join(_PASCAL_OVERRIDES.get(p, p.capitalize()) for p in parts) + "Connector"


def _build_connector_class_map() -> dict[str, tuple[str, str]]:
    """Derive connector_id → (module_name, class_name) from manifests.

    REST connectors use their own id for the module.
    MCP connectors share the module/class of their REST counterpart
    (identified via the ``system`` field).
    """
    # First pass: collect base (non-MCP) connectors keyed by system
    system_to_base_id: dict[str, str] = {}
    for defn in get_all_connectors():
        if defn.auth_type != "mcp":
            system_to_base_id[defn.system] = defn.connector_id

    class_map: dict[str, tuple[str, str]] = {}
    for defn in get_all_connectors():
        if defn.auth_type == "mcp":
            base_id = system_to_base_id.get(defn.system, defn.connector_id)
        else:
            base_id = defn.connector_id
        module_name = f"{base_id}_connector"
        class_name = _to_class_name(base_id)
        class_map[defn.connector_id] = (module_name, class_name)

    return class_map


_CONNECTOR_CLASS_MAP: dict[str, tuple[str, str]] = _build_connector_class_map()

_MCP_CONNECTOR_BY_SYSTEM = {
    definition.system: definition.connector_id
    for definition in get_all_connectors()
    if definition.auth_type == "mcp"
}


def _connector_system(connector_id: str) -> str:
    definition = get_connector_definition(connector_id)
    return definition.system if definition else connector_id


def _should_use_mcp(config: ConnectorConfig | ProjectConnectorConfig | None) -> bool:
    return bool(
        config
        and config.prefer_mcp
        and config.mcp_server_url
        and config.is_mcp_enabled_for(None)
        and is_mcp_feature_enabled(
            system=_connector_system(config.connector_id),
            project_id=getattr(config, "ppm_project_id", None),
        )
    )


def resolve_connector_id(
    connector_id: str,
    *,
    config: ConnectorConfig | ProjectConnectorConfig | None = None,
) -> str:
    if not _should_use_mcp(config):
        return connector_id
    system = _connector_system(connector_id)
    return _MCP_CONNECTOR_BY_SYSTEM.get(system, connector_id)


def get_connector_class(
    connector_id: str,
    *,
    config: ConnectorConfig | ProjectConnectorConfig | None = None,
) -> type[Any] | None:
    resolved_id = resolve_connector_id(connector_id, config=config)
    module_info = _CONNECTOR_CLASS_MAP.get(resolved_id)
    if not module_info:
        return None
    module_name, class_name = module_info
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        logger.warning("Connector module %s not found for %s", module_name, resolved_id)
        return None
    return getattr(module, class_name, None)
