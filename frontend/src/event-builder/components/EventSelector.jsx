/**
 * EventSelector Component
 * 事件选择器组件
 */
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchEvents } from '@shared/api/eventNodeBuilderApi';
import { SearchInput } from '@shared/ui';

export default function EventSelector({ gameGid, onSelect, selectedEvent }) {
  const [searchQuery, setSearchQuery] = useState('');

  // 使用普通useQuery而非useInfiniteQuery，因为API返回扁平结构
  const {
    data,
    isLoading,
  } = useQuery({
    queryKey: ['events', gameGid, searchQuery],
    queryFn: () => fetchEvents(gameGid, 1, searchQuery),
    enabled: !!gameGid,
  });

  // 显式验证：从data中提取events
  // fetchEvents返回的是事件数组，不是完整API响应
  const events = useMemo(() => {
    if (!data) {
      return [];
    }

    // fetchEvents函数直接返回事件数组: [{ id, event_name, event_name_cn }, ...]
    if (Array.isArray(data)) {
      return data;
    }

    // 兼容：data是完整API响应 { data: { events: [...] } }
    if (data.data && Array.isArray(data.data.events)) {
      return data.data.events;
    }

    // 兼容：带success的格式 { success: true, data: { events: [...] } }
    if (data.success && data.data && Array.isArray(data.data.events)) {
      return data.data.events;
    }

    // 兼容：data.events 直接是数组
    if (Array.isArray(data.events)) {
      return data.events;
    }

    console.warn('[EventSelector] Unexpected data structure:', data);
    return [];
  }, [data]);

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
            <div className="dropdown-loading">加载中...</div>
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
