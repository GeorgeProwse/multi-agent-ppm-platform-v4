import { useEffect, useMemo, useRef, useState } from 'react';
import type { MouseEvent } from 'react';
import { FocusTrap } from './FocusTrap';
import styles from './ConfirmDialog.module.css';

interface ConfirmDialogProps {
  title: string;
  description: string;
  confirmLabel: string;
  cancelLabel: string;
  variant?: 'danger' | 'default';
  confirmDisabled?: boolean;
  onConfirm: () => Promise<void> | void;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel,
  cancelLabel,
  variant = 'default',
  confirmDisabled = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const [isConfirming, setIsConfirming] = useState(false);
  const cancelRef = useRef<HTMLButtonElement | null>(null);
  const descriptionId = useMemo(
    () => `confirm-dialog-description-${Math.random().toString(36).slice(2, 9)}`,
    []
  );

  useEffect(() => {
    if (variant === 'danger') {
      cancelRef.current?.focus();
    }
  }, [variant]);

  const handleConfirm = async () => {
    if (isConfirming || confirmDisabled) {
      return;
    }

    setIsConfirming(true);
    try {
      await onConfirm();
    } finally {
      setIsConfirming(false);
    }
  };

  const handleOverlayClick = (event: MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onCancel();
    }
  };

  return (
    <FocusTrap
      className={styles.overlay}
      role="alertdialog"
      aria-modal="true"
      aria-describedby={descriptionId}
      onClick={handleOverlayClick}
      onClose={onCancel}
    >
      <div className={styles.dialog} onClick={(event) => event.stopPropagation()}>
        <h2 className={styles.title}>{title}</h2>
        <p className={styles.description} id={descriptionId}>
          {description}
        </p>
        <div className={styles.actions}>
          <button
            ref={cancelRef}
            type="button"
            className={`${styles.button} ${styles.cancelButton}`}
            onClick={onCancel}
            disabled={isConfirming}
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            className={`${styles.button} ${
              variant === 'danger' ? styles.confirmDanger : styles.confirmDefault
            }`}
            onClick={() => {
              void handleConfirm();
            }}
            disabled={isConfirming || confirmDisabled}
          >
            {isConfirming ? 'Working…' : confirmLabel}
          </button>
        </div>
      </div>
    </FocusTrap>
  );
}

export default ConfirmDialog;
