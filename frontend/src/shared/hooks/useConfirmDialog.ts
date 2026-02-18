/**
 * Confirm Dialog Hook
 * 提供类似 window.confirm 的API但使用UI对话框
 */

import { useState, useCallback } from 'react';

export function useConfirmDialog() {
  const [dialogState, setDialogState] = useState({
    open: false,
    title: '确认',
    message: '',
    onConfirm: null,
    onCancel: null,
    confirmText: '确认',
    cancelText: '取消',
    variant: 'warning',
  });

  const confirm = useCallback((message, options = {}) => {
    return new Promise((resolve) => {
      setDialogState({
        open: true,
        title: options.title || '确认',
        message,
        confirmText: options.confirmText || '确认',
        cancelText: options.cancelText || '取消',
        variant: options.variant || 'warning',
        onConfirm: () => {
          setDialogState(prev => ({ ...prev, open: false }));
          resolve(true);
        },
        onCancel: () => {
          setDialogState(prev => ({ ...prev, open: false }));
          resolve(false);
        },
      });
    });
  }, []);

  const closeDialog = useCallback(() => {
    setDialogState(prev => ({ ...prev, open: false }));
  }, []);

  return {
    dialogState,
    confirm,
    closeDialog,
  };
}

export default useConfirmDialog;
