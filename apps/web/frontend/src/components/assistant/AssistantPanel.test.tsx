import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AssistantPanel } from './AssistantPanel';
import { useAssistantStore } from '@/store/assistant';
import { useMethodologyStore } from '@/store/methodology';
import { useAppStore } from '@/store/useAppStore';

const mockFetch = () =>
  vi.fn((input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes('/v1/api/llm/models')) {
      return Promise.resolve(new Response(JSON.stringify({ models: [{ provider: 'openai', model_id: 'gpt-4o-mini', display_name: 'GPT-4o Mini' }] }), { status: 200 }));
    }
    if (url.includes('/v1/api/llm/preferences')) {
      return Promise.resolve(new Response(JSON.stringify({ provider: 'openai', model_id: 'gpt-4o-mini' }), { status: 200 }));
    }
    return Promise.resolve(new Response(JSON.stringify({ suggestions: [], context: {}, generated_by: 'test' }), { status: 200 }));
  });

describe('AssistantPanel quick actions', () => {
  beforeEach(() => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(mockFetch());
    useAppStore.setState({
      session: {
        authenticated: true,
        loading: false,
        user: { id: 'u1', name: 'PMO', email: 'pmo@example.com', tenantId: 'tenant-a', roles: ['PMO_ADMIN'], permissions: ['config.manage'] },
      },
    });
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      value: vi.fn(),
      writable: true,
    });
    useMethodologyStore.getState().setCurrentActivity('act-charter');
  });

  afterEach(() => {
    useAssistantStore.setState({
      messages: [],
      actionChips: [],
      context: null,
      isGeneratingSuggestions: false,
    });
    vi.restoreAllMocks();
  });

  it('renders quick actions when assistant store has chips', async () => {
    useAssistantStore.setState({
      actionChips: [
        {
          id: 'qa-1',
          label: 'Open Charter',
          category: 'navigate',
          priority: 'high',
          actionType: 'open_activity',
          payload: { type: 'open_activity', activityId: 'act-charter' },
          enabled: true,
        },
      ],
    });

    render(
      <MemoryRouter>
        <AssistantPanel />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(useAssistantStore.getState().isGeneratingSuggestions).toBe(false);
    });

    expect(screen.getByLabelText(/select model/i)).toBeInTheDocument();
  });

  it('disables project default button for unauthorized users', async () => {
    useAppStore.setState({
      session: {
        authenticated: true,
        loading: false,
        user: { id: 'u2', name: 'User', email: 'u@example.com', tenantId: 'tenant-a', roles: ['TEAM_MEMBER'], permissions: ['portfolio.view'] },
      },
    });

    render(
      <MemoryRouter>
        <AssistantPanel />
      </MemoryRouter>
    );

    const button = await screen.findByRole('button', { name: /set project default/i });
    expect(button).toBeDisabled();
  });
});
