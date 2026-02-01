import styles from './KpiWidget.module.css';

interface KpiWidgetProps {
  label: string;
  value: string;
  delta?: string;
  description?: string;
}

const resolveTone = (delta?: string) => {
  if (!delta) return 'neutral';
  const trimmed = delta.trim();
  if (trimmed.startsWith('-') || trimmed.includes('▼') || trimmed.includes('↓')) {
    return 'negative';
  }
  if (trimmed.startsWith('+') || trimmed.includes('▲') || trimmed.includes('↑')) {
    return 'positive';
  }
  return 'neutral';
};

export function KpiWidget({ label, value, delta, description }: KpiWidgetProps) {
  const tone = resolveTone(delta);

  return (
    <div className={styles.card}>
      <p className={styles.label}>{label}</p>
      <div className={styles.value}>{value}</div>
      {delta ? (
        <div className={`${styles.delta} ${styles[tone]}`}>
          {delta}
          {description ? ` ${description}` : ''}
        </div>
      ) : (
        <div className={styles.deltaMuted}>No change vs last period</div>
      )}
    </div>
  );
}
