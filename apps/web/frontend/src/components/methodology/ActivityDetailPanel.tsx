import type { MethodologyActivity } from '@/store/methodology';
import styles from './MethodologyMapCanvas.module.css';

interface ActivityDetailPanelProps {
  activity: MethodologyActivity;
  stageLabel: string;
  isLocked: boolean;
  missingPrerequisites: string[];
  runtimeActionsAvailable: string[];
  onLifecycleAction: (event: 'generate' | 'update' | 'review' | 'approve' | 'publish') => void;
}

const EVENTS: Array<'generate' | 'update' | 'review' | 'approve' | 'publish'> = ['generate', 'update', 'review', 'approve', 'publish'];

export function ActivityDetailPanel({
  activity,
  stageLabel,
  isLocked,
  missingPrerequisites,
  runtimeActionsAvailable,
  onLifecycleAction,
}: ActivityDetailPanelProps) {
  return (
    <section className={styles.canvas}>
      <h2>{activity.name}</h2>
      <p><strong>Stage:</strong> {stageLabel}</p>
      <p><strong>Status:</strong> {activity.status.replace('_', ' ')}</p>
      <p>{activity.description || 'No description available.'}</p>
      {missingPrerequisites.length > 0 && (
        <p><strong>Missing prerequisites:</strong> {missingPrerequisites.join(', ')}</p>
      )}
      {isLocked && <p>This activity is currently locked.</p>}
      <div className={styles.monitoringRow}>
        {EVENTS.filter((event) => runtimeActionsAvailable.includes(event)).map((event) => (
          <button key={event} type="button" className={styles.card} onClick={() => onLifecycleAction(event)}>
            {event}
          </button>
        ))}
      </div>
    </section>
  );
}
