import { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@shared/ui';
import {
  EventData,
  EventsListResponse,
  PaginationInfo,
  PlaceholderData,
  LayoutContext
} from './types';

/** 占位数据 - 当没有选择游戏时使用 */
const placeholderData: PlaceholderData = {
  events: [],
  pagination: { total: 0, total_pages: 1, page: 1, per_page: 10 }
};

/**
 * 自定义 Hook：管理事件列表的状态和数据获取
 */
export function useEventsList(currentGame: LayoutContext['currentGame']) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { success, error: showError } = useToast();

  // ========== 状态管理 ==========

  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedEvents, setSelectedEvents] = useState<number[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  // ========== 游戏上下文检查 ==========

  const hasGameContext = !!currentGame;

  // ========== 数据获取 ==========

  const { data, isLoading, error: fetchError } = useQuery<EventsListResponse>({
    queryKey: ['events', currentPage, pageSize, selectedCategory, currentGame?.gid, searchTerm],
    queryFn: async () => {
      // 守卫：如果没有游戏上下文，返回占位数据
      if (!currentGame?.gid) {
        return placeholderData as EventsListResponse;
      }

      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: pageSize.toString(),
        game_gid: currentGame.gid.toString()
      });

      if (searchTerm) {
        params.append('search', searchTerm);
      }

      const response = await fetch(`/api/events?${params.toString()}`);
      if (!response.ok) throw new Error('Failed to fetch events');
      const result = await response.json();

      if (!result?.success) {
        throw new Error(result?.message || 'Failed to fetch events');
      }

      return result.data || placeholderData;
    },
    enabled: hasGameContext
  });

  // 当没有游戏上下文时使用占位数据
  const effectiveData: EventsListResponse = hasGameContext ? (data || placeholderData) : placeholderData;

  // ========== Mutations ==========

  const deleteMutation = useMutation({
    mutationFn: async (eventIds: number[]) => {
      const response = await fetch('/api/events/batch', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: eventIds })
      });
      if (!response.ok) throw new Error('Failed to delete events');
      return response.json();
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({
        queryKey: ['events', currentGame?.gid]
      });
      setSelectedEvents([]);
      const deletedCount = data?.data?.deleted_count ?? data?.deleted_count ?? 0;
      success(`成功删除 ${deletedCount} 个事件`);
    },
    onError: (err: Error) => {
      showError(`删除失败: ${err.message}`);
    }
  });

  // ========== 计算属性 ==========

  const filteredEvents = useMemo<EventData[]>(() => {
    const events = effectiveData?.events;
    if (!Array.isArray(events)) {
      return [];
    }

    const filtered = events.filter(event => {
      const matchesCategory = selectedCategory === 'all' ||
        event.category_name?.toLowerCase() === selectedCategory.toLowerCase();
      return matchesCategory;
    });

    return filtered;
  }, [effectiveData, selectedCategory]);

  const categories = useMemo<string[]>(() => {
    const events = effectiveData?.events;
    if (!Array.isArray(events)) {
      return ['all'];
    }

    const uniqueCategories = Array.from(new Set(events.map(e => e.category_name).filter((c): c is string => Boolean(c))));
    return ['all', ...uniqueCategories];
  }, [effectiveData]);

  const pagination: PaginationInfo = effectiveData?.pagination || { total: 0, total_pages: 1, page: 1, per_page: 10 };
  const totalPages = pagination.total_pages || 1;
  const total = pagination.total || 0;

  // ========== 事件处理器 ==========

  const handleViewEvent = useCallback((eventId: number) => {
    navigate(`/events/${eventId}?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  const handleEditEvent = useCallback((eventId: number) => {
    navigate(`/events/${eventId}/edit?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  const handleSearchChange = useCallback((value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  }, []);

  const handleToggleSelect = useCallback((eventId: number) => {
    setSelectedEvents(prev => {
      if (prev.includes(eventId)) {
        return prev.filter(id => id !== eventId);
      } else {
        return [...prev, eventId];
      }
    });
  }, []);

  const handleSelectAll = useCallback(() => {
    setSelectedEvents(prev => {
      if (prev.length === filteredEvents.length) {
        return [];
      } else {
        return filteredEvents.map(e => e.id);
      }
    });
  }, [filteredEvents]);

  const handleBatchDelete = useCallback(() => {
    if (selectedEvents.length === 0) {
      showError('请先选择要删除的事件');
      return;
    }
    deleteMutation.mutate(selectedEvents);
  }, [selectedEvents, deleteMutation, showError]);

  const handleDeleteEvent = useCallback((eventId: number, eventName: string) => {
    deleteMutation.mutate([eventId]);
  }, [deleteMutation]);

  const handleClearSelection = useCallback(() => {
    setSelectedEvents([]);
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
    navigate(`?page=${page}&per_page=${pageSize}`);
  }, [navigate, pageSize]);

  const handlePageSizeChange = useCallback((size: number) => {
    setPageSize(size);
    setCurrentPage(1);
    navigate(`?page=1&per_page=${size}`);
  }, [navigate]);

  return {
    // State
    searchTerm,
    selectedCategory,
    selectedEvents,
    currentPage,
    pageSize,
    hasGameContext,
    isLoading,
    fetchError,
    
    // Data
    filteredEvents,
    categories,
    pagination,
    totalPages,
    total,
    effectiveData,
    
    // Handlers
    handleViewEvent,
    handleEditEvent,
    handleSearchChange,
    handleToggleSelect,
    handleSelectAll,
    handleBatchDelete,
    handleDeleteEvent,
    handleClearSelection,
    handlePageChange,
    handlePageSizeChange,
    setSelectedCategory,
    
    // Mutations
    deleteMutation
  };
}
