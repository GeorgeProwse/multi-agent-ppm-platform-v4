import { Link, useLocation } from 'react-router-dom';
import { useAppStore } from '@/store';
import styles from './LeftPanel.module.css';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path?: string;
  children?: NavItem[];
}

const methodologyNav: NavItem[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
      </svg>
    ),
  },
  {
    id: 'initiate',
    label: 'Initiate',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
  {
    id: 'plan',
    label: 'Plan',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
        <path
          fillRule="evenodd"
          d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
  {
    id: 'execute',
    label: 'Execute',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
  {
    id: 'monitor',
    label: 'Monitor & Control',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
      </svg>
    ),
  },
  {
    id: 'close',
    label: 'Close',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path
          fillRule="evenodd"
          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
];

const configNav: NavItem[] = [
  {
    id: 'agents',
    label: 'Agents',
    path: '/config/agents',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
      </svg>
    ),
  },
  {
    id: 'connectors',
    label: 'Connectors',
    path: '/config/connectors',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path
          fillRule="evenodd"
          d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
  {
    id: 'templates',
    label: 'Templates',
    path: '/config/templates',
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
      </svg>
    ),
  },
];

export function LeftPanel() {
  const location = useLocation();
  const { leftPanelCollapsed, toggleLeftPanel, currentActivity, setCurrentActivity } =
    useAppStore();

  const handleActivityClick = (item: NavItem) => {
    if (item.path) return; // Let Link handle navigation
    setCurrentActivity(
      currentActivity?.id === item.id
        ? null
        : { id: item.id, name: item.label }
    );
  };

  return (
    <aside
      className={`${styles.panel} ${leftPanelCollapsed ? styles.collapsed : ''}`}
    >
      <div className={styles.header}>
        {!leftPanelCollapsed && <h2 className={styles.title}>Navigation</h2>}
        <button
          className={styles.collapseButton}
          onClick={toggleLeftPanel}
          title={leftPanelCollapsed ? 'Expand panel' : 'Collapse panel'}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="currentColor"
            style={{
              transform: leftPanelCollapsed ? 'rotate(180deg)' : 'none',
            }}
          >
            <path
              fillRule="evenodd"
              d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>

      <nav className={styles.nav}>
        <div className={styles.section}>
          {!leftPanelCollapsed && (
            <h3 className={styles.sectionTitle}>Methodology</h3>
          )}
          <ul className={styles.navList}>
            {methodologyNav.map((item) => (
              <li key={item.id}>
                <button
                  className={`${styles.navItem} ${
                    currentActivity?.id === item.id ? styles.active : ''
                  }`}
                  onClick={() => handleActivityClick(item)}
                  title={leftPanelCollapsed ? item.label : undefined}
                >
                  <span className={styles.icon}>{item.icon}</span>
                  {!leftPanelCollapsed && (
                    <span className={styles.label}>{item.label}</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className={styles.section}>
          {!leftPanelCollapsed && (
            <h3 className={styles.sectionTitle}>Configuration</h3>
          )}
          <ul className={styles.navList}>
            {configNav.map((item) => (
              <li key={item.id}>
                <Link
                  to={item.path!}
                  className={`${styles.navItem} ${
                    location.pathname === item.path ? styles.active : ''
                  }`}
                  title={leftPanelCollapsed ? item.label : undefined}
                >
                  <span className={styles.icon}>{item.icon}</span>
                  {!leftPanelCollapsed && (
                    <span className={styles.label}>{item.label}</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>
    </aside>
  );
}
