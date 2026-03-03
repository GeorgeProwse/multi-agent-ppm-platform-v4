import { render } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MethodologyEditor } from './MethodologyEditor';

vi.mock('@/store', () => ({
  useAppStore: () => ({
    selectedEntity: null,
    demoMode: true,
    userRoles: ['PMO_ADMIN'],
    session: { user: { permissions: ['methodology.edit'] } },
  }),
}));

vi.mock('@/auth/permissions', () => ({
  hasPermission: () => true,
}));

describe('MethodologyEditor', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ items: [], stages: [] }), { status: 200 })
    );
  });

  it('renders without crashing', () => {
    const { container } = render(<MethodologyEditor />);
    expect(container).toBeTruthy();
  });
});
