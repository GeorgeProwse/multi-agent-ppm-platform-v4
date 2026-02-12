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

describe('DocumentCanvas sanitization', () => {
  it('sanitizes initial artifact html before assigning to innerHTML', () => {
    render(
      <DocumentCanvas
        artifact={createArtifact('<p onclick="alert(1)">Safe</p><script>alert(2)</script>')}
      />
    );

    const editor = screen.getByRole('textbox');
    expect(editor.innerHTML).toBe('<p>Safe</p>');
  });

  it('sanitizes html emitted from onChange payload', () => {
    const onChange = vi.fn();

    render(<DocumentCanvas artifact={createArtifact('<p>Start</p>')} onChange={onChange} />);

    const editor = screen.getByRole('textbox');
    editor.innerHTML = '<p>Ok</p><img src=x onerror=alert(1) /><a href="javascript:alert(1)">bad</a>';
    fireEvent.input(editor);

    expect(onChange).toHaveBeenCalled();
    expect(onChange.mock.lastCall?.[0].html).toContain('<p>Ok</p>');
    expect(onChange.mock.lastCall?.[0].html).not.toContain('onerror');
    expect(onChange.mock.lastCall?.[0].html).not.toContain('javascript:');
  });
});
