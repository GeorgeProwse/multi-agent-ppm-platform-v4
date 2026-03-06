import { useCallback, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './NLWorkflowInput.module.css';

interface WorkflowStep {
  id: string;
  type: string;
  name: string;
  description: string;
  agent_id?: string;
  transitions: Array<{ target: string; condition?: string }>;
}

interface WorkflowDefinition {
  name: string;
  description: string;
  steps: WorkflowStep[];
}

const STEP_TYPE_COLORS: Record<string, string> = {
  task: '#3b82f6',
  decision: '#eab308',
  approval: '#ef4444',
  notification: '#22c55e',
  parallel: '#8b5cf6',
  api: '#6b7280',
};

interface NLWorkflowInputProps {
  onWorkflowGenerated?: (definition: WorkflowDefinition) => void;
}

export function NLWorkflowInput({ onWorkflowGenerated }: NLWorkflowInputProps) {
  const [description, setDescription] = useState('');
  const [definition, setDefinition] = useState<WorkflowDefinition | null>(null);
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);

  const generate = useCallback(async () => {
    setLoading(true);
    try {
      const result = await requestJson<{ definition: WorkflowDefinition }>('/v1/workflows/from-natural-language', {
        method: 'POST',
        body: JSON.stringify({ description }),
      });
      setDefinition(result.definition);
      onWorkflowGenerated?.(result.definition);
    } catch {
      // demo
    } finally {
      setLoading(false);
    }
  }, [description, onWorkflowGenerated]);

  const refine = useCallback(async () => {
    if (!definition) return;
    setLoading(true);
    try {
      const result = await requestJson<{ definition: WorkflowDefinition }>('/v1/workflows/from-natural-language/refine', {
        method: 'POST',
        body: JSON.stringify({ definition, feedback }),
      });
      setDefinition(result.definition);
      setFeedback('');
      onWorkflowGenerated?.(result.definition);
    } catch {
      // demo
    } finally {
      setLoading(false);
    }
  }, [definition, feedback, onWorkflowGenerated]);

  const deploy = useCallback(async () => {
    if (!definition) return;
    setLoading(true);
    try {
      await requestJson('/v1/workflows/from-natural-language/deploy', {
        method: 'POST',
        body: JSON.stringify({ definition }),
      });
    } catch {
      // demo
    } finally {
      setLoading(false);
    }
  }, [definition]);

  return (
    <div className={styles.container}>
      <div className={styles.inputSection}>
        <textarea
          className={styles.textarea}
          placeholder="Describe your workflow in plain English... e.g., 'When a new demand comes in, classify it, assess risks, route high-risk items for executive approval, then schedule the work and notify stakeholders.'"
          value={description}
          onChange={e => setDescription(e.target.value)}
          rows={4}
        />
        <button className={styles.generateBtn} onClick={generate} disabled={loading || !description.trim()}>
          {loading ? 'Generating...' : 'Generate Workflow'}
        </button>
      </div>

      {definition && (
        <div className={styles.previewSection}>
          <h3>{definition.name}</h3>
          <div className={styles.stepFlow}>
            {definition.steps.map((step, i) => (
              <div key={step.id} className={styles.stepNode}>
                <div className={styles.stepBadge} style={{ background: STEP_TYPE_COLORS[step.type] || '#6b7280' }}>{step.type}</div>
                <div className={styles.stepName}>{step.name}</div>
                <div className={styles.stepDesc}>{step.description}</div>
                {step.agent_id && <div className={styles.stepAgent}>Agent: {step.agent_id}</div>}
                {i < definition.steps.length - 1 && <div className={styles.arrow}>&#8595;</div>}
              </div>
            ))}
          </div>

          <div className={styles.refineSection}>
            <input
              className={styles.refineInput}
              type="text"
              placeholder="What would you like to change?"
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
            />
            <button className={styles.refineBtn} onClick={refine} disabled={!feedback.trim() || loading}>Refine</button>
          </div>

          <div className={styles.actionBar}>
            <button className={styles.deployBtn} onClick={deploy} disabled={loading}>Deploy Workflow</button>
            <button className={styles.resetBtn} onClick={() => { setDefinition(null); setDescription(''); }}>Start Over</button>
          </div>
        </div>
      )}
    </div>
  );
}
