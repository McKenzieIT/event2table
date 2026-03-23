/**
 * useFlowSave Hook 单元测试
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { useFlowSave } from '../useFlowSave';

// Mock数据
const mockSavedFlow = {
  id: 1,
  name: 'Test Flow',
  game_gid: 10000147,
  flow_data: {
    nodes: [],
    edges: [],
  },
};

const mockFlowData = {
  name: 'Test Flow',
  game_gid: 10000147,
  flow_data: {
    nodes: [],
    edges: [],
  },
};

const mockUpdateFlowData = {
  id: 1,
  name: 'Updated Flow',
  game_gid: 10000147,
  flow_data: {
    nodes: [],
    edges: [],
  },
};

// 创建QueryClient
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

// 测试wrapper
const wrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useFlowSave', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('创建Flow', () => {
    it('应该成功创建新的flow', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: mockSavedFlow,
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      result.current.mutate(mockFlowData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/flows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mockFlowData),
      });

      expect(result.current.data).toEqual(mockSavedFlow);
    });

    it('应该在创建失败时抛出错误', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        json: () =>
          Promise.resolve({
            error: 'Failed to create flow',
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      result.current.mutate(mockFlowData);

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toContain('Failed to create flow');
    });

    it('应该在API返回success=false时抛出错误', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            success: false,
            error: 'Validation failed',
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      result.current.mutate(mockFlowData);

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toBe('Validation failed');
    });
  });

  describe('更新Flow', () => {
    it('应该成功更新已有的flow', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: { ...mockSavedFlow, name: 'Updated Flow' },
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      result.current.mutate(mockUpdateFlowData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/flows/1', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mockUpdateFlowData),
      });
    });

    it('应该在更新失败时抛出错误', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: () =>
          Promise.resolve({
            error: 'Flow not found',
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      result.current.mutate(mockUpdateFlowData);

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toContain('Flow not found');
    });
  });

  describe('状态管理', () => {
    it('应该在mutation进行时显示loading状态', async () => {
      let resolveFetch: (value: any) => void;
      const mockFetch = vi.fn(
        () =>
          new Promise((resolve) => {
            resolveFetch = resolve;
          })
      );
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      result.current.mutate(mockFlowData);

      // 等待状态更新
      await waitFor(() => {
        expect(result.current.isPending).toBe(true);
      });

      resolveFetch!({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: mockSavedFlow,
          }),
      });

      await waitFor(() => {
        expect(result.current.isPending).toBe(false);
      });
    });

    it('应该在成功后重置loading状态', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: mockSavedFlow,
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      result.current.mutate(mockFlowData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.isPending).toBe(false);
    });

    it('应该在失败后重置loading状态', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        json: () =>
          Promise.resolve({
            error: 'Error',
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      result.current.mutate(mockFlowData);

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.isPending).toBe(false);
    });
  });

  describe('Query Cache Invalidation', () => {
    it('应该在成功后invalidate flows queries', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: mockSavedFlow,
          }),
      });
      global.fetch = mockFetch;

      const queryClient = createTestQueryClient();
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const customWrapper = ({ children }: { children: React.ReactNode }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      );

      const { result } = renderHook(() => useFlowSave(), {
        wrapper: customWrapper,
      });

      result.current.mutate(mockFlowData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ['flows', 'list'],
      });
    });
  });

  describe('mutateAsync', () => {
    it('应该支持promise-based mutation', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            data: mockSavedFlow,
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      const promise = result.current.mutateAsync(mockFlowData);

      await expect(promise).resolves.toEqual(mockSavedFlow);

      expect(mockFetch).toHaveBeenCalledWith('/api/flows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mockFlowData),
      });
    });

    it('应该在mutateAsync失败时抛出错误', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        json: () =>
          Promise.resolve({
            error: 'Failed',
          }),
      });
      global.fetch = mockFetch;

      const { result } = renderHook(() => useFlowSave(), { wrapper });

      await expect(result.current.mutateAsync(mockFlowData)).rejects.toThrow(
        'Failed'
      );
    });
  });
});