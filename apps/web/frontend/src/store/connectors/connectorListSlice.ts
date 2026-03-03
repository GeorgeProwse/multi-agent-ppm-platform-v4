/**
 * Connector List Slice
 *
 * State and actions for connector list operations, CRUD,
 * categories, certifications, and MCP configuration.
 */

import type { StateCreator } from 'zustand';
import type { CertificationRecord, McpToolSchema } from './types';
import type { ConnectorStoreState, ConnectorListState, ConnectorListActions } from './connectorStoreTypes';
import { API_BASE } from './connectorStoreTypes';
import {
  mapConnectorResponses,
  getMockConnectors,
  getDefaultCategories,
  updateConnectorConfigState,
  updateProjectMcpState,
  getProjectConnector,
  buildProjectConnectorConfigPayload,
  buildProjectMcpConfigPayload,
} from './connectorHelpers';

export type ConnectorListSlice = ConnectorListState & ConnectorListActions;

export const createConnectorListSlice: StateCreator<
  ConnectorStoreState,
  [],
  [],
  ConnectorListSlice
> = (set, get) => ({
  // ── Initial state ───────────────────────────────────────────────────
  connectors: [],
  connectorsLoading: false,
  connectorsError: null,
  projectConnectors: {},
  projectConnectorsLoading: {},
  projectConnectorsError: {},
  categories: [],
  categoriesLoading: false,
  certifications: {},
  certificationsLoading: false,
  certificationsError: null,
  mcpToolsBySystem: {},
  mcpToolsLoading: {},
  mcpToolsError: {},

  // ── Fetch all connectors ────────────────────────────────────────────
  fetchConnectors: async () => {
    set({ connectorsLoading: true, connectorsError: null });
    try {
      const response = await fetch(`${API_BASE}/connectors`);
      if (!response.ok) {
        const message = `Failed to fetch connectors: ${response.statusText}`;
        set({ connectorsError: message, connectorsLoading: false });
        return;
      }
      const data = await response.json();
      const mapped = mapConnectorResponses(data);
      set({ connectors: mapped, connectorsLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({ connectorsError: message, connectorsLoading: false });
      // Fall back to mock data only when the API is unreachable
      if (error instanceof TypeError && message.includes('Failed to fetch')) {
        set({ connectors: mapConnectorResponses(getMockConnectors()) });
      }
    }
  },

  fetchProjectConnectors: async (projectId) => {
    set((state) => ({
      projectConnectorsLoading: { ...state.projectConnectorsLoading, [projectId]: true },
      projectConnectorsError: { ...state.projectConnectorsError, [projectId]: null },
    }));
    try {
      const response = await fetch(`/api/projects/${projectId}/connectors`);
      if (!response.ok) {
        const message = `Failed to fetch connectors: ${response.statusText}`;
        set((state) => ({
          projectConnectorsError: { ...state.projectConnectorsError, [projectId]: message },
          projectConnectorsLoading: { ...state.projectConnectorsLoading, [projectId]: false },
        }));
        return;
      }
      const data = await response.json();
      const mapped = mapConnectorResponses(data);
      set((state) => ({
        projectConnectors: { ...state.projectConnectors, [projectId]: mapped },
        projectConnectorsLoading: { ...state.projectConnectorsLoading, [projectId]: false },
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set((state) => ({
        projectConnectorsError: { ...state.projectConnectorsError, [projectId]: message },
        projectConnectorsLoading: { ...state.projectConnectorsLoading, [projectId]: false },
      }));
      // Fall back to mock data only when the API is unreachable
      if (error instanceof TypeError && message.includes('Failed to fetch')) {
        set((state) => ({
          projectConnectors: {
            ...state.projectConnectors,
            [projectId]: mapConnectorResponses(getMockConnectors()),
          },
        }));
      }
    }
  },

  // ── Fetch categories ────────────────────────────────────────────────
  fetchCategories: async () => {
    set({ categoriesLoading: true });
    try {
      const response = await fetch(`${API_BASE}/connectors/categories`);
      if (!response.ok) {
        throw new Error(`Failed to fetch categories: ${response.statusText}`);
      }
      const data = await response.json();
      set({ categories: data, categoriesLoading: false });
    } catch (error) {
      set({ categoriesLoading: false });
      // Use default categories
      set({ categories: getDefaultCategories() });
    }
  },

  // ── Fetch certifications ────────────────────────────────────────────
  fetchCertifications: async () => {
    set({ certificationsLoading: true, certificationsError: null });
    try {
      const response = await fetch(`${API_BASE}/certifications`);
      if (!response.ok) {
        throw new Error(`Failed to fetch certifications: ${response.statusText}`);
      }
      const data = (await response.json()) as CertificationRecord[];
      const mapped = data.reduce<Record<string, CertificationRecord>>((acc, record) => {
        acc[record.connector_id] = record;
        return acc;
      }, {});
      set({ certifications: mapped, certificationsLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set({ certificationsError: message, certificationsLoading: false });
    }
  },

  // ── Fetch MCP tools ─────────────────────────────────────────────────
  fetchMcpTools: async (system) => {
    if (get().mcpToolsBySystem[system]) return;
    set((state) => ({
      mcpToolsLoading: { ...state.mcpToolsLoading, [system]: true },
      mcpToolsError: { ...state.mcpToolsError, [system]: null },
    }));
    try {
      const response = await fetch(`${API_BASE}/mcp/servers/${system}/tools`);
      if (!response.ok) {
        throw new Error(`Failed to fetch MCP tools: ${response.statusText}`);
      }
      const data = (await response.json()) as { tools: McpToolSchema[] };
      set((state) => ({
        mcpToolsBySystem: { ...state.mcpToolsBySystem, [system]: data.tools },
        mcpToolsLoading: { ...state.mcpToolsLoading, [system]: false },
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      set((state) => ({
        mcpToolsLoading: { ...state.mcpToolsLoading, [system]: false },
        mcpToolsError: { ...state.mcpToolsError, [system]: message },
      }));
    }
  },

  // ── Getters ─────────────────────────────────────────────────────────
  getConnector: (connectorId) => {
    return get().connectors.find((c) => c.connector_id === connectorId);
  },

  getCertification: (connectorId) => {
    return get().certifications[connectorId];
  },

  // ── Update connector configuration ──────────────────────────────────
  updateConnectorConfig: async (connectorId, config) => {
    try {
      const response = await fetch(`${API_BASE}/connectors/${connectorId}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        throw new Error(`Failed to update connector: ${response.statusText}`);
      }
      // Refresh connectors
      await get().fetchConnectors();
    } catch (error) {
      // Update locally for development
      set((state) => ({
        connectors: updateConnectorConfigState(state.connectors, connectorId, config),
      }));
    }
  },

  updateProjectConnectorConfig: async (projectId, connectorId, config) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/connectors/${connectorId}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        throw new Error(`Failed to update connector: ${response.statusText}`);
      }
      await get().fetchProjectConnectors(projectId);
    } catch (error) {
      set((state) => ({
        projectConnectors: {
          ...state.projectConnectors,
          [projectId]: updateConnectorConfigState(
            state.projectConnectors[projectId] || [],
            connectorId,
            config
          ),
        },
      }));
    }
  },

  // ── Certification actions ───────────────────────────────────────────
  updateCertification: async (connectorId, payload) => {
    try {
      const response = await fetch(`${API_BASE}/certifications/${connectorId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`Failed to update certification: ${response.statusText}`);
      }
      const record = (await response.json()) as CertificationRecord;
      set((state) => ({
        certifications: { ...state.certifications, [connectorId]: record },
      }));
      return record;
    } catch (error) {
      return null;
    }
  },

  uploadCertificationDocument: async (connectorId, file, uploadedBy) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (uploadedBy) {
        formData.append('uploaded_by', uploadedBy);
      }
      const response = await fetch(`${API_BASE}/certifications/${connectorId}/documents`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error(`Failed to upload certification evidence: ${response.statusText}`);
      }
      const record = (await response.json()) as CertificationRecord;
      set((state) => ({
        certifications: { ...state.certifications, [connectorId]: record },
      }));
      return record;
    } catch (error) {
      return null;
    }
  },

  // ── Enable / Disable ────────────────────────────────────────────────
  enableConnector: async (connectorId) => {
    try {
      const response = await fetch(`${API_BASE}/connectors/${connectorId}/enable`, {
        method: 'POST',
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to enable connector: ${response.statusText}`);
      }
      // Refresh connectors
      await get().fetchConnectors();
    } catch (error) {
      // Update locally for development with mutual exclusivity
      const connector = get().getConnector(connectorId);
      if (!connector) return;

      set((state) => ({
        connectors: state.connectors.map((c) => {
          if (c.connector_id === connectorId) {
            return { ...c, enabled: true };
          }
          // Disable others in same category
          if (c.category === connector.category && c.enabled) {
            return { ...c, enabled: false };
          }
          return c;
        }),
      }));
    }
  },

  enableProjectConnector: async (projectId, connectorId) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/connectors/${connectorId}/enable`, {
        method: 'POST',
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to enable connector: ${response.statusText}`);
      }
      await get().fetchProjectConnectors(projectId);
    } catch (error) {
      const connector = (get().projectConnectors[projectId] || []).find(
        (item) => item.connector_id === connectorId
      );
      if (!connector) return;
      set((state) => ({
        projectConnectors: {
          ...state.projectConnectors,
          [projectId]: (state.projectConnectors[projectId] || []).map((c) => {
            if (c.connector_id === connectorId) {
              return { ...c, enabled: true };
            }
            if (c.category === connector.category && c.enabled) {
              return { ...c, enabled: false };
            }
            return c;
          }),
        },
      }));
    }
  },

  disableConnector: async (connectorId) => {
    try {
      const response = await fetch(`${API_BASE}/connectors/${connectorId}/disable`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to disable connector: ${response.statusText}`);
      }
      // Refresh connectors
      await get().fetchConnectors();
    } catch (error) {
      // Update locally for development
      set((state) => ({
        connectors: state.connectors.map((c) =>
          c.connector_id === connectorId ? { ...c, enabled: false } : c
        ),
      }));
    }
  },

  disableProjectConnector: async (projectId, connectorId) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/connectors/${connectorId}/disable`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to disable connector: ${response.statusText}`);
      }
      await get().fetchProjectConnectors(projectId);
    } catch (error) {
      set((state) => ({
        projectConnectors: {
          ...state.projectConnectors,
          [projectId]: (state.projectConnectors[projectId] || []).map((c) =>
            c.connector_id === connectorId ? { ...c, enabled: false } : c
          ),
        },
      }));
    }
  },

  // ── MCP project operations ──────────────────────────────────────────
  setProjectMcpEnabled: async (projectId, connectorId, enabled, payload) => {
    const connector = getProjectConnector(get(), projectId, connectorId);
    if (!connector) return;
    try {
      if (enabled) {
        const mcpPayload = buildProjectMcpConfigPayload(connector, payload);
        const response = await fetch(
          `${API_BASE}/projects/${projectId}/connectors/${connector.system}/mcp`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mcpPayload),
          }
        );
        if (!response.ok) {
          throw new Error(`Failed to enable MCP: ${response.statusText}`);
        }
      } else {
        const fallbackPayload = buildProjectConnectorConfigPayload(connector, { mcp_enabled: false });
        const response = await fetch(`/api/projects/${projectId}/connectors/${connectorId}/config`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(fallbackPayload),
        });
        if (!response.ok) {
          throw new Error(`Failed to disable MCP: ${response.statusText}`);
        }
      }
      await get().fetchProjectConnectors(projectId);
    } catch (error) {
      set((state) => ({
        projectConnectors: {
          ...state.projectConnectors,
          [projectId]: updateProjectMcpState(
            state.projectConnectors[projectId] || [],
            connector,
            {
              mcp_enabled: enabled,
              mcp_server_id: payload?.mcp_server_id,
              mcp_server_url: payload?.mcp_server_url,
              mcp_tool_map: payload?.mcp_tool_map,
            }
          ),
        },
      }));
    }
  },

  updateProjectMcpToolMap: async (projectId, connectorId, toolMap, payload) => {
    const connector = getProjectConnector(get(), projectId, connectorId);
    if (!connector) return;
    try {
      const mcpPayload = buildProjectMcpConfigPayload(connector, {
        mcp_server_id: payload?.mcp_server_id,
        mcp_server_url: payload?.mcp_server_url,
        mcp_tool_map: toolMap,
      });
      const response = await fetch(
        `${API_BASE}/projects/${projectId}/connectors/${connector.system}/mcp`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mcpPayload),
        }
      );
      if (!response.ok) {
        throw new Error(`Failed to update MCP tool map: ${response.statusText}`);
      }
      await get().fetchProjectConnectors(projectId);
    } catch (error) {
      set((state) => ({
        projectConnectors: {
          ...state.projectConnectors,
          [projectId]: updateProjectMcpState(
            state.projectConnectors[projectId] || [],
            connector,
            {
              mcp_tool_map: toolMap,
              mcp_server_id: payload?.mcp_server_id,
              mcp_server_url: payload?.mcp_server_url,
            }
          ),
        },
      }));
    }
  },
});
