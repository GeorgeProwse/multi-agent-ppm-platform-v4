/**
 * Connector Helpers
 *
 * Shared utility functions, mock data, and default categories
 * used across connector store slices.
 */

import type {
  CategoryInfo,
  CertificationStatus,
  Connector,
  ConnectorConfigUpdate,
  ConnectorFilterState,
} from './types';
import type { ConnectorStoreState } from './connectorStoreTypes';

// ─── Connector response mapping ──────────────────────────────────────────

export const mapConnectorResponses = (
  connectors: Array<Partial<Connector> & Record<string, unknown>>
): Connector[] =>
  normalizeMcpDuplicates(
    connectors.map((connector) => ({
      connector_id: String(connector.connector_id ?? ''),
      name: String(connector.name ?? ''),
      description: String(connector.description ?? ''),
      category: (connector.category as Connector['category']) ?? 'pm',
      system: String(connector.system ?? connector.name ?? ''),
      connector_type:
        (connector.mcp_feature_enabled ?? true)
          ? ((connector.connector_type as Connector['connector_type'] | undefined) ?? (connector.mcp_preferred ? 'mcp' : 'rest'))
          : 'rest',
      mcp_server_id: String(connector.mcp_server_id ?? ''),
      supported_operations: Array.isArray(connector.supported_operations) ? connector.supported_operations.map(String) : [],
      mcp_preferred: Boolean(connector.mcp_preferred),
      status: (connector.status as Connector['status']) ?? 'beta',
      icon: String(connector.icon ?? ''),
      supported_sync_directions: (connector.supported_sync_directions as Connector['supported_sync_directions']) ?? ['inbound'],
      auth_type: String(connector.auth_type ?? 'api_key'),
      config_fields: (connector.config_fields as Connector['config_fields']) ?? [],
      env_vars: (connector.env_vars as Connector['env_vars']) ?? [],
      supported_objects: Array.isArray(connector.supported_objects) ? connector.supported_objects : [],
      limitations: Array.isArray(connector.limitations) ? connector.limitations : [],
      auth_requirements: Array.isArray(connector.auth_requirements) ? connector.auth_requirements : [],
      enabled: Boolean(connector.enabled),
      configured: Boolean(connector.configured),
      instance_url: String(connector.instance_url ?? ''),
      project_key: String(connector.project_key ?? ''),
      sync_direction: (connector.sync_direction as Connector['sync_direction']) ?? 'inbound',
      sync_frequency: (connector.sync_frequency as Connector['sync_frequency']) ?? 'daily',
      health_status: (connector.health_status as Connector['health_status']) ?? 'unknown',
      last_sync_at: (connector.last_sync_at as Connector['last_sync_at']) ?? null,
      certification_status: normalizeCertificationStatus(
        (connector as { certification_status?: string; certification?: string }).certification_status ??
          (connector as { certification?: string }).certification ??
          (connector.certification_status as string | undefined)
      ),
      custom_fields: (connector.custom_fields as Connector['custom_fields']) ?? undefined,
      mcp_server_url: connector.mcp_server_url as string | undefined,
      mcp_tools: connector.mcp_tools as string[] | undefined,
      mcp_tool_map: connector.mcp_tool_map as Record<string, unknown> | undefined,
      mcp_scopes: connector.mcp_scopes as string[] | undefined,
      mcp_enabled: connector.mcp_enabled as boolean | undefined,
      mcp_feature_enabled: connector.mcp_feature_enabled as boolean | undefined,
      mcp_enabled_operations: connector.mcp_enabled_operations as string[] | undefined,
      mcp_disabled_operations: connector.mcp_disabled_operations as string[] | undefined,
      client_id: connector.client_id as string | undefined,
      client_secret: connector.client_secret as string | undefined,
      scope: connector.scope as string | undefined,
      prefer_mcp: connector.prefer_mcp as boolean | undefined,
    }))
  );

// ─── MCP duplicate normalization ─────────────────────────────────────────

export const normalizeMcpDuplicates = (connectors: Connector[]): Connector[] => {
  const mcpEnabledSystems = new Set(
    connectors
      .filter(
        (connector) =>
          connector.connector_type === 'mcp' && (connector.enabled || connector.mcp_enabled)
      )
      .map((connector) => connector.system)
  );
  if (!mcpEnabledSystems.size) return connectors;
  return connectors.map((connector) => {
    if (connector.connector_type === 'rest' && mcpEnabledSystems.has(connector.system)) {
      return { ...connector, enabled: false };
    }
    return connector;
  });
};

