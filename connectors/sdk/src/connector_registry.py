"""
Connector Registry

Defines all available connectors in the platform, organized by category.
Only Jira is fully functional; others are stubs for future implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from base_connector import ConnectorCategory, SyncDirection


class ConnectorStatus(str, Enum):
    """Implementation status of a connector."""

    AVAILABLE = "available"  # Fully functional
    COMING_SOON = "coming_soon"  # Stub, planned for implementation
    BETA = "beta"  # In beta testing


@dataclass
class ConnectorDefinition:
    """Definition of an available connector."""

    connector_id: str
    name: str
    description: str
    category: ConnectorCategory
    status: ConnectorStatus = ConnectorStatus.COMING_SOON
    icon: str = ""  # Icon identifier for UI
    supported_sync_directions: list[SyncDirection] = field(
        default_factory=lambda: [SyncDirection.INBOUND]
    )
    auth_type: str = "api_key"  # api_key, oauth2, basic
    config_fields: list[dict[str, Any]] = field(default_factory=list)
    env_vars: list[str] = field(default_factory=list)  # Required environment variables

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector_id": self.connector_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "status": self.status.value,
            "icon": self.icon,
            "supported_sync_directions": [d.value for d in self.supported_sync_directions],
            "auth_type": self.auth_type,
            "config_fields": self.config_fields,
            "env_vars": self.env_vars,
        }


# =============================================================================
# CONNECTOR DEFINITIONS
# =============================================================================

# PPM Tools Category
PLANVIEW_CONNECTOR = ConnectorDefinition(
    connector_id="planview",
    name="Planview",
    description="Enterprise PPM platform for portfolio and resource management",
    category=ConnectorCategory.PPM,
    status=ConnectorStatus.COMING_SOON,
    icon="planview",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="api_key",
    config_fields=[
        {"name": "instance_url", "type": "url", "required": True, "label": "Instance URL"},
        {"name": "portfolio_id", "type": "string", "required": False, "label": "Portfolio ID"},
    ],
    env_vars=["PLANVIEW_API_URL", "PLANVIEW_API_TOKEN"],
)

CLARITY_CONNECTOR = ConnectorDefinition(
    connector_id="clarity",
    name="Clarity PPM",
    description="Broadcom Clarity PPM for enterprise project and portfolio management",
    category=ConnectorCategory.PPM,
    status=ConnectorStatus.COMING_SOON,
    icon="clarity",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="basic",
    config_fields=[
        {"name": "instance_url", "type": "url", "required": True, "label": "Instance URL"},
    ],
    env_vars=["CLARITY_URL", "CLARITY_USERNAME", "CLARITY_PASSWORD"],
)

MS_PROJECT_SERVER_CONNECTOR = ConnectorDefinition(
    connector_id="ms_project_server",
    name="Microsoft Project Server",
    description="Microsoft Project Server/Project Online for enterprise project management",
    category=ConnectorCategory.PPM,
    status=ConnectorStatus.COMING_SOON,
    icon="microsoft",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="oauth2",
    config_fields=[
        {"name": "tenant_id", "type": "string", "required": True, "label": "Azure Tenant ID"},
        {"name": "site_url", "type": "url", "required": True, "label": "Project Web App URL"},
    ],
    env_vars=["MS_PROJECT_TENANT_ID", "MS_PROJECT_CLIENT_ID", "MS_PROJECT_CLIENT_SECRET"],
)

# PM Tools Category
JIRA_CONNECTOR = ConnectorDefinition(
    connector_id="jira",
    name="Jira",
    description="Atlassian Jira for agile project tracking and issue management",
    category=ConnectorCategory.PM,
    status=ConnectorStatus.AVAILABLE,  # Fully implemented
    icon="jira",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="api_key",
    config_fields=[
        {"name": "instance_url", "type": "url", "required": True, "label": "Instance URL"},
        {"name": "project_key", "type": "string", "required": False, "label": "Project Key"},
    ],
    env_vars=["JIRA_INSTANCE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"],
)

AZURE_DEVOPS_CONNECTOR = ConnectorDefinition(
    connector_id="azure_devops",
    name="Azure DevOps",
    description="Microsoft Azure DevOps for source control, CI/CD, and work tracking",
    category=ConnectorCategory.PM,
    status=ConnectorStatus.COMING_SOON,
    icon="azure",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="api_key",
    config_fields=[
        {"name": "organization_url", "type": "url", "required": True, "label": "Organization URL"},
        {"name": "project_name", "type": "string", "required": True, "label": "Project Name"},
    ],
    env_vars=["AZURE_DEVOPS_ORG_URL", "AZURE_DEVOPS_PAT"],
)

MONDAY_CONNECTOR = ConnectorDefinition(
    connector_id="monday",
    name="Monday.com",
    description="Monday.com work management platform",
    category=ConnectorCategory.PM,
    status=ConnectorStatus.COMING_SOON,
    icon="monday",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="api_key",
    config_fields=[
        {"name": "board_ids", "type": "string", "required": False, "label": "Board IDs (comma-separated)"},
    ],
    env_vars=["MONDAY_API_TOKEN"],
)

ASANA_CONNECTOR = ConnectorDefinition(
    connector_id="asana",
    name="Asana",
    description="Asana project and task management",
    category=ConnectorCategory.PM,
    status=ConnectorStatus.COMING_SOON,
    icon="asana",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="oauth2",
    config_fields=[
        {"name": "workspace_gid", "type": "string", "required": True, "label": "Workspace GID"},
    ],
    env_vars=["ASANA_ACCESS_TOKEN"],
)

# Document Management Category
SHAREPOINT_CONNECTOR = ConnectorDefinition(
    connector_id="sharepoint",
    name="SharePoint",
    description="Microsoft SharePoint for document management and collaboration",
    category=ConnectorCategory.DOC_MGMT,
    status=ConnectorStatus.COMING_SOON,
    icon="sharepoint",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="oauth2",
    config_fields=[
        {"name": "site_url", "type": "url", "required": True, "label": "SharePoint Site URL"},
        {"name": "document_library", "type": "string", "required": False, "label": "Document Library"},
    ],
    env_vars=["SHAREPOINT_TENANT_ID", "SHAREPOINT_CLIENT_ID", "SHAREPOINT_CLIENT_SECRET"],
)

CONFLUENCE_CONNECTOR = ConnectorDefinition(
    connector_id="confluence",
    name="Confluence",
    description="Atlassian Confluence for team documentation and knowledge management",
    category=ConnectorCategory.DOC_MGMT,
    status=ConnectorStatus.COMING_SOON,
    icon="confluence",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="api_key",
    config_fields=[
        {"name": "instance_url", "type": "url", "required": True, "label": "Instance URL"},
        {"name": "space_key", "type": "string", "required": False, "label": "Space Key"},
    ],
    env_vars=["CONFLUENCE_URL", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"],
)

GOOGLE_DRIVE_CONNECTOR = ConnectorDefinition(
    connector_id="google_drive",
    name="Google Drive",
    description="Google Drive for cloud document storage and collaboration",
    category=ConnectorCategory.DOC_MGMT,
    status=ConnectorStatus.COMING_SOON,
    icon="google",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="oauth2",
    config_fields=[
        {"name": "folder_id", "type": "string", "required": False, "label": "Root Folder ID"},
    ],
    env_vars=["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"],
)

# ERP Category
SAP_CONNECTOR = ConnectorDefinition(
    connector_id="sap",
    name="SAP",
    description="SAP ERP for enterprise resource planning and financials",
    category=ConnectorCategory.ERP,
    status=ConnectorStatus.COMING_SOON,
    icon="sap",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="basic",
    config_fields=[
        {"name": "instance_url", "type": "url", "required": True, "label": "SAP Instance URL"},
        {"name": "client_id", "type": "string", "required": True, "label": "SAP Client ID"},
    ],
    env_vars=["SAP_URL", "SAP_USERNAME", "SAP_PASSWORD", "SAP_CLIENT"],
)

ORACLE_CONNECTOR = ConnectorDefinition(
    connector_id="oracle",
    name="Oracle ERP Cloud",
    description="Oracle ERP Cloud for enterprise resource planning",
    category=ConnectorCategory.ERP,
    status=ConnectorStatus.COMING_SOON,
    icon="oracle",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="oauth2",
    config_fields=[
        {"name": "instance_url", "type": "url", "required": True, "label": "Oracle Cloud URL"},
    ],
    env_vars=["ORACLE_URL", "ORACLE_CLIENT_ID", "ORACLE_CLIENT_SECRET"],
)

NETSUITE_CONNECTOR = ConnectorDefinition(
    connector_id="netsuite",
    name="NetSuite",
    description="Oracle NetSuite for ERP and financials",
    category=ConnectorCategory.ERP,
    status=ConnectorStatus.COMING_SOON,
    icon="netsuite",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="oauth2",
    config_fields=[
        {"name": "account_id", "type": "string", "required": True, "label": "Account ID"},
    ],
    env_vars=["NETSUITE_ACCOUNT_ID", "NETSUITE_CONSUMER_KEY", "NETSUITE_CONSUMER_SECRET"],
)

# HRIS Category
WORKDAY_CONNECTOR = ConnectorDefinition(
    connector_id="workday",
    name="Workday",
    description="Workday HCM for human capital management",
    category=ConnectorCategory.HRIS,
    status=ConnectorStatus.COMING_SOON,
    icon="workday",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="oauth2",
    config_fields=[
        {"name": "tenant_name", "type": "string", "required": True, "label": "Tenant Name"},
    ],
    env_vars=["WORKDAY_TENANT", "WORKDAY_CLIENT_ID", "WORKDAY_CLIENT_SECRET"],
)

SAP_SUCCESSFACTORS_CONNECTOR = ConnectorDefinition(
    connector_id="sap_successfactors",
    name="SAP SuccessFactors",
    description="SAP SuccessFactors for human capital management",
    category=ConnectorCategory.HRIS,
    status=ConnectorStatus.COMING_SOON,
    icon="sap",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="oauth2",
    config_fields=[
        {"name": "api_server", "type": "url", "required": True, "label": "API Server URL"},
        {"name": "company_id", "type": "string", "required": True, "label": "Company ID"},
    ],
    env_vars=["SF_API_SERVER", "SF_COMPANY_ID", "SF_CLIENT_ID", "SF_CLIENT_SECRET"],
)

ADP_CONNECTOR = ConnectorDefinition(
    connector_id="adp",
    name="ADP",
    description="ADP Workforce Now for payroll and HR",
    category=ConnectorCategory.HRIS,
    status=ConnectorStatus.COMING_SOON,
    icon="adp",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="oauth2",
    config_fields=[],
    env_vars=["ADP_CLIENT_ID", "ADP_CLIENT_SECRET", "ADP_CERT_PATH"],
)

# Collaboration Category
TEAMS_CONNECTOR = ConnectorDefinition(
    connector_id="teams",
    name="Microsoft Teams",
    description="Microsoft Teams for collaboration and communication",
    category=ConnectorCategory.COLLABORATION,
    status=ConnectorStatus.COMING_SOON,
    icon="teams",
    supported_sync_directions=[SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="oauth2",
    config_fields=[
        {"name": "team_id", "type": "string", "required": False, "label": "Team ID"},
        {"name": "channel_id", "type": "string", "required": False, "label": "Channel ID"},
    ],
    env_vars=["TEAMS_TENANT_ID", "TEAMS_CLIENT_ID", "TEAMS_CLIENT_SECRET"],
)

SLACK_CONNECTOR = ConnectorDefinition(
    connector_id="slack",
    name="Slack",
    description="Slack for team messaging and collaboration",
    category=ConnectorCategory.COLLABORATION,
    status=ConnectorStatus.COMING_SOON,
    icon="slack",
    supported_sync_directions=[SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="oauth2",
    config_fields=[
        {"name": "workspace_id", "type": "string", "required": False, "label": "Workspace ID"},
        {"name": "default_channel", "type": "string", "required": False, "label": "Default Channel"},
    ],
    env_vars=["SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET"],
)

ZOOM_CONNECTOR = ConnectorDefinition(
    connector_id="zoom",
    name="Zoom",
    description="Zoom for video conferencing",
    category=ConnectorCategory.COLLABORATION,
    status=ConnectorStatus.COMING_SOON,
    icon="zoom",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.OUTBOUND],
    auth_type="oauth2",
    config_fields=[],
    env_vars=["ZOOM_CLIENT_ID", "ZOOM_CLIENT_SECRET", "ZOOM_ACCOUNT_ID"],
)

# GRC Category
SERVICENOW_GRC_CONNECTOR = ConnectorDefinition(
    connector_id="servicenow_grc",
    name="ServiceNow GRC",
    description="ServiceNow Governance, Risk, and Compliance",
    category=ConnectorCategory.GRC,
    status=ConnectorStatus.COMING_SOON,
    icon="servicenow",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="oauth2",
    config_fields=[
        {"name": "instance_url", "type": "url", "required": True, "label": "Instance URL"},
    ],
    env_vars=["SERVICENOW_URL", "SERVICENOW_CLIENT_ID", "SERVICENOW_CLIENT_SECRET"],
)

ARCHER_CONNECTOR = ConnectorDefinition(
    connector_id="archer",
    name="RSA Archer",
    description="RSA Archer for integrated risk management",
    category=ConnectorCategory.GRC,
    status=ConnectorStatus.COMING_SOON,
    icon="archer",
    supported_sync_directions=[SyncDirection.INBOUND],
    auth_type="api_key",
    config_fields=[
        {"name": "instance_url", "type": "url", "required": True, "label": "Instance URL"},
    ],
    env_vars=["ARCHER_URL", "ARCHER_INSTANCE", "ARCHER_USERNAME", "ARCHER_PASSWORD"],
)

LOGICGATE_CONNECTOR = ConnectorDefinition(
    connector_id="logicgate",
    name="LogicGate",
    description="LogicGate for risk and compliance management",
    category=ConnectorCategory.GRC,
    status=ConnectorStatus.COMING_SOON,
    icon="logicgate",
    supported_sync_directions=[SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL],
    auth_type="api_key",
    config_fields=[
        {"name": "subdomain", "type": "string", "required": True, "label": "Subdomain"},
    ],
    env_vars=["LOGICGATE_API_KEY"],
)


# =============================================================================
# REGISTRY
# =============================================================================

ALL_CONNECTORS: list[ConnectorDefinition] = [
    # PPM
    PLANVIEW_CONNECTOR,
    CLARITY_CONNECTOR,
    MS_PROJECT_SERVER_CONNECTOR,
    # PM
    JIRA_CONNECTOR,
    AZURE_DEVOPS_CONNECTOR,
    MONDAY_CONNECTOR,
    ASANA_CONNECTOR,
    # Doc Management
    SHAREPOINT_CONNECTOR,
    CONFLUENCE_CONNECTOR,
    GOOGLE_DRIVE_CONNECTOR,
    # ERP
    SAP_CONNECTOR,
    ORACLE_CONNECTOR,
    NETSUITE_CONNECTOR,
    # HRIS
    WORKDAY_CONNECTOR,
    SAP_SUCCESSFACTORS_CONNECTOR,
    ADP_CONNECTOR,
    # Collaboration
    TEAMS_CONNECTOR,
    SLACK_CONNECTOR,
    ZOOM_CONNECTOR,
    # GRC
    SERVICENOW_GRC_CONNECTOR,
    ARCHER_CONNECTOR,
    LOGICGATE_CONNECTOR,
]

CONNECTORS_BY_ID: dict[str, ConnectorDefinition] = {c.connector_id: c for c in ALL_CONNECTORS}

CONNECTORS_BY_CATEGORY: dict[ConnectorCategory, list[ConnectorDefinition]] = {}
for connector in ALL_CONNECTORS:
    if connector.category not in CONNECTORS_BY_CATEGORY:
        CONNECTORS_BY_CATEGORY[connector.category] = []
    CONNECTORS_BY_CATEGORY[connector.category].append(connector)


def get_connector_definition(connector_id: str) -> ConnectorDefinition | None:
    """Get a connector definition by ID."""
    return CONNECTORS_BY_ID.get(connector_id)


def get_connectors_by_category(category: ConnectorCategory) -> list[ConnectorDefinition]:
    """Get all connectors in a category."""
    return CONNECTORS_BY_CATEGORY.get(category, [])


def get_all_connectors() -> list[ConnectorDefinition]:
    """Get all connector definitions."""
    return ALL_CONNECTORS


def get_available_connectors() -> list[ConnectorDefinition]:
    """Get all fully implemented connectors."""
    return [c for c in ALL_CONNECTORS if c.status == ConnectorStatus.AVAILABLE]
