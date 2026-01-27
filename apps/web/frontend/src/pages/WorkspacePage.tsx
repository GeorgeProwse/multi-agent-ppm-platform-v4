import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAppStore, type EntitySelection } from '@/store';
import styles from './WorkspacePage.module.css';

type EntityType = 'portfolio' | 'program' | 'project';

interface WorkspacePageProps {
  type: EntityType;
}

const typeLabels: Record<EntityType, string> = {
  portfolio: 'Portfolio',
  program: 'Program',
  project: 'Project',
};

const typeDescriptions: Record<EntityType, string> = {
  portfolio:
    'Strategic investment decisions and portfolio-level performance tracking.',
  program:
    'Coordination of related projects to achieve strategic objectives.',
  project: 'Execution of specific deliverables with defined scope and timeline.',
};

export function WorkspacePage({ type }: WorkspacePageProps) {
  const { portfolioId, programId, projectId } = useParams();
  const { setCurrentSelection, currentActivity, addTab, openTabs } = useAppStore();

  const entityId = portfolioId || programId || projectId || 'unknown';

  useEffect(() => {
    const selection: EntitySelection = {
      type,
      id: entityId,
      name: `${typeLabels[type]} ${entityId}`,
    };
    setCurrentSelection(selection);

    // Add a tab for this workspace if not already open
    const tabId = `${type}-${entityId}`;
    const existingTab = openTabs.find((t) => t.id === tabId);
    if (!existingTab) {
      addTab({
        id: tabId,
        title: `${typeLabels[type]}: ${entityId}`,
        type: 'dashboard',
        entityId,
      });
    }
  }, [type, entityId, setCurrentSelection, addTab, openTabs]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.badge}>{typeLabels[type]}</div>
        <h1 className={styles.title}>{entityId}</h1>
        <p className={styles.description}>{typeDescriptions[type]}</p>
      </header>

      <div className={styles.content}>
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Overview</h2>
          <div className={styles.placeholder}>
            <p>
              {typeLabels[type]} workspace content will be displayed here.
            </p>
            {currentActivity && (
              <p className={styles.activityNote}>
                Current activity: <strong>{currentActivity.name}</strong>
              </p>
            )}
          </div>
        </section>

        <div className={styles.grid}>
          <section className={styles.card}>
            <h3 className={styles.cardTitle}>Health Metrics</h3>
            <div className={styles.metrics}>
              <div className={styles.metric}>
                <span className={styles.metricValue}>--</span>
                <span className={styles.metricLabel}>Schedule</span>
              </div>
              <div className={styles.metric}>
                <span className={styles.metricValue}>--</span>
                <span className={styles.metricLabel}>Budget</span>
              </div>
              <div className={styles.metric}>
                <span className={styles.metricValue}>--</span>
                <span className={styles.metricLabel}>Quality</span>
              </div>
            </div>
          </section>

          <section className={styles.card}>
            <h3 className={styles.cardTitle}>Recent Activity</h3>
            <p className={styles.emptyState}>No recent activity</p>
          </section>

          <section className={styles.card}>
            <h3 className={styles.cardTitle}>Key Milestones</h3>
            <p className={styles.emptyState}>No milestones defined</p>
          </section>

          <section className={styles.card}>
            <h3 className={styles.cardTitle}>Risk Summary</h3>
            <p className={styles.emptyState}>No risks identified</p>
          </section>
        </div>
      </div>
    </div>
  );
}
