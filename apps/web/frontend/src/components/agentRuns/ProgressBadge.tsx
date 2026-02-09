import styles from './ProgressBadge.module.css';

interface ProgressBadgeProps {
  status: string;
  progress?: number | null;
}

const formatProgress = (progress?: number | null) => {
  if (progress === null || progress === undefined) return null;
  if (Number.isNaN(progress)) return null;
  return `${Math.round(progress)}%`;
};

export function ProgressBadge({ status, progress }: ProgressBadgeProps) {
  const progressText = formatProgress(progress);
  const label = progressText ? `${status} · ${progressText}` : status;
  return (
    <span className={styles.badge} data-status={status} aria-label={`Status: ${label}`}>
      <span className={styles.indicator} aria-hidden="true" />
      {label}
    </span>
  );
}
