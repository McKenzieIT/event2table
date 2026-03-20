/**
 * useRetry Hook
 *
 * 提供自动重试机制的React Hook，支持指数退避策略
 *
 * 功能：
 * 1. 自动重试机制
 * 2. 指数退避策略
 * 3. 最大重试次数配置
 * 4. 可配置的重试条件
 *
 * 创建日期: 2026-03-20
 */

import { useState, useCallback, useRef } from 'react';

// ============================================================================
// 类型定义
// ============================================================================

/**
 * 重试配置选项
 */
export interface RetryOptions {
  /** 最大重试次数 */
  maxRetries?: number;
  /** 初始延迟时间（毫秒） */
  initialDelay?: number;
  /** 指数退避因子 */
  backoffFactor?: number;
  /** 最大延迟时间（毫秒） */
  maxDelay?: number;
  /** 是否启用抖动 */
  jitter?: boolean;
  /** 判断是否应该重试的函数 */
  shouldRetry?: (error: unknown, attempt: number) => boolean;
  /** 重试前的回调 */
  onRetry?: (error: unknown, attempt: number) => void;
  /** 重试成功后的回调 */
  onSuccess?: (result: any, attempt: number) => void;
  /** 重试失败后的回调 */
  onFailure?: (error: unknown) => void;
}

/**
 * 重试状态
 */
export interface RetryState {
  /** 当前重试次数 */
  attempt: number;
  /** 是否正在重试 */
  isRetrying: boolean;
  /** 最后一次错误 */
  lastError: unknown | null;
  /** 是否已完成 */
  isComplete: boolean;
}

/**
 * 重试返回值
 */
export interface RetryReturn {
  /** 重试状态 */
  state: RetryState;
  /** 执行重试函数 */
  retry: () => void;
  /** 重置重试状态 */
  reset: () => void;
  /** 取消重试 */
  cancel: () => void;
}

// ============================================================================
// 默认配置
// ============================================================================

const DEFAULT_RETRY_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  initialDelay: 1000,
  backoffFactor: 2,
  maxDelay: 30000,
  jitter: true,
  shouldRetry: () => true,
  onRetry: () => {},
  onSuccess: () => {},
  onFailure: () => {},
};

// ============================================================================
// 辅助函数
// ============================================================================

/**
 * 计算延迟时间（带指数退避和抖动）
 */
function calculateDelay(
  attempt: number,
  initialDelay: number,
  backoffFactor: number,
  maxDelay: number,
  jitter: boolean
): number {
  // 计算指数退避延迟
  const exponentialDelay = initialDelay * Math.pow(backoffFactor, attempt);
  
  // 限制最大延迟
  const delay = Math.min(exponentialDelay, maxDelay);
  
  // 添加抖动（随机化延迟，避免重试风暴）
  if (jitter) {
    const jitterAmount = delay * 0.1; // 10% 的抖动
    const randomJitter = Math.random() * jitterAmount - jitterAmount / 2;
    return Math.max(0, delay + randomJitter);
  }
  
  return delay;
}

/**
 * 默认的重试判断函数
 */
function defaultShouldRetry(error: unknown, attempt: number): boolean {
  // 网络错误总是重试
  if (error instanceof TypeError) {
    const networkErrorMessages = [
      'Failed to fetch',
      'NetworkError',
      'Network request failed',
      'fetch failed',
    ];
    return networkErrorMessages.some(msg => error.message.includes(msg));
  }
  
  // AbortError 不重试
  if (error instanceof DOMException && error.name === 'AbortError') {
    return false;
  }
  
  // 5xx 错误重试
  if (error && typeof error === 'object') {
    const status = (error as Record<string, unknown>).status;
    if (typeof status === 'number' && status >= 500) {
      return true;
    }
  }
  
  // 其他错误不重试
  return false;
}

// ============================================================================
// useRetry Hook
// ============================================================================

/**
 * 重试 Hook
 *
 * @param asyncFn - 需要重试的异步函数
 * @param options - 重试配置选项
 * @returns 重试控制对象
 *
 * @example
 * ```tsx
 * const { state, retry, reset, cancel } = useRetry(
 *   async () => {
 *     const response = await fetch('/api/data');
 *     return response.json();
 *   },
 *   {
 *     maxRetries: 3,
 *     initialDelay: 1000,
 *     shouldRetry: (error) => error.status >= 500,
 *   }
 * );
 * ```
 */
