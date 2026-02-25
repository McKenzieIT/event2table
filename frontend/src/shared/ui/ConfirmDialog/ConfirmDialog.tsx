// @ts-nocheck - TypeScript检查暂禁用
import React, { useEffect, useRef } from 'react';
import { Button } from '../Button/Button';
import './ConfirmDialog.css';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info' | 'primary';
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmText = '确认',
  cancelText = '取消',
  variant = 'primary',
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const dialogRef = useRef(null);
  const confirmButtonRef = useRef(null);
  const cancelButtonRef = useRef(null);

  useEffect(() => {
    if (open) {
      // 聚焦到确认按钮
      setTimeout(() => {
        confirmButtonRef.current?.focus();
      }, 50);
      
      // 锁定body滚动
      document.body.style.overflow = 'hidden';
    } else {
      // 恢复body滚动
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  // 处理ESC键
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!open) return;
      
      if (e.key === 'Escape') {
        onCancel();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div 
      className="modal-overlay" 
      onClick={onCancel}
      role="presentation"
    >
      <div 
        ref={dialogRef}
        className="modal-content" 
        onClick={e => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-message"
      >
        <div className="modal-header">
          <h4 id="confirm-dialog-title">{title}</h4>
        </div>
        <div className="modal-body">
          <p id="confirm-dialog-message">{message}</p>
        </div>
        <div className="modal-footer">
          <Button 
            ref={cancelButtonRef}
            variant="secondary" 
            onClick={onCancel}
          >
            {cancelText}
          </Button>
          <Button 
            ref={confirmButtonRef}
            variant={variant === 'danger' ? 'danger' : variant} 
            onClick={onConfirm}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
}
