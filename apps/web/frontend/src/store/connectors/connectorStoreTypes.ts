/**
 * Connector Store Types
 *
 * Shared interfaces for the Zustand connector store slices.
 */

import type {
  CategoryInfo,
  CertificationRecord,
  Connector,
  ConnectorCategory,
  ConnectorConfigUpdate,
  ConnectorFilterState,
  ConnectionTestResult,
  McpToolSchema,
} from './types';

// ─── API base URL ──────────────────────────────────────────────────────────
export const API_BASE = '/v1';

// ─── Default filter ────────────────────────────────────────────────────────
export const DEFAULT_FILTER: ConnectorFilterState = {
  search: '',
  category: 'all',
  statusFilter: 'all',
  certificationFilter: 'all',
  enabledOnly: false,
};

// ─── Slice state interfaces ───────────────────────────────────────────────

export interface ConnectorListState {
  connectors: Connector[];
  connectorsLoading: boolean;
  connectorsError: string | null;
  projectConnectors: Record<string, Connector[]>;
  projectConnectorsLoading: Record<string, boolean>;
  projectConnectorsError: Record<string, string | null>;
  categories: CategoryInfo[];
  categoriesLoading: boolean;
  certifications: Record<string, CertificationRecord>;
  certificationsLoading: boolean;
  certificationsError: string | null;
  mcpToolsBySystem: Record<string, McpToolSchema[]>;
  mcpToolsLoading: Record<string, boolean>;
  mcpToolsError: Record<string, string | null>;
}

export interface ConnectorListActions {
  fetchConnectors: () => Promise<void>;
  fetchProjectConnectors: (projectId: string) => Promise<void>;
  fetchCategories: () => Promise<void>;
  fetchCertifications: () => Promise<void>;
  fetchMcpTools: (system: string) => Promise<void>;
  getConnector: (connectorId: string) => Connector | undefined;
  getCertification: (connectorId: string) => CertificationRecord | undefined;
  updateConnectorConfig: (connectorId: string, config: ConnectorConfigUpdate) => Promise<void>;
  updateProjectConnectorConfig: (
    projectId: string,
    connectorId: string,
    config: ConnectorConfigUpdate
  ) => Promise<void>;
  enableConnector: (connectorId: string) => Promise<void>;
  enableProjectConnector: (projectId: string, connectorId: string) => Promise<void>;
  disableConnector: (connectorId: string) => Promise<void>;
  disableProjectConnector: (projectId: string, connectorId: string) => Promise<void>;
  setProjectMcpEnabled: (
    projectId: string,
    connectorId: string,
    enabled: boolean,
    payload?: Pick<ConnectorConfigUpdate, 'mcp_server_url' | 'mcp_server_id' | 'mcp_tool_map'>
  ) => Promise<void>;
  updateProjectMcpToolMap: (
    projectId: string,
    connectorId: string,
    toolMap: Record<string, unknown>,
    payload?: Pick<ConnectorConfigUpdate, 'mcp_server_url' | 'mcp_server_id'>
  ) => Promise<void>;
  updateCertification: (
    connectorId: string,
    payload: Partial<Omit<CertificationRecord, 'connector_id' | 'tenant_id' | 'documents' | 'updated_at'>>
  ) => Promise<CertificationRecord | null>;
  uploadCertificationDocument: (
    connectorId: string,
    file: File,
    uploadedBy?: string
  ) => Promise<CertificationRecord | null>;
}

export interface ConnectorConnectionState {
  testingConnection: boolean;
  testResult: ConnectionTestResult | null;
}

export interface ConnectorConnectionActions {
  testConnection: (connectorId: string, instanceUrl?: string, projectKey?: string) => Promise<ConnectionTestResult>;
  testProjectConnection: (
    projectId: string,
    connectorId: string,
    instanceUrl?: string,
    projectKey?: string
  ) => Promise<ConnectionTestResult>;
  clearTestResult: () => void;
}

export interface ConnectorFilterStateSlice {
  filter: ConnectorFilterState;
}

export interface ConnectorFilterActions {
  setFilter: (filter: Partial<ConnectorFilterState>) => void;
  setCertificationFilter: (filter: ConnectorFilterState['certificationFilter']) => void;
  resetFilter: () => void;
  getFilteredConnectors: () => Connector[];
  getFilteredProjectConnectors: (projectId: string) => Connector[];
}

export interface ConnectorModalState {
  selectedConnector: Connector | null;
  isModalOpen: boolean;
}

export interface ConnectorModalActions {
  openConnectorModal: (connector: Connector) => void;
  closeConnectorModal: () => void;
  getConnectorsByCategory: (category: ConnectorCategory) => Connector[];
  getEnabledConnectorForCategory: (category: ConnectorCategory) => Connector | undefined;
  applyTemplateConnectors: (config: { enabled: string[]; disabled: string[] }) => void;
}

// ─── Combined store state ─────────────────────────────────────────────────

export type ConnectorStoreState = ConnectorListState &
  ConnectorListActions &
  ConnectorConnectionState &
  ConnectorConnectionActions &
  ConnectorFilterStateSlice &
  ConnectorFilterActions &
  ConnectorModalState &
  ConnectorModalActions;
