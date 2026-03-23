import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { useEventsList } from './hooks';

// Mock fetch
(globalThis as typeof globalThis & { fetch: typeof vi.fn }).fetch = vi.fn();

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn()
}));

// Mock useToast
vi.mock('@shared/ui', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn()
  })
}));

// Test data - complete game object with all required fields
const currentGame = { id: 1, gid: 10000147, name: 'Test Game', ods_db: 'ieu_ods' };

describe('useEventsList Hook', () => {
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
    it('应该成功获取事件列表', async () => {
      const mockData = {
        events: [
          { id: 1, name: 'event1', category_name: 'game' },
          { id: 2, name: 'event2', category_name: 'game' }
        ],
        pagination: { total: 2, total_pages: 1, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.filteredEvents).toHaveLength(2);
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/events?')
      );
    });

    it('应该处理 API 错误', async () => {
      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Network error' })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.fetchError).toBeDefined();
    });

    it('应该在没有游戏上下文时返回占位数据', () => {
      const { result } = renderHook(() => useEventsList(null), { wrapper });

      expect(result.current.hasGameContext).toBe(false);
      expect(result.current.filteredEvents).toHaveLength(0);
      expect(globalThis.fetch).not.toHaveBeenCalled();
    });
  });

  describe('状态管理测试', () => {
    it('应该管理搜索词状态', () => {
      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      expect(result.current.searchTerm).toBe('');

      // 注意：由于 searchTerm 是内部状态，我们无法直接修改它
      // 这个测试验证了初始状态
    });

    it('应该管理分页状态', () => {
      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      expect(result.current.currentPage).toBe(1);
      expect(result.current.pageSize).toBe(10);
    });

    it('应该管理分类选择状态', () => {
      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      expect(result.current.selectedCategory).toBe('all');
    });

    it('应该管理选中事件状态', () => {
      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      expect(result.current.selectedEvents).toEqual([]);
    });
  });

  describe('数据转换测试', () => {
    it('应该正确过滤事件', async () => {
      const mockData = {
        events: [
          { id: 1, name: 'event1', category_name: 'game' },
          { id: 2, name: 'event2', category_name: 'system' }
        ],
        pagination: { total: 2, total_pages: 1, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.filteredEvents).toHaveLength(2);
      expect(result.current.categories).toContain('all');
      expect(result.current.categories).toContain('game');
      expect(result.current.categories).toContain('system');
    });

    it('应该正确提取分类列表', async () => {
      const mockData = {
        events: [
          { id: 1, name: 'event1', category_name: 'game' },
          { id: 2, name: 'event2', category_name: 'game' },
          { id: 3, name: 'event3', category_name: 'system' }
        ],
        pagination: { total: 3, total_pages: 1, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.categories).toEqual(['all', 'game', 'system']);
    });

    it('应该处理分页信息', async () => {
      const mockData = {
        events: [],
        pagination: { total: 100, total_pages: 10, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.total).toBe(100);
      expect(result.current.totalPages).toBe(10);
      expect(result.current.pagination.page).toBe(1);
    });
  });

  describe('业务流程测试', () => {
    it('应该处理批量删除', async () => {
      (globalThis.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { events: [], pagination: { total: 0, total_pages: 1, page: 1, per_page: 10 } } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { deleted_count: 2 } })
        });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // 选择事件
      result.current.handleToggleSelect(1);
      result.current.handleToggleSelect(2);

      expect(result.current.selectedEvents).toHaveLength(2);

      // 批量删除
      result.current.handleBatchDelete();

      await waitFor(() => {
        expect(result.current.deleteMutation.isSuccess).toBe(true);
      });
    });

    it('应该处理单个删除', async () => {
      (globalThis.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { events: [{ id: 1, name: 'event1', category_name: 'game' }], pagination: { total: 1, total_pages: 1, page: 1, per_page: 10 } } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { deleted_count: 1 } })
        });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.handleDeleteEvent(1, 'event1');

      await waitFor(() => {
        expect(result.current.deleteMutation.isSuccess).toBe(true);
      });
    });

    it('应该处理全选操作', async () => {
      const mockData = {
        events: [
          { id: 1, name: 'event1', category_name: 'game' },
          { id: 2, name: 'event2', category_name: 'game' }
        ],
        pagination: { total: 2, total_pages: 1, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // 全选
      result.current.handleSelectAll();
      expect(result.current.selectedEvents).toHaveLength(2);

      // 取消全选
      result.current.handleSelectAll();
      expect(result.current.selectedEvents).toHaveLength(0);
    });

    it('应该处理单个选择/取消选择', async () => {
      const mockData = {
        events: [
          { id: 1, name: 'event1', category_name: 'game' }
        ],
        pagination: { total: 1, total_pages: 1, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // 选择
      result.current.handleToggleSelect(1);
      expect(result.current.selectedEvents).toContain(1);

      // 取消选择
      result.current.handleToggleSelect(1);
      expect(result.current.selectedEvents).not.toContain(1);
    });

    it('应该处理清空选择', async () => {
      const mockData = {
        events: [
          { id: 1, name: 'event1', category_name: 'game' }
        ],
        pagination: { total: 1, total_pages: 1, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.handleToggleSelect(1);
      expect(result.current.selectedEvents).toHaveLength(1);

      result.current.handleClearSelection();
      expect(result.current.selectedEvents).toHaveLength(0);
    });
  });

  describe('边界情况测试', () => {
    it('应该处理空事件列表', async () => {
      const mockData = {
        events: [],
        pagination: { total: 0, total_pages: 1, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.filteredEvents).toHaveLength(0);
      expect(result.current.categories).toEqual(['all']);
    });

    it('应该处理没有分类的事件', async () => {
      const mockData = {
        events: [
          { id: 1, name: 'event1', category_name: null },
          { id: 2, name: 'event2', category_name: undefined }
        ],
        pagination: { total: 2, total_pages: 1, page: 1, per_page: 10 }
      };

      (globalThis.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      });

      const { result } = renderHook(() => useEventsList(currentGame), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.categories).toEqual(['all']);
    });
  });
});
