/**
 * ConnectorCard - Renders a single connector card with toggle, status badges,
 * and action buttons.
 */

import { Link } from 'react-router-dom';
import {
  STATUS_LABELS,
  STATUS_BADGE_CLASSES,
  CERTIFICATION_LABELS,
  CERTIFICATION_BADGE_CLASSES,
  isConnectorToggleable,
  type ConnectorCardProps,
} from './connectorGalleryTypes';
import { ConnectorIcon } from './ConnectorIcon';
import styles from './ConnectorGallery.module.css';

export function ConnectorCard({
  connector,
  onToggleEnabled,
  onOpenConfig,
  onOpenCertification,
  canManage,
  certification,
  projectId,
}: ConnectorCardProps) {
  const statusLabel = STATUS_LABELS[connector.status];
  const statusClassName = STATUS_BADGE_CLASSES[connector.status];
  const isToggleable = isConnectorToggleable(connector.status);
  const canToggle = canManage && isToggleable;
  const certStatus = connector.certification_status ?? certification?.compliance_status ?? 'not_started';
  const certLabel = CERTIFICATION_LABELS[certStatus];
  const certBadgeClass = CERTIFICATION_BADGE_CLASSES[certStatus];
  const connectorTypeLabel = connector.connector_type === 'mcp' ? 'MCP' : 'REST';
  const connectorTypeClass =
    connector.connector_type === 'mcp' ? styles.protocolBadgeMcp : styles.protocolBadgeRest;

  return (
    <div
      className={`${styles.connectorCard} ${
        !isToggleable ? styles.unavailable : ''
      } ${connector.enabled ? styles.enabled : ''}`}
    >
      <div className={styles.cardHeader}>
        <div className={styles.connectorIcon}>
          <ConnectorIcon name={connector.icon} />
        </div>
        <div className={styles.connectorTitle}>
          <h3 className={styles.connectorName}>{connector.name}</h3>
          <div className={styles.badgeRow}>
            <span className={`${styles.statusBadge} ${statusClassName}`}>{statusLabel}</span>
            <span className={`${styles.certificationBadge} ${certBadgeClass}`}>{certLabel}</span>
            <span className={`${styles.protocolBadge} ${connectorTypeClass}`}>{connectorTypeLabel}</span>
          </div>
        </div>
        <label
          className={styles.toggleSwitch}
          title={
            !isToggleable
              ? 'Not available yet'
              : canManage
              ? 'Toggle enabled'
              : 'Read-only'
          }
        >
          <input
            type="checkbox"
            checked={connector.enabled}
            onChange={onToggleEnabled}
            disabled={!canToggle}
            aria-label={`Toggle ${connector.name}`}
          />
          <span className={styles.toggleSlider}></span>
        </label>
      </div>

      <p className={styles.connectorDescription}>{connector.description}</p>

      <div className={styles.connectorMeta}>
        <span className={styles.syncDirection}>{projectId ? `Scope: Project (${projectId})` : "Scope: Global / all projects"}</span>
        <span className={styles.syncDirection}>
          {connector.sync_direction === 'inbound' && 'Read'}
          {connector.sync_direction === 'outbound' && 'Write'}
          {connector.sync_direction === 'bidirectional' && 'Read/Write'}
        </span>
        {connector.configured && (
          <span className={`${styles.healthStatus} ${styles[connector.health_status]}`}>
            {connector.health_status === 'healthy' && 'Connected'}
            {connector.health_status === 'unhealthy' && 'Disconnected'}
            {connector.health_status === 'unknown' && 'Not tested'}
          </span>
        )}
      </div>

      <div className={styles.cardActions}>
        <button
          className={styles.configButton}
          onClick={onOpenConfig}
          disabled={!canToggle}
          title={
            !isToggleable
              ? 'Not available yet'
              : canManage
              ? 'Configure connector'
              : 'Read-only'
          }
        >
          Configure
        </button>
        <Link className={styles.certButton} to={`/app/config/connectors/${connector.connector_id}`}>Details</Link>
        <button
          className={styles.certButton}
          onClick={onOpenCertification}
          data-tour="certification-evidence"
        >
          {canManage ? 'Manage Evidence' : 'View Evidence'}
        </button>
      </div>
    </div>
  );
}
