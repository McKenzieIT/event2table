// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import { Modal } from '@shared/ui';
import { Button } from '@shared/ui';
import React from 'react';

export interface DeleteConfirmModalProps {
  isOpen: boolean;
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

export function DeleteConfirmModal({
  isOpen,
  title = '确认删除',
  message,
  confirmText = '删除',
  cancelText = '取消',
  onConfirm,
  onCancel
}: DeleteConfirmModalProps) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onCancel}
      enableEscClose={true}
      closeOnBackdropClick={true}
    >
      <div className="delete-confirm-modal">
        <div className="modal-header">
          <h4>{title}</h4>
          <button className="modal-close" onClick={onCancel} aria-label="关闭对话框">✕</button>
        </div>
        <div className="modal-body">
          <p>{message}</p>
        </div>
        <div className="modal-footer">
          <Button variant="secondary" onClick={onCancel}>
            {cancelText}
          </Button>
          <Button variant="danger" onClick={onConfirm}>
            {confirmText}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
