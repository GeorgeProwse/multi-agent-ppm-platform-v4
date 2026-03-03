/**
 * ConnectorGallery - Connector configuration gallery page
 *
 * Features:
 * - List connectors by category
 * - Search and filter functionality
 * - Enable/disable connectors with mutual exclusivity
 * - Open configuration modal for detailed settings
 * - Test connection functionality
 */

import { useEffect, useMemo, useState } from 'react';
import {
  useConnectorStore,
  type CertificationStatus,
  type Connector,
  type ConnectorCategory,
} from '@/store/connectors';
import { useAppStore } from '@/store';
import { canManageConfig } from '@/auth/permissions';
import { isConnectorToggleable } from './connectorGalleryTypes';
import { SyncStatusPanel } from './SyncStatusPanel';
import { ConnectorSearchFilters } from './ConnectorSearchFilters';
import { CategorySection } from './CategorySection';
import { ConnectorConfigModal } from './ConnectorConfigModal';
import { CertificationModal } from './CertificationModal';
import styles from './ConnectorGallery.module.css';

interface ConnectorGalleryProps {
  projectId?: string;
}

export function ConnectorGallery({ projectId }: ConnectorGalleryProps) {
  const {
    connectors,
    connectorsLoading,
    connectorsError,
    projectConnectors,
    projectConnectorsLoading,
    projectConnectorsError,
    certifications,
    certificationsLoading,
    fetchCertifications,
    filter,
    fetchConnectors,
    fetchProjectConnectors,
    fetchCategories,
    setCertificationFilter,
    setFilter,
    resetFilter,
    getFilteredConnectors,
    getFilteredProjectConnectors,
    enableConnector,
    enableProjectConnector,
    disableConnector,
    disableProjectConnector,
    openConnectorModal,
    isModalOpen,
    selectedConnector,
    closeConnectorModal,
    updateConnectorConfig,
    updateProjectConnectorConfig,
    testConnection,
    testProjectConnection,
    testingConnection,
    testResult,
    clearTestResult,
    updateCertification,
    uploadCertificationDocument,
  } = useConnectorStore();
  const scopedConnectors = projectId ? projectConnectors[projectId] || [] : connectors;
  const scopedLoading = projectId ? projectConnectorsLoading[projectId] || false : connectorsLoading;
  const scopedError = projectId ? projectConnectorsError[projectId] || null : connectorsError;
  const { session } = useAppStore();
  const canManage = canManageConfig(session.user?.permissions);
  const [certModalOpen, setCertModalOpen] = useState(false);
  const [certModalConnector, setCertModalConnector] = useState<Connector | null>(null);

  // Initialize store
  useEffect(() => {
    if (projectId) {
      fetchProjectConnectors(projectId);
    } else {
      fetchConnectors();
    }
    fetchCategories();
    fetchCertifications();
  }, [fetchConnectors, fetchProjectConnectors, fetchCategories, fetchCertifications, projectId]);

  // Get filtered connectors
  const filteredConnectors = useMemo(
    () => (projectId ? getFilteredProjectConnectors(projectId) : getFilteredConnectors()),
    [projectId, scopedConnectors, filter, getFilteredConnectors, getFilteredProjectConnectors]
  );

  // Group connectors by category
  const connectorsByCategory = useMemo(() => {
    const grouped: Record<ConnectorCategory, Connector[]> = {
      ppm: [],
      pm: [],
      doc_mgmt: [],
      erp: [],
      hris: [],
      collaboration: [],
      grc: [],
      compliance: [],
      iot: [],
    };
    filteredConnectors.forEach((connector) => {
      if (grouped[connector.category]) {
        grouped[connector.category].push(connector);
      }
    });
    return grouped;
  }, [filteredConnectors]);

  // Get categories that have connectors
  const activeCategories = useMemo(() => {
    return (Object.keys(connectorsByCategory) as ConnectorCategory[]).filter(
      (cat) => connectorsByCategory[cat].length > 0
    );
  }, [connectorsByCategory]);

  const handleToggleEnabled = async (connector: Connector) => {
    if (!canManage) return;
    if (!isConnectorToggleable(connector.status)) return;
    if (connector.enabled) {
      if (projectId) {
        await disableProjectConnector(projectId, connector.connector_id);
      } else {
        await disableConnector(connector.connector_id);
      }
    } else {
      if (projectId) {
        await enableProjectConnector(projectId, connector.connector_id);
      } else {
        await enableConnector(connector.connector_id);
      }
    }
  };

  const handleOpenConfig = (connector: Connector) => {
    if (!canManage) return;
    openConnectorModal(connector);
  };

  const handleOpenCertification = (connector: Connector) => {
    setCertModalConnector(connector);
    setCertModalOpen(true);
  };

  const handleCloseCertification = () => {
    setCertModalConnector(null);
    setCertModalOpen(false);
  };

  const scopeSuffix = projectId ? ' for this project' : '';
  const certificationCounts = useMemo(() => {
    return scopedConnectors.reduce(
      (acc, connector) => {
        const status = connector.certification_status ?? certifications[connector.connector_id]?.compliance_status ?? 'not_started';
        acc[status] += 1;
        return acc;
      },
      {
        certified: 0,
        pending: 0,
        expired: 0,
        not_certified: 0,
        not_started: 0,
      } satisfies Record<CertificationStatus, number>
    );
  }, [scopedConnectors, certifications]);

  if (scopedLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading connectors...</div>
      </div>
    );
  }

  if (scopedError && scopedConnectors.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <p>Error loading connectors: {scopedError}</p>
          <button
            onClick={() =>
              projectId ? fetchProjectConnectors(projectId) : fetchConnectors()
            }
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container} data-tour="connector-gallery">
      <SyncStatusPanel />
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>Connector Gallery</h1>
          <p className={styles.subtitle}>
            Configure integrations with external systems. Enable connectors to sync data with your PPM platform.
          </p>
        </div>
        <div className={styles.headerMeta}>
          <span className={styles.connectorStats}>
            {scopedConnectors.filter((c) => c.enabled).length} of {scopedConnectors.length} connectors enabled{scopeSuffix}
          </span>
          <span className={styles.connectorStats}>
            {certificationCounts.certified} certified, {certificationCounts.pending} pending
          </span>
        </div>
      </div>

      {/* Filters */}
      <ConnectorSearchFilters
        filter={filter}
        setFilter={setFilter}
        setCertificationFilter={setCertificationFilter}
        resetFilter={resetFilter}
      />

      {/* Stats */}
      <div className={styles.stats}>
        <span>
          Showing {filteredConnectors.length} of {scopedConnectors.length} connectors{scopeSuffix}
        </span>
      </div>

      {/* Connector List by Category */}
      <div className={styles.connectorList}>
        {activeCategories.length === 0 ? (
          <div className={styles.empty}>
            <p>No connectors match your filters.</p>
          </div>
        ) : (
          activeCategories.map((category) => (
            <CategorySection
              key={category}
              category={category}
              connectors={connectorsByCategory[category]}
              onToggleEnabled={handleToggleEnabled}
              onOpenConfig={handleOpenConfig}
              onOpenCertification={handleOpenCertification}
              canManage={canManage}
              certifications={certifications}
              projectId={projectId}
            />
          ))
        )}
      </div>

      {/* Config Modal */}
      {isModalOpen && selectedConnector && (
        <ConnectorConfigModal
          connector={selectedConnector}
          onClose={closeConnectorModal}
          onSave={(connectorId, config) =>
            projectId
              ? updateProjectConnectorConfig(projectId, connectorId, config)
              : updateConnectorConfig(connectorId, config)
          }
          onTestConnection={(connectorId, instanceUrl, projectKey) =>
            projectId
              ? testProjectConnection(projectId, connectorId, instanceUrl, projectKey)
              : testConnection(connectorId, instanceUrl, projectKey)
          }
          testingConnection={testingConnection}
          testResult={testResult}
          clearTestResult={clearTestResult}
        />
      )}

      {certModalOpen && certModalConnector && (
        <CertificationModal
          connector={certModalConnector}
          certification={certifications[certModalConnector.connector_id]}
          canManage={canManage}
          loading={certificationsLoading}
          onClose={handleCloseCertification}
          onSave={updateCertification}
          onUploadDocument={uploadCertificationDocument}
          updatedBy={session.user?.name ?? session.user?.id ?? undefined}
        />
      )}
    </div>
  );
}

export default ConnectorGallery;
