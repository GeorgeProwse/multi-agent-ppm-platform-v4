import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  fetchGlobalSearch,
  type SearchResult,
  type SearchResultType,
} from '@/services/searchApi';
import type { DocumentSummary, LessonRecord } from '@/services/knowledgeApi';
import styles from './GlobalSearch.module.css';

const TYPE_LABELS: Record<SearchResultType, string> = {
  document: 'Documents',
  work_item: 'Work Items',
  risk: 'Risks',
  lesson: 'Lessons Learned',
};

const DEFAULT_TYPES: SearchResultType[] = [
  'document',
  'work_item',
  'risk',
  'lesson',
];

const PAGE_SIZE = 12;

export function GlobalSearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') ?? '';
  const [query, setQuery] = useState(initialQuery);
  const [projectFilter, setProjectFilter] = useState(
    searchParams.get('projects') ?? ''
  );
  const [selectedTypes, setSelectedTypes] = useState<Set<SearchResultType>>(
    new Set(DEFAULT_TYPES)
  );
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const projectIds = useMemo(
    () =>
      projectFilter
        .split(',')
        .map((entry) => entry.trim())
        .filter(Boolean),
    [projectFilter]
  );

  const groupedResults = useMemo(() => {
    const groups: Record<SearchResultType, SearchResult[]> = {
      document: [],
      work_item: [],
      risk: [],
      lesson: [],
    };
    results.forEach((result) => {
      groups[result.type].push(result);
    });
    return groups;
  }, [results]);

  const loadResults = useCallback(
    async (offset = 0, append = false) => {
      if (!query.trim()) {
        setResults([]);
        setTotal(0);
        return;
      }
      setLoading(true);
      try {
        const response = await fetchGlobalSearch({
          query: query.trim(),
          types: Array.from(selectedTypes),
          projectIds,
          offset,
          limit: PAGE_SIZE,
        });
        setTotal(response.total);
        setResults((prev) =>
          append ? prev.concat(response.results) : response.results
        );
      } catch (error) {
        console.error('Failed to load global search results', error);
      } finally {
        setLoading(false);
      }
    },
    [projectIds, query, selectedTypes]
  );

  useEffect(() => {
    const params = new URLSearchParams(searchParams);
    const queryParam = params.get('q') ?? '';
    if (queryParam !== query) {
      setQuery(queryParam);
    }
    const projectsParam = params.get('projects') ?? '';
    if (projectsParam !== projectFilter) {
      setProjectFilter(projectsParam);
    }
  }, [projectFilter, query, searchParams]);

  useEffect(() => {
    if (query.trim()) {
      loadResults(0, false);
    } else {
      setResults([]);
      setTotal(0);
    }
  }, [loadResults, query, projectIds, selectedTypes]);

  const handleSearch = () => {
    const params = new URLSearchParams();
    if (query.trim()) {
      params.set('q', query.trim());
    }
    if (projectFilter.trim()) {
      params.set('projects', projectFilter.trim());
    }
    setSearchParams(params);
  };

  const toggleType = (type: SearchResultType) => {
    setSelectedTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  };

  const handleLoadMore = () => {
    loadResults(results.length, true);
  };

  const hasMore = results.length < total;

  const renderDocumentCard = (result: SearchResult) => {
    const payload = result.payload as DocumentSummary;
    return (
      <li key={result.id} className={styles.resultCard}>
        <div className={styles.cardHeader}>
          <div>
            <h3>{payload.name}</h3>
            <p>{payload.docType} · {payload.classification}</p>
          </div>
          <span className={styles.badge}>{payload.latestStatus}</span>
        </div>
        <div className={styles.metaRow}>
          <span>Project {payload.projectId}</span>
          <span>Updated {new Date(payload.updatedAt).toLocaleString()}</span>
        </div>
        {result.highlights?.excerpt && (
          <p
            className={styles.excerpt}
            dangerouslySetInnerHTML={{ __html: result.highlights.excerpt }}
          />
        )}
      </li>
    );
  };

  const renderLessonCard = (result: SearchResult) => {
    const payload = result.payload as LessonRecord;
    return (
      <li key={result.id} className={styles.resultCard}>
        <div className={styles.cardHeader}>
          <div>
            <h3>{payload.title}</h3>
            <p>
              {payload.stageName ?? 'General'} · Project {payload.projectId}
            </p>
          </div>
        </div>
        <p className={styles.lessonDescription}>{payload.description}</p>
        <div className={styles.chipRow}>
          {payload.tags.map((tag) => (
            <span key={`tag-${payload.lessonId}-${tag}`} className={styles.chip}>
              #{tag}
            </span>
          ))}
          {payload.topics.map((topic) => (
            <span
              key={`topic-${payload.lessonId}-${topic}`}
              className={styles.chipAlt}
            >
              {topic}
            </span>
          ))}
        </div>
      </li>
    );
  };

  const renderGenericCard = (result: SearchResult) => {
    return (
      <li key={result.id} className={styles.resultCard}>
        <div className={styles.cardHeader}>
          <div>
            <h3>{result.title}</h3>
            <p>Project {result.projectId ?? 'N/A'}</p>
          </div>
        </div>
        <p className={styles.lessonDescription}>{result.summary}</p>
      </li>
    );
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <h1>Global Search</h1>
          <p>Search documents, work items, risks, and lessons across portfolios.</p>
        </div>
        <div className={styles.searchControls}>
          <input
            className={styles.searchInput}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search across the portfolio"
          />
          <button className={styles.primaryButton} onClick={handleSearch}>
            Search
          </button>
        </div>
        <div className={styles.filterRow}>
          <div className={styles.filterGroup}>
            {DEFAULT_TYPES.map((type) => (
              <label key={type} className={styles.filterChip}>
                <input
                  type="checkbox"
                  checked={selectedTypes.has(type)}
                  onChange={() => toggleType(type)}
                />
                {TYPE_LABELS[type]}
              </label>
            ))}
          </div>
          <input
            className={styles.filterInput}
            value={projectFilter}
            onChange={(event) => setProjectFilter(event.target.value)}
            placeholder="Project IDs (comma separated)"
          />
        </div>
      </header>

      <div className={styles.resultsWrapper}>
        {loading && results.length === 0 && (
          <div className={styles.emptyState}>Searching...</div>
        )}
        {!loading && results.length === 0 && (
          <div className={styles.emptyState}>
            {query.trim()
              ? 'No results found. Try refining your filters.'
              : 'Enter a query to search across the portfolio.'}
          </div>
        )}

        {DEFAULT_TYPES.map((type) => (
          <section key={type} className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>{TYPE_LABELS[type]}</h2>
              <span className={styles.countBadge}>{groupedResults[type].length}</span>
            </div>
            {groupedResults[type].length === 0 && (
              <div className={styles.emptyState}>No results yet.</div>
            )}
            {groupedResults[type].length > 0 && (
              <ul className={styles.resultList}>
                {groupedResults[type].map((result) => {
                  if (result.type === 'document') {
                    return renderDocumentCard(result);
                  }
                  if (result.type === 'lesson') {
                    return renderLessonCard(result);
                  }
                  return renderGenericCard(result);
                })}
              </ul>
            )}
          </section>
        ))}

        {hasMore && (
          <div className={styles.loadMore}>
            <button
              className={styles.secondaryButton}
              onClick={handleLoadMore}
              disabled={loading}
            >
              {loading ? 'Loading…' : 'Load more results'}
            </button>
            <span className={styles.resultsMeta}>
              Showing {results.length} of {total}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
