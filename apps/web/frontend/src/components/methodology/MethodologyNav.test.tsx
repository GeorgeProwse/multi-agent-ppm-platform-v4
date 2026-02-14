import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { useMethodologyStore } from '@/store/methodology';
import { MethodologyNav } from './MethodologyNav';

vi.mock('@/components/icon/Icon', () => ({
  Icon: ({ label }: { label?: string }) => <span>{label ?? 'icon'}</span>,
}));

describe('MethodologyNav', () => {
  it('renders compact stage/activity navigation', () => {
    render(<MemoryRouter><MethodologyNav /></MemoryRouter>);
    expect(screen.getAllByRole('button').length).toBeGreaterThan(0);
    expect(screen.queryByText('Template Runtime Mapping')).not.toBeInTheDocument();
  });

  it('selects activity and resolves runtime view without opening artifact', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/api/workspace/') && url.includes('/select')) {
        return new Response(JSON.stringify({ ok: true }), { status: 200 });
      }
      if (url.includes('/api/methodology/runtime/actions')) {
        return new Response(JSON.stringify({ actions: ['view'] }), { status: 200 });
      }
      if (url.includes('/api/methodology/runtime/resolve')) {
        return new Response(JSON.stringify({ resolution_contract: { canvas: { canvas_type: 'document', renderer_component: 'DocumentCanvas', default_view: 'edit' } } }), { status: 200 });
      }
      return new Response(JSON.stringify({}), { status: 200 });
    });
    vi.stubGlobal('fetch', fetchMock);

    const stage = useMethodologyStore.getState().projectMethodology.methodology.stages[0];
    useMethodologyStore.setState((state) => ({
      expandedStageIds: [stage.id],
      projectMethodology: {
        ...state.projectMethodology,
        methodology: {
          ...state.projectMethodology.methodology,
          stages: [{ ...stage, activities: [{ id: 'activity-runtime-test', name: 'Runtime Test Activity', status: 'not_started', canvasType: 'document', prerequisites: [], order: 1 }] }, ...state.projectMethodology.methodology.stages.slice(1)],
        },
      },
    }));

    render(<MemoryRouter><MethodologyNav /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: /Runtime Test Activity/i }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/workspace/'), expect.objectContaining({ method: 'POST' }));
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/methodology/runtime/resolve'), undefined);
    });
  });
});
