/**
 * DocumentCanvas - Rich text document editor
 *
 * A basic contenteditable-based rich text editor for documents like
 * project charters, reports, and notes.
 */

import { useCallback, useRef, useEffect } from 'react';
import type { ClipboardEvent, FormEvent } from 'react';
import type { CanvasComponentProps } from '../../types/canvas';
import type { CanvasArtifact, EditHistoryEntry, ProvenanceMetadata } from '../../types/artifact';
import type { DocumentContent } from '../../types/artifact';
import styles from './DocumentCanvas.module.css';
import { sanitizeRichTextHtml } from '../../security/htmlSanitizer';
import {
  applyFormattingCommand,
  createHistoryState,
  mapInputTypeToCommand,
  type FormattingCommand,
} from './richTextAdapter';

export interface DocumentCanvasProps extends CanvasComponentProps<DocumentContent> {
  onSaveDraft?: (artifact: CanvasArtifact<DocumentContent>) => void;
  onPublish?: (artifact: CanvasArtifact<DocumentContent>) => void;
  showProvenance?: boolean;
}

export function DocumentCanvas({
  artifact,
  readOnly = false,
  onChange,
  onSaveDraft,
  onPublish,
  className,
  showProvenance = false,
}: DocumentCanvasProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const isInitialMount = useRef(true);
  const historyRef = useRef(createHistoryState());

  // Initialize editor content
  useEffect(() => {
    if (editorRef.current && isInitialMount.current) {
      editorRef.current.innerHTML = sanitizeRichTextHtml(artifact.content.html);
      isInitialMount.current = false;
    }
  }, [artifact.content.html]);

  const handleInput = useCallback(() => {
    if (editorRef.current && onChange) {
      const html = sanitizeRichTextHtml(editorRef.current.innerHTML);
      const plainText = editorRef.current.textContent || '';
      onChange({ html, plainText });
    }
  }, [onChange]);

  const runCommand = useCallback((command: FormattingCommand) => {
    if (!editorRef.current) return;
    applyFormattingCommand(editorRef.current, command, historyRef.current);
    editorRef.current.focus();
    handleInput();
  }, [handleInput]);

  const handleBeforeInput = useCallback((event: FormEvent<HTMLDivElement>) => {
    const nativeEvent = event.nativeEvent as InputEvent;
    const command = mapInputTypeToCommand(nativeEvent.inputType);
    if (!command || !editorRef.current) return;
    event.preventDefault();
    applyFormattingCommand(editorRef.current, command, historyRef.current);
    handleInput();
  }, [handleInput]);

  const handlePaste = useCallback((event: ClipboardEvent<HTMLDivElement>) => {
    if (!editorRef.current) return;

    event.preventDefault();
    historyRef.current.past.push(editorRef.current.innerHTML);
    historyRef.current.future = [];

    const html = event.clipboardData.getData('text/html');
    const plainText = event.clipboardData.getData('text/plain');
    const sanitized = sanitizeRichTextHtml(html || `<p>${plainText}</p>`);

    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) {
      editorRef.current.innerHTML += sanitized;
      handleInput();
      return;
    }

    const range = selection.getRangeAt(0);
    range.deleteContents();
    const fragment = range.createContextualFragment(sanitized);
    range.insertNode(fragment);
    selection.collapseToEnd();

    handleInput();
  }, [handleInput]);

  const provenance = artifact.metadata?.provenance as ProvenanceMetadata | undefined;
  const editHistory =
    (artifact.metadata?.editHistory as EditHistoryEntry[] | undefined) ?? [];
  const showProvenancePanel =
    showProvenance && (Boolean(provenance) || editHistory.length > 0);

  const formatTimestamp = (value?: string) => {
    if (!value) return 'Unknown';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString();
  };

  return (
    <div className={`${styles.container} ${className ?? ''}`}>
      {!readOnly && (
        <div className={styles.formatBar}>
          <div className={styles.actionGroup}>
            <button
              className={styles.actionButton}
              onClick={() => onSaveDraft?.(artifact)}
              type="button"
            >
              Save Draft
            </button>
            <button
              className={`${styles.actionButton} ${styles.primaryAction}`}
              onClick={() => onPublish?.(artifact)}
              type="button"
            >
              Publish
            </button>
          </div>
          <div className={styles.separator} />
          <div className={styles.formatGroup}>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('bold')}
              title="Bold (Ctrl+B)"
              aria-label="Bold"
            >
              <strong>B</strong>
            </button>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('italic')}
              title="Italic (Ctrl+I)"
              aria-label="Italic"
            >
              <em>I</em>
            </button>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('underline')}
              title="Underline (Ctrl+U)"
              aria-label="Underline"
            >
              <u>U</u>
            </button>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('strikeThrough')}
              title="Strikethrough"
              aria-label="Strikethrough"
            >
              <s>S</s>
            </button>
          </div>

          <div className={styles.separator} />

          <div className={styles.formatGroup}>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('formatH1')}
              title="Heading 1"
              aria-label="Heading 1"
            >
              H1
            </button>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('formatH2')}
              title="Heading 2"
              aria-label="Heading 2"
            >
              H2
            </button>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('formatH3')}
              title="Heading 3"
              aria-label="Heading 3"
            >
              H3
            </button>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('formatParagraph')}
              title="Paragraph"
              aria-label="Paragraph"
            >
              P
            </button>
          </div>

          <div className={styles.separator} />

          <div className={styles.formatGroup}>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('insertUnorderedList')}
              title="Bullet list"
              aria-label="Bullet list"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="8" y1="6" x2="21" y2="6" />
                <line x1="8" y1="12" x2="21" y2="12" />
                <line x1="8" y1="18" x2="21" y2="18" />
                <circle cx="4" cy="6" r="1" fill="currentColor" />
                <circle cx="4" cy="12" r="1" fill="currentColor" />
                <circle cx="4" cy="18" r="1" fill="currentColor" />
              </svg>
            </button>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('insertOrderedList')}
              title="Numbered list"
              aria-label="Numbered list"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="10" y1="6" x2="21" y2="6" />
                <line x1="10" y1="12" x2="21" y2="12" />
                <line x1="10" y1="18" x2="21" y2="18" />
                <text x="3" y="8" fontSize="8" fill="currentColor">1</text>
                <text x="3" y="14" fontSize="8" fill="currentColor">2</text>
                <text x="3" y="20" fontSize="8" fill="currentColor">3</text>
              </svg>
            </button>
          </div>

          <div className={styles.separator} />

          <div className={styles.formatGroup}>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('undo')}
              title="Undo (Ctrl+Z)"
              aria-label="Undo"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 7v6h6" />
                <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
              </svg>
            </button>
            <button
              className={styles.formatButton}
              onClick={() => runCommand('redo')}
              title="Redo (Ctrl+Y)"
              aria-label="Redo"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 7v6h-6" />
                <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {showProvenancePanel && (
        <div className={styles.provenancePanel}>
          {provenance && (
            <div className={styles.provenanceBlock}>
              <div className={styles.provenanceTitle}>Provenance</div>
              <div className={styles.provenanceRow}>
                <span>Source agent</span>
                <strong>{provenance.sourceAgent ?? 'Unknown'}</strong>
              </div>
              <div className={styles.provenanceRow}>
                <span>Generated</span>
                <strong>{formatTimestamp(provenance.generatedAt)}</strong>
              </div>
              {provenance.correlationId && (
                <div className={styles.provenanceRow}>
                  <span>Correlation</span>
                  <strong>{provenance.correlationId}</strong>
                </div>
              )}
            </div>
          )}
          {editHistory.length > 0 && (
            <div className={styles.editHistoryBlock}>
              <div className={styles.provenanceTitle}>Edit history</div>
              <ul className={styles.editHistoryList}>
                {editHistory.slice(0, 5).map((entry) => (
                  <li key={`${entry.version}-${entry.editedAt}`} className={styles.editHistoryItem}>
                    <span className={styles.editHistoryVersion}>v{entry.version}</span>
                    <span>{entry.status ?? 'draft'}</span>
                    <span>{formatTimestamp(entry.editedAt)}</span>
                    <span>{entry.editedBy ?? 'unknown'}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div
        ref={editorRef}
        className={styles.editor}
        contentEditable={!readOnly}
        onBeforeInput={handleBeforeInput}
        onInput={handleInput}
        onPaste={handlePaste}
        onBlur={handleInput}
        role="textbox"
        aria-multiline="true"
        aria-label={`Edit ${artifact.title}`}
        data-placeholder="Start typing your document..."
      />
    </div>
  );
}
