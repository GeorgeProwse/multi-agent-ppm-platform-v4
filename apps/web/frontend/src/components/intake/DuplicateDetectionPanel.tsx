import { useCallback, useEffect, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './DuplicateDetectionPanel.module.css';

interface DuplicateMatch {
  demand_id: string;
  title: string;
  description: string;
  status: string;
  similarity_score: number;
}

interface DuplicateDetectionPanelProps {
  title: string;
  description: string;
}

export function DuplicateDetectionPanel({ title, description }: DuplicateDetectionPanelProps) {
  const [matches, setMatches] = useState<DuplicateMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const checkDuplicates = useCallback(async () => {
    if (description.length < 50) return;
    setLoading(true);
    try {
      const result = await requestJson<DuplicateMatch[]>('/api/intake/check-duplicates', {
        method: 'POST',
        body: JSON.stringify({ title, description }),
      });
      setMatches(result);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [title, description]);

  useEffect(() => {
    const timer = setTimeout(checkDuplicates, 500);
    return () => clearTimeout(timer);
  }, [checkDuplicates]);

  if (description.length < 50 && matches.length === 0) return null;

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.label}>Duplicate Detection</span>
        {loading && <span className={styles.spinner} />}
      </div>
      {matches.length === 0 && !loading ? (
        <p className={styles.noMatches}>No similar demands found</p>
      ) : (
        <ul className={styles.matchList}>
          {matches.map(m => (
            <li key={m.demand_id} className={styles.matchItem}>
              <div className={styles.matchHeader} onClick={() => setExpanded(expanded === m.demand_id ? null : m.demand_id)}>
                <span className={styles.matchTitle}>{m.title}</span>
                <div className={styles.matchMeta}>
                  <div className={styles.similarityBar}>
                    <div className={styles.similarityFill} style={{ width: `${Math.round(m.similarity_score * 100)}%` }} />
                  </div>
                  <span className={styles.similarityPct}>{Math.round(m.similarity_score * 100)}%</span>
                  <span className={`${styles.statusBadge} ${styles[`status-${m.status}`]}`}>{m.status}</span>
                </div>
              </div>
              {expanded === m.demand_id && (
                <div className={styles.matchDetail}>
                  <p>{m.description}</p>
                  <div className={styles.matchActions}>
                    <button className={styles.linkBtn}>Link as Duplicate</button>
                    <button className={styles.dismissBtn}>Not a Duplicate</button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
