/**
 * useGameFormToast Hook
 *
 * 游戏表单专用Toast通知系统
 * - 全流程通知：验证、创建中、成功、失败
 * - 简洁型错误消息
 * - 自动管理loading状态
 */

import { useRef, useCallback } from 'react';
import { useToast } from '@shared/ui';

interface ToastOptions {
  duration?: number;
  isLoading?: boolean;
  icon?: string;
}

interface ToastFunction {
  (message: string, options?: ToastOptions): string | undefined;
}

interface ErrorWithStatus extends Error {
  status?: number;
}

export const useGameFormToast = () => {
  const { success, error, info, dismiss } = useToast();
  const creatingToastId = useRef<string | null>(null);
  const validationToasts = useRef<Set<string>>(new Set());

  const onValidation = useCallback((field: string, message: string) => {
    const key = `${field}:${message}`;
    if (!validationToasts.current.has(key)) {
      validationToasts.current.add(key);
      error(`${field}: ${message}`, {
        duration: 3000,
        icon: '⚠'
      });

      setTimeout(() => {
        validationToasts.current.delete(key);
      }, 3000);
    }
  }, [error]);

  const onCreating = useCallback(() => {
    creatingToastId.current = info('正在创建游戏...', {
      duration: 0,
      isLoading: true,
      icon: '⏳'
    });
  }, [info]);

  const onSuccess = useCallback((game: { name: string; gid: string | number }) => {
    if (creatingToastId.current) {
      dismiss(creatingToastId.current);
      creatingToastId.current = null;
    }

    success(`游戏创建成功: ${game.name} (GID: ${game.gid})`, {
      duration: 3000,
      icon: '✓'
    });

    validationToasts.current.clear();
  }, [success, dismiss]);

  const onError = useCallback((err: ErrorWithStatus) => {
    if (creatingToastId.current) {
      dismiss(creatingToastId.current);
      creatingToastId.current = null;
    }

    let message = '创建失败';

    if (err.message) {
      if (err.message.includes('already exists') || err.status === 409) {
        message = '游戏GID已存在';
      } else if (err.message.includes('invalid') || err.status === 400) {
        message = '表单验证失败';
      } else if (err.status === 500) {
        message = '服务器错误，请稍后重试';
      } else if (err.message.includes('必须是有效的正整数')) {
        message = '游戏GID格式错误';
      } else {
        message = err.message;
      }
    }

    error(message, {
      duration: 5000,
      icon: '✕'
    });
  }, [error, dismiss]);

  return {
    onValidation,
    onCreating,
    onSuccess,
    onError
  };
};
