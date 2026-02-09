import { useEffect, useMemo, useState } from 'react';
import { useAppStore } from '@/store';
import { AgentRunList } from '@/components/agentRuns/AgentRunList';
import { AgentRunDetail } from '@/components/agentRuns/AgentRunDetail';
import type { AgentRunRecord } from '@/types/agentRuns';
import styles from './AgentRunsPage.module.css';

const API_BASE = '/v1';

export function AgentRunsPage() {
  const { featureFlags } = useAppStore();
  const [runs, setRuns] = useState<AgentRunRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const featureEnabled = featureFlags.agent_run_ui === true;

  useEffect(() => {
    if (!featureEnabled) {
      setLoading(false);
      return;
    }
    let mounted = true;
    const load = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE}/agent-runs?limit=200`);
        if (!response.ok) {
          throw new Error('Failed to fetch agent runs');
        }
        const data = (await response.json()) as AgentRunRecord[];
        if (!mounted) return;
        setRuns(data);
        setSelectedId((prev) => prev ?? data[0]?.id ?? null);
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setRuns([]);
        setError(err instanceof Error ? err.message : 'Unable to load agent runs');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, [featureEnabled]);

  const selectedRun = useMemo(
    () => runs.find((run) => run.id === selectedId) ?? null,
    [runs, selectedId]
  );

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Agent Runs</h1>
        <p>Track execution history, audit activity, and run progress for orchestration tasks.</p>
      </header>

      {!featureEnabled && (
        <div className={styles.notice} role="status">
          Agent run monitoring is currently disabled.
        </div>
      )}

      {featureEnabled && loading && (
        <div className={styles.loading} role="status" aria-live="polite">
          Loading agent runs...
        </div>
      )}

      {featureEnabled && error && !loading && (
        <div className={styles.error} role="alert">
          {error}
        </div>
      )}

      {featureEnabled && !loading && !error && (
        <div className={styles.grid}>
          <AgentRunList
            runs={runs}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
          <AgentRunDetail run={selectedRun} />
        </div>
      )}
    </div>
  );
}
