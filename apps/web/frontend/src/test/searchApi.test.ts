import { describe, expect, it, vi, afterEach } from 'vitest';
import { fetchGlobalSearch } from '@/services/searchApi';

describe('fetchGlobalSearch', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('uses q query parameter for search requests', async () => {
    const responseBody = {
      query: 'risk',
      offset: 2,
      limit: 5,
      total: 0,
      results: [],
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(responseBody), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );
    vi.stubGlobal('fetch', fetchMock);

    await fetchGlobalSearch({
      query: 'risk',
      types: ['document', 'project'],
      projectIds: ['phoenix'],
      offset: 2,
      limit: 5,
    });

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/search?q=risk&types=document%2Cproject&project_ids=phoenix&offset=2&limit=5'
    );
  });
});
