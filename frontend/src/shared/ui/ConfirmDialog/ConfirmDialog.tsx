// PERF: React Performance Optimization - Phase 3
// - Added React.memo with custom comparison for open state
// - Added useCallback for event handlers to prevent re-renders
// - Optimized conditional rendering (return null when closed)
// See: docs/reports/2026-03-06/REACT-PERFORMANCE-OPTIMIZATION-REPORT.md

import React, { useEffect, useRef, useCallback } from 'react';
import { Button } from '@shared/ui';
import './ConfirmDialog.css';

interface ConfirmDialogProps {
  /** 对话框是否打开 */
  open: boolean;
  /** 对话框标题 */
  title: string;
  /** 对话框消息内容 */
  message: string;
  /** 确认按钮文本，默认为"确认" */
  confirmText?: string;
  /** 取消按钮文本，默认为"取消" */
  cancelText?: string;
  /** 对话框变体类型，默认为"primary" */
  variant?: 'danger' | 'warning' | 'info' | 'primary';
  /** 确认按钮回调函数 */
  onConfirm: () => void;
  /** 取消按钮回调函数 */
  onCancel: () => void;
}

const ConfirmDialogComponent = ({
  open,
  title,
  message,
  confirmText = '确认',
  cancelText = '取消',
  variant = 'primary',
  onConfirm,
  onCancel,
}: ConfirmDialogProps) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  // PERF: useCallback - 稳定ESC键处理器引用
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!open) return;

      if (e.key === 'Escape') {
        onCancel();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, onCancel]);

  // PERF: useCallback - 稳定背景点击回调引用
  const handleOverlayClick = useCallback(() => {
    onCancel();
  }, [onCancel]);

  // PERF: useCallback - 稳定内容点击回调引用
  const handleContentClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    e.stopPropagation();
  }, []);

  // PERF: 条件渲染优化 - 对话框关闭时不渲染
  if (!open) return null;

  return (
    <div
      className="modal-overlay"
      onClick={handleOverlayClick}
      role="presentation"
    >
      <div
        ref={dialogRef}
        className="modal-content"
        onClick={handleContentClick}
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
            variant="secondary"
            onClick={onCancel}
          >
            {cancelText}
          </Button>
          <Button
            variant={variant === 'danger' ? 'danger' : variant}
            onClick={onConfirm}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
};

// PERF: React.memo with custom comparison - 只在open状态变化时重新渲染
const MemoizedConfirmDialog = React.memo(ConfirmDialogComponent, (prevProps, nextProps) => {
  // 如果open状态相同且内容相同，跳过渲染
  return prevProps.open === nextProps.open &&
         prevProps.title === nextProps.title &&
         prevProps.message === nextProps.message;
});

MemoizedConfirmDialog.displayName = 'ConfirmDialog';

// Export both as default and named for compatibility
export default MemoizedConfirmDialog;
export { MemoizedConfirmDialog as ConfirmDialog };
