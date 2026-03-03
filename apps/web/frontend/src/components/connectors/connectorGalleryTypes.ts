/**
 * Shared types, constants, and utility functions for the ConnectorGallery family of components.
 */

import type {
  CertificationStatus,
  CertificationRecord,
  Connector,
  ConnectorCategory,
  ConnectorConfigUpdate,
  ConnectorType,
} from '@/store/connectors';

import styles from './ConnectorGallery.module.css';

/* ------------------------------------------------------------------ */
/*  Re-exports for convenience                                        */
/* ------------------------------------------------------------------ */
export type {
  CertificationStatus,
  CertificationRecord,
  Connector,
  ConnectorCategory,
  ConnectorConfigUpdate,
  ConnectorType,
};

/* ------------------------------------------------------------------ */
/*  Status & certification label / badge maps                         */
/* ------------------------------------------------------------------ */

export const STATUS_LABELS: Record<Connector['status'], string> = {
  available: 'Available',
  coming_soon: 'Coming Soon',
  beta: 'Beta',
  production: 'Production',
};

export const STATUS_BADGE_CLASSES: Record<Connector['status'], string> = {
  available: styles.statusBadgeAvailable,
  coming_soon: styles.statusBadgeComingSoon,
  beta: styles.statusBadgeBeta,
  production: styles.statusBadgeProduction,
};

export const CERTIFICATION_LABELS: Record<CertificationStatus, string> = {
  certified: 'Certified',
  pending: 'Pending',
  expired: 'Expired',
  not_certified: 'Not certified',
  not_started: 'Not started',
};

export const CERTIFICATION_BADGE_CLASSES: Record<CertificationStatus, string> = {
  certified: styles.certBadgeCertified,
  pending: styles.certBadgePending,
  expired: styles.certBadgeExpired,
  not_certified: styles.certBadgeNotCertified,
  not_started: styles.certBadgeNotStarted,
};

/* ------------------------------------------------------------------ */
/*  Filter option definitions                                         */
/* ------------------------------------------------------------------ */

export const STATUS_OPTIONS: { value: Connector['status'] | 'all'; label: string }[] = [
  { value: 'all', label: 'All Status' },
  { value: 'production', label: 'Production' },
  { value: 'available', label: 'Available' },
  { value: 'beta', label: 'Beta' },
  { value: 'coming_soon', label: 'Coming Soon' },
];

export const CERTIFICATION_OPTIONS: { value: CertificationStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All Certifications' },
  { value: 'certified', label: 'Certified' },
  { value: 'pending', label: 'Pending' },
  { value: 'expired', label: 'Expired' },
  { value: 'not_certified', label: 'Not certified' },
  { value: 'not_started', label: 'Not started' },
];

/* ------------------------------------------------------------------ */
/*  Utility functions                                                  */
/* ------------------------------------------------------------------ */

export const isConnectorToggleable = (status: Connector['status']): boolean =>
  status === 'available' || status === 'production';

export const buildInitialToolMap = (connector: Connector): Record<string, string> => {
  const existing = connector.mcp_tool_map ?? {};
  const baseOperations = connector.supported_operations.length
    ? connector.supported_operations
    : Object.keys(existing);
  const operations = baseOperations.length ? baseOperations : ['projects.read', 'projects.write'];
  const allOperations = [...operations, ...Object.keys(existing).filter((op) => !operations.includes(op))];
  return allOperations.reduce<Record<string, string>>((acc, operation) => {
    acc[operation] = existing[operation] ? String(existing[operation]) : '';
    return acc;
  }, {});
};

/* ------------------------------------------------------------------ */
/*  Shared prop interfaces                                             */
/* ------------------------------------------------------------------ */

export interface ConnectorGalleryProps {
  projectId?: string;
}

export interface CategorySectionProps {
  category: ConnectorCategory;
  connectors: Connector[];
  projectId?: string;
  onToggleEnabled: (connector: Connector) => void;
  onOpenConfig: (connector: Connector) => void;
  onOpenCertification: (connector: Connector) => void;
  canManage: boolean;
  certifications: Record<string, CertificationRecord>;
}

export interface ConnectorCardProps {
  connector: Connector;
  projectId?: string;
  onToggleEnabled: () => void;
  onOpenConfig: () => void;
  onOpenCertification: () => void;
  canManage: boolean;
  certification?: CertificationRecord;
}

export interface ConnectorConfigModalProps {
  connector: Connector;
  onClose: () => void;
  onSave: (connectorId: string, config: ConnectorConfigUpdate) => Promise<void>;
  onTestConnection: (connectorId: string, instanceUrl?: string, projectKey?: string) => Promise<{ status: string; message: string }>;
  testingConnection: boolean;
  testResult: { status: string; message: string; details: Record<string, unknown> } | null;
  clearTestResult: () => void;
}

export interface CertificationModalProps {
  connector: Connector;
  certification?: CertificationRecord;
  canManage: boolean;
  loading: boolean;
  updatedBy?: string;
  onClose: () => void;
  onSave: (
    connectorId: string,
    payload: Partial<{
      compliance_status: CertificationRecord['compliance_status'];
      certification_date: string | null;
      expires_at: string | null;
      audit_reference: string | null;
      notes: string | null;
      updated_by?: string;
    }>
  ) => Promise<CertificationRecord | null>;
  onUploadDocument: (
    connectorId: string,
    file: File,
    uploadedBy?: string
  ) => Promise<CertificationRecord | null>;
}
