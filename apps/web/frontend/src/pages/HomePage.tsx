import { Link } from 'react-router-dom';
import { useCanvasStore, SAMPLE_ARTIFACT_IDS } from '@/store/useCanvasStore';
import { Icon } from '@/components/icon/Icon';
import type { IconSemantic } from '@/components/icon/iconMap';
import styles from './HomePage.module.css';

const quickLinks: { title: string; description: string; path: string; icon: IconSemantic }[] = [
  {
    title: 'Portfolios',
    description: 'Manage strategic portfolios and investments',
    path: '/portfolio/demo',
    icon: 'domain.portfolio',
  },
  {
    title: 'Programs',
    description: 'Coordinate related projects and initiatives',
    path: '/program/demo',
    icon: 'domain.program',
  },
  {
    title: 'Projects',
    description: 'Execute and track individual projects',
    path: '/project/demo',
    icon: 'domain.project',
  },
];

const configLinks = [
  {
    title: 'Agents',
    description: 'Configure AI agents and their capabilities',
    path: '/config/agents',
  },
  {
    title: 'Connectors',
    description: 'Manage integrations with external systems',
    path: '/config/connectors',
  },
  {
    title: 'Connector Marketplace',
    description: 'Enable, configure, and track connector availability',
    path: '/marketplace/connectors',
  },
  {
    title: 'Workflows',
    description: 'Adjust workflow routing and orchestration settings',
    path: '/config/workflows',
  },
];

export function HomePage() {
  const { artifacts, openArtifact } = useCanvasStore();

  const handleOpenCharter = () => {
    const artifact = artifacts[SAMPLE_ARTIFACT_IDS.charter];
    if (artifact) openArtifact(artifact);
  };

  const handleOpenWBS = () => {
    const artifact = artifacts[SAMPLE_ARTIFACT_IDS.wbs];
    if (artifact) openArtifact(artifact);
  };

  const handleOpenTimeline = () => {
    const artifact = artifacts[SAMPLE_ARTIFACT_IDS.timeline];
    if (artifact) openArtifact(artifact);
  };

  const handleOpenSpreadsheet = () => {
    const artifact = artifacts[SAMPLE_ARTIFACT_IDS.spreadsheet];
    if (artifact) openArtifact(artifact);
  };

  const handleOpenDashboard = () => {
    const artifact = artifacts[SAMPLE_ARTIFACT_IDS.dashboard];
    if (artifact) openArtifact(artifact);
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Welcome to PPM Platform</h1>
        <p className={styles.subtitle}>
          Multi-agent project, program, and portfolio management
        </p>
      </header>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Open Canvas</h2>
        <p className={styles.sectionDescription}>
          Try the new Canvas framework with multi-tab management
        </p>
        <div className={styles.canvasButtons}>
          <button onClick={handleOpenCharter} className={styles.canvasButton}>
            <span className={styles.canvasIcon}>
              <Icon semantic="artifact.document" decorative />
            </span>
            Open Charter (Doc)
          </button>
          <button onClick={handleOpenWBS} className={styles.canvasButton}>
            <span className={styles.canvasIcon}>
              <Icon semantic="artifact.tree" decorative />
            </span>
            Open WBS (Tree)
          </button>
          <button onClick={handleOpenTimeline} className={styles.canvasButton}>
            <span className={styles.canvasIcon}>
              <Icon semantic="artifact.timeline" decorative />
            </span>
            Open Timeline
          </button>
          <button onClick={handleOpenSpreadsheet} className={styles.canvasButton}>
            <span className={styles.canvasIcon}>
              <Icon semantic="artifact.spreadsheet" decorative />
            </span>
            Open Spreadsheet
          </button>
          <button onClick={handleOpenDashboard} className={styles.canvasButton}>
            <span className={styles.canvasIcon}>
              <Icon semantic="artifact.dashboard" decorative />
            </span>
            Open Dashboard
          </button>
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Quick Access</h2>
        <div className={styles.cardGrid}>
          {quickLinks.map((link) => (
            <Link key={link.path} to={link.path} className={styles.card}>
              <div className={styles.cardIcon}>
                <Icon semantic={link.icon} decorative size="lg" />
              </div>
              <h3 className={styles.cardTitle}>{link.title}</h3>
              <p className={styles.cardDescription}>{link.description}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Configuration</h2>
        <div className={styles.linkList}>
          {configLinks.map((link) => (
            <Link key={link.path} to={link.path} className={styles.linkItem}>
              <div>
                <h3 className={styles.linkTitle}>{link.title}</h3>
                <p className={styles.linkDescription}>{link.description}</p>
              </div>
              <Icon semantic="navigation.next" decorative />
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
