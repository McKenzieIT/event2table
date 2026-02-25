import { useState, useCallback } from 'react';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';

/**
 * Promise-based confirm dialog hook
 * 提供类似 window.confirm() 的同步体验，但使用自定义对话框
 * 
 * @returns {confirm, ConfirmDialogComponent}
 * 
 * @example
 * const { confirm, ConfirmDialog } = usePromiseConfirm();
 * 
 * // 在处理函数中
 * const confirmed = await confirm('确定要删除吗？');
 * if (confirmed) { ... }
 */
export function usePromiseConfirm() {
  const [dialogState, setDialogState] = useState({
    open: false,
    title: '确认',
    message: '',
    variant: 'danger',
  });

  const [resolveRef, setResolveRef] = useState(null);

  const confirm = useCallback((message, options = {}) => {
    return new Promise((resolve) => {
      setDialogState({
        open: true,
        title: options.title || '确认',
        message,
        variant: options.variant || 'danger',
      });
      setResolveRef(() => resolve);
    });
  }, []);

  const handleConfirm = useCallback(() => {
    if (resolveRef) {
      resolveRef(true);
    }
    setDialogState(prev => ({ ...prev, open: false }));
    setResolveRef(null);
  }, [resolveRef]);

  const handleCancel = useCallback(() => {
    if (resolveRef) {
      resolveRef(false);
    }
    setDialogState(prev => ({ ...prev, open: false }));
    setResolveRef(null);
  }, [resolveRef]);

  const ConfirmDialogComponent = () => (
    <ConfirmDialog
      open={dialogState.open}
      title={dialogState.title}
      message={dialogState.message}
      variant={dialogState.variant}
      confirmText="确认"
      cancelText="取消"
      onConfirm={handleConfirm}
      onCancel={handleCancel}
    />
  );

  return { confirm, ConfirmDialogComponent };
}

export default usePromiseConfirm;
