import { useState, useCallback } from 'react';

export type ConfirmVariant = 'warning' | 'danger' | 'info' | 'success';

export interface ConfirmOptions {
  title?: string;
  message?: string;
  variant?: ConfirmVariant;
  confirmText?: string;
  cancelText?: string;
  data?: unknown;
}

export interface ConfirmState {
  open: boolean;
  title: string;
  message: string;
  variant: ConfirmVariant;
  confirmText: string;
  cancelText: string;
  onConfirm: (() => void) | null;
  data: unknown;
}

export function useConfirm() {
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    open: false,
    title: '',
    message: '',
    variant: 'warning',
    confirmText: '确认',
    cancelText: '取消',
    onConfirm: null,
    data: null,
  });

  const confirm = useCallback((options: ConfirmOptions): Promise<boolean> => {
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
        data: options.data ?? null,
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
