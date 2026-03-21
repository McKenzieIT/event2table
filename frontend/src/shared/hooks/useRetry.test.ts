/**
 * useRetry Hook 单元测试
 *
 * 测试重试机制、指数退避策略和错误处理
 */

import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useRetry, useAsyncRetry } from './useRetry';

// Mock setTimeout 和 clearTimeout
vi.useFakeTimers();

describe('useRetry', () => {
  beforeEach(() => {
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
      const asyncFn = vi.fn()
        .mockRejectedValueOnce(new Error('Failed'))
        .mockResolvedValue('success');
      
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
      }));

      let returnValue: string | undefined;
      await act(async () => {
        returnValue = await result.current.execute();
      });

      expect(returnValue).toBe('success');
      expect(asyncFn).toHaveBeenCalledTimes(2);
      expect(result.current.state.attempt).toBe(2);
    });

    it('应该在达到最大重试次数后抛出错误', async () => {
      const asyncFn = vi.fn().mockRejectedValue(new Error('Failed'));
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
      }));

      await expect(result.current.execute()).rejects.toThrow('Failed');
      expect(asyncFn).toHaveBeenCalledTimes(3); // 初始调用 + 2次重试
    });
  });

  describe('指数退避策略', () => {
    it('应该使用指数退避计算延迟时间', async () => {
      const asyncFn = vi.fn()
        .mockRejectedValueOnce(new Error('Failed'))
        .mockRejectedValueOnce(new Error('Failed'))
        .mockResolvedValue('success');
      
      const onRetry = vi.fn();
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 3,
        initialDelay: 100,
        backoffFactor: 2,
        onRetry,
      }));

      act(() => {
        result.current.execute();
      });

      // 第一次重试应该在 100ms 后
      vi.advanceTimersByTime(100);
      await waitFor(() => {
        expect(onRetry).toHaveBeenCalledTimes(1);
      });

      // 第二次重试应该在 200ms 后 (100 * 2)
      vi.advanceTimersByTime(200);
      await waitFor(() => {
        expect(onRetry).toHaveBeenCalledTimes(2);
      });

      // 第三次重试应该在 400ms 后 (100 * 2^2)
      vi.advanceTimersByTime(400);
      await waitFor(() => {
        expect(onRetry).toHaveBeenCalledTimes(3);
      });
    });

    it('应该限制最大延迟时间', async () => {
      const asyncFn = vi.fn()
        .mockRejectedValue(new Error('Failed'));
      
      const onRetry = vi.fn();
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 5,
        initialDelay: 100,
        backoffFactor: 10,
        maxDelay: 500,
        onRetry,
      }));

      act(() => {
        result.current.execute();
      });

      // 所有重试都应该在 maxDelay 限制内
      vi.advanceTimersByTime(500);
      await waitFor(() => {
        expect(onRetry).toHaveBeenCalled();
      });
    });
  });

  describe('重试条件判断', () => {
    it('应该根据 shouldRetry 函数决定是否重试', async () => {
      const asyncFn = vi.fn().mockRejectedValue(new Error('Failed'));
      const shouldRetry = vi.fn(() => false);

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 3,
        shouldRetry,
      }));

      await expect(result.current.execute()).rejects.toThrow('Failed');
      expect(asyncFn).toHaveBeenCalledTimes(1); // 不应该重试
      expect(shouldRetry).toHaveBeenCalled();
    });

    it('应该默认重试网络错误', async () => {
      const asyncFn = vi.fn()
        .mockRejectedValueOnce(new TypeError('Failed to fetch'))
        .mockResolvedValue('success');
      
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
      }));

      act(() => {
        result.current.execute();
      });

      vi.advanceTimersByTime(100);
      await waitFor(() => {
        expect(result.current.state.isComplete).toBe(true);
      });

      expect(asyncFn).toHaveBeenCalledTimes(2);
    });

    it('应该默认重试 5xx 错误', async () => {
      const asyncFn = vi.fn()
        .mockRejectedValueOnce({ status: 500 })
        .mockResolvedValue('success');
      
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
      }));

      act(() => {
        result.current.execute();
      });

      vi.advanceTimersByTime(100);
      await waitFor(() => {
        expect(result.current.state.isComplete).toBe(true);
      });

      expect(asyncFn).toHaveBeenCalledTimes(2);
    });

    it('不应该重试 4xx 错误', async () => {
      const asyncFn = vi.fn().mockRejectedValue({ status: 404 });
      
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
      }));

      await expect(result.current.execute()).rejects.toEqual({ status: 404 });
      expect(asyncFn).toHaveBeenCalledTimes(1);
    });
  });

  describe('回调函数', () => {
    it('应该在重试时调用 onRetry 回调', async () => {
      const asyncFn = vi.fn()
        .mockRejectedValueOnce(new Error('Failed'))
        .mockResolvedValue('success');
      
      const onRetry = vi.fn();
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
        onRetry,
      }));

      act(() => {
        result.current.execute();
      });

      vi.advanceTimersByTime(100);
      await waitFor(() => {
        expect(onRetry).toHaveBeenCalledTimes(1);
        expect(onRetry).toHaveBeenCalledWith(expect.any(Error), 1);
      });
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
      const asyncFn = vi.fn().mockRejectedValue(new Error('Failed'));
      const onFailure = vi.fn();

      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        onFailure,
      }));

      await expect(result.current.execute()).rejects.toThrow('Failed');
      expect(onFailure).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  describe('状态管理', () => {
    it('应该正确更新重试状态', async () => {
      const asyncFn = vi.fn()
        .mockRejectedValueOnce(new Error('Failed'))
        .mockResolvedValue('success');
      
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 2,
        initialDelay: 100,
      }));

      act(() => {
        result.current.execute();
      });

      // 初始状态
      expect(result.current.state.isRetrying).toBe(true);
      expect(result.current.state.attempt).toBe(1);

      // 第一次重试
      vi.advanceTimersByTime(100);
      await waitFor(() => {
        expect(result.current.state.attempt).toBe(2);
      });

      // 完成状态
      await waitFor(() => {
        expect(result.current.state.isComplete).toBe(true);
        expect(result.current.state.isRetrying).toBe(false);
      });
    });

    it('应该记录最后一次错误', async () => {
      const asyncFn = vi.fn().mockRejectedValue(new Error('Failed'));
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 1,
      }));

      await expect(result.current.execute()).rejects.toThrow('Failed');
      expect(result.current.state.lastError).toBeInstanceOf(Error);
    });
  });

  describe('控制方法', () => {
    it('应该支持重置状态', async () => {
      const asyncFn = vi.fn().mockRejectedValue(new Error('Failed'));
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 1,
      }));

      await expect(result.current.execute()).rejects.toThrow('Failed');
      expect(result.current.state.attempt).toBe(2);

      act(() => {
        result.current.reset();
      });

      expect(result.current.state.attempt).toBe(0);
      expect(result.current.state.lastError).toBeNull();
      expect(result.current.state.isComplete).toBe(false);
    });

    it('应该支持取消重试', async () => {
      const asyncFn = vi.fn()
        .mockRejectedValue(new Error('Failed'))
        .mockResolvedValue('success');
      
      const { result } = renderHook(() => useRetry(asyncFn, {
        maxRetries: 3,
        initialDelay: 1000,
      }));

      act(() => {
        result.current.execute();
      });

      // 在第一次失败后取消
      vi.advanceTimersByTime(100);
      await waitFor(() => {
        expect(result.current.state.lastError).toBeInstanceOf(Error);
      });

      act(() => {
        result.current.cancel();
      });

      // 不应该继续重试
      vi.advanceTimersByTime(2000);
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
    const asyncFn = vi.fn().mockRejectedValue(new Error('Failed'));
    const { result } = renderHook(() => useAsyncRetry(asyncFn, {
      maxRetries: 1,
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
