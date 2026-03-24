/**
 * useRetry Hook 单元测试
 *
 * 测试重试机制、指数退避策略和错误处理
 */

import { renderHook, act } from '@test/test-utils';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

import { useRetry, useAsyncRetry } from './useRetry';

// Helper to create a rejected promise that won't trigger unhandled rejection warnings
function createRejectedPromise<T = never>(error: Error): Promise<T> {
  const promise = Promise.reject<T>(error);
  // Attach a catch handler to prevent unhandled rejection warnings
  // The actual error will be caught by the test's try/catch
  promise.catch(() => {});
  return promise;
}

describe('useRetry', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  describe('基本重试功能', () => {
    it('应该在第一次成功时立即返回结果', async () => {
      const asyncFn = vi.fn().mockResolvedValue('success');
      const { result } = renderHook(() => useRetry(asyncFn));

      let returnValue: string | undefined;
      await act(async () => {
        returnValue = await result.current.execute();
      });

      expect(returnValue).toBe('success');
      expect(asyncFn).toHaveBeenCalledTimes(1);
      expect(result.current.state.attempt).toBe(1);
      expect(result.current.state.isComplete).toBe(true);
    });

    it('应该在失败时进行重试', async () => {
      let callCount = 0;
      const asyncFn = vi.fn().mockImplementation(async () => {
        callCount++;
        if (callCount === 1) {
          throw new Error('Failed');
        }
        return 'success';
      });

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
        jitter: false, // Disable jitter for deterministic testing
        shouldRetry: () => true, // Force retry for generic Error
      }));

      let returnValue: string | undefined;
      await act(async () => {
        const promise = result.current.execute();
        // Use runAllTimersAsync to complete all pending timers
        await vi.runAllTimersAsync();
        returnValue = await promise;
      });

      expect(returnValue).toBe('success');
      expect(asyncFn).toHaveBeenCalledTimes(2);
      expect(result.current.state.attempt).toBe(2);
    });

    it('应该在达到最大重试次数后抛出错误', async () => {
      // Use mockReturnValue with pre-caught rejected promise
      const asyncFn = vi.fn().mockReturnValue(createRejectedPromise<string>(new Error('Failed')));

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
        jitter: false,
        shouldRetry: () => true, // Force retry for all errors
      }));

      let error: Error | null = null;
      await act(async () => {
        try {
          const promise = result.current.execute();
          await vi.runAllTimersAsync();
          await promise;
        } catch (e) {
          error = e as Error;
        }
      });

      expect(error).toBeInstanceOf(Error);
      expect((error as Error)?.message).toBe('Failed');
      expect(asyncFn).toHaveBeenCalledTimes(3); // 初始调用 + 2次重试
    });
  });

  describe('指数退避策略', () => {
    it('应该使用指数退避计算延迟时间', async () => {
      let callCount = 0;
      const asyncFn = vi.fn().mockImplementation(async () => {
        callCount++;
        if (callCount <= 2) {
          throw new Error('Failed');
        }
        return 'success';
      });

      const onRetry = vi.fn();
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 3,
        initialDelay: 100,
        backoffFactor: 2,
        jitter: false,
        onRetry,
        shouldRetry: () => true, // Force retry for generic Error
      }));

      await act(async () => {
        const promise = result.current.execute();
        await vi.runAllTimersAsync();
        await promise;
      });

      expect(onRetry).toHaveBeenCalledTimes(2);
      expect(asyncFn).toHaveBeenCalledTimes(3);
    });

    it('应该限制最大延迟时间', async () => {
      // Use mockReturnValue with pre-caught rejected promise
      const asyncFn = vi.fn().mockReturnValue(createRejectedPromise<string>(new Error('Failed')));

      const onRetry = vi.fn();
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 5,
        initialDelay: 100,
        backoffFactor: 10,
        maxDelay: 500,
        jitter: false,
        onRetry,
        shouldRetry: () => true, // Force retry
      }));

      let error: Error | null = null;
      await act(async () => {
        try {
          const promise = result.current.execute();
          await vi.runAllTimersAsync();
          await promise;
        } catch (e) {
          error = e as Error;
        }
      });

      expect(error).toBeInstanceOf(Error);
      expect(onRetry).toHaveBeenCalled();
    });
  });

  describe('重试条件判断', () => {
    it('应该根据 shouldRetry 函数决定是否重试', async () => {
      const asyncFn = vi.fn().mockImplementation(async () => {
        throw new Error('Failed');
      });
      const shouldRetry = vi.fn(() => false);

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 3,
        shouldRetry,
      }));

      let error: Error | null = null;
      await act(async () => {
        try {
          await result.current.execute();
        } catch (e) {
          error = e as Error;
        }
      });

      expect(error).toBeInstanceOf(Error);
      expect(asyncFn).toHaveBeenCalledTimes(1); // 不应该重试
      expect(shouldRetry).toHaveBeenCalled();
    });

    it('应该默认重试网络错误', async () => {
      let callCount = 0;
      const asyncFn = vi.fn().mockImplementation(async () => {
        callCount++;
        if (callCount === 1) {
          throw new TypeError('Failed to fetch');
        }
        return 'success';
      });

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
        jitter: false,
      }));

      await act(async () => {
        const promise = result.current.execute();
        await vi.runAllTimersAsync();
        await promise;
      });

      expect(asyncFn).toHaveBeenCalledTimes(2);
      expect(result.current.state.isComplete).toBe(true);
    });

    it('应该默认重试 5xx 错误', async () => {
      let callCount = 0;
      const asyncFn = vi.fn().mockImplementation(async () => {
        callCount++;
        if (callCount === 1) {
          const err = new Error('Server error') as Error & { status: number };
          err.status = 500;
          throw err;
        }
        return 'success';
      });

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
        jitter: false,
      }));

      await act(async () => {
        const promise = result.current.execute();
        await vi.runAllTimersAsync();
        await promise;
      });

      expect(asyncFn).toHaveBeenCalledTimes(2);
      expect(result.current.state.isComplete).toBe(true);
    });

    it('不应该重试 4xx 错误', async () => {
      const asyncFn = vi.fn().mockImplementation(async () => {
        const err = new Error('Not found') as Error & { status: number };
        err.status = 404;
        throw err;
      });

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
      }));

      let error: Error | null = null;
      await act(async () => {
        try {
          await result.current.execute();
        } catch (e) {
          error = e as Error;
        }
      });

      expect(error).toBeInstanceOf(Error);
      expect((error as Error & { status: number })?.status).toBe(404);
      expect(asyncFn).toHaveBeenCalledTimes(1);
    });
  });

  describe('回调函数', () => {
    it('应该在重试时调用 onRetry 回调', async () => {
      let callCount = 0;
      const asyncFn = vi.fn().mockImplementation(async () => {
        callCount++;
        if (callCount === 1) {
          throw new Error('Failed');
        }
        return 'success';
      });

      const onRetry = vi.fn();
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
        jitter: false,
        onRetry,
        shouldRetry: () => true, // Force retry for generic Error
      }));

      await act(async () => {
        const promise = result.current.execute();
        await vi.runAllTimersAsync();
        await promise;
      });

      expect(onRetry).toHaveBeenCalledTimes(1);
      expect(onRetry).toHaveBeenCalledWith(expect.any(Error), 1);
    });

    it('应该在成功时调用 onSuccess 回调', async () => {
      const asyncFn = vi.fn().mockResolvedValue('success');
      const onSuccess = vi.fn();

      const { result } = renderHook(() => useRetry(asyncFn, {
        onSuccess,
      }));

      await act(async () => {
        await result.current.execute();
      });

      expect(onSuccess).toHaveBeenCalledWith('success', 1);
    });

    it('应该在失败时调用 onFailure 回调', async () => {
      // Use mockReturnValue with pre-caught rejected promise
      const asyncFn = vi.fn().mockReturnValue(createRejectedPromise<string>(new Error('Failed')));
      const onFailure = vi.fn();

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        onFailure,
        shouldRetry: () => true,
        jitter: false,
      }));

      let error: Error | null = null;
      await act(async () => {
        try {
          const promise = result.current.execute();
          await vi.runAllTimersAsync();
          await promise;
        } catch (e) {
          error = e as Error;
        }
      });

      expect(error).toBeInstanceOf(Error);
      expect(onFailure).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  describe('状态管理', () => {
    it('应该正确更新重试状态', async () => {
      let callCount = 0;
      const asyncFn = vi.fn().mockImplementation(async () => {
        callCount++;
        if (callCount === 1) {
          throw new Error('Failed');
        }
        return 'success';
      });

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
        jitter: false,
        shouldRetry: () => true, // Force retry for generic Error
      }));

      // Initial state
      expect(result.current.state.isRetrying).toBe(false);
      expect(result.current.state.attempt).toBe(0);
      expect(result.current.state.isComplete).toBe(false);

      await act(async () => {
        const promise = result.current.execute();
        // Advance timers
        await vi.runAllTimersAsync();
        await promise;
      });

      // Final state after successful retry
      expect(result.current.state.isComplete).toBe(true);
      expect(result.current.state.isRetrying).toBe(false);
      expect(result.current.state.attempt).toBe(2);
      expect(result.current.state.lastError).toBeNull();
    });

    it('应该记录最后一次错误', async () => {
      // Use mockReturnValue with pre-caught rejected promise
      const asyncFn = vi.fn().mockReturnValue(createRejectedPromise<string>(new Error('Failed')));

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 1,
        initialDelay: 100,
        jitter: false,
        shouldRetry: () => true,
      }));

      let error: Error | null = null;
      await act(async () => {
        try {
          const promise = result.current.execute();
          await vi.runAllTimersAsync();
          await promise;
        } catch (e) {
          error = e as Error;
        }
      });

      expect(error).toBeInstanceOf(Error);
      expect(result.current.state.lastError).toBeInstanceOf(Error);
    });
  });

  describe('控制方法', () => {
    it('应该支持重置状态', async () => {
      const asyncFn = vi.fn().mockImplementation(async () => {
        throw new Error('Failed');
      });

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 1,
        initialDelay: 100,
        jitter: false,
        shouldRetry: () => true,
      }));

      let error: Error | null = null;
      await act(async () => {
        try {
          const promise = result.current.execute();
          await vi.runAllTimersAsync();
          await promise;
        } catch (e) {
          error = e as Error;
        }
      });

      expect(error).toBeInstanceOf(Error);
      expect(result.current.state.attempt).toBe(2);

      act(() => {
        result.current.reset();
      });

      expect(result.current.state.attempt).toBe(0);
      expect(result.current.state.lastError).toBeNull();
      expect(result.current.state.isComplete).toBe(false);
    });

    it('应该支持取消重试', async () => {
      let callCount = 0;
      const asyncFn = vi.fn().mockImplementation(async () => {
        callCount++;
        if (callCount === 1) {
          throw new Error('Failed');
        }
        return 'success';
      });

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 3,
        initialDelay: 1000,
        jitter: false,
      }));

      // Start execution
      await act(async () => {
        result.current.execute();
        // Wait a bit for the first attempt to fail (but not enough for retry)
        await vi.advanceTimersByTimeAsync(10);
      });

      // Verify first attempt failed
      expect(result.current.state.lastError).toBeInstanceOf(Error);

      // Cancel the retry
      act(() => {
        result.current.cancel();
      });

      // Advance more time - should not retry
      await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
      });

      expect(asyncFn).toHaveBeenCalledTimes(1);
    });
  });
});

describe('useAsyncRetry', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  it('应该管理异步操作的状态', async () => {
    const asyncFn = vi.fn().mockResolvedValue('success');
    const { result } = renderHook(() => useAsyncRetry(asyncFn));

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();

    await act(async () => {
      await result.current.retry();
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBe('success');
    expect(result.current.error).toBeNull();
  });

  it('应该在失败时记录错误', async () => {
    const asyncFn = vi.fn().mockImplementation(async () => {
      throw new Error('Failed');
    });
    const { result } = renderHook(() => useAsyncRetry(asyncFn, {
      maxRetries: 1,
      shouldRetry: () => false,
    }));

    await act(async () => {
      try {
        await result.current.retry();
      } catch (e) {
        // Expected error
      }
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeInstanceOf(Error);
  });

  it('应该支持重置状态', async () => {
    const asyncFn = vi.fn().mockResolvedValue('success');
    const { result } = renderHook(() => useAsyncRetry(asyncFn));

    await act(async () => {
      await result.current.retry();
    });

    expect(result.current.data).toBe('success');

    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });
});
