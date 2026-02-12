import { describe, expect, it } from 'vitest';
import {
  SANITIZATION_POLICY,
  sanitizeHighlightHtml,
  sanitizeRichTextHtml,
  tokenizeHighlight,
} from './htmlSanitizer';

describe('htmlSanitizer', () => {
  it('strips scripts and event handlers from highlight html', () => {
    const sanitized = sanitizeHighlightHtml(
      '<mark onclick="alert(1)">ok</mark><script>alert(2)</script><img src=x onerror=alert(3) />'
    );

    expect(sanitized).toBe('<mark>ok</mark>');
  });

  it('strips javascript urls from rich text links', () => {
    const sanitized = sanitizeRichTextHtml(
      '<a href="javascript:alert(1)">Click</a><a href="https://example.com">Safe</a>'
    );

    expect(sanitized).toContain('<a>Click</a>');
    expect(sanitized).toContain('<a href="https://example.com">Safe</a>');
    expect(sanitized).not.toContain('javascript:');
  });

  it('tokenizes sanitized highlights into plain-text and mark segments', () => {
    const tokens = tokenizeHighlight('fallback', 'hello <mark>world</mark><script>x</script>');

    expect(tokens).toEqual([
      { text: 'hello ', highlighted: false },
      { text: 'world', highlighted: true },
    ]);
  });

  it('documents explicit allowed protocols policy for rich text links', () => {
    expect(SANITIZATION_POLICY.richText.allowedProtocols).toEqual([
      'http',
      'https',
      'mailto',
    ]);
  });

  it('preserves paragraph breaks when unwrapping unsupported block elements', () => {
    const sanitized = sanitizeRichTextHtml('line1<div>line2</div><div>line3</div>tail');

    expect(sanitized).toBe('line1<br>line2<br>line3<br>tail');
  });
});
