/**
 * useErrorHandler Hook
 * 统一错误处理 Hook
 * 
 * 提供错误捕获、重试机制和错误状态管理
 */

import { useCallback, useState } from 'react';
import type { ErrorHandler, ErrorType, StandardizedError } from '../ui/ErrorBoundary/types';

export interface ErrorHandlerOptions {
  /** 重试回调 */
  onRetry?: () => void;
  /** 最大重试次数 */
  maxRetries?: number;
  /** 是否显示 Toast */
  showToast?: boolean;
  /** 错误处理器 */
  errorHandler?: ErrorHandler;
}

export interface ErrorHandlerState {
  /** 当前错误 */
  error: StandardizedError | null;
  /** 重试次数 */
  retryCount: number;
}

export interface ErrorHandlerResult extends ErrorHandlerState {
  /** 是否可以重试 */
  canRetry: boolean;
  /** 处理错误 */
  handleError: (error: Error, type?: ErrorType) => void;
  /** 重试 */
  retry: () => void;
  /** 重置错误状态 */
  reset: () => void;
  /** 清除错误 */
  clearError: () => void;
}

/**
 * 标准化错误对象
 */
function standardizeError(error: Error, type: ErrorType = 'runtime'): StandardizedError {
  return {
    name: error.name,
    message: error.message,
    stack: error.stack,
    type,
    timestamp: Date.now(),
    recoverable: type !== 'fatal',
  };
}

/**
 * 统一错误处理 Hook
 * 
 * @example
 * ```tsx
 * const { error, handleError, retry, canRetry } = useErrorHandler({
 *   maxRetries: 3,
 *   onRetry: () => fetchData(),
 * });
 * 
 * try {
 *   await riskyOperation();
 * } catch (err) {
 *   handleError(err as Error);
 * }
 * ```
 */
export function useErrorHandler(options: ErrorHandlerOptions = {}): ErrorHandlerResult {
  const { 
    onRetry, 
    maxRetries = 3, 
    showToast = true,
    errorHandler,
  } = options;
  
  const [state, setState] = useState<ErrorHandlerState>({
    error: null,
    retryCount: 0,
  });

  const handleError = useCallback((error: Error, type: ErrorType = 'runtime'): void => {
    const standardizedError = standardizeError(error, type);
    
    console.error('[ErrorHandler]', {
      name: standardizedError.name,
      message: standardizedError.message,
      type: standardizedError.type,
      timestamp: new Date(standardizedError.timestamp).toISOString(),
    });
    
    setState(prev => ({ 
      ...prev, 
      error: standardizedError,
    }));
    
    // 调用外部错误处理器
    errorHandler?.(standardizedError);
    
    // 显示 Toast（如果启用且有 Toast 服务）
    if (showToast) {
      // Toast 服务集成点
      // toast.error(error.message);
    }
  }, [showToast, errorHandler]);

  const retry = useCallback((): void => {
    if (state.retryCount < maxRetries && onRetry) {
      setState(prev => ({ 
        ...prev, 
        retryCount: prev.retryCount + 1,
        error: null,
      }));
      onRetry();
    }
  }, [state.retryCount, maxRetries, onRetry]);

  const reset = useCallback((): void => {
    setState({ error: null, retryCount: 0 });
  }, []);

  const clearError = useCallback((): void => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    error: state.error,
    retryCount: state.retryCount,
    canRetry: state.retryCount < maxRetries,
    handleError,
    retry,
    reset,
    clearError,
  };
}

export default useErrorHandler;
