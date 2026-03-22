/**
 * useAsyncAction Hook
 * 异步操作管理 Hook
 * 
 * 提供异步操作的状态管理、错误处理和加载状态
 */

import { useCallback, useState, useRef } from 'react';
import type { ErrorType } from '../ui/ErrorBoundary/types';

export interface AsyncState<T> {
  /** 返回数据 */
  data: T | null;
  /** 加载状态 */
  loading: boolean;
  /** 错误信息 */
  error: Error | null;
}

export interface AsyncActionOptions<T> {
  /** 成功回调 */
  onSuccess?: (data: T) => void;
  /** 错误回调 */
  onError?: (error: Error) => void;
  /** 完成回调（无论成功或失败） */
  onFinally?: () => void;
  /** 错误类型 */
  errorType?: ErrorType;
  /** 是否在组件卸载时取消 */
  cancelOnUnmount?: boolean;
}

export interface AsyncActionResult<T> extends AsyncState<T> {
  /** 执行异步操作 */
  execute: () => Promise<T | null>;
  /** 重置状态 */
  reset: () => void;
  /** 是否已取消 */
  isCancelled: boolean;
  /** 取消操作 */
  cancel: () => void;
}

/**
 * 异步操作管理 Hook
 * 
 * @example
 * ```tsx
 * const { data, loading, error, execute } = useAsyncAction(
 *   async () => {
 *     const response = await fetch('/api/data');
 *     return response.json();
 *   },
 *   {
 *     onSuccess: (data) => console.log('Success:', data),
 *     onError: (error) => console.error('Error:', error),
 *   }
 * );
 * 
 * // 执行
 * <button onClick={execute} disabled={loading}>
 *   {loading ? 'Loading...' : 'Fetch Data'}
 * </button>
 * ```
 */
export function useAsyncAction<T>(
  asyncFn: () => Promise<T>,
  options: AsyncActionOptions<T> = {}
): AsyncActionResult<T> {
  const {
    onSuccess,
    onError,
    onFinally,
    errorType = 'network',
    cancelOnUnmount = true,
  } = options;

  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const cancelledRef = useRef(false);

  const execute = useCallback(async (): Promise<T | null> => {
    // 重置取消状态
    cancelledRef.current = false;
    
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await asyncFn();
      
      // 检查是否已取消
      if (cancelledRef.current) {
        return null;
      }

      setState({ data, loading: false, error: null });
      onSuccess?.(data);
      return data;
    } catch (error) {
      // 检查是否已取消
      if (cancelledRef.current) {
        return null;
      }

      const err = error instanceof Error ? error : new Error(String(error));
      err.name = errorType;
      
      setState(prev => ({ ...prev, loading: false, error: err }));
      onError?.(err);
      throw err;
    } finally {
      if (!cancelledRef.current) {
        onFinally?.();
      }
    }
  }, [asyncFn, onSuccess, onError, onFinally, errorType]);

  const reset = useCallback((): void => {
    setState({ data: null, loading: false, error: null });
    cancelledRef.current = false;
  }, []);

  const cancel = useCallback((): void => {
    cancelledRef.current = true;
    setState(prev => ({ ...prev, loading: false }));
  }, []);

  return {
    ...state,
    execute,
    reset,
    isCancelled: cancelledRef.current,
    cancel,
  };
}

/**
 * 带参数的异步操作 Hook
 * 
 * @example
 * ```tsx
 * const { data, loading, execute } = useAsyncActionWithParams(
 *   async (id: string) => {
 *     const response = await fetch(`/api/data/${id}`);
 *     return response.json();
 *   }
 * );
 * 
 * // 执行时传入参数
 * <button onClick={() => execute('123')}>Fetch</button>
 * ```
 */
export function useAsyncActionWithParams<T, P extends unknown[]>(
  asyncFn: (...params: P) => Promise<T>,
  options: AsyncActionOptions<T> = {}
): AsyncActionResult<T> & { executeWithParams: (...params: P) => Promise<T | null> } {
  const {
    onSuccess,
    onError,
    onFinally,
    errorType = 'network',
    cancelOnUnmount = true,
  } = options;

  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const cancelledRef = useRef(false);

  const executeWithParams = useCallback(async (...params: P): Promise<T | null> => {
    cancelledRef.current = false;
    
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await asyncFn(...params);
      
      if (cancelledRef.current) {
        return null;
      }

      setState({ data, loading: false, error: null });
      onSuccess?.(data);
      return data;
    } catch (error) {
      if (cancelledRef.current) {
        return null;
      }

      const err = error instanceof Error ? error : new Error(String(error));
      err.name = errorType;
      
      setState(prev => ({ ...prev, loading: false, error: err }));
      onError?.(err);
      throw err;
    } finally {
      if (!cancelledRef.current) {
        onFinally?.();
      }
    }
  }, [asyncFn, onSuccess, onError, onFinally, errorType]);

  const reset = useCallback((): void => {
    setState({ data: null, loading: false, error: null });
    cancelledRef.current = false;
  }, []);

  const cancel = useCallback((): void => {
    cancelledRef.current = true;
    setState(prev => ({ ...prev, loading: false }));
  }, []);

  return {
    ...state,
    execute: executeWithParams as () => Promise<T | null>,
    executeWithParams,
    reset,
    isCancelled: cancelledRef.current,
    cancel,
  };
}

export default useAsyncAction;
