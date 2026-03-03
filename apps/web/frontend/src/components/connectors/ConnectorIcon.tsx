/**
 * ConnectorIcon - Resolves a connector icon name to the Icon component.
 */

import { Icon } from '@/components/icon/Icon';
import type { IconSemantic } from '@/components/icon/iconMap';
import styles from './ConnectorGallery.module.css';

const iconMap: Record<string, IconSemantic> = {
  jira: 'connectors.jira',
  azure: 'connectors.azure',
  planview: 'domain.portfolio',
  slack: 'connectors.slack',
  teams: 'connectors.teams',
  sharepoint: 'connectors.sharepoint',
  sap: 'domain.platform',
  workday: 'communication.user',
  servicenow: 'provenance.auditLog',
  'shield-check': 'domain.governance',
  'cpu-chip': 'connectors.cpuChip',
  'chart-bar': 'domain.portfolio',
  'clipboard-list': 'provenance.auditLog',
  folder: 'artifact.folder',
  'building-office': 'domain.platform',
  users: 'communication.user',
  'chat-bubble-left-right': 'communication.message',
  default: 'connectors.default',
};

export function ConnectorIcon({ name }: { name: string }) {
  const resolved = name.includes('.') ? (name as IconSemantic) : (iconMap[name] ?? iconMap.default);

  return (
    <Icon
      semantic={resolved}
      decorative
      className={styles.iconSvg}
      size="lg"
    />
  );
}
