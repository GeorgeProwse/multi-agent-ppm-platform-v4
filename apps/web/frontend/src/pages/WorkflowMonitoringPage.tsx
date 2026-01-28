import { useEffect, useState } from 'react';
import styles from './WorkflowMonitoringPage.module.css';

const API_BASE = '/api/v1';

interface WorkflowInstance {
  run_id: string;
  workflow_id: string;
  status: string;
  current_step_id?: string | null;
  created_at: string;
  updated_at: string;
}

interface WorkflowEvent {
  event_id: string;
  step_id?: string | null;
  status: string;
  message: string;
  created_at: string;
}

const samplePayload = {
  charter_id: 'charter-2024-001',
  requester: 'project-manager',
  project_id: 'project-alpha',
  description: 'Publish charter for Project Alpha',
  requires_approval: true,
};

export function WorkflowMonitoringPage() {
  const [instances, setInstances] = useState<WorkflowInstance[]>([]);
  const [selectedInstance, setSelectedInstance] =
    useState<WorkflowInstance | null>(null);
  const [timeline, setTimeline] = useState<WorkflowEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchInstances = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/workflows/instances`);
      const data = await response.json();
      setInstances(data);
    } catch (error) {
      console.error('Failed to fetch workflow instances', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTimeline = async (runId: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/workflows/instances/${runId}/timeline`
      );
      const data = await response.json();
      setTimeline(data);
    } catch (error) {
      console.error('Failed to fetch timeline', error);
    }
  };

  const startSampleWorkflow = async () => {
    try {
      await fetch(`${API_BASE}/workflows/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: 'publish-charter',
          payload: samplePayload,
          actor: { id: 'project-manager', type: 'user' },
        }),
      });
      await fetchInstances();
    } catch (error) {
      console.error('Failed to start workflow', error);
    }
  };

  useEffect(() => {
    fetchInstances();
  }, []);

  useEffect(() => {
    if (selectedInstance) {
      fetchTimeline(selectedInstance.run_id);
    }
  }, [selectedInstance]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Workflow Monitoring</h1>
        <p>
          Track workflow instances and review their execution timelines in real
          time.
        </p>
        <button className={styles.primaryButton} onClick={startSampleWorkflow}>
          Start “Publish Charter” workflow
        </button>
      </header>

      <div className={styles.layout}>
        <section className={styles.listSection}>
          <div className={styles.sectionHeader}>
            <h2>Instances</h2>
            <button onClick={fetchInstances} className={styles.secondaryButton}>
              Refresh
            </button>
          </div>
          {loading && <div className={styles.emptyState}>Loading...</div>}
          {!loading && instances.length === 0 && (
            <div className={styles.emptyState}>
              No workflow instances yet. Start the sample workflow to populate
              the list.
            </div>
          )}
          <ul className={styles.instanceList}>
            {instances.map((instance) => (
              <li
                key={instance.run_id}
                className={`${styles.instanceCard} ${
                  selectedInstance?.run_id === instance.run_id
                    ? styles.activeCard
                    : ''
                }`}
                onClick={() => setSelectedInstance(instance)}
              >
                <div>
                  <h3>{instance.workflow_id}</h3>
                  <p>Run ID: {instance.run_id}</p>
                </div>
                <div className={styles.instanceMeta}>
                  <span className={styles.statusBadge}>{instance.status}</span>
                  <span>
                    Step: {instance.current_step_id ?? 'completed'}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <aside className={styles.timelineSection}>
          <h2>Timeline</h2>
          {!selectedInstance && (
            <div className={styles.emptyState}>
              Select a workflow instance to view its timeline.
            </div>
          )}
          {selectedInstance && (
            <>
              <div className={styles.timelineHeader}>
                <h3>{selectedInstance.workflow_id}</h3>
                <p>{selectedInstance.run_id}</p>
              </div>
              <ul className={styles.timelineList}>
                {timeline.length === 0 && (
                  <li className={styles.emptyState}>No events recorded yet.</li>
                )}
                {timeline.map((event) => (
                  <li key={event.event_id} className={styles.timelineItem}>
                    <div>
                      <strong>{event.status}</strong>
                      <span>{event.created_at}</span>
                    </div>
                    <p>{event.message}</p>
                    {event.step_id && (
                      <span className={styles.stepTag}>{event.step_id}</span>
                    )}
                  </li>
                ))}
              </ul>
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
