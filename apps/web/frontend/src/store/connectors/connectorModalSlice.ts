/**
 * Connector Modal Slice
 *
 * State and actions for the connector detail modal,
 * category helpers, and template application.
 */

import type { StateCreator } from 'zustand';
import type { ConnectorCategory } from './types';
import type { ConnectorStoreState, ConnectorModalState, ConnectorModalActions } from './connectorStoreTypes';
import { mapConnectorResponses, getMockConnectors } from './connectorHelpers';

export type ConnectorModalSlice = ConnectorModalState & ConnectorModalActions;

export const createConnectorModalSlice: StateCreator<
  ConnectorStoreState,
  [],
  [],
  ConnectorModalSlice
> = (set, get) => ({
  // ── Initial state ───────────────────────────────────────────────────
  selectedConnector: null,
  isModalOpen: false,

  // ── Open connector modal ────────────────────────────────────────────
  openConnectorModal: (connector) => {
    set({ selectedConnector: connector, isModalOpen: true, testResult: null });
  },

  // ── Close connector modal ───────────────────────────────────────────
  closeConnectorModal: () => {
    set({ selectedConnector: null, isModalOpen: false, testResult: null });
  },

  // ── Apply template connectors ───────────────────────────────────────
  applyTemplateConnectors: (config) => {
    set((state) => {
      const enabledSet = new Set(config.enabled);
      const disabledSet = new Set(config.disabled);
      const baseConnectors =
        state.connectors.length > 0 ? state.connectors : mapConnectorResponses(getMockConnectors());

      const updated = baseConnectors.map((connector) => {
        if (enabledSet.has(connector.connector_id)) {
          return { ...connector, enabled: true };
        }
        if (disabledSet.has(connector.connector_id)) {
          return { ...connector, enabled: false };
        }
        return connector;
      });

      const seenCategories = new Set<ConnectorCategory>();
      const normalized = updated.map((connector) => {
        if (!connector.enabled) return connector;
        if (seenCategories.has(connector.category)) {
          return { ...connector, enabled: false };
        }
        seenCategories.add(connector.category);
        return connector;
      });

      return { connectors: normalized };
    });
  },

  // ── Category helpers ────────────────────────────────────────────────
  getConnectorsByCategory: (category) => {
    return get().connectors.filter((c) => c.category === category);
  },

  getEnabledConnectorForCategory: (category) => {
    return get().connectors.find((c) => c.category === category && c.enabled);
  },
});
