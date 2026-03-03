import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { WorkspacePage } from './WorkspacePage';

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: 'test-workspace-1' }),
    useNavigate: () => vi.fn(),
  };
});

vi.mock('@/store', () => ({
  useAppStore: () => ({
    selectedEntity: null,
    setSelectedEntity: vi.fn(),
    setCurrentSelection: vi.fn(),
    currentActivity: null,
    addTab: vi.fn(),
    openTabs: [],
    demoMode: true,
    featureFlags: { scenario_modeling: false, multi_agent_collab: false },
  }),
}));

describe('WorkspacePage', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
  });

  it('renders without crashing for portfolio type', () => {
    render(
      <MemoryRouter>
        <WorkspacePage type="portfolio" />
      </MemoryRouter>
    );

    // Should render some content without throwing
    expect(document.body).toBeTruthy();
  });

  it('renders without crashing for project type', () => {
    render(
      <MemoryRouter>
        <WorkspacePage type="project" />
      </MemoryRouter>
    );

    expect(document.body).toBeTruthy();
  });
});
