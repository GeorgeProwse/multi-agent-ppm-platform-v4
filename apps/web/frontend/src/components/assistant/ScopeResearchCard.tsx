import { useMemo, useState } from 'react';
import type { ScopeResearchItem, ScopeResearchMessageData, ScopeResearchStatus } from '@/store/assistant';
import styles from './ScopeResearchCard.module.css';

type ScopeSection = 'scope' | 'requirements' | 'wbs';

interface ScopeResearchCardProps {
  data: ScopeResearchMessageData;
  onApplyAcceptedItems: (data: ScopeResearchMessageData, acceptedItems: ScopeResearchItem[]) => boolean;
}

export function ScopeResearchCard({ data, onApplyAcceptedItems }: ScopeResearchCardProps) {
  const [itemsBySection, setItemsBySection] = useState({
    scope: data.scope ?? [],
    requirements: data.requirements ?? [],
    wbs: data.wbs ?? [],
  });
  const [sectionsOpen, setSectionsOpen] = useState({
    scope: true,
    requirements: true,
    wbs: true,
  });
  const [previewOpen, setPreviewOpen] = useState(false);

  const acceptedItems = useMemo(
    () => [...itemsBySection.scope, ...itemsBySection.requirements, ...itemsBySection.wbs].filter((item) => item.status === 'accepted'),
    [itemsBySection]
  );

  const setStatus = (section: ScopeSection, id: string, status: ScopeResearchStatus) => {
    setItemsBySection((prev) => ({
      ...prev,
      [section]: prev[section].map((item) => (item.id === id ? { ...item, status } : item)),
    }));
  };

  const renderSection = (title: string, section: ScopeSection, items: ScopeResearchItem[]) => (
    <section className={styles.section}>
      <button
        type="button"
        className={styles.sectionToggle}
        onClick={() => setSectionsOpen((prev) => ({ ...prev, [section]: !prev[section] }))}
      >
        <span>{title}</span>
        <span>{sectionsOpen[section] ? '▾' : '▸'}</span>
      </button>
      {sectionsOpen[section] && (
        <div className={styles.sectionBody}>
          {items.length === 0 ? (
            <p className={styles.empty}>No suggestions yet.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className={styles.itemRow}>
                <span>{item.text}</span>
                <div className={styles.actions}>
                  <button
                    type="button"
                    className={`${styles.actionButton} ${item.status === 'accepted' ? styles.accepted : ''}`}
                    onClick={() => setStatus(section, item.id, 'accepted')}
                  >
                    Accept
                  </button>
                  <button
                    type="button"
                    className={`${styles.actionButton} ${item.status === 'rejected' ? styles.rejected : ''}`}
                    onClick={() => setStatus(section, item.id, 'rejected')}
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </section>
  );

  return (
    <div className={styles.card}>
      <h4 className={styles.header}>Scope Research Results</h4>

      {data.notice && <p className={styles.notice}>{data.notice}</p>}

      {renderSection('Scope statements', 'scope', itemsBySection.scope)}
      {renderSection('Requirements', 'requirements', itemsBySection.requirements)}
      {renderSection('WBS', 'wbs', itemsBySection.wbs)}

      <div className={styles.footer}>
        <button type="button" className={styles.secondary} onClick={() => setPreviewOpen((v) => !v)}>
          {previewOpen ? 'Hide preview' : 'Preview'}
        </button>
        <button
          type="button"
          className={styles.primary}
          onClick={() => onApplyAcceptedItems({ ...data, ...itemsBySection }, acceptedItems)}
        >
          Apply accepted items
        </button>
      </div>

      {previewOpen && (
        <p className={styles.preview}>Accepted items: {acceptedItems.length}</p>
      )}

      <div className={styles.sources}>
        <h5>Sources</h5>
        {data.sources && data.sources.length > 0 ? (
          <ul>
            {data.sources.map((source) => (
              <li key={source}>{source}</li>
            ))}
          </ul>
        ) : (
          <p>No sources provided for this response.</p>
        )}
      </div>
    </div>
  );
}
