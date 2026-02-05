import { describe, expect, it } from 'vitest';
import { formatAssistantResponse } from '@/utils/assistantResponses';

describe('formatAssistantResponse', () => {
  it('formats a summary with list items', () => {
    const formatted = formatAssistantResponse({
      summary: 'Top risk exposure projects:',
      items: ['Phoenix', 'Orion'],
    });
    expect(formatted).toContain('Top risk exposure projects:');
    expect(formatted).toContain('• Phoenix');
    expect(formatted).toContain('• Orion');
  });

  it('returns summary when no list items', () => {
    const formatted = formatAssistantResponse({ summary: 'All clear.' });
    expect(formatted).toBe('All clear.');
  });
});
