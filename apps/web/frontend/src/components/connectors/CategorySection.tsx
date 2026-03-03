/**
 * CategorySection - Renders a group of connector cards under a category header.
 */

import { CATEGORY_INFO } from '@/store/connectors';
import type { CategorySectionProps } from './connectorGalleryTypes';
import { ConnectorCard } from './ConnectorCard';
import styles from './ConnectorGallery.module.css';

export function CategorySection({
  category,
  connectors,
  onToggleEnabled,
  onOpenConfig,
  onOpenCertification,
  canManage,
  certifications,
  projectId,
}: CategorySectionProps) {
  const info = CATEGORY_INFO[category];
  const enabledConnector = connectors.find((c) => c.enabled);

  return (
    <section className={styles.categorySection}>
      <div className={styles.categoryHeader}>
        <div className={styles.categoryInfo}>
          <h2 className={styles.categoryTitle}>{info.label}</h2>
          <p className={styles.categoryDescription}>{info.description}</p>
        </div>
        <div className={styles.categoryMeta}>
          <span className={styles.categoryCount}>{connectors.length} connectors</span>
          {enabledConnector && (
            <span className={styles.enabledBadge}>
              {enabledConnector.name} enabled
            </span>
          )}
        </div>
      </div>

      <div className={styles.connectorGrid}>
        {connectors.map((connector) => (
          <ConnectorCard
            key={connector.connector_id}
            connector={connector}
            onToggleEnabled={() => onToggleEnabled(connector)}
            onOpenConfig={() => onOpenConfig(connector)}
            onOpenCertification={() => onOpenCertification(connector)}
            canManage={canManage}
            certification={certifications[connector.connector_id]}
            projectId={projectId}
          />
        ))}
      </div>
    </section>
  );
}
