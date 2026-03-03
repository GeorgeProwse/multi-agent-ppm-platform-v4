/**
 * ProjectConnectorGallery - Project-scoped connector configuration gallery page
 *
 * Features:
 * - List connectors by category
 * - Search and filter functionality
 * - Enable/disable connectors with mutual exclusivity
 * - Open configuration modal for detailed settings
 * - Test connection functionality
 */

import { useEffect, useMemo, useState } from 'react';
import { useConnectorStore } from '@/store/connectors';
import type { Connector, ConnectorCategory } from '@/store/connectors';
import { useAppStore } from '@/store';
import { canManageConfig } from '@/auth/permissions';
import { SyncStatusPanel } from '../connectors/SyncStatusPanel';
import styles from '../connectors/ConnectorGallery.module.css';

import { ConnectorFilterBar } from './ConnectorFilterBar';
import { ConnectorCategorySection } from './ConnectorCategorySection';
import { ConnectorConfigModal } from './ConnectorConfigModal';
import { CertificationModal } from './CertificationModal';
import { isConnectorToggleable } from './projectConnectorTypes';
import type { ProjectConnectorGalleryProps } from './projectConnectorTypes';

export function ProjectConnectorGallery({ projectId }: ProjectConnectorGalleryProps) {
  const {
    projectConnectors,
    projectConnectorsLoading,
    projectConnectorsError,
    certifications,
    certificationsLoading,
    fetchCertifications,
    filter,
    fetchProjectConnectors,
    fetchCategories,
    setCertificationFilter,
    setFilter,
    resetFilter,
    getFilteredProjectConnectors,
    enableProjectConnector,
    disableProjectConnector,
    openConnectorModal,
    isModalOpen,
    selectedConnector,
    closeConnectorModal,
    updateProjectConnectorConfig,
    testProjectConnection,
    testingConnection,
    testResult,
    clearTestResult,
    updateCertification,
    uploadCertificationDocument,
    setProjectMcpEnabled,
    updateProjectMcpToolMap,
  } = useConnectorStore();

  const connectors = projectConnectors[projectId] || [];
  const connectorsLoading = projectConnectorsLoading[projectId] || false;
  const connectorsError = projectConnectorsError[projectId] || null;
  const { session } = useAppStore();
  const canManage = canManageConfig(session.user?.permissions);
  const [certModalOpen, setCertModalOpen] = useState(false);
  const [certModalConnector, setCertModalConnector] = useState<Connector | null>(null);

  // Initialize store
  useEffect(() => {
    fetchProjectConnectors(projectId);
    fetchCategories();
    fetchCertifications();
  }, [fetchProjectConnectors, fetchCategories, fetchCertifications, projectId]);

  // Get filtered connectors
  const filteredConnectors = useMemo(
    () => getFilteredProjectConnectors(projectId),
    [getFilteredProjectConnectors, projectId]
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
      crm: [],
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
      await disableProjectConnector(projectId, connector.connector_id);
    } else {
      await enableProjectConnector(projectId, connector.connector_id);
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

  if (connectorsLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading connectors...</div>
      </div>
    );
  }

  if (connectorsError && connectors.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <p>Error loading connectors: {connectorsError}</p>
          <button onClick={() => fetchProjectConnectors(projectId)}>Retry</button>
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
            {connectors.filter((c) => c.enabled).length} of {connectors.length} connectors enabled
          </span>
        </div>
      </div>

      {/* Filters */}
      <ConnectorFilterBar
        filter={filter}
        setFilter={setFilter}
        setCertificationFilter={setCertificationFilter}
        resetFilter={resetFilter}
      />

      {/* Stats */}
      <div className={styles.stats}>
        <span>
          Showing {filteredConnectors.length} of {connectors.length} connectors
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
            <ConnectorCategorySection
              key={category}
              category={category}
              connectors={connectorsByCategory[category]}
              onToggleEnabled={handleToggleEnabled}
              onOpenConfig={handleOpenConfig}
              onOpenCertification={handleOpenCertification}
              onToggleMcpEnabled={setProjectMcpEnabled}
              onUpdateMcpToolMap={updateProjectMcpToolMap}
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
            updateProjectConnectorConfig(projectId, connectorId, config)
          }
          onTestConnection={(connectorId, instanceUrl, projectKey) =>
            testProjectConnection(projectId, connectorId, instanceUrl, projectKey)
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

export default ProjectConnectorGallery;
