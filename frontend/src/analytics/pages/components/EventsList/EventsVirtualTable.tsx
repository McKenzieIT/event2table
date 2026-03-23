import { Button, Checkbox, Badge, Spinner, EmptyState } from '@shared/ui';
import React from 'react';

import { EventData, EventsVirtualTableProps } from './types';

import OptimizedVirtualList from '@/shared/components/VirtualList/OptimizedVirtualList';


/**
 * EventsVirtualTable 组件
 * 虚拟表格，使用虚拟滚动优化大量数据的渲染性能
 */
const EventsVirtualTable: React.FC<EventsVirtualTableProps> = React.memo(({
  events,
  selectedEvents,
  onToggleSelect,
  onViewEvent,
  onEditEvent,
  onDeleteEvent,
  isLoading
}) => {
  if (isLoading) {
    return (
      <div className="loading-state">
        <Spinner size="lg" label="正在加载事件列表..." />
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <EmptyState
        icon={<i className="bi bi-inbox" style={{ fontSize: '48px' }} />}
        title="暂无日志事件"
        description="暂无事件，请先创建事件。"
      />
    );
  }

  return (
    <div className="events-table-container glass-card">
      {/* Table Header */}
      <div className="virtual-table-header">
        <div className="table-row">
          <div className="table-cell" style={{ width: '50px' }}>
            <Checkbox
              checked={selectedEvents.length === events.length && events.length > 0}
              onChange={() => {
                // 全选逻辑由父组件处理
              }}
            />
          </div>
          <div className="table-cell" style={{ width: '70px' }}>ID</div>
          <div className="table-cell" style={{ width: '25%' }}>事件名称</div>
          <div className="table-cell" style={{ width: '20%' }}>游戏</div>
          <div className="table-cell" style={{ width: '120px' }}>分类</div>
          <div className="table-cell" style={{ width: '80px' }}>参数</div>
          <div className="table-cell" style={{ width: '220px' }}>操作</div>
        </div>
      </div>

      {/* Virtual List */}
      <OptimizedVirtualList
        items={events}
        renderItem={(event: EventData) => (
          <div className={`table-row ${selectedEvents.includes(event.id) ? 'selected' : ''}`}>
            <div className="table-cell" style={{ textAlign: 'center' }}>
              <Checkbox
                checked={selectedEvents.includes(event.id)}
                onChange={() => onToggleSelect(event.id)}
              />
            </div>
            <div className="table-cell text-muted">#{event.id}</div>
            <div className="table-cell">
              <div>
                <div className="event-name">{event.event_name}</div>
                <div className="event-name-cn">{event.event_name_cn}</div>
              </div>
            </div>
            <div className="table-cell">
              <div className="game-info">
                <span>{event.game_name} ({event.gid})</span>
              </div>
            </div>
            <div className="table-cell">
              {event.category_name ? (
                <Badge variant="info">
                  {event.category_name}
                </Badge>
              ) : (
                <Badge variant="secondary">
                  未分类
                </Badge>
              )}
            </div>
            <div className="table-cell" style={{ textAlign: 'center' }}>
              <Badge variant="primary">
                {event.param_count !== undefined ? event.param_count : '-'}
              </Badge>
            </div>
            <div className="table-cell">
              <div className="action-buttons">
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => onViewEvent(event.id)}
                  title="查看事件详情"
                >
                  查看
                </Button>
                <Button
                  variant="outline-secondary"
                  size="sm"
                  onClick={() => onEditEvent(event.id)}
                  title="编辑事件"
                >
                  编辑
                </Button>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => onDeleteEvent(event.id, event.event_name_cn || event.event_name)}
                  title="删除事件"
                >
                  删除
                </Button>
              </div>
            </div>
          </div>
        )}
        itemHeight={80}
        height={600}
        overscan={5}
        className="virtual-table-body"
      />
    </div>
  );
});

EventsVirtualTable.displayName = 'EventsVirtualTable';

export default EventsVirtualTable;
