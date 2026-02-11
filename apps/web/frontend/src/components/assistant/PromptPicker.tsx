import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { PromptDefinition } from '@/types/prompt';
import styles from './PromptPicker.module.css';

interface PromptPickerProps {
  prompts: PromptDefinition[];
  onClose: () => void;
  onSelectPrompt: (prompt: PromptDefinition) => void;
}

export function PromptPicker({ prompts, onClose, onSelectPrompt }: PromptPickerProps) {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const filteredPrompts = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return prompts;
    }

    return prompts.filter((prompt) => {
      const label = prompt.label.toLowerCase();
      const description = prompt.description.toLowerCase();
      return label.includes(normalizedQuery) || description.includes(normalizedQuery);
    });
  }, [prompts, query]);

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => {
      window.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  return (
    <div className={styles.popover} role="dialog" aria-label="Prompt picker">
      <div className={styles.header}>Prompt picker</div>
      <div className={styles.searchArea}>
        <label htmlFor="assistant-prompt-search" className={styles.visuallyHidden}>
          Search prompts
        </label>
        <input
          id="assistant-prompt-search"
          className={styles.searchInput}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search prompts"
          autoFocus
        />
      </div>

      <div className={styles.results} role="listbox" aria-label="Prompt results">
        {filteredPrompts.length === 0 ? (
          <p className={styles.empty}>No prompts found.</p>
        ) : (
          filteredPrompts.map((prompt) => (
            <button
              key={prompt.id}
              type="button"
              className={styles.resultRow}
              onClick={() => {
                onSelectPrompt(prompt);
                onClose();
              }}
            >
              <span className={styles.resultLabel}>{prompt.label}</span>
              <span className={styles.resultDescription}>{prompt.description}</span>
            </button>
          ))
        )}
      </div>

      <button
        type="button"
        className={styles.manageLink}
        onClick={() => {
          onClose();
          navigate('/config/prompts');
        }}
      >
        Manage prompts
      </button>
    </div>
  );
}

export default PromptPicker;
