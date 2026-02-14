import {
  forwardRef,
  useEffect,
  useId,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '@/components/icon/Icon';
import { fetchGlobalSearch, type SearchResult } from '@/services/searchApi';
import styles from './SearchOverlay.module.css';

const RECENT_SEARCHES_KEY = 'ppm.global.recent.searches';
const MAX_RECENT_SEARCHES = 5;
const MAX_INLINE_RESULTS = 5;

function readRecentSearches(): string[] {
  try {
    const parsed = JSON.parse(localStorage.getItem(RECENT_SEARCHES_KEY) ?? '[]') as string[];
    return Array.isArray(parsed) ? parsed.slice(0, MAX_RECENT_SEARCHES) : [];
  } catch {
    return [];
  }
}

function writeRecentSearches(query: string) {
  const normalized = query.trim();
  if (!normalized) {
    return;
  }
  const next = [normalized, ...readRecentSearches().filter((entry) => entry !== normalized)].slice(
    0,
    MAX_RECENT_SEARCHES
  );
  localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(next));
}

function getResultPath(result: SearchResult, query: string): string {
  if (result.type === 'project') {
    return `/projects/${result.id}`;
  }
  if (result.type === 'document') {
    return `/knowledge/documents?q=${encodeURIComponent(query)}`;
  }
  if (result.type === 'knowledge') {
    return `/knowledge/lessons?q=${encodeURIComponent(query)}`;
  }
  if (result.type === 'approval') {
    return '/approvals';
  }
  if (result.type === 'workflow') {
    return '/workflows/monitoring';
  }
  return `/search?q=${encodeURIComponent(query)}`;
}

function getEntityBadge(result: SearchResult): string {
  const payloadType = String((result.payload as { entityType?: string }).entityType ?? '').toLowerCase();
  if (['portfolio', 'program', 'project', 'document'].includes(payloadType)) {
    return payloadType.charAt(0).toUpperCase() + payloadType.slice(1);
  }

  if (result.type === 'document') return 'Document';
  if (result.type === 'project') return 'Project';
  if (result.type === 'knowledge') return 'Program';
  return 'Portfolio';
}

export type SearchOverlayHandle = {
  focus: () => void;
  open: () => void;
};

type SearchOverlayProps = {
  isMobile: boolean;
  query: string;
  onQueryChange: (value: string) => void;
  onSubmit: (query: string) => void;
  open: boolean;
  onOpenChange: (value: boolean) => void;
};

export const SearchOverlay = forwardRef<SearchOverlayHandle, SearchOverlayProps>(function SearchOverlay(
  { isMobile, query, onQueryChange, onSubmit, open, onOpenChange },
  ref
) {
  const navigate = useNavigate();
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const panelId = useId();

  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current?.focus(),
    open: () => {
      onOpenChange(true);
      requestAnimationFrame(() => inputRef.current?.focus());
    },
  }));

  useEffect(() => {
    setRecentSearches(readRecentSearches());
  }, [open]);

  useEffect(() => {
    if (!open && isMobile) {
      return;
    }

    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      setLoading(false);
      return;
    }

    const timer = window.setTimeout(async () => {
      setLoading(true);
      try {
        const response = await fetchGlobalSearch({ query: trimmed, limit: MAX_INLINE_RESULTS });
        setResults(response.results.slice(0, MAX_INLINE_RESULTS));
      } catch (error) {
        console.error('Unable to load search preview results', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => {
      window.clearTimeout(timer);
    };
  }, [isMobile, open, query]);

  useEffect(() => {
    setActiveIndex(-1);
  }, [query, open]);

  const previewItems = useMemo(() => {
    if (!query.trim()) {
      return recentSearches.map((value) => ({
        id: `recent-${value}`,
        label: value,
        summary: 'Recent search',
        badge: 'Recent',
        onSelect: () => {
          onQueryChange(value);
          onSubmit(value);
        },
      }));
    }

    return results.map((result) => ({
      id: result.id,
      label: result.title,
      summary: result.summary,
      badge: getEntityBadge(result),
      onSelect: () => {
        writeRecentSearches(query);
        navigate(getResultPath(result, query));
        onOpenChange(false);
      },
    }));
  }, [navigate, onOpenChange, onQueryChange, onSubmit, query, recentSearches, results]);

  const closeOverlay = () => onOpenChange(false);

  const handleKeyboard = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActiveIndex((prev) => (previewItems.length === 0 ? -1 : (prev + 1) % previewItems.length));
      return;
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveIndex((prev) =>
        previewItems.length === 0 ? -1 : prev <= 0 ? previewItems.length - 1 : prev - 1
      );
      return;
    }

    if (event.key === 'Enter') {
      event.preventDefault();
      if (activeIndex >= 0 && previewItems[activeIndex]) {
        previewItems[activeIndex].onSelect();
        return;
      }
      writeRecentSearches(query);
      onSubmit(query);
      onOpenChange(false);
      return;
    }

    if (event.key === 'Escape') {
      event.preventDefault();
      closeOverlay();
    }
  };

  const content = (
    <div className={isMobile ? styles.mobileContent : styles.desktopContent}>
      <div className={styles.inputRow}>
        <label className={styles.visuallyHidden} htmlFor="header-search-overlay-input">
          Global search
        </label>
        <input
          id="header-search-overlay-input"
          ref={inputRef}
          className={styles.searchInput}
          value={query}
          placeholder="Search portfolios, programs, projects, and documents"
          onChange={(event) => onQueryChange(event.target.value)}
          onKeyDown={handleKeyboard}
          onFocus={() => onOpenChange(true)}
          role="combobox"
          aria-expanded={open}
          aria-controls={panelId}
          aria-activedescendant={
            activeIndex >= 0 && previewItems[activeIndex] ? `${panelId}-${previewItems[activeIndex].id}` : undefined
          }
        />
        {!isMobile && (
          <button
            className={styles.submitButton}
            type="button"
            onClick={() => {
              writeRecentSearches(query);
              onSubmit(query);
            }}
          >
            Search
          </button>
        )}
      </div>

      {open && (
        <ul id={panelId} className={styles.resultsList} role="listbox">
          {loading && <li className={styles.empty}>Searching…</li>}
          {!loading && previewItems.length === 0 && (
            <li className={styles.empty}>Start typing to search or use a recent query.</li>
          )}
          {!loading &&
            previewItems.map((item, index) => (
              <li
                key={item.id}
                id={`${panelId}-${item.id}`}
                role="option"
                aria-selected={index === activeIndex}
                className={`${styles.resultItem} ${index === activeIndex ? styles.active : ''}`.trim()}
              >
                <button
                  type="button"
                  className={styles.resultAction}
                  onMouseEnter={() => setActiveIndex(index)}
                  onClick={item.onSelect}
                >
                  <span>
                    <strong>{item.label}</strong>
                    <small>{item.summary}</small>
                  </span>
                  <span className={styles.badge}>{item.badge}</span>
                </button>
              </li>
            ))}
        </ul>
      )}
    </div>
  );

  if (isMobile) {
    return (
      <>
        <button
          type="button"
          className={styles.mobileTrigger}
          aria-label="Open global search"
          onClick={() => onOpenChange(true)}
        >
          <Icon semantic="navigation.search" label="Open search" />
        </button>
        {open && (
          <div className={styles.mobileOverlay}>
            <div className={styles.mobileHeader}>
              <h2>Search</h2>
              <button type="button" onClick={closeOverlay} className={styles.closeButton}>
                <Icon semantic="actions.cancelDismiss" label="Close search" />
              </button>
            </div>
            {content}
          </div>
        )}
      </>
    );
  }

  return <>{content}</>;
});
