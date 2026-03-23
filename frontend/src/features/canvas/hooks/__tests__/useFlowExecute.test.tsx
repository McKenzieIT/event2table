/**
 * useFlowExecute Hook Tests
 *
 * 测试 useFlowExecute hook 的功能
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@test/test-utils';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useFlowExecute } from '../useFlowExecute';

// Mock fetch
global.fetch = vi.fn();

describe('useFlowExecute Hook', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  describe('API 调用测试', () => {
    it('应该成功执行流程并返回 HQL', async () => {
      const mockResult = {
        hql: 'SELECT * FROM events WHERE event_id = 1',
        execution_time: 100,
        metadata: { flow_id: 1 }
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockResult })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({ flowId: 1 });
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResult);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/flows/execute',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ flow_id: 1 }),
        })
      );
    });

    it('应该处理 HTTP 错误响应', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        try {
          await result.current.mutateAsync({ flowId: 1 });
        } catch (error) {
          // Expected error
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toContain('Server error');
    });

    it('应该处理 API 返回的失败状态', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false, error: 'Execution failed' })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        try {
          await result.current.mutateAsync({ flowId: 1 });
        } catch (error) {
          // Expected error
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toContain('Execution failed');
    });

    it('应该验证 flowId 参数', async () => {
      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        try {
          await result.current.mutateAsync({ flowId: null as any });
        } catch (error) {
          // Expected error
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toContain('flowId is required');
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('应该验证 flowId 为 undefined 的情况', async () => {
      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        try {
          await result.current.mutateAsync({ flowId: undefined as any });
        } catch (error) {
          // Expected error
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toContain('flowId is required');
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  describe('状态管理测试', () => {
    it('应该显示加载状态', async () => {
      (global.fetch as any).mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      act(() => {
        result.current.mutate({ flowId: 1 });
      });

      // Wait for state to update
      await waitFor(() => {
        expect(result.current.isPending).toBe(true);
      });
    });

    it('应该在成功后重置加载状态', async () => {
      const mockResult = {
        hql: 'SELECT * FROM events',
        execution_time: 50
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockResult })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({ flowId: 1 });
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.isPending).toBe(false);
    });

    it('应该在错误后重置加载状态', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Network error' })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        try {
          await result.current.mutateAsync({ flowId: 1 });
        } catch (error) {
          // Expected error
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.isPending).toBe(false);
    });
  });

  describe('数据转换测试', () => {
    it('应该正确返回完整的执行结果', async () => {
      const mockResult = {
        hql: 'SELECT * FROM events WHERE game_id = 10000147',
        execution_time: 123.456,
        metadata: {
          flow_id: 1,
          game_gid: 10000147,
          node_count: 5
        }
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockResult })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({ flowId: 1 });
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResult);
      expect(result.current.data?.hql).toBe(mockResult.hql);
      expect(result.current.data?.execution_time).toBe(mockResult.execution_time);
      expect(result.current.data?.metadata).toEqual(mockResult.metadata);
    });

    it('应该处理最小化的执行结果', async () => {
      const mockResult = {
        hql: 'SELECT * FROM events'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockResult })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({ flowId: 1 });
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResult);
      expect(result.current.data?.hql).toBe(mockResult.hql);
      expect(result.current.data?.execution_time).toBeUndefined();
    });
  });

  describe('业务流程测试', () => {
    it('应该支持使用 mutate 回调方式调用', async () => {
      const mockResult = {
        hql: 'SELECT * FROM events',
        execution_time: 100
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockResult })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      let onSuccessCalled = false;
      let onErrorCalled = false;

      act(() => {
        result.current.mutate(
          { flowId: 1 },
          {
            onSuccess: () => {
              onSuccessCalled = true;
            },
            onError: () => {
              onErrorCalled = true;
            }
          }
        );
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(onSuccessCalled).toBe(true);
      expect(onErrorCalled).toBe(false);
    });

    it('应该在 mutate 回调中处理错误', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Execution error' })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      let onSuccessCalled = false;
      let onErrorCalled = false;

      act(() => {
        result.current.mutate(
          { flowId: 1 },
          {
            onSuccess: () => {
              onSuccessCalled = true;
            },
            onError: () => {
              onErrorCalled = true;
            }
          }
        );
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(onSuccessCalled).toBe(false);
      expect(onErrorCalled).toBe(true);
    });

    it('应该正确发送请求体格式', async () => {
      const mockResult = { hql: 'SELECT * FROM events' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockResult })
      });

      const { result } = renderHook(() => useFlowExecute(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({ flowId: 123 });
      });

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/flows/execute',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ flow_id: 123 }),
        })
      );
    });
  });
});