export function useRetry<T>(
  asyncFn: () => Promise<T>,
  options: RetryOptions = {}
): RetryReturn & { execute: () => Promise<T> } {
  const mergedOptions = { ...DEFAULT_RETRY_OPTIONS, ...options };
  
  // 使用自定义的重试判断函数或默认的
  const shouldRetryFn = options.shouldRetry || defaultShouldRetry;
  
  const [state, setState] = useState<RetryState>({
    attempt: 0,
    isRetrying: false,
    lastError: null,
    isComplete: false,
  });
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const isCancelledRef = useRef(false);
  
  /**
   * 重置重试状态
   */
  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    isCancelledRef.current = false;
    setState({
      attempt: 0,
      isRetrying: false,
      lastError: null,
      isComplete: false,
    });
  }, []);
  
  /**
   * 取消重试
   */
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    isCancelledRef.current = true;
    setState((prev) => ({
      ...prev,
      isRetrying: false,
    }));
  }, []);
  
  /**
   * 执行重试
   */
  const execute = useCallback(async (): Promise<T> => {
    reset();
    isCancelledRef.current = false;
    
    let lastError: unknown = null;
    
    for (let attempt = 0; attempt <= mergedOptions.maxRetries; attempt++) {
      // 检查是否被取消
      if (isCancelledRef.current) {
        throw new Error('Retry cancelled');
      }
      
      setState({
        attempt: attempt + 1,
        isRetrying: true,
        lastError: null,
        isComplete: false,
      });
      
      try {
        // 执行异步函数
        const result = await asyncFn();
        
        // 成功
        setState({
          attempt: attempt + 1,
          isRetrying: false,
          lastError: null,
          isComplete: true,
        });
        
        mergedOptions.onSuccess(result, attempt + 1);
        return result;
        
      } catch (error) {
        lastError = error;
        
        // 检查是否应该重试
        const canRetry =
          attempt < mergedOptions.maxRetries &&
          shouldRetryFn(error, attempt + 1);
        
        if (!canRetry) {
          // 不再重试，直接抛出错误
          setState({
            attempt: attempt + 1,
            isRetrying: false,
            lastError: error,
            isComplete: true,
          });
          
          mergedOptions.onFailure(error);
          throw error;
        }
        
        // 更新状态
        setState({
          attempt: attempt + 1,
          isRetrying: true,
          lastError: error,
          isComplete: false,
        });
        
        // 调用重试回调
        mergedOptions.onRetry(error, attempt + 1);
        
        // 计算延迟时间
        const delay = calculateDelay(
          attempt,
          mergedOptions.initialDelay,
          mergedOptions.backoffFactor,
          mergedOptions.maxDelay,
          mergedOptions.jitter
        );
        
        // 等待延迟
        await new Promise<void>((resolve) => {
          const timeout = setTimeout(resolve, delay);
          
          // 如果被取消，清除超时
          if (isCancelledRef.current) {
            clearTimeout(timeout);
            resolve();
          }
        });
      }
    }
    
    // 理论上不应该到达这里
    throw lastError;
  }, [asyncFn, mergedOptions, shouldRetryFn, reset]);
  
  /**
   * 手动触发重试
   */
  const retry = useCallback(() => {
    execute();
  }, [execute]);
  
  return {
    state,
    execute,
    retry,
    reset,
    cancel,
  };
}

// ============================================================================
// 便捷 Hook
// ============================================================================

/**
 * 使用带重试的异步操作 Hook
 *
 * @example
 * ```tsx
 * const { data, error, loading, retry } = useAsyncRetry(
 *   () => fetch('/api/data').then(res => res.json()),
 *   { maxRetries: 3 }
 * );
 * ```
 */
export function useAsyncRetry<T>(
  asyncFn: () => Promise<T>,
  options: RetryOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [loading, setLoading] = useState(false);
  
  const { state, execute, reset, cancel } = useRetry(asyncFn, options);
  
  const run = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await execute();
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [execute]);
  
  return {
    data,
    error,
    loading,
    retry: run,
    reset: () => {
      reset();
      setData(null);
      setError(null);
    },
    cancel,
    state,
  };
}

// ============================================================================
// 导出
// ============================================================================

export default useRetry;