// ─── Certification status normalization ──────────────────────────────────

export const normalizeCertificationStatus = (status?: string | null): CertificationStatus => {
  if (!status) return 'not_started';
  const normalized = status.toLowerCase().replace(/[\s-]+/g, '_');
  switch (normalized) {
    case 'certified':
    case 'pending':
    case 'expired':
    case 'not_certified':
    case 'not_started':
      return normalized;
    default:
      return 'not_started';
  }
};

// ─── Connector config state updater ──────────────────────────────────────

export const updateConnectorConfigState = (
  connectors: Connector[],
  connectorId: string,
  config: ConnectorConfigUpdate
): Connector[] => {
  const next = connectors.map((c) =>
    c.connector_id === connectorId
      ? {
          ...c,
          ...config,
          configured: true,
        }
      : c
  );
  const updatedConnector = next.find((c) => c.connector_id === connectorId);
  if (!updatedConnector || updatedConnector.connector_type !== 'mcp') {
    return next;
  }
  return disableRestDuplicates(next, updatedConnector);
};

// ─── Project MCP state updater ───────────────────────────────────────────

export const updateProjectMcpState = (
  connectors: Connector[],
  connector: Connector,
  updates: Pick<
    ConnectorConfigUpdate,
    'mcp_enabled' | 'mcp_server_id' | 'mcp_server_url' | 'mcp_tool_map'
  >
): Connector[] => {
  const next = connectors.map((c) =>
    c.connector_id === connector.connector_id
      ? {
          ...c,
          ...updates,
          connector_type:
            updates.mcp_enabled && (connector.mcp_feature_enabled ?? true)
              ? 'mcp'
              : c.connector_type,
        }
      : c
  );
  if (!updates.mcp_enabled) {
    return next;
  }
  return disableRestDuplicates(next, connector);
};

// ─── REST duplicate disabler ─────────────────────────────────────────────

export const disableRestDuplicates = (connectors: Connector[], source: Connector): Connector[] =>
  connectors.map((c) => {
    if (c.connector_id === source.connector_id) {
      return c;
    }
    if (c.system === source.system && c.connector_type === 'rest' && c.enabled) {
      return { ...c, enabled: false };
    }
    return c;
  });

// ─── Project connector lookup ────────────────────────────────────────────

export const getProjectConnector = (
  state: ConnectorStoreState,
  projectId: string,
  connectorId: string
) =>
  (state.projectConnectors[projectId] || []).find(
    (connector) => connector.connector_id === connectorId
  );

// ─── Payload builders ────────────────────────────────────────────────────

export const buildProjectConnectorConfigPayload = (
  connector: Connector,
  overrides: ConnectorConfigUpdate
): ConnectorConfigUpdate => ({
  instance_url: connector.instance_url || '',
  project_key: connector.project_key || '',
  mcp_server_url: connector.mcp_server_url || '',
  mcp_server_id: connector.mcp_server_id || '',
  mcp_tool_map: connector.mcp_tool_map || {},
  mcp_scopes: connector.mcp_scopes || [],
  mcp_tools: connector.mcp_tools || [],
  prefer_mcp: connector.prefer_mcp ?? false,
  mcp_enabled: connector.mcp_enabled ?? true,
  mcp_enabled_operations: connector.mcp_enabled_operations || [],
  mcp_disabled_operations: connector.mcp_disabled_operations || [],
  sync_direction: connector.sync_direction,
  sync_frequency: connector.sync_frequency,
  custom_fields: connector.custom_fields || {},
  ...overrides,
});

export const buildProjectMcpConfigPayload = (
  connector: Connector,
  overrides?: Pick<ConnectorConfigUpdate, 'mcp_server_url' | 'mcp_server_id' | 'mcp_tool_map'>
): Pick<ConnectorConfigUpdate, 'mcp_server_url' | 'mcp_server_id' | 'mcp_tool_map'> => ({
  mcp_server_url: connector.mcp_server_url || '',
  mcp_server_id: connector.mcp_server_id || '',
  mcp_tool_map: connector.mcp_tool_map || {},
  ...overrides,
});

// ─── Filter helpers ──────────────────────────────────────────────────────

export const getConnectorCertificationStatus = (connector: Connector): CertificationStatus =>
  connector.certification_status ?? 'not_started';

export const matchesStatusFilter = (
  connector: Connector,
  filter: ConnectorFilterState['statusFilter']
) => connector.status === filter;

