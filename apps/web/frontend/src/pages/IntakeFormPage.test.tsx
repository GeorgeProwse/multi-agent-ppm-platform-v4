import { render } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { IntakeFormPage } from './IntakeFormPage';

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useLocation: () => ({ pathname: '/intake', search: '', hash: '', state: null }),
    useNavigate: () => vi.fn(),
  };
});

vi.mock('@/store', () => ({
  useAppStore: () => ({
    selectedEntity: null,
    demoMode: true,
    featureFlags: { multimodal_intake: false },
    rightPanelCollapsed: false,
    toggleRightPanel: vi.fn(),
  }),
}));

vi.mock('@/store/assistant/useIntakeAssistantStore', () => ({
  useIntakeAssistantStore: () => ({
    messages: [],
    isLoading: false,
    sendMessage: vi.fn(),
    setContext: vi.fn(),
    clearContext: vi.fn(),
    pendingPatches: [],
    consumePatch: vi.fn(),
  }),
}));

describe('IntakeFormPage', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({}), { status: 200 })
    );
  });

  it('renders without crashing', () => {
    const { container } = render(
      <MemoryRouter>
        <IntakeFormPage />
      </MemoryRouter>
    );

    expect(container).toBeTruthy();
  });
});
