/**
 * ConnectorCategorySection - Renders a group of connector cards under a
 * single category heading (e.g. PPM, PM, ERP, ...).
 */

import { CATEGORY_INFO } from '@/store/connectors';
import styles from '../connectors/ConnectorGallery.module.css';
import { ConnectorCard } from './ConnectorCard';
import type { CategorySectionProps } from './projectConnectorTypes';

export function ConnectorCategorySection({
  category,
  connectors,
  onToggleEnabled,
  onOpenConfig,
  onOpenCertification,
  onToggleMcpEnabled,
  onUpdateMcpToolMap,
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
            onToggleMcpEnabled={onToggleMcpEnabled}
            onUpdateMcpToolMap={onUpdateMcpToolMap}
            projectId={projectId}
          />
        ))}
      </div>
    </section>
  );
}
