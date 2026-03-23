import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { useEventConfigs } from './useEventConfigs';

// Mock fetch
global.fetch = vi.fn();

describe('useEventConfigs Hook', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  describe('API 调用测试', () => {
    it('应该成功获取事件配置列表', async () => {
      const mockData = [
        { id: 1, name: 'event1', nameCn: '事件1' },
        { id: 2, name: 'event2', nameCn: '事件2' }
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventConfigs(10000147), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith(
        '/event_node_builder/api/list?game_gid=10000147'
      );
    });

    it('应该处理 API 错误响应', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Network error' })
      });

      const { result } = renderHook(() => useEventConfigs(10000147), { wrapper });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toContain('Network error');
    });

    it('应该处理 API 返回的失败状态', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false, error: 'Server error' })
      });

      const { result } = renderHook(() => useEventConfigs(10000147), { wrapper });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toContain('Server error');
    });
  });

  describe('状态管理测试', () => {
    it('应该在 gameGid 为 undefined 时不执行查询', () => {
      const { result } = renderHook(() => useEventConfigs(undefined), { wrapper });

      expect(result.current.fetchStatus).toBe('idle');
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('应该在 gameGid 为 null 时不执行查询', () => {
      const { result } = renderHook(() => useEventConfigs(null), { wrapper });

      expect(result.current.fetchStatus).toBe('idle');
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('应该在 gameGid 为 0 时执行查询', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: [] })
      });

      const { result } = renderHook(() => useEventConfigs(0), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(global.fetch).toHaveBeenCalledWith(
        '/event_node_builder/api/list?game_gid=0'
      );
    });

    it('应该显示加载状态', () => {
      (global.fetch as any).mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() => useEventConfigs(10000147), { wrapper });

      expect(result.current.isLoading).toBe(true);
    });
  });

  describe('数据转换测试', () => {
    it('应该正确转换 API 返回的数据格式', async () => {
      const mockApiData = [
        { id: 1, event_name: 'test_event', event_name_cn: '测试事件' }
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockApiData })
      });

      const { result } = renderHook(() => useEventConfigs(10000147), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockApiData);
    });

    it('应该处理空数据数组', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: [] })
      });

      const { result } = renderHook(() => useEventConfigs(10000147), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual([]);
    });
  });

  describe('业务流程测试', () => {
    it('应该缓存相同 gameGid 的查询结果', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: [{ id: 1 }] })
      });

      const { result, rerender } = renderHook(
        ({ gameGid }) => useEventConfigs(gameGid),
        {
          wrapper,
          initialProps: { gameGid: 10000147 }
        }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // 重新渲染相同的 gameGid
      rerender({ gameGid: 10000147 });

      // 应该使用缓存，不会再次调用 fetch
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('应该在 gameGid 变化时重新获取数据', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: [{ id: 1 }] })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: [{ id: 2 }] })
        });

      const { result, rerender } = renderHook(
        ({ gameGid }) => useEventConfigs(gameGid),
        {
          wrapper,
          initialProps: { gameGid: 10000147 }
        }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      rerender({ gameGid: 10000148 });

      await waitFor(() => {
        expect(result.current.data).toEqual([{ id: 2 }]);
      });

      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
});
