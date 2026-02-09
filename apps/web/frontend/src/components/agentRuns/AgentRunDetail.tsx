import { Link } from 'react-router-dom';
import { ProgressBadge } from './ProgressBadge';
import type { AgentRunRecord } from '@/types/agentRuns';
import styles from './AgentRunDetail.module.css';

interface AgentRunDetailProps {
  run?: AgentRunRecord | null;
}

const formatTimestamp = (value?: string | null) => {
  if (!value) return 'Not available';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
};

const extractAuditIds = (metadata?: Record<string, unknown>): string[] => {
  if (!metadata) return [];
  const candidates = [
    'audit_event_id',
    'audit_event_ids',
    'audit_event',
    'audit_events',
    'audit_id',
    'audit_ids',
    'auditId',
    'auditIds',
  ];
  const collectIds = (value: unknown): string[] => {
    if (!value) return [];
    if (typeof value === 'string') return [value];
    if (Array.isArray(value)) return value.flatMap(collectIds).filter(Boolean);
    if (typeof value === 'object') {
      const record = value as Record<string, unknown>;
      if (typeof record.id === 'string') return [record.id];
      if (typeof record.event_id === 'string') return [record.event_id];
    }
    return [];
  };
  const ids = candidates.flatMap((key) => collectIds(metadata[key]));
  return Array.from(new Set(ids));
};

const getProgress = (metadata?: Record<string, unknown>) => {
  if (!metadata) return null;
  const progress = metadata.progress ?? metadata.progress_percent ?? metadata.progressPercent;
  if (typeof progress === 'number') return progress;
  if (typeof progress === 'string') {
    const parsed = Number(progress);
    return Number.isNaN(parsed) ? null : parsed;
  }
  return null;
};

export function AgentRunDetail({ run }: AgentRunDetailProps) {
  if (!run) {
    return <div className={styles.empty}>Select a run to see details.</div>;
  }

  const metadata = run.data.metadata ?? {};
  const auditIds = extractAuditIds(metadata);

  return (
    <section className={styles.panel}>
      <header className={styles.header}>
        <div>
          <h2 className={styles.title}>{run.data.id}</h2>
          <p className={styles.subTitle}>Agent: {run.data.agent_id}</p>
        </div>
        <ProgressBadge status={run.data.status} progress={getProgress(metadata)} />
      </header>

      <div className={styles.section}>
        <h3>Timeline</h3>
        <dl className={styles.definition}>
          <dt>Created</dt>
          <dd>{formatTimestamp(run.data.created_at)}</dd>
          <dt>Started</dt>
          <dd>{formatTimestamp(run.data.started_at)}</dd>
          <dt>Completed</dt>
          <dd>{formatTimestamp(run.data.completed_at)}</dd>
          <dt>Updated</dt>
          <dd>{formatTimestamp(run.data.updated_at)}</dd>
        </dl>
      </div>

      <div className={styles.section}>
        <h3>Audit trail</h3>
        {auditIds.length ? (
          <div className={styles.linkList}>
            {auditIds.map((auditId) => (
              <Link
                key={auditId}
                className={styles.link}
                to={`/admin/audit?eventId=${encodeURIComponent(auditId)}`}
              >
                Audit event {auditId}
              </Link>
            ))}
          </div>
        ) : (
          <p className={styles.subTitle}>No audit identifiers were recorded for this run.</p>
        )}
      </div>

      <div className={styles.section}>
        <h3>Metadata</h3>
        <pre className={styles.metadata}>{JSON.stringify(metadata, null, 2)}</pre>
      </div>
    </section>
  );
}
