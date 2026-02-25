import React from 'react';
import { BaseModal } from '@shared/ui/BaseModal';
import { Button } from '../ui/Button';

export function DeleteConfirmModal({
  isOpen,
  title = '确认删除',
  message,
  confirmText = '删除',
  cancelText = '取消',
  onConfirm,
  onCancel
}) {
  return (
    <BaseModal
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
    </BaseModal>
  );
}
