/**
 * Connector Filter Slice
 *
 * State and actions for search, filter, and connector
 * result computation.
 */

import type { StateCreator } from 'zustand';
import type { ConnectorStoreState, ConnectorFilterStateSlice, ConnectorFilterActions } from './connectorStoreTypes';
import { DEFAULT_FILTER } from './connectorStoreTypes';
import { matchesStatusFilter, matchesCertificationFilter } from './connectorHelpers';

export type ConnectorFilterSlice = ConnectorFilterStateSlice & ConnectorFilterActions;

export const createConnectorFilterSlice: StateCreator<
  ConnectorStoreState,
  [],
  [],
  ConnectorFilterSlice
> = (set, get) => ({
  // ── Initial state ───────────────────────────────────────────────────
  filter: DEFAULT_FILTER,

  // ── Set filter ──────────────────────────────────────────────────────
  setFilter: (filter) => {
    set((state) => ({
      filter: { ...state.filter, ...filter },
    }));
  },

  // ── Set certification filter ────────────────────────────────────────
  setCertificationFilter: (certificationFilter) => {
    set((state) => ({
      filter: { ...state.filter, certificationFilter },
    }));
  },

  // ── Reset filter ────────────────────────────────────────────────────
  resetFilter: () => {
    set({ filter: DEFAULT_FILTER });
  },

  // ── Get filtered connectors ─────────────────────────────────────────
  getFilteredConnectors: () => {
    const { connectors, filter } = get();
    let filtered = [...connectors];

    // Apply search filter
    if (filter.search) {
      const search = filter.search.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.name.toLowerCase().includes(search) ||
          c.description.toLowerCase().includes(search) ||
          c.connector_id.toLowerCase().includes(search)
      );
    }

    // Apply category filter
    if (filter.category !== 'all') {
      filtered = filtered.filter((c) => c.category === filter.category);
    }

    // Apply status filter
    if (filter.statusFilter !== 'all') {
      filtered = filtered.filter((c) => matchesStatusFilter(c, filter.statusFilter));
    }

    // Apply certification filter
    if (filter.certificationFilter !== 'all') {
      filtered = filtered.filter((c) =>
        matchesCertificationFilter(c, filter.certificationFilter)
      );
    }

    // Apply enabled filter
    if (filter.enabledOnly) {
      filtered = filtered.filter((c) => c.enabled);
    }

    return filtered;
  },

  // ── Get filtered project connectors ─────────────────────────────────
  getFilteredProjectConnectors: (projectId) => {
    const { projectConnectors, filter } = get();
    let filtered = [...(projectConnectors[projectId] || [])];

    if (filter.search) {
      const search = filter.search.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.name.toLowerCase().includes(search) ||
          c.description.toLowerCase().includes(search) ||
          c.connector_id.toLowerCase().includes(search)
      );
    }

    if (filter.category !== 'all') {
      filtered = filtered.filter((c) => c.category === filter.category);
    }

    if (filter.statusFilter !== 'all') {
      filtered = filtered.filter((c) => matchesStatusFilter(c, filter.statusFilter));
    }

    if (filter.certificationFilter !== 'all') {
      filtered = filtered.filter((c) =>
        matchesCertificationFilter(c, filter.certificationFilter)
      );
    }

    if (filter.enabledOnly) {
      filtered = filtered.filter((c) => c.enabled);
    }

    return filtered;
  },
});
