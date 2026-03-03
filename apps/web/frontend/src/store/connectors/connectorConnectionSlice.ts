/**
 * Connector Connection Slice
 *
 * State and actions for connection testing operations.
 */

import type { StateCreator } from 'zustand';
import type { ConnectionTestResult } from './types';
import type { ConnectorStoreState, ConnectorConnectionState, ConnectorConnectionActions } from './connectorStoreTypes';
import { API_BASE } from './connectorStoreTypes';

export type ConnectorConnectionSlice = ConnectorConnectionState & ConnectorConnectionActions;

export const createConnectorConnectionSlice: StateCreator<
  ConnectorStoreState,
  [],
  [],
  ConnectorConnectionSlice
> = (set, get) => ({
  // ── Initial state ───────────────────────────────────────────────────
  testingConnection: false,
  testResult: null,

  // ── Test connection ─────────────────────────────────────────────────
  testConnection: async (connectorId, instanceUrl, projectKey) => {
    set({ testingConnection: true, testResult: null });
    try {
      const response = await fetch(`${API_BASE}/connectors/${connectorId}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instance_url: instanceUrl || '',
          project_key: projectKey || '',
        }),
      });

      const result: ConnectionTestResult = await response.json();
      set({ testResult: result, testingConnection: false });

      // If connection was successful, refresh connectors to get updated health status
      if (result.status === 'connected') {
        await get().fetchConnectors();
      }

      return result;
    } catch (error) {
      const result: ConnectionTestResult = {
        status: 'failed',
        message: error instanceof Error ? error.message : 'Connection test failed',
        details: {},
        tested_at: new Date().toISOString(),
      };
      set({ testResult: result, testingConnection: false });
      return result;
    }
  },

  // ── Test project connection ─────────────────────────────────────────
  testProjectConnection: async (projectId, connectorId, instanceUrl, projectKey) => {
    set({ testingConnection: true, testResult: null });
    try {
      const response = await fetch(`/api/projects/${projectId}/connectors/${connectorId}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instance_url: instanceUrl || '',
          project_key: projectKey || '',
        }),
      });

      const result: ConnectionTestResult = await response.json();
      set({ testResult: result, testingConnection: false });

      if (result.status === 'connected') {
        await get().fetchProjectConnectors(projectId);
      }

      return result;
    } catch (error) {
      const result: ConnectionTestResult = {
        status: 'failed',
        message: error instanceof Error ? error.message : 'Connection test failed',
        details: {},
        tested_at: new Date().toISOString(),
      };
      set({ testResult: result, testingConnection: false });
      return result;
    }
  },

  // ── Clear test result ───────────────────────────────────────────────
  clearTestResult: () => {
    set({ testResult: null });
  },
});
