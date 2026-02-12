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
  const blockLikeTags = new Set([
    'address',
    'article',
    'aside',
    'blockquote',
    'div',
    'dl',
    'fieldset',
    'figcaption',
    'figure',
    'footer',
    'form',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'header',
    'hr',
    'li',
    'main',
    'nav',
    'ol',
    'p',
    'pre',
    'section',
    'table',
    'ul',
  ]);
  const supportsLineBreakTag = allowedTags.has('br');

  const hasMeaningfulContent = (node: Node): boolean => {
    if (node.nodeType === Node.TEXT_NODE) {
      return Boolean(node.textContent?.trim());
    }

    if (node.nodeType !== Node.ELEMENT_NODE) {
      return false;
    }

    const tagName = (node as HTMLElement).tagName.toLowerCase();
    if (forbiddenTags.has(tagName)) {
      return false;
    }

    return true;
  };

  const appendLineBreakIfNeeded = (targetNode: Node) => {
    if (!supportsLineBreakTag || targetNode.nodeType !== Node.ELEMENT_NODE) {
      return;
    }

    const element = targetNode as Element;
    const lastChild = element.lastChild;
    if (lastChild?.nodeType === Node.ELEMENT_NODE) {
      const lastTagName = (lastChild as HTMLElement).tagName.toLowerCase();
      if (lastTagName === 'br') {
        return;
      }
    }

    targetNode.appendChild(targetDoc.createElement('br'));
  };

  const appendSanitizedChildren = (sourceNode: ParentNode, targetNode: Node) => {
    const childNodes = Array.from(sourceNode.childNodes);

    for (const [index, child] of childNodes.entries()) {
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
        const isBlockLikeUnsupportedTag = blockLikeTags.has(tagName);
        const hasPriorSiblingContent = childNodes
          .slice(0, index)
          .some((sibling) => hasMeaningfulContent(sibling));
        const hasFollowingSiblingContent = childNodes
          .slice(index + 1)
          .some((sibling) => hasMeaningfulContent(sibling));

        if (isBlockLikeUnsupportedTag && hasPriorSiblingContent) {
          appendLineBreakIfNeeded(targetNode);
        }

        appendSanitizedChildren(sourceElement, targetNode);

        if (isBlockLikeUnsupportedTag && hasFollowingSiblingContent) {
          appendLineBreakIfNeeded(targetNode);
        }

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
