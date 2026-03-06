import { useCallback, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './PolicyEditor.module.css';

interface PolicyCondition {
  field: string;
  operator: string;
  value: string;
}

interface PolicyDef {
  policy_id: string;
  name: string;
  description: string;
  effect: string;
  subjects: Record<string, unknown>;
  resources: Record<string, unknown>;
  actions: string[];
  conditions: PolicyCondition[];
  enabled: boolean;
}

const ACTIONS = ['read', 'write', 'delete', 'export'];
const OPERATORS = ['equals', 'not_equals', 'in', 'not_in', 'gt', 'lt', 'gte', 'lte', 'between', 'not_between', 'contains', 'not_contains'];

export function PolicyEditor() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [effect, setEffect] = useState<'allow' | 'deny'>('deny');
  const [selectedActions, setSelectedActions] = useState<string[]>([]);
  const [conditions, setConditions] = useState<PolicyCondition[]>([{ field: '', operator: 'equals', value: '' }]);
  const [testResult, setTestResult] = useState<{ decision: string; explanation: string } | null>(null);

  const toggleAction = (action: string) => {
    setSelectedActions(prev =>
      prev.includes(action) ? prev.filter(a => a !== action) : [...prev, action]
    );
  };

  const updateCondition = (index: number, field: keyof PolicyCondition, value: string) => {
    setConditions(prev => prev.map((c, i) => i === index ? { ...c, [field]: value } : c));
  };

  const addCondition = () => setConditions(prev => [...prev, { field: '', operator: 'equals', value: '' }]);
  const removeCondition = (index: number) => setConditions(prev => prev.filter((_, i) => i !== index));

  const buildPolicy = (): PolicyDef => ({
    policy_id: `pol-custom-${Date.now()}`,
    name,
    description,
    effect,
    subjects: {},
    resources: {},
    actions: selectedActions,
    conditions: conditions.filter(c => c.field),
    enabled: true,
  });

  const testPolicy = useCallback(async () => {
    try {
      const result = await requestJson<{ decision: string; explanation: string }>('/api/security/policies/test', {
        method: 'POST',
        body: JSON.stringify({
          policy: buildPolicy(),
          context: { subject: { role: 'analyst', region: 'US' }, resource: { classification: 'confidential' } },
        }),
      });
      setTestResult(result);
    } catch {}
  }, [name, description, effect, selectedActions, conditions]);

  const savePolicy = useCallback(async () => {
    try {
      await requestJson('/api/security/policies', {
        method: 'POST',
        body: JSON.stringify(buildPolicy()),
      });
    } catch {}
  }, [name, description, effect, selectedActions, conditions]);

  const yamlPreview = `policy:
  name: "${name}"
  effect: ${effect}
  actions: [${selectedActions.join(', ')}]
  conditions:
${conditions.filter(c => c.field).map(c => `    - field: ${c.field}\n      operator: ${c.operator}\n      value: ${c.value}`).join('\n')}`;

  return (
    <div className={styles.editor}>
      <div className={styles.form}>
        <div className={styles.field}>
          <label>Policy Name</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="e.g., Export Control" />
        </div>

        <div className={styles.field}>
          <label>Description</label>
          <input type="text" value={description} onChange={e => setDescription(e.target.value)} placeholder="What does this policy do?" />
        </div>

        <div className={styles.field}>
          <label>Effect</label>
          <div className={styles.toggleGroup}>
            <button className={`${styles.toggleBtn} ${effect === 'allow' ? styles.toggleActive : ''}`} onClick={() => setEffect('allow')}>Allow</button>
            <button className={`${styles.toggleBtn} ${effect === 'deny' ? styles.toggleActive : ''}`} onClick={() => setEffect('deny')}>Deny</button>
          </div>
        </div>

        <div className={styles.field}>
          <label>Actions</label>
          <div className={styles.checkboxRow}>
            {ACTIONS.map(a => (
              <label key={a} className={styles.checkLabel}>
                <input type="checkbox" checked={selectedActions.includes(a)} onChange={() => toggleAction(a)} />
                {a}
              </label>
            ))}
          </div>
        </div>

        <div className={styles.field}>
          <label>Conditions</label>
          {conditions.map((c, i) => (
            <div key={i} className={styles.conditionRow}>
              <input type="text" placeholder="field (e.g., subject.role)" value={c.field} onChange={e => updateCondition(i, 'field', e.target.value)} />
              <select value={c.operator} onChange={e => updateCondition(i, 'operator', e.target.value)}>
                {OPERATORS.map(op => <option key={op} value={op}>{op}</option>)}
              </select>
              <input type="text" placeholder="value" value={c.value} onChange={e => updateCondition(i, 'value', e.target.value)} />
              <button className={styles.removeBtn} onClick={() => removeCondition(i)}>x</button>
            </div>
          ))}
          <button className={styles.addBtn} onClick={addCondition}>+ Add Condition</button>
        </div>

        <div className={styles.actionBar}>
          <button className={styles.testBtn} onClick={testPolicy}>Test Policy</button>
          <button className={styles.saveBtn} onClick={savePolicy} disabled={!name}>Save Policy</button>
        </div>

        {testResult && (
          <div className={styles.testResult}>
            <strong>Decision: {testResult.decision}</strong>
            <p>{testResult.explanation}</p>
          </div>
        )}
      </div>

      <div className={styles.preview}>
        <h3>YAML Preview</h3>
        <pre>{yamlPreview}</pre>
      </div>
    </div>
  );
}
