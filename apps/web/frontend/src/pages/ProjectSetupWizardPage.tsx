import { useCallback, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './ProjectSetupWizardPage.module.css';

interface MethodologyRec {
  methodology: string;
  match_score: number;
  rationale: string;
  strengths: string[];
}

interface ProjectTemplate {
  template_id: string;
  name: string;
  methodology: string;
  industry: string;
  description: string;
  stages: Array<{ id: string; name: string; activities: string[] }>;
  activity_count: number;
}

const INDUSTRIES = ['technology', 'pharma', 'construction', 'finance', 'government', 'other'];
const RISK_LEVELS = ['low', 'medium', 'high'];
const REGULATIONS = ['SOX', 'GDPR', 'HIPAA', 'GxP'];

export default function ProjectSetupWizardPage() {
  const [step, setStep] = useState(0);
  const [industry, setIndustry] = useState('technology');
  const [teamSize, setTeamSize] = useState(10);
  const [duration, setDuration] = useState(6);
  const [riskLevel, setRiskLevel] = useState('medium');
  const [regulatory, setRegulatory] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<MethodologyRec[]>([]);
  const [selectedMethodology, setSelectedMethodology] = useState('');
  const [templates, setTemplates] = useState<ProjectTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ProjectTemplate | null>(null);
  const [projectName, setProjectName] = useState('');
  const [creating, setCreating] = useState(false);
  const [created, setCreated] = useState(false);

  const fetchRecommendations = useCallback(async () => {
    try {
      const recs = await requestJson<MethodologyRec[]>('/api/project-setup/recommend-methodology', {
        method: 'POST',
        body: JSON.stringify({ industry, team_size: teamSize, duration_months: duration, risk_level: riskLevel, regulatory }),
      });
      setRecommendations(recs);
      setStep(1);
    } catch { setStep(1); }
  }, [industry, teamSize, duration, riskLevel, regulatory]);

  const fetchTemplates = useCallback(async () => {
    try {
      const tmpls = await requestJson<ProjectTemplate[]>(`/api/project-setup/templates?methodology=${selectedMethodology}&industry=${industry}`);
      setTemplates(tmpls);
      if (tmpls.length === 0) {
        const all = await requestJson<ProjectTemplate[]>('/api/project-setup/templates');
        setTemplates(all);
      }
      setStep(2);
    } catch { setStep(2); }
  }, [selectedMethodology, industry]);

  const createProject = useCallback(async () => {
    if (!selectedTemplate || !projectName) return;
    setCreating(true);
    try {
      await requestJson('/api/project-setup/configure-workspace', {
        method: 'POST',
        body: JSON.stringify({ project_name: projectName, template_id: selectedTemplate.template_id }),
      });
      setCreated(true);
    } catch {
      // demo
    } finally {
      setCreating(false);
    }
  }, [selectedTemplate, projectName]);

  const toggleReg = (r: string) => setRegulatory(prev => prev.includes(r) ? prev.filter(x => x !== r) : [...prev, r]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>New Project Setup</h1>
        <div className={styles.steps}>
          {['Profile', 'Methodology', 'Template', 'Launch'].map((label, i) => (
            <span key={label} className={`${styles.stepDot} ${i === step ? styles.active : ''} ${i < step ? styles.completed : ''}`}>{label}</span>
          ))}
        </div>
      </header>

      {step === 0 && (
        <section className={styles.card}>
          <h2>Project Profile</h2>
          <div className={styles.formGrid}>
            <label>Industry<select value={industry} onChange={e => setIndustry(e.target.value)}>{INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}</select></label>
            <label>Team Size<input type="range" min="1" max="500" value={teamSize} onChange={e => setTeamSize(+e.target.value)} /><span>{teamSize}</span></label>
            <label>Duration (months)<input type="number" min="1" max="60" value={duration} onChange={e => setDuration(+e.target.value)} /></label>
            <label>Risk Level<select value={riskLevel} onChange={e => setRiskLevel(e.target.value)}>{RISK_LEVELS.map(r => <option key={r} value={r}>{r}</option>)}</select></label>
            <label>Regulatory<div className={styles.chipGroup}>{REGULATIONS.map(r => <button key={r} className={`${styles.chip} ${regulatory.includes(r) ? styles.chipActive : ''}`} onClick={() => toggleReg(r)}>{r}</button>)}</div></label>
          </div>
          <button className={styles.nextBtn} onClick={fetchRecommendations}>Next: Get Recommendations</button>
        </section>
      )}

      {step === 1 && (
        <section className={styles.card}>
          <h2>AI Methodology Recommendation</h2>
          <div className={styles.recGrid}>
            {recommendations.map(r => (
              <div key={r.methodology} className={`${styles.recCard} ${selectedMethodology === r.methodology ? styles.recSelected : ''}`} onClick={() => setSelectedMethodology(r.methodology)}>
                <div className={styles.recScore}>{Math.round(r.match_score * 100)}% match</div>
                <h3>{r.methodology}</h3>
                <p>{r.rationale}</p>
                <ul>{r.strengths.map(s => <li key={s}>{s}</li>)}</ul>
              </div>
            ))}
          </div>
          <div className={styles.navButtons}>
            <button onClick={() => setStep(0)}>Back</button>
            <button className={styles.nextBtn} onClick={fetchTemplates} disabled={!selectedMethodology}>Next: Browse Templates</button>
          </div>
        </section>
      )}

      {step === 2 && (
        <section className={styles.card}>
          <h2>Template Gallery</h2>
          <div className={styles.templateGrid}>
            {templates.map(t => (
              <div key={t.template_id} className={`${styles.templateCard} ${selectedTemplate?.template_id === t.template_id ? styles.templateSelected : ''}`} onClick={() => setSelectedTemplate(t)}>
                <h3>{t.name}</h3>
                <span className={styles.methodBadge}>{t.methodology}</span>
                <p>{t.description}</p>
                <div className={styles.stageList}>{t.stages.map(s => <span key={s.id} className={styles.stageBadge}>{s.name}</span>)}</div>
                <span className={styles.actCount}>{t.activity_count} activities</span>
              </div>
            ))}
          </div>
          <div className={styles.navButtons}>
            <button onClick={() => setStep(1)}>Back</button>
            <button className={styles.nextBtn} onClick={() => setStep(3)} disabled={!selectedTemplate}>Next: Configure & Launch</button>
          </div>
        </section>
      )}

      {step === 3 && (
        <section className={styles.card}>
          <h2>Configure & Launch</h2>
          {created ? (
            <div className={styles.successMsg}>Project created successfully!</div>
          ) : (
            <>
              <div className={styles.configForm}>
                <label>Project Name<input type="text" value={projectName} onChange={e => setProjectName(e.target.value)} placeholder="Enter project name" /></label>
                {selectedTemplate && (
                  <div className={styles.templatePreview}>
                    <h3>{selectedTemplate.name}</h3>
                    <p>Methodology: {selectedTemplate.methodology} | Stages: {selectedTemplate.stages.length} | Activities: {selectedTemplate.activity_count}</p>
                  </div>
                )}
              </div>
              <div className={styles.navButtons}>
                <button onClick={() => setStep(2)}>Back</button>
                <button className={styles.launchBtn} onClick={createProject} disabled={!projectName || creating}>{creating ? 'Creating...' : 'Create Project'}</button>
              </div>
            </>
          )}
        </section>
      )}
    </div>
  );
}
