import { useState, useCallback } from 'react';

export function useConfirm() {
  const [confirmState, setConfirmState] = useState({
    open: false,
    title: '',
    message: '',
    variant: 'warning',
    confirmText: '确认',
    cancelText: '取消',
    onConfirm: null,
    data: null,
  });

  const confirm = useCallback((options) => {
    return new Promise((resolve) => {
      setConfirmState({
        open: true,
        title: options.title || '确认',
        message: options.message || '确定要继续吗？',
        variant: options.variant || 'warning',
        confirmText: options.confirmText || '确认',
        cancelText: options.cancelText || '取消',
        onConfirm: () => {
          setConfirmState(prev => ({ ...prev, open: false }));
          resolve(true);
        },
        data: options.data,
      });
    });
  }, []);

  const cancelConfirm = useCallback(() => {
    setConfirmState(prev => ({ ...prev, open: false }));
  }, []);

  return {
    confirmState,
    confirm,
    cancelConfirm,
  };
}
