/**
 * CertificationModal - Modal for managing certification evidence, status,
 * audit references, and document uploads for a connector.
 */

import { useEffect, useState } from 'react';
import { Icon } from '@/components/icon/Icon';
import type { CertificationModalProps, CertificationRecord } from './connectorGalleryTypes';
import { ConnectorIcon } from './ConnectorIcon';
import styles from './ConnectorGallery.module.css';

export function CertificationModal({
  connector,
  certification,
  canManage,
  loading,
  updatedBy,
  onClose,
  onSave,
  onUploadDocument,
}: CertificationModalProps) {
  const [status, setStatus] = useState<CertificationRecord['compliance_status']>(
    certification?.compliance_status ?? 'pending'
  );
  const [certificationDate, setCertificationDate] = useState(certification?.certification_date ?? '');
  const [expiresAt, setExpiresAt] = useState(certification?.expires_at ?? '');
  const [auditReference, setAuditReference] = useState(certification?.audit_reference ?? '');
  const [notes, setNotes] = useState(certification?.notes ?? '');
  const [file, setFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    setStatus(certification?.compliance_status ?? 'pending');
    setCertificationDate(certification?.certification_date ?? '');
    setExpiresAt(certification?.expires_at ?? '');
    setAuditReference(certification?.audit_reference ?? '');
    setNotes(certification?.notes ?? '');
  }, [certification]);

  const handleSave = async () => {
    setSaving(true);
    await onSave(connector.connector_id, {
      compliance_status: status,
      certification_date: certificationDate || null,
      expires_at: expiresAt || null,
      audit_reference: auditReference || null,
      notes: notes || null,
      updated_by: updatedBy,
    });
    setSaving(false);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    await onUploadDocument(connector.connector_id, file, updatedBy);
    setFile(null);
    setUploading(false);
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={(event) => event.stopPropagation()}>
        <div className={styles.modalHeader}>
          <div className={styles.modalTitleSection}>
            <ConnectorIcon name={connector.icon} />
            <h2 className={styles.modalTitle}>{connector.name} Certification Evidence</h2>
          </div>
          <button
            className={styles.modalClose}
            onClick={onClose}
            aria-label="Close certification evidence"
          >
            <Icon semantic="actions.cancelDismiss" label="Close certification evidence" />
          </button>
        </div>
        <div className={styles.modalBody}>
          <p className={styles.modalDescription}>
            Track certification status, audit references, and evidence documents for this connector.
          </p>

          <div className={styles.certGrid}>
            <label className={styles.field}>
              <span>Status</span>
              <select
                value={status}
                onChange={(event) =>
                  setStatus(event.target.value as CertificationRecord['compliance_status'])
                }
                disabled={!canManage || loading}
              >
                <option value="certified">Certified</option>
                <option value="pending">Pending review</option>
                <option value="expired">Expired</option>
                <option value="not_certified">Not certified</option>
              </select>
            </label>

            <label className={styles.field}>
              <span>Certification date</span>
              <input
                type="date"
                value={certificationDate ?? ''}
                onChange={(event) => setCertificationDate(event.target.value)}
                disabled={!canManage || loading}
              />
            </label>

            <label className={styles.field}>
              <span>Expiration date</span>
              <input
                type="date"
                value={expiresAt ?? ''}
                onChange={(event) => setExpiresAt(event.target.value)}
                disabled={!canManage || loading}
              />
            </label>
          </div>

          <label className={styles.field}>
            <span>Audit reference</span>
            <input
              type="text"
              value={auditReference ?? ''}
              onChange={(event) => setAuditReference(event.target.value)}
              disabled={!canManage || loading}
              placeholder="SOC 2 report ID, ISO certificate number, etc."
            />
          </label>

          <label className={styles.field}>
            <span>Notes</span>
            <textarea
              value={notes ?? ''}
              onChange={(event) => setNotes(event.target.value)}
              disabled={!canManage || loading}
              rows={3}
            />
          </label>

          <div className={styles.certDocuments}>
            <h3>Evidence documents</h3>
            {certification?.documents?.length ? (
              <ul className={styles.documentList}>
                {certification.documents.map((doc) => (
                  <li key={doc.document_id}>
                    <div className={styles.documentName}>{doc.filename}</div>
                    <div className={styles.documentMeta}>
                      <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                      {doc.uploaded_by && <span>Uploaded by {doc.uploaded_by}</span>}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className={styles.emptyDocuments}>No evidence uploaded yet.</p>
            )}

            {canManage && (
              <div className={styles.uploadRow}>
                <input
                  type="file"
                  onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                />
                <button
                  className={styles.uploadButton}
                  onClick={handleUpload}
                  disabled={!file || uploading}
                >
                  {uploading ? 'Uploading...' : 'Upload Evidence'}
                </button>
              </div>
            )}
          </div>
        </div>

        <div className={styles.modalFooter}>
          <button className={styles.secondaryButton} onClick={onClose}>
            Close
          </button>
          {canManage && (
            <button className={styles.primaryButton} onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save Updates'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
