import { useCallback, useState } from 'react';
import { requestJson } from '@/services/apiClient';
import styles from './ExecutiveBriefingPage.module.css';

interface BriefingResponse {
  briefing_id: string;
  title: string;
  generated_at: string;
  audience: string;
  content: string;
  sections: Array<{ title: string; content: string }>;
}

const AUDIENCES = [
  { value: 'board', label: 'Board of Directors' },
  { value: 'c_suite', label: 'C-Suite Executive' },
  { value: 'pmo', label: 'PMO Leadership' },
  { value: 'delivery_team', label: 'Delivery Team' },
];

const SECTIONS = ['highlights', 'risks', 'financials', 'schedule', 'resources', 'recommendations'];

export default function ExecutiveBriefingPage() {
  const [audience, setAudience] = useState('c_suite');
  const [tone, setTone] = useState('formal');
  const [selectedSections, setSelectedSections] = useState<string[]>(SECTIONS);
  const [briefing, setBriefing] = useState<BriefingResponse | null>(null);
  const [generating, setGenerating] = useState(false);

  const toggleSection = (s: string) => {
    setSelectedSections(prev =>
      prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]
    );
  };

  const generate = useCallback(async () => {
    setGenerating(true);
    try {
      const result = await requestJson<BriefingResponse>('/api/briefings/generate', {
        method: 'POST',
        body: JSON.stringify({
          portfolio_id: 'default',
          audience,
          tone,
          sections: selectedSections,
          format: 'markdown',
        }),
      });
      setBriefing(result);
    } catch {
      // demo fallback
    } finally {
      setGenerating(false);
    }
  }, [audience, tone, selectedSections]);

  const copyToClipboard = () => {
    if (briefing) navigator.clipboard.writeText(briefing.content);
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Executive Briefing Generator</h1>
      </header>

      <div className={styles.layout}>
        {/* Config Panel */}
        <aside className={styles.configPanel}>
          <div className={styles.configSection}>
            <label>Audience</label>
            <select value={audience} onChange={e => setAudience(e.target.value)}>
              {AUDIENCES.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
            </select>
          </div>

          <div className={styles.configSection}>
            <label>Tone</label>
            <div className={styles.radioGroup}>
              {['formal', 'concise', 'detailed'].map(t => (
                <label key={t} className={styles.radioLabel}>
                  <input type="radio" name="tone" value={t} checked={tone === t} onChange={() => setTone(t)} />
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </label>
              ))}
            </div>
          </div>

          <div className={styles.configSection}>
            <label>Sections</label>
            <div className={styles.checkboxGroup}>
              {SECTIONS.map(s => (
                <label key={s} className={styles.checkboxLabel}>
                  <input type="checkbox" checked={selectedSections.includes(s)} onChange={() => toggleSection(s)} />
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </label>
              ))}
            </div>
          </div>

          <button className={styles.generateBtn} onClick={generate} disabled={generating}>
            {generating ? 'Generating...' : 'Generate Briefing'}
          </button>
        </aside>

        {/* Preview */}
        <main className={styles.previewPanel}>
          {briefing ? (
            <>
              <div className={styles.previewHeader}>
                <h2>{briefing.title}</h2>
                <div className={styles.previewActions}>
                  <button onClick={copyToClipboard}>Copy</button>
                  <button onClick={generate}>Regenerate</button>
                </div>
              </div>
              <div className={styles.previewContent}>
                <pre>{briefing.content}</pre>
              </div>
            </>
          ) : (
            <div className={styles.emptyState}>
              <p>Configure your briefing parameters and click "Generate Briefing" to create an AI-powered executive summary.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
