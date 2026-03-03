/**
 * Connector Store
 *
 * Zustand store for managing connector configurations,
 * connection testing, and category-based filtering.
 *
 * This is the composition layer that combines all connector
 * store slices into a single unified store. Individual slices
 * are defined in their own files:
 *
 *   - connectorListSlice.ts     — connector list, CRUD, categories, certifications, MCP
 *   - connectorConnectionSlice.ts — connection testing
 *   - connectorFilterSlice.ts   — search/filter state and operations
 *   - connectorModalSlice.ts    — modal, category helpers, template application
 *
 * Shared types live in connectorStoreTypes.ts.
 * Shared utilities live in connectorHelpers.ts.
 */

import { create } from 'zustand';
import type { ConnectorStoreState } from './connectorStoreTypes';
import { createConnectorListSlice } from './connectorListSlice';
import { createConnectorConnectionSlice } from './connectorConnectionSlice';
import { createConnectorFilterSlice } from './connectorFilterSlice';
import { createConnectorModalSlice } from './connectorModalSlice';

export const useConnectorStore = create<ConnectorStoreState>((...args) => ({
  ...createConnectorListSlice(...args),
  ...createConnectorConnectionSlice(...args),
  ...createConnectorFilterSlice(...args),
  ...createConnectorModalSlice(...args),
}));

export default useConnectorStore;
