import styles from './StatusIndicator.module.css';

type StatusTone =
  | 'healthy'
  | 'watch'
  | 'risk'
  | 'neutral'
  | 'info'
  | 'success'
  | 'warning'
  | 'danger';

interface StatusIndicatorProps {
  status: StatusTone | string;
  label?: string;
  className?: string;
}

const resolveTone = (status: string): StatusTone => {
  if (status in styles) return status as StatusTone;
  const normalized = status.toLowerCase();
  if (['healthy', 'on track', 'good', 'green'].includes(normalized)) return 'healthy';
  if (['watch', 'medium', 'amber'].includes(normalized)) return 'watch';
  if (['risk', 'high', 'red'].includes(normalized)) return 'risk';
  if (['warning'].includes(normalized)) return 'warning';
  if (['danger', 'critical'].includes(normalized)) return 'danger';
  if (['success'].includes(normalized)) return 'success';
  if (['info'].includes(normalized)) return 'info';
  return 'neutral';
};

export function StatusIndicator({ status, label, className }: StatusIndicatorProps) {
  const tone = resolveTone(status);
  const classes = [styles.indicator, styles[tone], className].filter(Boolean).join(' ');

  return (
    <span className={classes} role="status" aria-label={label ?? status} />
  );
}
