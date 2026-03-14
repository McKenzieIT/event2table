// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * EventSelector Component
 * 事件选择器组件
 */
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchEvents } from '@shared/api/events';
import { SearchInput, Skeleton, ErrorState } from '@shared/ui';
import type { Event } from '@shared/types/event-types';

/**
 * 组件Props接口
 */
export interface EventSelectorProps {
  gameGid: number;
  onSelect: (event: Event) => void;
  selectedEvent?: Event | null;
}

/**
 * EventSelector Component
 */
export default function EventSelector({ gameGid, onSelect, selectedEvent }: EventSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');

  console.log('[EventSelector] Component render - searchQuery:', searchQuery, 'gameGid:', gameGid);

  // 使用普通useQuery而非useInfiniteQuery，因为API返回扁平结构
  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['events', gameGid, searchQuery],
    queryFn: () => fetchEvents(gameGid, 1, searchQuery),
    enabled: !!gameGid,
  });

  console.log('[EventSelector] React Query state:', {
    isLoading,
    isError,
    hasData: !!data,
    searchQuery,
    queryKey: ['events', gameGid, searchQuery]
  });

  if (data) {
    console.log('[EventSelector] React Query data received:', {
      success: data.success,
      hasData: !!data.data,
      eventsCount: data.data?.events?.length || 0,
      firstEvent: data.data?.events?.[0]?.event_name
    });
  }

  // 显式验证：从data中提取events
  // fetchEvents返回的是完整API响应: { success: true, data: { events: [...], pagination: {...} } }
  const events = useMemo(() => {
    console.log('[EventSelector] useMemo called - data:', !!data);

    if (!data) {
      console.log('[EventSelector] useMemo: No data, returning []');
      return [];
    }

    // ✅ 主要格式：fetchEvents返回的完整API响应
    // { success: true, data: { events: [...], pagination: {...} } }
    if (data.success && data.data && Array.isArray(data.data.events)) {
      const events = data.data.events as Event[];
      console.log('[EventSelector] useMemo: Matched primary format, returning', events.length, 'events');
      console.log('[EventSelector] useMemo: First 3 events:', events.slice(0, 3).map(e => e.event_name));
      return events;
    }

    // 兼容：data是完整API响应 { data: { events: [...] } }
    if (data.data && Array.isArray(data.data.events)) {
      const events = data.data.events as Event[];
      console.log('[EventSelector] useMemo: Matched secondary format, returning', events.length, 'events');
      return events;
    }

    // 兼容：fetchEvents直接返回事件数组
    if (Array.isArray(data)) {
      console.log('[EventSelector] useMemo: Matched array format, returning', data.length, 'events');
      return data as Event[];
    }

    // 兼容：data.events 直接是数组
    if (Array.isArray(data.events)) {
      console.log('[EventSelector] useMemo: Matched data.events format, returning', data.events.length, 'events');
      return data.events as Event[];
    }

    console.warn('[EventSelector] useMemo: Unexpected data structure:', data);
    return [];
  }, [data]);

  console.log('[EventSelector] Final events array length:', events.length);

  return (
    <div className="sidebar-section glass-card-dark">
      <div className="section-header">
        <h3>
          <i className="bi bi-box-seam"></i>
                   事件选择
        </h3>
        <i className="bi bi-chevron-down toggle-icon"></i>
      </div>
      <div className="section-content">
        <div className="search-box">
          <SearchInput
            placeholder="搜索事件..."
            value={searchQuery}
            onChange={(value) => setSearchQuery(value)}
          />
        </div>
        <div className="dropdown-list">
          {isLoading && events.length === 0 ? (
            <div className="dropdown-loading">
              <Skeleton type="inline" rows={5} height={40} />
            </div>
          ) : isError ? (
            <ErrorState
              message="无法加载事件列表"
              error={error as Error}
              onRetry={refetch}
            />
          ) : events.length === 0 ? (
            <div className="dropdown-placeholder">没有找到事件</div>
          ) : (
            events.map(event => (
              <div
                key={event.id}
                data-testid={`event-item-${event.event_name}`}
                className={`dropdown-item ${selectedEvent?.id === event.id ? 'selected' : ''}`}
                onClick={() => onSelect(event)}
              >
                <span>{event.event_name_cn || event.event_name}</span>
                <small>{event.event_name}</small>
              </div>
            ))
          )}
          {isLoading && events.length > 0 && (
            <div className="dropdown-loading">加载更多...</div>
          )}
        </div>
      </div>
    </div>
  );
}
