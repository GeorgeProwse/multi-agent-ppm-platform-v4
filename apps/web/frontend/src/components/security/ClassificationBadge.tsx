import styles from './ClassificationBadge.module.css';

const CLASSIFICATION_STYLES: Record<string, { bg: string; color: string }> = {
  public: { bg: '#f3f4f6', color: '#374151' },
  internal: { bg: '#dbeafe', color: '#1e40af' },
  confidential: { bg: '#fef3c7', color: '#92400e' },
  restricted: { bg: '#fee2e2', color: '#991b1b' },
};

interface ClassificationBadgeProps {
  classification: string;
}

export function ClassificationBadge({ classification }: ClassificationBadgeProps) {
  const style = CLASSIFICATION_STYLES[classification] || CLASSIFICATION_STYLES.internal;
  return (
    <span className={styles.badge} style={{ background: style.bg, color: style.color }}>
      {classification}
    </span>
  );
}
