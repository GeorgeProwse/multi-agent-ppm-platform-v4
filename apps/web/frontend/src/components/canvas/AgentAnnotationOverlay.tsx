import styles from './AgentAnnotationOverlay.module.css';

export interface AnnotationData {
  annotation_id: string;
  agent_name: string;
  block_id: string;
  content: string;
  annotation_type: 'suggestion' | 'warning' | 'insight' | 'quality';
  dismissed: boolean;
}

interface AgentAnnotationOverlayProps {
  annotations: AnnotationData[];
  onDismiss: (annotationId: string) => void;
  onApply: (annotationId: string) => void;
}

const TYPE_STYLES: Record<string, { color: string; icon: string }> = {
  suggestion: { color: '#3b82f6', icon: '\uD83D\uDCA1' },
  warning: { color: '#eab308', icon: '\u26A0\uFE0F' },
  insight: { color: '#22c55e', icon: '\uD83D\uDD0D' },
  quality: { color: '#ef4444', icon: '\u2714\uFE0F' },
};

export function AgentAnnotationOverlay({ annotations, onDismiss, onApply }: AgentAnnotationOverlayProps) {
  const active = annotations.filter(a => !a.dismissed);
  if (active.length === 0) return null;

  return (
    <div className={styles.overlay}>
      {active.map(ann => {
        const typeStyle = TYPE_STYLES[ann.annotation_type] || TYPE_STYLES.suggestion;
        return (
          <div
            key={ann.annotation_id}
            className={styles.annotation}
            style={{ borderLeftColor: typeStyle.color }}
          >
            <div className={styles.annotationHeader}>
              <span className={styles.agentName}>{ann.agent_name}</span>
              <span className={styles.typeBadge} style={{ background: typeStyle.color }}>
                {ann.annotation_type}
              </span>
            </div>
            <p className={styles.content}>{ann.content}</p>
            <div className={styles.actions}>
              <button className={styles.applyBtn} onClick={() => onApply(ann.annotation_id)}>Apply</button>
              <button className={styles.dismissBtn} onClick={() => onDismiss(ann.annotation_id)}>Dismiss</button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
