import styles from './RecommendationSidebar.module.css';

interface Recommendation {
  recommendation_id: string;
  title: string;
  description: string;
  priority: string;
  source_lesson_id: string;
  source_lesson_title: string;
  actionable_text: string;
}

const PRIORITY_STYLES: Record<string, { bg: string; color: string }> = {
  critical: { bg: '#fee2e2', color: '#991b1b' },
  important: { bg: '#fef9c3', color: '#854d0e' },
  informational: { bg: '#dbeafe', color: '#1e40af' },
};

interface RecommendationSidebarProps {
  recommendations: Recommendation[];
  onSelectSource?: (nodeId: string) => void;
}

export function RecommendationSidebar({ recommendations, onSelectSource }: RecommendationSidebarProps) {
  if (recommendations.length === 0) return null;

  return (
    <div className={styles.sidebar}>
      <h3>AI Recommendations</h3>
      <ul className={styles.list}>
        {recommendations.map(rec => {
          const pStyle = PRIORITY_STYLES[rec.priority] || PRIORITY_STYLES.informational;
          return (
            <li key={rec.recommendation_id} className={styles.item}>
              <div className={styles.itemHeader}>
                <span className={styles.priorityBadge} style={{ background: pStyle.bg, color: pStyle.color }}>{rec.priority}</span>
                <h4>{rec.title}</h4>
              </div>
              <p className={styles.description}>{rec.description}</p>
              <p className={styles.actionable}>{rec.actionable_text}</p>
              <button
                className={styles.sourceLink}
                onClick={() => onSelectSource?.(rec.source_lesson_id)}
              >
                Source: {rec.source_lesson_title}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
