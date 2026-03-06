import { useCallback, useEffect, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './SecurityPostureDashboardPage.module.css';

interface SecurityPosture {
  posture_score: number;
  policy_count: number;
  abac_coverage_pct: number;
  mfa_enabled_pct: number;
  secrets_rotation_status: string;
  recent_violations: number;
  compliance_checks: Array<{ framework: string; status: string; last_audit: string | null }>;
  classification_distribution: Record<string, number>;
}

const statusColors: Record<string, string> = { pass: '#22c55e', partial: '#eab308', na: '#9ca3af', fail: '#ef4444' };
const classColors: Record<string, string> = { public: '#9ca3af', internal: '#3b82f6', confidential: '#f59e0b', restricted: '#ef4444' };

function PostureScore({ score }: { score: number }) {
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? '#22c55e' : score >= 60 ? '#eab308' : '#ef4444';
  return (
    <div className={styles.scoreContainer}>
      <svg width="140" height="140" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="54" fill="none" stroke="#e5e7eb" strokeWidth="8" />
        <circle cx="60" cy="60" r="54" fill="none" stroke={color} strokeWidth="8" strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" transform="rotate(-90 60 60)" />
        <text x="60" y="60" textAnchor="middle" dominantBaseline="central" fontSize="28" fontWeight="700" fill={color}>{score}</text>
        <text x="60" y="80" textAnchor="middle" fontSize="10" fill="#666">/ 100</text>
      </svg>
    </div>
  );
}

export default function SecurityPostureDashboardPage() {
  const [posture, setPosture] = useState<SecurityPosture | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await requestJson<SecurityPosture>('/api/security/posture');
      setPosture(data);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (!posture) return <div className={styles.loading}>Loading security posture...</div>;

  const totalEntities = Object.values(posture.classification_distribution).reduce((a, b) => a + b, 0);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Security Posture Dashboard</h1>
      </header>

      <div className={styles.grid}>
        {/* Posture Score */}
        <section className={styles.card}>
          <h2>Security Score</h2>
          <PostureScore score={posture.posture_score} />
          <div className={styles.metrics}>
            <div className={styles.metric}><span className={styles.metricValue}>{posture.policy_count}</span><span className={styles.metricLabel}>Active Policies</span></div>
            <div className={styles.metric}><span className={styles.metricValue}>{posture.abac_coverage_pct}%</span><span className={styles.metricLabel}>ABAC Coverage</span></div>
            <div className={styles.metric}><span className={styles.metricValue}>{posture.mfa_enabled_pct}%</span><span className={styles.metricLabel}>MFA Enabled</span></div>
            <div className={styles.metric}><span className={styles.metricValue}>{posture.recent_violations}</span><span className={styles.metricLabel}>Recent Violations</span></div>
          </div>
        </section>

        {/* Classification Distribution */}
        <section className={styles.card}>
          <h2>Data Classification</h2>
          <div className={styles.classChart}>
            {Object.entries(posture.classification_distribution).map(([label, count]) => (
              <div key={label} className={styles.classRow}>
                <span className={styles.classLabel} style={{ color: classColors[label] }}>{label}</span>
                <div className={styles.classBar}>
                  <div className={styles.classFill} style={{ width: `${(count / totalEntities) * 100}%`, background: classColors[label] }} />
                </div>
                <span className={styles.classCount}>{count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Compliance */}
        <section className={styles.card}>
          <h2>Compliance Status</h2>
          <div className={styles.complianceList}>
            {posture.compliance_checks.map(c => (
              <div key={c.framework} className={styles.complianceItem}>
                <span className={styles.complianceDot} style={{ background: statusColors[c.status] }} />
                <span className={styles.complianceFramework}>{c.framework}</span>
                <span className={styles.complianceStatus}>{c.status}</span>
                {c.last_audit && <span className={styles.complianceDate}>Audit: {c.last_audit}</span>}
              </div>
            ))}
          </div>
        </section>

        {/* Quick Actions */}
        <section className={styles.card}>
          <h2>Policy Management</h2>
          <p className={styles.policyInfo}>
            {posture.policy_count} policies active with {posture.abac_coverage_pct}% entity coverage.
            Secrets rotation: <strong>{posture.secrets_rotation_status}</strong>.
          </p>
          <p className={styles.hint}>Visit Admin &gt; Roles &gt; Policies tab to manage ABAC policies visually.</p>
        </section>
      </div>
    </div>
  );
}
