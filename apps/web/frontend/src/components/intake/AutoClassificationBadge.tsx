import { useCallback, useEffect, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './AutoClassificationBadge.module.css';

interface ClassificationResult {
  category: string;
  confidence: number;
  all_scores: Record<string, number>;
}

const CATEGORY_COLORS: Record<string, string> = {
  strategic: '#3b82f6',
  operational: '#22c55e',
  regulatory: '#ef4444',
  maintenance: '#6b7280',
  innovation: '#8b5cf6',
};

const ALL_CATEGORIES = ['strategic', 'operational', 'regulatory', 'maintenance', 'innovation'];

interface AutoClassificationBadgeProps {
  description: string;
  onClassified?: (category: string) => void;
}

export function AutoClassificationBadge({ description, onClassified }: AutoClassificationBadgeProps) {
  const [classification, setClassification] = useState<ClassificationResult | null>(null);
  const [showOverride, setShowOverride] = useState(false);
  const [loading, setLoading] = useState(false);

  const classify = useCallback(async () => {
    if (!description || description.length < 20) return;
    setLoading(true);
    try {
      const result = await requestJson<ClassificationResult>('/api/intake/auto-classify', {
        method: 'POST',
        body: JSON.stringify({ description }),
      });
      setClassification(result);
      onClassified?.(result.category);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [description, onClassified]);

  useEffect(() => {
    const timer = setTimeout(classify, 800);
    return () => clearTimeout(timer);
  }, [classify]);

  if (!classification && !loading) return null;

  const bgColor = classification ? CATEGORY_COLORS[classification.category] || '#6b7280' : '#6b7280';

  return (
    <div className={styles.container}>
      {loading ? (
        <span className={styles.loadingBadge}>Classifying...</span>
      ) : classification ? (
        <>
          <button
            className={styles.badge}
            style={{ background: bgColor }}
            onClick={() => setShowOverride(!showOverride)}
            title="Click to override"
          >
            {classification.category}
            <span className={styles.confidence}>{Math.round(classification.confidence * 100)}%</span>
          </button>
          {showOverride && (
            <div className={styles.overrideDropdown}>
              {ALL_CATEGORIES.map(cat => (
                <button
                  key={cat}
                  className={styles.overrideOption}
                  onClick={() => {
                    setClassification({ ...classification, category: cat, confidence: 1.0 });
                    setShowOverride(false);
                    onClassified?.(cat);
                  }}
                >
                  <span className={styles.catDot} style={{ background: CATEGORY_COLORS[cat] }} />
                  {cat}
                </button>
              ))}
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}
