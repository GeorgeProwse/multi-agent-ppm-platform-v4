export type FormattingCommand =
  | 'bold'
  | 'italic'
  | 'underline'
  | 'strikeThrough'
  | 'formatH1'
  | 'formatH2'
  | 'formatH3'
  | 'formatParagraph'
  | 'insertUnorderedList'
  | 'insertOrderedList'
  | 'undo'
  | 'redo';

/**
 * Inventory of legacy execCommand usage retained for compatibility fallback + migration observability.
 */
export const LEGACY_EXEC_COMMANDS: Record<FormattingCommand, { command: string; value?: string }> = {
  bold: { command: 'bold' },
  italic: { command: 'italic' },
  underline: { command: 'underline' },
  strikeThrough: { command: 'strikeThrough' },
  formatH1: { command: 'formatBlock', value: 'h1' },
  formatH2: { command: 'formatBlock', value: 'h2' },
  formatH3: { command: 'formatBlock', value: 'h3' },
  formatParagraph: { command: 'formatBlock', value: 'p' },
  insertUnorderedList: { command: 'insertUnorderedList' },
  insertOrderedList: { command: 'insertOrderedList' },
  undo: { command: 'undo' },
  redo: { command: 'redo' },
};

type HistoryState = {
  past: string[];
  future: string[];
};

const INLINE_TAG: Partial<Record<FormattingCommand, keyof HTMLElementTagNameMap>> = {
  bold: 'strong',
  italic: 'em',
  underline: 'u',
  strikeThrough: 's',
};

const BLOCK_TAG: Partial<Record<FormattingCommand, keyof HTMLElementTagNameMap>> = {
  formatH1: 'h1',
  formatH2: 'h2',
  formatH3: 'h3',
  formatParagraph: 'p',
};

const isSelectionInside = (selection: Selection, editor: HTMLElement) => {
  if (selection.rangeCount === 0) return false;
  const range = selection.getRangeAt(0);
  return editor.contains(range.commonAncestorContainer);
};

const captureSnapshot = (editor: HTMLElement, history: HistoryState) => {
  if (history.past[history.past.length - 1] !== editor.innerHTML) {
    history.past.push(editor.innerHTML);
  }
  history.future = [];
};

const getActiveBlock = (range: Range, editor: HTMLElement): HTMLElement | null => {
  let node: Node | null = range.startContainer;
  while (node && node !== editor) {
    if (
      node instanceof HTMLElement &&
      ['P', 'H1', 'H2', 'H3', 'DIV', 'LI'].includes(node.tagName)
    ) {
      return node;
    }
    node = node.parentNode;
  }
  return editor.firstElementChild instanceof HTMLElement ? editor.firstElementChild : null;
};

const wrapSelectionInline = (editor: HTMLElement, tag: keyof HTMLElementTagNameMap) => {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0 || selection.isCollapsed) return false;
  if (!isSelectionInside(selection, editor)) return false;

  const range = selection.getRangeAt(0);
  const element = document.createElement(tag);

  try {
    range.surroundContents(element);
  } catch {
    const content = range.extractContents();
    element.append(content);
    range.insertNode(element);
  }

  const newRange = document.createRange();
  newRange.selectNodeContents(element);
  selection.removeAllRanges();
  selection.addRange(newRange);
  return true;
};

const replaceBlockTag = (editor: HTMLElement, tag: keyof HTMLElementTagNameMap) => {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return false;
  if (!isSelectionInside(selection, editor)) return false;

  const range = selection.getRangeAt(0);
  const block = getActiveBlock(range, editor);
  if (!block) return false;

  if (block.tagName.toLowerCase() === tag) {
    return true;
  }

  const replacement = document.createElement(tag);
  replacement.innerHTML = block.innerHTML;
  block.replaceWith(replacement);

  const newRange = document.createRange();
  newRange.selectNodeContents(replacement);
  selection.removeAllRanges();
  selection.addRange(newRange);
  return true;
};

const convertToList = (editor: HTMLElement, ordered: boolean) => {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return false;
  if (!isSelectionInside(selection, editor)) return false;

  const range = selection.getRangeAt(0);
  const block = getActiveBlock(range, editor);
  if (!block) return false;

  const list = document.createElement(ordered ? 'ol' : 'ul');
  const item = document.createElement('li');
  item.innerHTML = block.innerHTML;
  list.append(item);
  block.replaceWith(list);

  const newRange = document.createRange();
  newRange.selectNodeContents(item);
  selection.removeAllRanges();
  selection.addRange(newRange);
  return true;
};

const runUndo = (editor: HTMLElement, history: HistoryState) => {
  if (history.past.length === 0) return false;
  history.future.push(editor.innerHTML);
  const prev = history.past.pop();
  if (typeof prev !== 'string') return false;
  editor.innerHTML = prev;
  return true;
};

const runRedo = (editor: HTMLElement, history: HistoryState) => {
  if (history.future.length === 0) return false;
  history.past.push(editor.innerHTML);
  const next = history.future.pop();
  if (typeof next !== 'string') return false;
  editor.innerHTML = next;
  return true;
};

const fallbackExecCommand = (command: FormattingCommand) => {
  const legacy = LEGACY_EXEC_COMMANDS[command];
  if (!legacy || typeof document.execCommand !== 'function') return false;
  return document.execCommand(legacy.command, false, legacy.value);
};

export const createHistoryState = (): HistoryState => ({
  past: [],
  future: [],
});

export const applyFormattingCommand = (
  editor: HTMLElement,
  command: FormattingCommand,
  history: HistoryState
) => {
  if (command === 'undo') return runUndo(editor, history) || fallbackExecCommand(command);
  if (command === 'redo') return runRedo(editor, history) || fallbackExecCommand(command);

  captureSnapshot(editor, history);

  const inlineTag = INLINE_TAG[command];
  if (inlineTag) {
    return wrapSelectionInline(editor, inlineTag) || fallbackExecCommand(command);
  }

  const blockTag = BLOCK_TAG[command];
  if (blockTag) {
    return replaceBlockTag(editor, blockTag) || fallbackExecCommand(command);
  }

  if (command === 'insertUnorderedList') {
    return convertToList(editor, false) || fallbackExecCommand(command);
  }

  if (command === 'insertOrderedList') {
    return convertToList(editor, true) || fallbackExecCommand(command);
  }

  return fallbackExecCommand(command);
};

export const mapInputTypeToCommand = (inputType: string): FormattingCommand | null => {
  switch (inputType) {
    case 'formatBold':
      return 'bold';
    case 'formatItalic':
      return 'italic';
    case 'formatUnderline':
      return 'underline';
    case 'formatStrikeThrough':
      return 'strikeThrough';
    case 'insertUnorderedList':
      return 'insertUnorderedList';
    case 'insertOrderedList':
      return 'insertOrderedList';
    case 'historyUndo':
      return 'undo';
    case 'historyRedo':
      return 'redo';
    default:
      return null;
  }
};
