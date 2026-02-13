import { create } from 'zustand';
import type {
  EntitySelection,
  Activity,
  CanvasTab,
  ChatMessage,
  SessionState,
  FeatureFlags,
  TenantContextState,
} from './types';

interface AppState {
  // Session state
  session: SessionState;
  setSession: (session: Partial<SessionState>) => void;
  tenantContext: TenantContextState;
  setTenantContext: (context: Partial<TenantContextState>) => void;

  // Feature flags
  featureFlags: FeatureFlags;
  setFeatureFlags: (flags: FeatureFlags) => void;

  // Current selection (project/program/portfolio)
  currentSelection: EntitySelection | null;
  setCurrentSelection: (selection: EntitySelection | null) => void;

  // Current activity selection (methodology navigation)
  currentActivity: Activity | null;
  setCurrentActivity: (activity: Activity | null) => void;

  // Open canvas tabs
  openTabs: CanvasTab[];
  activeTabId: string | null;
  addTab: (tab: CanvasTab) => void;
  closeTab: (tabId: string) => void;
  setActiveTab: (tabId: string) => void;
  updateTab: (tabId: string, updates: Partial<CanvasTab>) => void;

  // Assistant chat messages
  chatMessages: ChatMessage[];
  addChatMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  clearChatMessages: () => void;

  // UI state
  leftPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;
  toggleLeftPanel: () => void;
  toggleRightPanel: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Session state
  session: {
    authenticated: false,
    user: null,
    loading: true,
  },
  setSession: (session) =>
    set((state) => ({
      session: { ...state.session, ...session },
    })),

  tenantContext: {
    tenantId: null,
    tenantName: null,
  },
  setTenantContext: (context) =>
    set((state) => ({
      tenantContext: { ...state.tenantContext, ...context },
    })),

  featureFlags: {},
  setFeatureFlags: (flags) => set({ featureFlags: flags }),

  // Current selection
  currentSelection: null,
  setCurrentSelection: (selection) =>
    set({ currentSelection: selection }),

  // Current activity
  currentActivity: null,
  setCurrentActivity: (activity) =>
    set({ currentActivity: activity }),

  // Canvas tabs
  openTabs: [],
  activeTabId: null,
  addTab: (tab) =>
    set((state) => {
      const existingTab = state.openTabs.find((t) => t.id === tab.id);
      if (existingTab) {
        return { activeTabId: tab.id };
      }
      return {
        openTabs: [...state.openTabs, tab],
        activeTabId: tab.id,
      };
    }),
  closeTab: (tabId) =>
    set((state) => {
      const newTabs = state.openTabs.filter((t) => t.id !== tabId);
      let newActiveId = state.activeTabId;
      if (state.activeTabId === tabId) {
        const closedIndex = state.openTabs.findIndex((t) => t.id === tabId);
        newActiveId = newTabs[closedIndex - 1]?.id ?? newTabs[0]?.id ?? null;
      }
      return { openTabs: newTabs, activeTabId: newActiveId };
    }),
  setActiveTab: (tabId) =>
    set({ activeTabId: tabId }),
  updateTab: (tabId, updates) =>
    set((state) => ({
      openTabs: state.openTabs.map((t) =>
        t.id === tabId ? { ...t, ...updates } : t
      ),
    })),

  // Chat messages
  chatMessages: [],
  addChatMessage: (message) =>
    set((state) => ({
      chatMessages: [
        ...state.chatMessages,
        {
          ...message,
          id: crypto.randomUUID(),
          timestamp: new Date(),
        },
      ],
    })),
  clearChatMessages: () =>
    set({ chatMessages: [] }),

  // UI state
  leftPanelCollapsed: false,
  rightPanelCollapsed: false,
  toggleLeftPanel: () =>
    set((state) => ({ leftPanelCollapsed: !state.leftPanelCollapsed })),
  toggleRightPanel: () =>
    set((state) => ({ rightPanelCollapsed: !state.rightPanelCollapsed })),
}));