export const matchesCertificationFilter = (
  connector: Connector,
  filter: ConnectorFilterState['certificationFilter']
) => getConnectorCertificationStatus(connector) === filter;

// ─── Mock connectors ────────────────────────────────────────────────────

export function getMockConnectors(): Array<Partial<Connector> & Record<string, unknown>> {
  return [
    // PM Tools
    {
      connector_id: 'jira',
      name: 'Jira',
      description: 'Atlassian Jira for adaptive project tracking and issue management',
      category: 'pm',
      system: 'jira',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'production',
      icon: 'jira',
      supported_sync_directions: ['inbound'],
      auth_type: 'api_key',
      config_fields: [
        { name: 'instance_url', type: 'url', required: true, label: 'Instance URL' },
        { name: 'project_key', type: 'string', required: false, label: 'Project Key' },
      ],
      env_vars: ['JIRA_INSTANCE_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
    },
    {
      connector_id: 'azure_devops',
      name: 'Azure DevOps',
      description: 'Microsoft Azure DevOps for source control, CI/CD, and work tracking',
      category: 'pm',
      system: 'azure_devops',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'azure',
      supported_sync_directions: ['inbound', 'bidirectional'],
      auth_type: 'api_key',
      config_fields: [],
      env_vars: ['AZURE_DEVOPS_ORG_URL', 'AZURE_DEVOPS_PAT'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
    },
    // PPM Tools
    {
      connector_id: 'planview',
      name: 'Planview',
      description: 'Enterprise PPM platform for portfolio and resource management',
      category: 'ppm',
      system: 'planview',
      connector_type: 'mcp',
      mcp_server_id: 'mcp-planview',
      supported_operations: ['portfolio.read', 'project.write', 'resource.read'],
      mcp_preferred: true,
      status: 'beta',
      icon: 'planview',
      supported_sync_directions: ['inbound', 'bidirectional'],
      auth_type: 'api_key',
      config_fields: [],
      env_vars: ['PLANVIEW_API_URL', 'PLANVIEW_API_TOKEN'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
      mcp_server_url: 'https://mcp.planview.example.com',
      mcp_scopes: ['portfolio:read', 'projects:write'],
      mcp_tool_map: {
        'portfolio.read': true,
      },
      mcp_enabled: true,
    },
    // Collaboration
    {
      connector_id: 'slack',
      name: 'Slack',
      description: 'Slack for team messaging and collaboration',
      category: 'collaboration',
      system: 'slack',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'slack',
      supported_sync_directions: ['outbound', 'bidirectional'],
      auth_type: 'api_key',
      config_fields: [
        { name: 'slack_bot_token', type: 'string', required: true, label: 'Bot Token' },
        { name: 'slack_signing_secret', type: 'string', required: true, label: 'Signing Secret' },
        { name: 'default_channel', type: 'string', required: false, label: 'Default Channel' },
      ],
      env_vars: ['SLACK_API_URL', 'SLACK_BOT_TOKEN', 'SLACK_SIGNING_SECRET'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'outbound',
      sync_frequency: 'realtime',
      health_status: 'unknown',
      last_sync_at: null,
      custom_fields: {
        slack_bot_token: '',
        slack_signing_secret: '',
        default_channel: '',
      },
    },
    {
      connector_id: 'm365',
      name: 'Microsoft 365',
      description:
        'Microsoft 365 suite for Teams, Exchange, SharePoint, Planner, OneDrive, Power BI, and Viva.',
      category: 'collaboration',
      system: 'm365',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'microsoft',
      supported_sync_directions: ['inbound'],
      auth_type: 'oauth2',
      config_fields: [
        { name: 'instance_url', type: 'url', required: false, label: 'Graph API Base URL' },
        { name: 'tenant_id', type: 'string', required: true, label: 'Tenant ID' },
        { name: 'client_id', type: 'string', required: true, label: 'App (client) ID' },
        { name: 'app_object_id', type: 'string', required: false, label: 'App Object ID' },
        {
          name: 'service_principal_object_id',
          type: 'string',
          required: false,
          label: 'Service Principal Object ID',
        },
        {
          name: 'application_id_uri',
          type: 'string',
          required: false,
          label: 'Application ID URI',
        },
        {
          name: 'scopes',
          type: 'multiselect',
          required: false,
          label: 'Microsoft Graph Scopes',
          options: [
            'User.Read',
            'Group.Read.All',
            'Team.ReadBasic.All',
            'Channel.ReadBasic.All',
            'Mail.Read',
            'Calendars.Read',
            'Files.Read.All',
            'Sites.Read.All',
            'Tasks.Read',
            'Reports.Read.All',
            'EmployeeExperience.Read.All',
          ],
        },
        { name: 'enable_teams', type: 'boolean', required: false, label: 'Enable Teams workload' },
        {
          name: 'enable_exchange',
          type: 'boolean',
          required: false,
          label: 'Enable Exchange/Outlook workload',
        },
        {
          name: 'enable_sharepoint',
          type: 'boolean',
          required: false,
          label: 'Enable SharePoint workload',
        },
        { name: 'enable_planner', type: 'boolean', required: false, label: 'Enable Planner workload' },
        { name: 'enable_onedrive', type: 'boolean', required: false, label: 'Enable OneDrive workload' },
        { name: 'enable_power_bi', type: 'boolean', required: false, label: 'Enable Power BI workload' },
        { name: 'enable_viva', type: 'boolean', required: false, label: 'Enable Viva workload' },
      ],
      env_vars: [
        'M365_API_URL',
        'M365_TENANT_ID',
        'M365_CLIENT_ID',
        'M365_CLIENT_SECRET',
        'M365_REFRESH_TOKEN',
        'M365_SCOPES',
      ],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
      custom_fields: {
        instance_url: '',
        tenant_id: '',
        client_id: '',
        app_object_id: '',
        service_principal_object_id: '',
        application_id_uri: '',
        scopes: [],
        enable_teams: false,
        enable_exchange: false,
        enable_sharepoint: false,
        enable_planner: false,
        enable_onedrive: false,
        enable_power_bi: false,
        enable_viva: false,
      },
    },
    {
      connector_id: 'teams',
      name: 'Microsoft Teams',
      description: 'Microsoft Teams for collaboration and communication',
      category: 'collaboration',
      system: 'teams',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'teams',
      supported_sync_directions: ['outbound', 'bidirectional'],
      auth_type: 'oauth2',
      config_fields: [],
      env_vars: ['TEAMS_TENANT_ID', 'TEAMS_CLIENT_ID', 'TEAMS_CLIENT_SECRET'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'outbound',
      sync_frequency: 'realtime',
      health_status: 'unknown',
      last_sync_at: null,
    },
    // Document Management
    {
      connector_id: 'sharepoint',
      name: 'SharePoint',
      description: 'Microsoft SharePoint for document management and collaboration',
      category: 'doc_mgmt',
      system: 'sharepoint',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'sharepoint',
      supported_sync_directions: ['inbound', 'bidirectional'],
      auth_type: 'oauth2',
      config_fields: [],
      env_vars: ['SHAREPOINT_TENANT_ID', 'SHAREPOINT_CLIENT_ID', 'SHAREPOINT_CLIENT_SECRET'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
    },
    // ERP
    {
      connector_id: 'sap',
      name: 'SAP',
      description: 'SAP ERP for enterprise resource planning and financials',
      category: 'erp',
      system: 'sap',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'sap',
      supported_sync_directions: ['inbound'],
      auth_type: 'basic',
      config_fields: [],
      env_vars: ['SAP_URL', 'SAP_USERNAME', 'SAP_PASSWORD', 'SAP_CLIENT'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
    },
    // HRIS
    {
      connector_id: 'workday',
      name: 'Workday',
      description: 'Workday HCM for human capital management',
      category: 'hris',
      system: 'workday',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'workday',
      supported_sync_directions: ['inbound'],
      auth_type: 'oauth2',
      config_fields: [
        { name: 'tenant', type: 'string', required: true, label: 'Tenant' },
        { name: 'client_id', type: 'string', required: true, label: 'Client ID' },
        { name: 'client_secret', type: 'string', required: true, label: 'Client Secret' },
        { name: 'refresh_token', type: 'string', required: true, label: 'Refresh Token' },
        { name: 'token_url', type: 'url', required: false, label: 'Token URL' },
      ],
      env_vars: [
        'WORKDAY_API_URL',
        'WORKDAY_CLIENT_ID',
        'WORKDAY_CLIENT_SECRET',
        'WORKDAY_REFRESH_TOKEN',
        'WORKDAY_TOKEN_URL',
      ],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
      custom_fields: {
        tenant: '',
        client_id: '',
        client_secret: '',
        refresh_token: '',
        token_url: '',
      },
    },
    // GRC
    {
      connector_id: 'servicenow_grc',
      name: 'ServiceNow GRC',
      description: 'ServiceNow Governance, Risk, and Compliance',
      category: 'grc',
      system: 'servicenow_grc',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'servicenow',
      supported_sync_directions: ['inbound', 'bidirectional'],
      auth_type: 'oauth2',
      config_fields: [],
      env_vars: ['SERVICENOW_URL', 'SERVICENOW_CLIENT_ID', 'SERVICENOW_CLIENT_SECRET'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
    },
    // Compliance
    {
      connector_id: 'regulatory_compliance',
      name: 'Regulatory Compliance',
      description: 'Regulatory compliance APIs for My Health Records Act 2012 and Therapeutic Goods (Medical Devices) Regulations 2002 audit trails',
      category: 'compliance',
      system: 'regulatory_compliance',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'beta',
      icon: 'shield-check',
      supported_sync_directions: ['inbound', 'outbound'],
      auth_type: 'api_key',
      config_fields: [
        { name: 'endpoint_url', type: 'url', required: true, label: 'Compliance API Endpoint' },
        { name: 'api_key', type: 'string', required: true, label: 'API Key' },
        { name: 'supported_regulations', type: 'string', required: false, label: 'Supported Regulations (comma-separated)' },
      ],
      env_vars: ['REGULATORY_COMPLIANCE_ENDPOINT', 'REGULATORY_COMPLIANCE_API_KEY'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'daily',
      health_status: 'unknown',
      last_sync_at: null,
    },
    // IoT Integrations
    {
      connector_id: 'iot',
      name: 'IoT Integrations',
      description: 'Custom hardware and sensor integrations via device endpoints',
      category: 'iot',
      system: 'iot',
      connector_type: 'rest',
      mcp_server_id: '',
      supported_operations: [],
      mcp_preferred: false,
      status: 'coming_soon',
      icon: 'cpu-chip',
      supported_sync_directions: ['inbound', 'outbound'],
      auth_type: 'api_key',
      config_fields: [
        { name: 'device_endpoint', type: 'url', required: true, label: 'Device Endpoint' },
        { name: 'auth_token', type: 'string', required: true, label: 'Auth Token' },
        { name: 'sensor_types', type: 'string', required: false, label: 'Supported Sensor Types' },
      ],
      env_vars: ['IOT_DEVICE_ENDPOINT', 'IOT_AUTH_TOKEN'],
      enabled: false,
      configured: false,
      instance_url: '',
      project_key: '',
      sync_direction: 'inbound',
      sync_frequency: 'realtime',
      health_status: 'unknown',
      last_sync_at: null,
      custom_fields: {
        device_endpoint: '',
        auth_token: '',
        sensor_types: '',
      },
    },
  ];
}

// ─── Default categories ──────────────────────────────────────────────────

export function getDefaultCategories(): CategoryInfo[] {
  return [
    { value: 'ppm', label: 'PPM Tools', icon: 'domain.portfolio', description: 'Portfolio and Project Management platforms', connector_count: 3, enabled_connector: null },
    { value: 'pm', label: 'PM Tools', icon: 'provenance.auditLog', description: 'Project management and work tracking tools', connector_count: 4, enabled_connector: null },
    { value: 'doc_mgmt', label: 'Document Management', icon: 'artifact.folder', description: 'Document storage and collaboration platforms', connector_count: 3, enabled_connector: null },
    { value: 'erp', label: 'ERP Systems', icon: 'domain.platform', description: 'Enterprise resource planning systems', connector_count: 3, enabled_connector: null },
    { value: 'hris', label: 'HRIS', icon: 'communication.user', description: 'Human resource information systems', connector_count: 3, enabled_connector: null },
    { value: 'collaboration', label: 'Collaboration', icon: 'communication.message', description: 'Team communication and collaboration tools', connector_count: 4, enabled_connector: null },
    { value: 'grc', label: 'GRC', icon: 'domain.governance', description: 'Governance, Risk, and Compliance platforms', connector_count: 3, enabled_connector: null },
    { value: 'compliance', label: 'Compliance', icon: 'domain.governance', description: 'Specialised regulatory compliance platforms', connector_count: 1, enabled_connector: null },
    { value: 'iot', label: 'IoT Integrations', icon: 'connectors.cpuChip', description: 'Custom hardware and sensor integrations', connector_count: 1, enabled_connector: null },
  ];
}
