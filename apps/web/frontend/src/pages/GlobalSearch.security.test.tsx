import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { GlobalSearchPage } from './GlobalSearch';

const { fetchGlobalSearchMock } = vi.hoisted(() => ({
  fetchGlobalSearchMock: vi.fn(),
}));

vi.mock('@/services/searchApi', async () => {
  const actual = await vi.importActual<typeof import('@/services/searchApi')>(
    '@/services/searchApi'
  );

  return {
    ...actual,
    fetchGlobalSearch: fetchGlobalSearchMock,
  };
});

describe('GlobalSearchPage sanitization', () => {
  it('renders highlighted results without injecting unsafe html', async () => {
    fetchGlobalSearchMock.mockResolvedValueOnce({
      query: 'roadmap',
      offset: 0,
      limit: 12,
      total: 2,
      results: [
        {
          id: 'doc-1',
          type: 'document',
          title: 'doc title',
          summary: 'doc summary',
          projectId: 'project-1',
          highlights: {
            excerpt:
              '<mark onclick="alert(1)">safe</mark><img src=x onerror=alert(1) /><script>alert(1)</script>',
          },
          payload: {
            documentId: 'doc-1',
            documentKey: 'DOC-1',
            projectId: 'project-1',
            name: 'Project Charter',
            docType: 'Charter',
            classification: 'Internal',
            latestVersion: 2,
            latestStatus: 'published',
            createdAt: '2026-01-01T00:00:00.000Z',
            updatedAt: '2026-01-01T00:00:00.000Z',
          },
        },
        {
          id: 'project-1',
          type: 'project',
          title: 'Project <script>alert(1)</script> Alpha',
          summary: 'see <a href="javascript:alert(1)">unsafe</a>',
          projectId: 'project-1',
          highlights: {
            title: 'Project <mark>Alpha</mark><script>alert(1)</script>',
            summary: 'see <mark>unsafe</mark> <a href="javascript:alert(1)">bad</a>',
          },
          payload: {},
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={['/search?q=roadmap']}>
        <Routes>
          <Route path="/search" element={<GlobalSearchPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Project Charter')).toBeInTheDocument();
    expect(screen.getByText('safe')).toContainHTML('<mark>safe</mark>');
    expect(screen.getByText('Alpha')).toContainHTML('<mark>Alpha</mark>');

    expect(document.querySelector('script')).toBeNull();
    expect(document.querySelector('img')).toBeNull();
    const link = document.querySelector('a[href^="javascript:"]');
    expect(link).toBeNull();
  });
});
