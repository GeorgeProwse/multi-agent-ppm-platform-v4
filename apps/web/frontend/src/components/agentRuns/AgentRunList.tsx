import { ProgressBadge } from './ProgressBadge';
import type { AgentRunRecord } from '@/types/agentRuns';
import styles from './AgentRunList.module.css';

interface AgentRunListProps {
  runs: AgentRunRecord[];
  selectedId?: string | null;
  onSelect: (runId: string) => void;
}

const formatTimestamp = (value?: string | null) => {
  if (!value) return 'Unknown';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
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

export function AgentRunList({ runs, selectedId, onSelect }: AgentRunListProps) {
  if (!runs.length) {
    return <div className={styles.empty}>No agent runs found.</div>;
  }

  return (
    <div className={styles.list}>
      {runs.map((run) => (
        <button
          key={run.id}
          type="button"
          className={`${styles.item} ${selectedId === run.id ? styles.selected : ''}`}
          onClick={() => onSelect(run.id)}
        >
          <div className={styles.row}>
            <div className={styles.runId}>{run.data.id}</div>
            <ProgressBadge
              status={run.data.status}
              progress={getProgress(run.data.metadata)}
            />
          </div>
          <div className={styles.row}>
            <span className={styles.agentId}>{run.data.agent_id}</span>
            <span className={styles.meta}>Created {formatTimestamp(run.data.created_at)}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
