import { useCallback, useEffect, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './PredictiveDashboardPage.module.css';

interface HealthPrediction {
  project_id: string;
  project_name: string;
  current_health_score: number;
  predicted_health_30d: number;
  predicted_health_60d: number;
  predicted_health_90d: number;
  risk_signal: number;
  schedule_signal: number;
  budget_signal: number;
  resource_signal: number;
  trend: string;
}

interface RiskHeatmapCell {
  project_id: string;
  project_name: string;
  risk_category: string;
  risk_score: number;
  trend: string;
}

interface BottleneckPrediction {
  resource_type: string;
  skill_area: string;
  severity: string;
  demand_capacity_ratio: number;
  bottleneck_start_date: string;
  bottleneck_end_date: string;
}

function healthColor(score: number): string {
  if (score >= 0.7) return '#22c55e';
  if (score >= 0.4) return '#eab308';
  return '#ef4444';
}

function riskColor(score: number): string {
  if (score >= 0.7) return '#ef4444';
  if (score >= 0.4) return '#eab308';
  return '#22c55e';
}

function trendArrow(trend: string): string {
  if (trend === 'improving' || trend === 'down') return '\u2193';
  if (trend === 'declining' || trend === 'up') return '\u2191';
  return '\u2192';
}

export default function PredictiveDashboardPage() {
  const [health, setHealth] = useState<HealthPrediction[]>([]);
  const [heatmap, setHeatmap] = useState<RiskHeatmapCell[]>([]);
  const [bottlenecks, setBottlenecks] = useState<BottleneckPrediction[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [h, r, b] = await Promise.all([
        requestJson<HealthPrediction[]>('/v1/predictive/health-forecast?portfolio_id=default'),
        requestJson<RiskHeatmapCell[]>('/v1/predictive/risk-heatmap?portfolio_id=default'),
        requestJson<BottleneckPrediction[]>('/v1/predictive/resource-bottlenecks?portfolio_id=default'),
      ]);
      setHealth(h);
      setHeatmap(r);
      setBottlenecks(b);
    } catch {
      // demo fallback
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const riskCategories = [...new Set(heatmap.map(c => c.risk_category))];
  const projects = [...new Set(heatmap.map(c => c.project_name))];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Predictive Intelligence Dashboard</h1>
        <button className={styles.refreshBtn} onClick={fetchData} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </header>

      <div className={styles.grid}>
        {/* Health Forecast */}
        <section className={styles.card}>
          <h2>Health Forecast</h2>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Project</th>
                <th>Current</th>
                <th>30d</th>
                <th>60d</th>
                <th>90d</th>
                <th>Trend</th>
              </tr>
            </thead>
            <tbody>
              {health.map(h => (
                <tr key={h.project_id}>
                  <td>{h.project_name}</td>
                  <td><span className={styles.scoreBadge} style={{ background: healthColor(h.current_health_score) }}>{Math.round(h.current_health_score * 100)}</span></td>
                  <td><span className={styles.scoreBadge} style={{ background: healthColor(h.predicted_health_30d) }}>{Math.round(h.predicted_health_30d * 100)}</span></td>
                  <td><span className={styles.scoreBadge} style={{ background: healthColor(h.predicted_health_60d) }}>{Math.round(h.predicted_health_60d * 100)}</span></td>
                  <td><span className={styles.scoreBadge} style={{ background: healthColor(h.predicted_health_90d) }}>{Math.round(h.predicted_health_90d * 100)}</span></td>
                  <td className={styles.trend}>{trendArrow(h.trend)} {h.trend}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* Risk Heatmap */}
        <section className={styles.card}>
          <h2>Risk Heatmap</h2>
          <div className={styles.heatmapGrid}>
            <div className={styles.heatmapCorner} />
            {riskCategories.map(cat => <div key={cat} className={styles.heatmapHeader}>{cat}</div>)}
            {projects.map(proj => (
              <>
                <div key={`label-${proj}`} className={styles.heatmapRowLabel}>{proj}</div>
                {riskCategories.map(cat => {
                  const cell = heatmap.find(c => c.project_name === proj && c.risk_category === cat);
                  const score = cell?.risk_score ?? 0;
                  return (
                    <div
                      key={`${proj}-${cat}`}
                      className={styles.heatmapCell}
                      style={{ background: riskColor(score), opacity: 0.3 + score * 0.7 }}
                      title={`${proj} - ${cat}: ${Math.round(score * 100)}%`}
                    >
                      {Math.round(score * 100)}
                    </div>
                  );
                })}
              </>
            ))}
          </div>
        </section>

        {/* Resource Bottlenecks */}
        <section className={styles.card}>
          <h2>Resource Bottleneck Predictions</h2>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Skill Area</th>
                <th>Severity</th>
                <th>Demand/Capacity</th>
                <th>Period</th>
              </tr>
            </thead>
            <tbody>
              {bottlenecks.map((b, i) => (
                <tr key={i}>
                  <td>{b.skill_area}</td>
                  <td><span className={`${styles.severityBadge} ${styles[`severity-${b.severity}`]}`}>{b.severity}</span></td>
                  <td>{Math.round(b.demand_capacity_ratio * 100)}%</td>
                  <td>{b.bottleneck_start_date} to {b.bottleneck_end_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* Scenario Comparison placeholder */}
        <section className={styles.card}>
          <h2>Scenario Comparison</h2>
          <p className={styles.placeholder}>Select scenarios to compare using the Monte Carlo simulator.</p>
        </section>
      </div>
    </div>
  );
}
