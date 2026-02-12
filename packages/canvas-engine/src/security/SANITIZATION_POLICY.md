# HTML Sanitization Policy

This package defines the canonical sanitization policy used by rendering boundaries that may receive user-generated or external HTML.

## Policy presets

Configured in `htmlSanitizer.ts`:

- `highlight`
  - Allowed tags: `mark`
  - Allowed attributes: none
  - Intended for global search highlight snippets.
- `richText`
  - Allowed tags: `p`, `br`, `strong`, `em`, `u`, `s`, `ul`, `ol`, `li`, `h1`, `h2`, `h3`, `blockquote`, `a`
  - Allowed attributes: `href`, `target`, `rel`
  - Allowed URL protocols for `href`: `http`, `https`, `mailto`
  - Intended for rich text document canvas content.

## Security guarantees

- `script` and `style` tags are stripped.
- Inline event handlers (for example `onclick`, `onerror`) are stripped.
- `javascript:` URLs are stripped from links.
- Highlight rendering should use tokenized text plus `<mark>` nodes rather than raw `dangerouslySetInnerHTML`.
