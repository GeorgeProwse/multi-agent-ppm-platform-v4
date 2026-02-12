const SANITIZER_PROTOCOLS = ['http', 'https', 'mailto'];

export const SANITIZATION_POLICY = {
  highlight: {
    allowedTags: ['mark'],
    allowedAttrs: [],
    allowedProtocols: [],
  },
  richText: {
    allowedTags: [
      'p',
      'br',
      'strong',
      'em',
      'u',
      's',
      'ul',
      'ol',
      'li',
      'h1',
      'h2',
      'h3',
      'blockquote',
      'a',
    ],
    allowedAttrs: ['href', 'target', 'rel'],
    allowedProtocols: SANITIZER_PROTOCOLS,
  },
} as const;

interface SanitizerPolicy {
  allowedTags: readonly string[];
  allowedAttrs: readonly string[];
  allowedProtocols: readonly string[];
}

function isAllowedProtocol(url: string, allowedProtocols: readonly string[]): boolean {
  const normalized = url.trim().toLowerCase();

  if (!normalized.includes(':')) {
    return true;
  }

  return allowedProtocols.some((protocol) => normalized.startsWith(`${protocol}:`));
}

function sanitizeWithPolicy(input: string, policy: SanitizerPolicy): string {
  if (!input) {
    return '';
  }

  const parser = new DOMParser();
  const sourceDoc = parser.parseFromString(input, 'text/html');
  const targetDoc = document.implementation.createHTMLDocument('sanitized');
  const allowedTags = new Set(policy.allowedTags.map((tag) => tag.toLowerCase()));
  const allowedAttrs = new Set(policy.allowedAttrs.map((attr) => attr.toLowerCase()));
  const forbiddenTags = new Set(['script', 'style']);

  const appendSanitizedChildren = (sourceNode: ParentNode, targetNode: Node) => {
    for (const child of Array.from(sourceNode.childNodes)) {
      if (child.nodeType === Node.TEXT_NODE) {
        targetNode.appendChild(targetDoc.createTextNode(child.textContent ?? ''));
        continue;
      }

      if (child.nodeType !== Node.ELEMENT_NODE) {
        continue;
      }

      const sourceElement = child as HTMLElement;
      const tagName = sourceElement.tagName.toLowerCase();

      if (forbiddenTags.has(tagName)) {
        continue;
      }

      if (!allowedTags.has(tagName)) {
        appendSanitizedChildren(sourceElement, targetNode);
        continue;
      }

      const safeElement = targetDoc.createElement(tagName);

      for (const attribute of Array.from(sourceElement.attributes)) {
        const name = attribute.name.toLowerCase();
        if (name.startsWith('on') || !allowedAttrs.has(name)) {
          continue;
        }

        if (name === 'href' && !isAllowedProtocol(attribute.value, policy.allowedProtocols)) {
          continue;
        }

        safeElement.setAttribute(name, attribute.value);
      }

      appendSanitizedChildren(sourceElement, safeElement);
      targetNode.appendChild(safeElement);
    }
  };

  const container = targetDoc.createElement('div');
  appendSanitizedChildren(sourceDoc.body, container);
  return container.innerHTML;
}

export function sanitizeHighlightHtml(input: string | null | undefined): string {
  return sanitizeWithPolicy(input ?? '', SANITIZATION_POLICY.highlight);
}

export function sanitizeRichTextHtml(input: string | null | undefined): string {
  return sanitizeWithPolicy(input ?? '', SANITIZATION_POLICY.richText);
}

export interface HighlightToken {
  text: string;
  highlighted: boolean;
}

export function tokenizeHighlight(
  fallbackText: string,
  highlightHtml?: string | null
): HighlightToken[] {
  const sanitizedHighlight = sanitizeHighlightHtml(highlightHtml);

  if (!sanitizedHighlight) {
    return [{ text: fallbackText, highlighted: false }];
  }

  const container = document.createElement('div');
  container.innerHTML = sanitizedHighlight;

  const tokens: HighlightToken[] = [];

  const appendToken = (text: string, highlighted: boolean) => {
    if (!text) {
      return;
    }

    const prior = tokens[tokens.length - 1];
    if (prior && prior.highlighted === highlighted) {
      prior.text += text;
      return;
    }
    tokens.push({ text, highlighted });
  };

  for (const node of Array.from(container.childNodes)) {
    if (node.nodeType === Node.TEXT_NODE) {
      appendToken(node.textContent ?? '', false);
      continue;
    }

    if (node.nodeType === Node.ELEMENT_NODE) {
      const element = node as HTMLElement;
      appendToken(element.textContent ?? '', element.tagName.toLowerCase() === 'mark');
    }
  }

  return tokens.length > 0 ? tokens : [{ text: fallbackText, highlighted: false }];
}
