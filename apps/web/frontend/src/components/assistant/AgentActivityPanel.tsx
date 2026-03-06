import { useCopilotStore, type AgentExecutionState } from '@/store/copilot';
import styles from './AgentActivityPanel.module.css';

function formatAgentName(agentId: string): string {
  return agentId
    .replace(/-/g, ' ')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function ConfidenceBadge({ score }: { score: number | null }) {
  if (score === null) return null;
  const pct = Math.round(score * 100);
  const cls =
    score >= 0.8 ? styles.confidenceHigh : score >= 0.5 ? styles.confidenceMedium : styles.confidenceLow;
  return <span className={`${styles.confidenceBadge} ${cls}`}>{pct}%</span>;
}

function StatusIndicator({ status }: { status: AgentExecutionState['status'] }) {
  switch (status) {
    case 'thinking':
      return <span className={styles.spinner} aria-label="Thinking" />;
    case 'completed':
      return <span className={styles.checkmark} aria-label="Completed" />;
    case 'error':
      return <span className={styles.errorIcon} aria-label="Error" />;
    default:
      return <span className={styles.pendingDot} aria-label="Pending" />;
  }
}

function ElapsedTime({ startedAt, completedAt }: { startedAt: number | null; completedAt: number | null }) {
  if (!startedAt) return null;
  const endTime = completedAt ?? Date.now() / 1000;
  const elapsed = Math.round(endTime - startedAt);
  return <span className={styles.elapsed}>{elapsed}s</span>;
}

export function AgentActivityPanel() {
  const { activeAgents, orchestrationStatus } = useCopilotStore();
  const agents = Object.entries(activeAgents);

  if (orchestrationStatus === 'idle' || agents.length === 0) return null;

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.headerLabel}>Agent Activity</span>
        {orchestrationStatus === 'running' && <span className={styles.liveIndicator}>LIVE</span>}
      </div>
      <ul className={styles.agentList}>
        {agents.map(([taskId, agent]) => (
          <li key={taskId} className={styles.agentRow}>
            <StatusIndicator status={agent.status} />
            <span className={styles.agentName}>{formatAgentName(agent.agentId)}</span>
            <ElapsedTime startedAt={agent.startedAt} completedAt={agent.completedAt} />
            <ConfidenceBadge score={agent.confidence} />
          </li>
        ))}
      </ul>
    </div>
  );
}
