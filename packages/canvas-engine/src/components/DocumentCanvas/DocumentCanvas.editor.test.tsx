import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { DocumentCanvas } from './DocumentCanvas';
import type { CanvasArtifact, DocumentContent } from '../../types/artifact';

const createArtifact = (html: string): CanvasArtifact<DocumentContent> => ({
  id: 'artifact-1',
  type: 'document',
  title: 'Test doc',
  projectId: 'project-1',
  content: {
    html,
    plainText: 'plain',
  },
  version: 1,
  status: 'draft',
  metadata: {
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'tester',
  },
});

const selectNodeContents = (node: Node) => {
  const selection = window.getSelection();
  if (!selection) return;
  const range = document.createRange();
  range.selectNodeContents(node);
  selection.removeAllRanges();
  selection.addRange(range);
};

describe('DocumentCanvas editor adapter', () => {
  it('applies inline formatting via toolbar action', () => {
    render(<DocumentCanvas artifact={createArtifact('<p>Hello world</p>')} onChange={vi.fn()} />);

    const editor = screen.getByRole('textbox');
    const paragraph = editor.querySelector('p');
    expect(paragraph).toBeTruthy();
    selectNodeContents(paragraph!.firstChild!);

    fireEvent.click(screen.getByRole('button', { name: 'Bold' }));

    expect(editor.innerHTML).toContain('<strong>Hello world</strong>');
  });

  it('supports undo/redo for formatting actions', () => {
    render(<DocumentCanvas artifact={createArtifact('<p>Hello world</p>')} onChange={vi.fn()} />);

    const editor = screen.getByRole('textbox');
    const paragraph = editor.querySelector('p');
    expect(paragraph).toBeTruthy();
    selectNodeContents(paragraph!.firstChild!);

    fireEvent.click(screen.getByRole('button', { name: 'Bold' }));
    expect(editor.innerHTML).toContain('<strong>Hello world</strong>');

    fireEvent.click(screen.getByRole('button', { name: 'Undo' }));
    expect(editor.innerHTML).toBe('<p>Hello world</p>');

    fireEvent.click(screen.getByRole('button', { name: 'Redo' }));
    expect(editor.innerHTML).toContain('<strong>Hello world</strong>');
  });

  it('ignores formatting command when selection is outside editor', () => {
    render(
      <>
        <DocumentCanvas artifact={createArtifact('<p>Hello world</p>')} onChange={vi.fn()} />
        <p data-testid="outside">Outside selection</p>
      </>
    );

    const editor = screen.getByRole('textbox');
    selectNodeContents(screen.getByTestId('outside').firstChild!);

    fireEvent.click(screen.getByRole('button', { name: 'Italic' }));

    expect(editor.innerHTML).toBe('<p>Hello world</p>');
  });

  it('sanitizes pasted html before insertion', () => {
    const onChange = vi.fn();
    render(<DocumentCanvas artifact={createArtifact('<p>Start</p>')} onChange={onChange} />);

    const editor = screen.getByRole('textbox');
    const paragraph = editor.querySelector('p');
    expect(paragraph).toBeTruthy();
    selectNodeContents(paragraph!);

    const clipboardData = {
      getData: (type: string) => {
        if (type === 'text/html') {
          return '<p onclick="alert(1)">Paste</p><script>alert(2)</script>';
        }
        return 'Paste';
      },
    };

    fireEvent.paste(editor, { clipboardData });

    expect(editor.innerHTML).toContain('<p>Paste</p>');
    expect(editor.innerHTML).not.toContain('onclick');
    expect(editor.innerHTML).not.toContain('<script>');
    expect(onChange).toHaveBeenCalled();
  });
});
