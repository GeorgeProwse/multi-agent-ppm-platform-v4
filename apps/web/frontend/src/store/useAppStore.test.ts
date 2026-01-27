import { describe, it, expect, beforeEach } from 'vitest';
import { useAppStore } from './useAppStore';

describe('useAppStore', () => {
  beforeEach(() => {
    // Reset the store before each test
    useAppStore.setState({
      session: { authenticated: false, user: null, loading: true },
      currentSelection: null,
      currentActivity: null,
      openTabs: [],
      activeTabId: null,
      chatMessages: [],
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
    });
  });

  describe('session management', () => {
    it('should update session state', () => {
      const { setSession } = useAppStore.getState();

      setSession({ authenticated: true, loading: false });

      const { session } = useAppStore.getState();
      expect(session.authenticated).toBe(true);
      expect(session.loading).toBe(false);
    });
  });

  describe('selection management', () => {
    it('should set current selection', () => {
      const { setCurrentSelection } = useAppStore.getState();

      setCurrentSelection({
        type: 'project',
        id: 'test-project',
        name: 'Test Project',
      });

      const { currentSelection } = useAppStore.getState();
      expect(currentSelection).toEqual({
        type: 'project',
        id: 'test-project',
        name: 'Test Project',
      });
    });

    it('should clear current selection', () => {
      const { setCurrentSelection } = useAppStore.getState();

      setCurrentSelection({ type: 'project', id: 'test', name: 'Test' });
      setCurrentSelection(null);

      const { currentSelection } = useAppStore.getState();
      expect(currentSelection).toBeNull();
    });
  });

  describe('tab management', () => {
    it('should add a new tab', () => {
      const { addTab } = useAppStore.getState();

      addTab({
        id: 'tab-1',
        title: 'Test Tab',
        type: 'dashboard',
      });

      const { openTabs, activeTabId } = useAppStore.getState();
      expect(openTabs).toHaveLength(1);
      expect(openTabs[0].id).toBe('tab-1');
      expect(activeTabId).toBe('tab-1');
    });

    it('should not duplicate existing tab', () => {
      const { addTab } = useAppStore.getState();

      addTab({ id: 'tab-1', title: 'Test Tab', type: 'dashboard' });
      addTab({ id: 'tab-1', title: 'Test Tab', type: 'dashboard' });

      const { openTabs } = useAppStore.getState();
      expect(openTabs).toHaveLength(1);
    });

    it('should close a tab', () => {
      const { addTab, closeTab } = useAppStore.getState();

      addTab({ id: 'tab-1', title: 'Tab 1', type: 'dashboard' });
      addTab({ id: 'tab-2', title: 'Tab 2', type: 'dashboard' });
      closeTab('tab-1');

      const { openTabs, activeTabId } = useAppStore.getState();
      expect(openTabs).toHaveLength(1);
      expect(openTabs[0].id).toBe('tab-2');
      expect(activeTabId).toBe('tab-2');
    });
  });

  describe('chat messages', () => {
    it('should add a chat message', () => {
      const { addChatMessage } = useAppStore.getState();

      addChatMessage({ role: 'user', content: 'Hello' });

      const { chatMessages } = useAppStore.getState();
      expect(chatMessages).toHaveLength(1);
      expect(chatMessages[0].content).toBe('Hello');
      expect(chatMessages[0].role).toBe('user');
      expect(chatMessages[0].id).toBeDefined();
      expect(chatMessages[0].timestamp).toBeInstanceOf(Date);
    });

    it('should clear chat messages', () => {
      const { addChatMessage, clearChatMessages } = useAppStore.getState();

      addChatMessage({ role: 'user', content: 'Hello' });
      addChatMessage({ role: 'assistant', content: 'Hi!' });
      clearChatMessages();

      const { chatMessages } = useAppStore.getState();
      expect(chatMessages).toHaveLength(0);
    });
  });

  describe('panel toggle', () => {
    it('should toggle left panel', () => {
      const { toggleLeftPanel } = useAppStore.getState();

      expect(useAppStore.getState().leftPanelCollapsed).toBe(false);
      toggleLeftPanel();
      expect(useAppStore.getState().leftPanelCollapsed).toBe(true);
      toggleLeftPanel();
      expect(useAppStore.getState().leftPanelCollapsed).toBe(false);
    });

    it('should toggle right panel', () => {
      const { toggleRightPanel } = useAppStore.getState();

      expect(useAppStore.getState().rightPanelCollapsed).toBe(false);
      toggleRightPanel();
      expect(useAppStore.getState().rightPanelCollapsed).toBe(true);
      toggleRightPanel();
      expect(useAppStore.getState().rightPanelCollapsed).toBe(false);
    });
  });
});
