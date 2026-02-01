import { Link, useLocation } from 'react-router-dom';
import { useAppStore } from '@/store';
import { useTour } from '@/components/tours';
import { Icon } from '@/components/icon/Icon';
import styles from './Header.module.css';

interface BreadcrumbItem {
  label: string;
  path?: string;
}

function getBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const parts = pathname.split('/').filter(Boolean);
  const crumbs: BreadcrumbItem[] = [{ label: 'Home', path: '/' }];

  if (parts.length === 0) {
    return crumbs;
  }

  if (parts[0] === 'portfolio' && parts[1]) {
    crumbs.push({ label: 'Portfolio', path: `/portfolio/${parts[1]}` });
  } else if (parts[0] === 'program' && parts[1]) {
    crumbs.push({ label: 'Program', path: `/program/${parts[1]}` });
  } else if (parts[0] === 'project' && parts[1]) {
    crumbs.push({ label: 'Project', path: `/project/${parts[1]}` });
  } else if (parts[0] === 'config') {
    crumbs.push({ label: 'Configuration' });
    if (parts[1] === 'agents') {
      crumbs.push({ label: 'Agents', path: '/config/agents' });
    } else if (parts[1] === 'connectors') {
      crumbs.push({ label: 'Connectors', path: '/config/connectors' });
    } else if (parts[1] === 'workflows') {
      crumbs.push({ label: 'Workflows', path: '/config/workflows' });
    }
  }

  return crumbs;
}

export function Header() {
  const location = useLocation();
  const { session } = useAppStore();
  const { startTour } = useTour();
  const breadcrumbs = getBreadcrumbs(location.pathname);

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <Link to="/" className={styles.logo}>
          <Icon semantic="domain.platform" decorative size="lg" color="accent" />
          <span className={styles.logoText}>PPM Platform</span>
        </Link>

        <nav className={styles.breadcrumb} aria-label="Breadcrumb">
          <ol>
            {breadcrumbs.map((crumb, index) => (
              <li key={crumb.path ?? index}>
                {index > 0 && (
                  <span className={styles.separator} aria-hidden="true">
                    /
                  </span>
                )}
                {crumb.path && index < breadcrumbs.length - 1 ? (
                  <Link to={crumb.path}>{crumb.label}</Link>
                ) : (
                  <span aria-current={index === breadcrumbs.length - 1 ? 'page' : undefined}>
                    {crumb.label}
                  </span>
                )}
              </li>
            ))}
          </ol>
        </nav>
      </div>

      <div className={styles.right}>
        <button
          className={styles.helpButton}
          title="Help and walkthrough"
          onClick={startTour}
          data-tour="help-menu"
        >
          <span>Help</span>
          <Icon semantic="actions.help" decorative />
        </button>
        <button className={styles.iconButton} title="Notifications" aria-label="Notifications">
          <Icon semantic="communication.notifications" label="Notifications" />
        </button>

        <button className={styles.iconButton} title="Settings" aria-label="Settings">
          <Icon semantic="actions.settings" label="Settings" />
        </button>

        <div className={styles.userMenu}>
          <button className={styles.userButton}>
            <div className={styles.avatar}>
              {session.user?.name?.charAt(0).toUpperCase() ?? 'U'}
            </div>
            <span className={styles.userName}>
              {session.user?.name ?? 'User'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}
