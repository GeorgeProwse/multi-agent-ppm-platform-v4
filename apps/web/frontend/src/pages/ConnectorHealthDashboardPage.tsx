import { useCallback, useEffect, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './ConnectorHealthDashboardPage.module.css';

interface ConnectorHealth {
  connector_id: string;
  name: string;
  category: string;
  status: string;
  circuit_state: string;
  last_sync: string | null;
  error_rate_1h: number;
  sync_direction: string;
}

interface FreshnessRecord {
  connector_id: string;
  connector_name: string;
  entity_type: string;
  last_synced_at: string | null;
  record_count: number;
  freshness_status: string;
}

interface ConflictRecord {
  conflict_id: string;
  connector_name: string;
  entity_type: string;
  entity_id: string;
  source_value: string;
  canonical_value: string;
  detected_at: string;
  status: string;
}

const statusColors: Record<string, string> = {
  healthy: '#22c55e',
  degraded: '#eab308',
  down: '#ef4444',
};

const freshnessColors: Record<string, string> = {
  fresh: '#22c55e',
  stale: '#eab308',
  critical: '#ef4444',
};

export default function ConnectorHealthDashboardPage() {
  const [health, setHealth] = useState<ConnectorHealth[]>([]);
  const [freshness, setFreshness] = useState<FreshnessRecord[]>([]);
  const [conflicts, setConflicts] = useState<ConflictRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [h, f, c] = await Promise.all([
        requestJson<ConnectorHealth[]>('/v1/connectors/health/summary'),
        requestJson<FreshnessRecord[]>('/v1/connectors/health/freshness'),
        requestJson<ConflictRecord[]>('/v1/connectors/health/conflicts'),
      ]);
      setHealth(h);
      setFreshness(f);
      setConflicts(c);
    } catch {
      // demo fallback
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleResolve = async (conflictId: string, strategy: string) => {
    try {
      await requestJson(`/v1/connectors/health/conflicts/${conflictId}/resolve`, {
        method: 'POST',
        body: JSON.stringify({ strategy }),
      });
      setConflicts(prev => prev.filter(c => c.conflict_id !== conflictId));
    } catch {
      // ignore
    }
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Connector Health Dashboard</h1>
        <button className={styles.refreshBtn} onClick={fetchData} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </header>

      {/* Status Overview */}
      <section className={styles.section}>
        <h2>Connector Status</h2>
        <div className={styles.statusGrid}>
          {health.map(c => (
            <div key={c.connector_id} className={styles.statusCard}>
              <div className={styles.statusDot} style={{ background: statusColors[c.status] || '#999' }} />
              <div className={styles.statusInfo}>
                <strong>{c.name}</strong>
                <span className={styles.category}>{c.category}</span>
                <span className={styles.meta}>
                  {c.status} | {c.sync_direction} | err: {Math.round(c.error_rate_1h * 100)}%
                </span>
                {c.last_sync && <span className={styles.lastSync}>Last sync: {new Date(c.last_sync).toLocaleString()}</span>}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Data Freshness */}
      <section className={styles.section}>
        <h2>Data Freshness</h2>
        <table className={styles.table}>
          <thead>
            <tr><th>Connector</th><th>Entity Type</th><th>Last Synced</th><th>Records</th><th>Status</th></tr>
          </thead>
          <tbody>
            {freshness.map((f, i) => (
              <tr key={i}>
                <td>{f.connector_name}</td>
                <td>{f.entity_type}</td>
                <td>{f.last_synced_at ? new Date(f.last_synced_at).toLocaleString() : 'Never'}</td>
                <td>{f.record_count.toLocaleString()}</td>
                <td><span className={styles.freshnessBadge} style={{ background: freshnessColors[f.freshness_status] || '#999' }}>{f.freshness_status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Conflict Queue */}
      <section className={styles.section}>
        <h2>Conflict Resolution Queue</h2>
        {conflicts.length === 0 ? (
          <p className={styles.empty}>No unresolved conflicts</p>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr><th>Connector</th><th>Entity</th><th>Source Value</th><th>Canonical Value</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {conflicts.map(c => (
                <tr key={c.conflict_id}>
                  <td>{c.connector_name}</td>
                  <td>{c.entity_type} / {c.entity_id}</td>
                  <td><code>{c.source_value}</code></td>
                  <td><code>{c.canonical_value}</code></td>
                  <td className={styles.actions}>
                    <button onClick={() => handleResolve(c.conflict_id, 'accept_source')}>Accept Source</button>
                    <button onClick={() => handleResolve(c.conflict_id, 'keep_canonical')}>Keep Canonical</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
