import { describe, expect, it, beforeEach, vi } from 'vitest';
import { useAgentConfigStore, getMockAgents } from './useAgentConfigStore';
import type { AgentConfig, AgentParameter } from './types';

// Mock global fetch for API calls
global.fetch = vi.fn();

/** Helper to build a minimal AgentConfig object for testing. */
function makeAgent(overrides: Partial<AgentConfig> = {}): AgentConfig {
  return {
    catalog_id: 'test-agent',
    agent_id: 'test',
    display_name: 'Test Agent',
    description: 'A test agent',
    category: 'core',
    enabled: true,
    capabilities: ['test_capability'],
    parameters: [],
    ...overrides,
  };
}

/** Helper to build a minimal AgentParameter for testing. */
function makeParameter(overrides: Partial<AgentParameter> = {}): AgentParameter {
  return {
    name: 'test_param',
    display_name: 'Test Parameter',
    description: 'A test parameter',
    param_type: 'string',
    default_value: 'default',
    current_value: 'current',
    required: true,
    ...overrides,
  };
}

describe('useAgentConfigStore', () => {
  beforeEach(() => {
    // Reset store data between tests - do NOT use replace (true) which strips action functions
    useAgentConfigStore.setState({
      agents: [],
      agentsLoading: false,
      agentsError: null,
      projectConfigs: {},
      projectConfigsLoading: false,
      currentUser: null,
      canConfigure: false,
      filter: {
        search: '',
        category: 'all',
        enabledOnly: false,
        sortBy: 'name',
      },
      selectedAgent: null,
      isModalOpen: false,
    });
    vi.resetAllMocks();
  });

  describe('initial state', () => {
    it('should have empty agents array', () => {
      const state = useAgentConfigStore.getState();
      expect(state.agents).toEqual([]);
    });

    it('should have loading flags set to false', () => {
      const state = useAgentConfigStore.getState();
      expect(state.agentsLoading).toBe(false);
      expect(state.projectConfigsLoading).toBe(false);
    });

    it('should have null error state', () => {
      const state = useAgentConfigStore.getState();
      expect(state.agentsError).toBeNull();
    });

    it('should have default filter state', () => {
      const state = useAgentConfigStore.getState();
      expect(state.filter).toEqual({
        search: '',
        category: 'all',
        enabledOnly: false,
        sortBy: 'name',
      });
    });

    it('should have modal closed and no selected agent', () => {
      const state = useAgentConfigStore.getState();
      expect(state.isModalOpen).toBe(false);
      expect(state.selectedAgent).toBeNull();
    });

    it('should have no current user and canConfigure false', () => {
      const state = useAgentConfigStore.getState();
      expect(state.currentUser).toBeNull();
      expect(state.canConfigure).toBe(false);
    });

    it('should have empty projectConfigs', () => {
      const state = useAgentConfigStore.getState();
      expect(state.projectConfigs).toEqual({});
    });
  });

  describe('fetchAgents', () => {
    it('should set loading state while fetching', async () => {
      const mockResponse = new Response(JSON.stringify([]), { status: 200 });
      vi.mocked(fetch).mockResolvedValue(mockResponse);

      const fetchPromise = useAgentConfigStore.getState().fetchAgents();
      expect(useAgentConfigStore.getState().agentsLoading).toBe(true);

      await fetchPromise;
      expect(useAgentConfigStore.getState().agentsLoading).toBe(false);
    });

    it('should populate agents on successful response', async () => {
      const mockAgents = [
        makeAgent({ catalog_id: 'agent-1', agent_id: 'a1', display_name: 'Agent One' }),
      ];
      const mockResponse = new Response(JSON.stringify(mockAgents), { status: 200 });
      vi.mocked(fetch).mockResolvedValue(mockResponse);

      await useAgentConfigStore.getState().fetchAgents();

      const state = useAgentConfigStore.getState();
      expect(state.agents.length).toBe(1);
      expect(state.agents[0].catalog_id).toBe('agent-1');
      expect(state.agentsLoading).toBe(false);
      expect(state.agentsError).toBeNull();
    });

    it('should set error and fall back to mock agents when API response is not ok', async () => {
      const mockResponse = new Response(null, { status: 500, statusText: 'Internal Server Error' });
      vi.mocked(fetch).mockResolvedValue(mockResponse);

      await useAgentConfigStore.getState().fetchAgents();

      const state = useAgentConfigStore.getState();
      expect(state.agentsError).toBe('Failed to fetch agents: Internal Server Error');
      expect(state.agentsLoading).toBe(false);
      // Should fall back to mock agents
      expect(state.agents.length).toBeGreaterThan(0);
    });

    it('should set error and fall back to mock agents when fetch throws', async () => {
      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().fetchAgents();

      const state = useAgentConfigStore.getState();
      expect(state.agentsError).toBe('Network error');
      expect(state.agentsLoading).toBe(false);
      // Should fall back to mock agents
      expect(state.agents.length).toBeGreaterThan(0);
    });
  });

  describe('getAgent', () => {
    it('should find an agent by catalog_id', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'agent-1', display_name: 'Agent One' }),
          makeAgent({ catalog_id: 'agent-2', display_name: 'Agent Two' }),
        ],
      });

      const agent = useAgentConfigStore.getState().getAgent('agent-1');
      expect(agent?.display_name).toBe('Agent One');
    });

    it('should return undefined for unknown catalog_id', () => {
      useAgentConfigStore.setState({
        agents: [makeAgent({ catalog_id: 'agent-1' })],
      });

      const agent = useAgentConfigStore.getState().getAgent('nonexistent');
      expect(agent).toBeUndefined();
    });
  });

  describe('updateAgent', () => {
    it('should update agent locally when API call fails', async () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'agent-1', display_name: 'Old Name', enabled: true }),
        ],
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().updateAgent('agent-1', { display_name: 'New Name' });

      const agent = useAgentConfigStore.getState().getAgent('agent-1');
      expect(agent?.display_name).toBe('New Name');
    });

    it('should update agent from API response on success', async () => {
      const updatedAgent = makeAgent({ catalog_id: 'agent-1', display_name: 'Updated Name' });
      useAgentConfigStore.setState({
        agents: [makeAgent({ catalog_id: 'agent-1', display_name: 'Old Name' })],
      });

      const mockResponse = new Response(JSON.stringify(updatedAgent), { status: 200 });
      vi.mocked(fetch).mockResolvedValue(mockResponse);

      await useAgentConfigStore.getState().updateAgent('agent-1', { display_name: 'Updated Name' });

      const agent = useAgentConfigStore.getState().getAgent('agent-1');
      expect(agent?.display_name).toBe('Updated Name');
    });

    it('should not modify other agents when updating one', async () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'agent-1', display_name: 'Agent One' }),
          makeAgent({ catalog_id: 'agent-2', display_name: 'Agent Two' }),
        ],
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().updateAgent('agent-1', { display_name: 'Updated' });

      const agent2 = useAgentConfigStore.getState().getAgent('agent-2');
      expect(agent2?.display_name).toBe('Agent Two');
    });
  });

  describe('toggleAgentEnabled', () => {
    it('should toggle agent from enabled to disabled', async () => {
      useAgentConfigStore.setState({
        agents: [makeAgent({ catalog_id: 'agent-1', enabled: true })],
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().toggleAgentEnabled('agent-1');

      const agent = useAgentConfigStore.getState().getAgent('agent-1');
      expect(agent?.enabled).toBe(false);
    });

    it('should toggle agent from disabled to enabled', async () => {
      useAgentConfigStore.setState({
        agents: [makeAgent({ catalog_id: 'agent-1', enabled: false })],
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().toggleAgentEnabled('agent-1');

      const agent = useAgentConfigStore.getState().getAgent('agent-1');
      expect(agent?.enabled).toBe(true);
    });

    it('should be a no-op for nonexistent agent', async () => {
      useAgentConfigStore.setState({
        agents: [makeAgent({ catalog_id: 'agent-1', enabled: true })],
      });

      await useAgentConfigStore.getState().toggleAgentEnabled('nonexistent');

      const agent = useAgentConfigStore.getState().getAgent('agent-1');
      expect(agent?.enabled).toBe(true);
    });
  });

  describe('fetchProjectConfigs', () => {
    it('should set projectConfigsLoading while fetching', async () => {
      const mockResponse = new Response(JSON.stringify([]), { status: 200 });
      vi.mocked(fetch).mockResolvedValue(mockResponse);

      const fetchPromise = useAgentConfigStore.getState().fetchProjectConfigs('proj-1');
      expect(useAgentConfigStore.getState().projectConfigsLoading).toBe(true);

      await fetchPromise;
      expect(useAgentConfigStore.getState().projectConfigsLoading).toBe(false);
    });

    it('should store project configs under the project ID', async () => {
      const mockConfigs = [
        { project_id: 'proj-1', agent_id: 'agent-1', enabled: true, parameter_overrides: {} },
      ];
      const mockResponse = new Response(JSON.stringify(mockConfigs), { status: 200 });
      vi.mocked(fetch).mockResolvedValue(mockResponse);

      await useAgentConfigStore.getState().fetchProjectConfigs('proj-1');

      const state = useAgentConfigStore.getState();
      expect(state.projectConfigs['proj-1']).toHaveLength(1);
      expect(state.projectConfigs['proj-1'][0].agent_id).toBe('agent-1');
    });

    it('should initialize empty array for project on API failure', async () => {
      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().fetchProjectConfigs('proj-1');

      const state = useAgentConfigStore.getState();
      expect(state.projectConfigs['proj-1']).toEqual([]);
      expect(state.projectConfigsLoading).toBe(false);
    });
  });

  describe('setProjectAgentEnabled', () => {
    it('should update project agent config locally on API failure', async () => {
      useAgentConfigStore.setState({
        projectConfigs: { 'proj-1': [] },
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().setProjectAgentEnabled('proj-1', 'agent-1', true);

      const state = useAgentConfigStore.getState();
      const config = state.projectConfigs['proj-1'].find((c) => c.agent_id === 'agent-1');
      expect(config?.enabled).toBe(true);
    });

    it('should update existing project agent config', async () => {
      useAgentConfigStore.setState({
        projectConfigs: {
          'proj-1': [
            { project_id: 'proj-1', agent_id: 'agent-1', enabled: true, parameter_overrides: {} },
          ],
        },
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().setProjectAgentEnabled('proj-1', 'agent-1', false);

      const state = useAgentConfigStore.getState();
      const config = state.projectConfigs['proj-1'].find((c) => c.agent_id === 'agent-1');
      expect(config?.enabled).toBe(false);
    });

    it('should add new config when agent not yet in project configs', async () => {
      useAgentConfigStore.setState({
        projectConfigs: {
          'proj-1': [
            { project_id: 'proj-1', agent_id: 'agent-1', enabled: true, parameter_overrides: {} },
          ],
        },
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().setProjectAgentEnabled('proj-1', 'agent-2', true);

      const state = useAgentConfigStore.getState();
      expect(state.projectConfigs['proj-1']).toHaveLength(2);
      const config = state.projectConfigs['proj-1'].find((c) => c.agent_id === 'agent-2');
      expect(config?.enabled).toBe(true);
    });
  });

  describe('applyTemplateAgents', () => {
    it('should set enabled and disabled agents for a project', () => {
      useAgentConfigStore.getState().applyTemplateAgents('proj-1', {
        enabled: ['agent-1', 'agent-2'],
        disabled: ['agent-3'],
      });

      const state = useAgentConfigStore.getState();
      const configs = state.projectConfigs['proj-1'];
      expect(configs).toHaveLength(3);

      const agent1 = configs.find((c) => c.agent_id === 'agent-1');
      const agent2 = configs.find((c) => c.agent_id === 'agent-2');
      const agent3 = configs.find((c) => c.agent_id === 'agent-3');
      expect(agent1?.enabled).toBe(true);
      expect(agent2?.enabled).toBe(true);
      expect(agent3?.enabled).toBe(false);
    });

    it('should overwrite existing project configs', () => {
      useAgentConfigStore.setState({
        projectConfigs: {
          'proj-1': [
            { project_id: 'proj-1', agent_id: 'old-agent', enabled: true, parameter_overrides: {} },
          ],
        },
      });

      useAgentConfigStore.getState().applyTemplateAgents('proj-1', {
        enabled: ['new-agent'],
        disabled: [],
      });

      const state = useAgentConfigStore.getState();
      const configs = state.projectConfigs['proj-1'];
      expect(configs).toHaveLength(1);
      expect(configs[0].agent_id).toBe('new-agent');
    });
  });

  describe('isAgentEnabledForProject', () => {
    it('should return project-specific config when available', () => {
      useAgentConfigStore.setState({
        agents: [makeAgent({ agent_id: 'agent-1', enabled: true })],
        projectConfigs: {
          'proj-1': [
            { project_id: 'proj-1', agent_id: 'agent-1', enabled: false, parameter_overrides: {} },
          ],
        },
      });

      const result = useAgentConfigStore.getState().isAgentEnabledForProject('proj-1', 'agent-1');
      expect(result).toBe(false);
    });

    it('should fall back to global agent config when no project config exists', () => {
      useAgentConfigStore.setState({
        agents: [makeAgent({ agent_id: 'agent-1', enabled: true })],
        projectConfigs: {},
      });

      const result = useAgentConfigStore.getState().isAgentEnabledForProject('proj-1', 'agent-1');
      expect(result).toBe(true);
    });

    it('should return true by default when neither project nor global config exists', () => {
      useAgentConfigStore.setState({
        agents: [],
        projectConfigs: {},
      });

      const result = useAgentConfigStore.getState().isAgentEnabledForProject('proj-1', 'agent-1');
      expect(result).toBe(true);
    });
  });

  describe('getEnabledAgentsForProject', () => {
    it('should return only enabled agents for a project', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ agent_id: 'agent-1', catalog_id: 'cat-1', enabled: true }),
          makeAgent({ agent_id: 'agent-2', catalog_id: 'cat-2', enabled: true }),
        ],
        projectConfigs: {
          'proj-1': [
            { project_id: 'proj-1', agent_id: 'agent-1', enabled: true, parameter_overrides: {} },
            { project_id: 'proj-1', agent_id: 'agent-2', enabled: false, parameter_overrides: {} },
          ],
        },
      });

      const enabledAgents = useAgentConfigStore.getState().getEnabledAgentsForProject('proj-1');
      expect(enabledAgents).toHaveLength(1);
      expect(enabledAgents[0].agent_id).toBe('agent-1');
    });

    it('should return all agents when no project config exists (falls back to global)', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ agent_id: 'agent-1', enabled: true }),
          makeAgent({ agent_id: 'agent-2', enabled: true }),
        ],
        projectConfigs: {},
      });

      const enabledAgents = useAgentConfigStore.getState().getEnabledAgentsForProject('proj-1');
      expect(enabledAgents).toHaveLength(2);
    });
  });

  describe('setCurrentUser', () => {
    it('should set user from API response on success', async () => {
      const mockUser = {
        user_id: 'admin',
        name: 'PMO Admin',
        email: 'admin@example.com',
        role: 'PMO_ADMIN',
        tenant_id: 'default',
      };
      // First call: fetch user, second call: check can configure
      vi.mocked(fetch)
        .mockResolvedValueOnce(new Response(JSON.stringify(mockUser), { status: 200 }))
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ can_configure_agents: true }), { status: 200 })
        );

      await useAgentConfigStore.getState().setCurrentUser('admin');

      const state = useAgentConfigStore.getState();
      expect(state.currentUser?.user_id).toBe('admin');
      expect(state.currentUser?.role).toBe('PMO_ADMIN');
      expect(state.canConfigure).toBe(true);
    });

    it('should fall back to mock admin user on API failure', async () => {
      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().setCurrentUser('admin');

      const state = useAgentConfigStore.getState();
      expect(state.currentUser?.user_id).toBe('admin');
      expect(state.currentUser?.name).toBe('PMO Admin');
      expect(state.currentUser?.role).toBe('PMO_ADMIN');
      expect(state.canConfigure).toBe(true);
    });

    it('should fall back to mock PM user on API failure', async () => {
      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().setCurrentUser('pm');

      const state = useAgentConfigStore.getState();
      expect(state.currentUser?.user_id).toBe('pm');
      expect(state.currentUser?.name).toBe('Project Manager');
      expect(state.currentUser?.role).toBe('PM');
      expect(state.canConfigure).toBe(true);
    });

    it('should set canConfigure false for non-admin/pm users on API failure', async () => {
      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().setCurrentUser('viewer');

      const state = useAgentConfigStore.getState();
      expect(state.currentUser?.user_id).toBe('viewer');
      expect(state.canConfigure).toBe(false);
    });
  });

  describe('checkCanConfigure', () => {
    it('should set canConfigure false when no user is set', async () => {
      await useAgentConfigStore.getState().checkCanConfigure();

      expect(useAgentConfigStore.getState().canConfigure).toBe(false);
    });

    it('should set canConfigure from API response', async () => {
      useAgentConfigStore.setState({
        currentUser: {
          user_id: 'admin',
          name: 'Admin',
          email: 'admin@example.com',
          role: 'PMO_ADMIN',
          tenant_id: 'default',
        },
      });

      vi.mocked(fetch).mockResolvedValue(
        new Response(JSON.stringify({ can_configure_agents: true }), { status: 200 })
      );

      await useAgentConfigStore.getState().checkCanConfigure();

      expect(useAgentConfigStore.getState().canConfigure).toBe(true);
    });

    it('should fall back to role-based check on API failure for PMO_ADMIN', async () => {
      useAgentConfigStore.setState({
        currentUser: {
          user_id: 'admin',
          name: 'Admin',
          email: 'admin@example.com',
          role: 'PMO_ADMIN',
          tenant_id: 'default',
        },
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().checkCanConfigure();

      expect(useAgentConfigStore.getState().canConfigure).toBe(true);
    });

    it('should fall back to role-based check on API failure for TEAM_MEMBER', async () => {
      useAgentConfigStore.setState({
        currentUser: {
          user_id: 'member',
          name: 'Member',
          email: 'member@example.com',
          role: 'TEAM_MEMBER',
          tenant_id: 'default',
        },
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().checkCanConfigure();

      expect(useAgentConfigStore.getState().canConfigure).toBe(false);
    });
  });

  describe('filter actions', () => {
    it('should update filter with setFilter', () => {
      useAgentConfigStore.getState().setFilter({ search: 'schedule' });

      const state = useAgentConfigStore.getState();
      expect(state.filter.search).toBe('schedule');
      // Other filter values remain unchanged
      expect(state.filter.category).toBe('all');
      expect(state.filter.enabledOnly).toBe(false);
      expect(state.filter.sortBy).toBe('name');
    });

    it('should merge multiple filter fields', () => {
      useAgentConfigStore.getState().setFilter({ search: 'test', category: 'delivery' });

      const state = useAgentConfigStore.getState();
      expect(state.filter.search).toBe('test');
      expect(state.filter.category).toBe('delivery');
    });

    it('should reset filter to defaults', () => {
      useAgentConfigStore.getState().setFilter({
        search: 'test',
        category: 'portfolio',
        enabledOnly: true,
        sortBy: 'status',
      });
      useAgentConfigStore.getState().resetFilter();

      const state = useAgentConfigStore.getState();
      expect(state.filter).toEqual({
        search: '',
        category: 'all',
        enabledOnly: false,
        sortBy: 'name',
      });
    });
  });

  describe('getFilteredAgents', () => {
    it('should filter agents by search term in display_name', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', display_name: 'Schedule Agent', description: 'Plans' }),
          makeAgent({ catalog_id: 'a2', display_name: 'Risk Agent', description: 'Risks' }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ search: 'schedule' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered).toHaveLength(1);
      expect(filtered[0].catalog_id).toBe('a1');
    });

    it('should filter agents by search term in description', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', display_name: 'Agent A', description: 'Manages budgets' }),
          makeAgent({ catalog_id: 'a2', display_name: 'Agent B', description: 'Manages risks' }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ search: 'budgets' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered).toHaveLength(1);
      expect(filtered[0].catalog_id).toBe('a1');
    });

    it('should filter agents by search term in agent_id', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', agent_id: 'schedule-planning', display_name: 'Agent A', description: 'desc' }),
          makeAgent({ catalog_id: 'a2', agent_id: 'risk-mgmt', display_name: 'Agent B', description: 'desc' }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ search: 'schedule-planning' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered).toHaveLength(1);
      expect(filtered[0].catalog_id).toBe('a1');
    });

    it('should filter agents by category', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', category: 'delivery' }),
          makeAgent({ catalog_id: 'a2', category: 'portfolio' }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ category: 'portfolio' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered).toHaveLength(1);
      expect(filtered[0].catalog_id).toBe('a2');
    });

    it('should return all agents when category is "all"', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', category: 'delivery' }),
          makeAgent({ catalog_id: 'a2', category: 'portfolio' }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ category: 'all' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered).toHaveLength(2);
    });

    it('should filter agents by enabledOnly', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', enabled: true }),
          makeAgent({ catalog_id: 'a2', enabled: false }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ enabledOnly: true });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered).toHaveLength(1);
      expect(filtered[0].catalog_id).toBe('a1');
    });

    it('should sort agents by name', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', display_name: 'Zebra Agent' }),
          makeAgent({ catalog_id: 'a2', display_name: 'Alpha Agent' }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ sortBy: 'name' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered[0].display_name).toBe('Alpha Agent');
      expect(filtered[1].display_name).toBe('Zebra Agent');
    });

    it('should sort agents by category', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', category: 'portfolio' }),
          makeAgent({ catalog_id: 'a2', category: 'core' }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ sortBy: 'category' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered[0].category).toBe('core');
      expect(filtered[1].category).toBe('portfolio');
    });

    it('should sort agents by status (enabled first)', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', display_name: 'Disabled', enabled: false }),
          makeAgent({ catalog_id: 'a2', display_name: 'Enabled', enabled: true }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ sortBy: 'status' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered[0].enabled).toBe(true);
      expect(filtered[1].enabled).toBe(false);
    });

    it('should combine search and category filters', () => {
      useAgentConfigStore.setState({
        agents: [
          makeAgent({ catalog_id: 'a1', display_name: 'Schedule Agent', category: 'delivery' }),
          makeAgent({ catalog_id: 'a2', display_name: 'Schedule Tracker', category: 'portfolio' }),
          makeAgent({ catalog_id: 'a3', display_name: 'Risk Agent', category: 'delivery' }),
        ],
      });

      useAgentConfigStore.getState().setFilter({ search: 'schedule', category: 'delivery' });
      const filtered = useAgentConfigStore.getState().getFilteredAgents();
      expect(filtered).toHaveLength(1);
      expect(filtered[0].catalog_id).toBe('a1');
    });
  });

  describe('modal actions', () => {
    it('should open the agent modal', () => {
      const agent = makeAgent({ catalog_id: 'agent-1', display_name: 'Test Agent' });
      useAgentConfigStore.getState().openAgentModal(agent);

      const state = useAgentConfigStore.getState();
      expect(state.isModalOpen).toBe(true);
      expect(state.selectedAgent?.catalog_id).toBe('agent-1');
    });

    it('should close the agent modal and clear selected agent', () => {
      const agent = makeAgent({ catalog_id: 'agent-1' });
      useAgentConfigStore.getState().openAgentModal(agent);
      useAgentConfigStore.getState().closeAgentModal();

      const state = useAgentConfigStore.getState();
      expect(state.isModalOpen).toBe(false);
      expect(state.selectedAgent).toBeNull();
    });
  });

  describe('saveAgentConfig', () => {
    it('should update agent parameters and close modal', async () => {
      const params = [
        makeParameter({ name: 'threshold', current_value: 20 }),
      ];
      useAgentConfigStore.setState({
        agents: [makeAgent({ catalog_id: 'agent-1', parameters: [] })],
        selectedAgent: makeAgent({ catalog_id: 'agent-1' }),
        isModalOpen: true,
      });

      vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

      await useAgentConfigStore.getState().saveAgentConfig('agent-1', params);

      const state = useAgentConfigStore.getState();
      expect(state.isModalOpen).toBe(false);
      expect(state.selectedAgent).toBeNull();

      const agent = state.getAgent('agent-1');
      expect(agent?.parameters).toHaveLength(1);
      expect(agent?.parameters[0].name).toBe('threshold');
    });
  });

  describe('getMockAgents', () => {
    it('should return an array of mock agents', () => {
      const mockAgents = getMockAgents();
      expect(Array.isArray(mockAgents)).toBe(true);
      expect(mockAgents.length).toBeGreaterThan(0);
    });

    it('should include agents with expected structure', () => {
      const mockAgents = getMockAgents();
      const firstAgent = mockAgents[0];
      expect(firstAgent.catalog_id).toBeDefined();
      expect(firstAgent.agent_id).toBeDefined();
      expect(firstAgent.display_name).toBeDefined();
      expect(firstAgent.description).toBeDefined();
      expect(firstAgent.category).toBeDefined();
      expect(typeof firstAgent.enabled).toBe('boolean');
      expect(Array.isArray(firstAgent.capabilities)).toBe(true);
      expect(Array.isArray(firstAgent.parameters)).toBe(true);
    });

    it('should include agents from different categories', () => {
      const mockAgents = getMockAgents();
      const categories = new Set(mockAgents.map((a) => a.category));
      expect(categories.size).toBeGreaterThan(1);
    });
  });
});
