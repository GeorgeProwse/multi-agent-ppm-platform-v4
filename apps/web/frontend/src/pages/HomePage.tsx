import { Link } from 'react-router-dom';
import styles from './HomePage.module.css';

const quickLinks = [
  {
    title: 'Portfolios',
    description: 'Manage strategic portfolios and investments',
    path: '/portfolio/demo',
    icon: (
      <svg width="24" height="24" viewBox="0 0 20 20" fill="currentColor">
        <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
      </svg>
    ),
  },
  {
    title: 'Programs',
    description: 'Coordinate related projects and initiatives',
    path: '/program/demo',
    icon: (
      <svg width="24" height="24" viewBox="0 0 20 20" fill="currentColor">
        <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
      </svg>
    ),
  },
  {
    title: 'Projects',
    description: 'Execute and track individual projects',
    path: '/project/demo',
    icon: (
      <svg width="24" height="24" viewBox="0 0 20 20" fill="currentColor">
        <path
          fillRule="evenodd"
          d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm2 10a1 1 0 10-2 0v3a1 1 0 102 0v-3zm2-3a1 1 0 011 1v5a1 1 0 11-2 0v-5a1 1 0 011-1zm4-1a1 1 0 10-2 0v7a1 1 0 102 0V8z"
          clipRule="evenodd"
        />
      </svg>
    ),
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
    title: 'Templates',
    description: 'Define reusable project templates',
    path: '/config/templates',
  },
];

export function HomePage() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Welcome to PPM Platform</h1>
        <p className={styles.subtitle}>
          Multi-agent project, program, and portfolio management
        </p>
      </header>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Quick Access</h2>
        <div className={styles.cardGrid}>
          {quickLinks.map((link) => (
            <Link key={link.path} to={link.path} className={styles.card}>
              <div className={styles.cardIcon}>{link.icon}</div>
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
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
