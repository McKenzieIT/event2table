/**
 * Confirm Dialog Hook
 * 提供类似 window.confirm 的API但使用UI对话框
 */

import { useState, useCallback } from 'react';

interface ConfirmDialogOptions {
  title?: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'warning' | 'danger' | 'info' | 'success';
}

interface DialogState {
  open: boolean;
  title: string;
  message: string;
  onConfirm: (() => void) | null;
  onCancel: (() => void) | null;
  confirmText: string;
  cancelText: string;
  variant: ConfirmDialogOptions['variant'];
}

interface UseConfirmDialogReturn {
  dialogState: DialogState;
  confirm: (message: string, options?: ConfirmDialogOptions) => Promise<boolean>;
  closeDialog: () => void;
}

export function useConfirmDialog(): UseConfirmDialogReturn {
  const [dialogState, setDialogState] = useState<DialogState>({
    open: false,
    title: '确认',
    message: '',
    onConfirm: null,
    onCancel: null,
    confirmText: '确认',
    cancelText: '取消',
    variant: 'warning',
  });

  const confirm = useCallback((message: string, options: ConfirmDialogOptions = {}): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
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
