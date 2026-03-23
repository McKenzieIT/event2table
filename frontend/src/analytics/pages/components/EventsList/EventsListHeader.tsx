import { Button } from '@shared/ui';
import React from 'react';

import { EventsListHeaderProps } from './types';

/**
 * EventsListHeader 组件
 * 页面头部，包含标题和操作按钮
 */
const EventsListHeader: React.FC<EventsListHeaderProps> = React.memo(({
  selectedCount,
  onBatchEdit,
  onBatchValidate,
  onBatchDelete,
  onCreateEvent,
  onImportEvents
}) => {
  return (
    <div className="page-header">
      <div className="header-title">
        <div className="hero-icon-box blue">
          <span>事件</span>
        </div>
        <div>
          <h1>日志事件管理</h1>
          <p>管理和配置所有日志事件</p>
        </div>
      </div>
      <div className="header-actions">
        {selectedCount > 0 && (
          <>
            <Button
              variant="outline-primary"
              onClick={onBatchEdit}
            >
              批量编辑
            </Button>
            <Button
              variant="outline-secondary"
              onClick={onBatchValidate}
            >
              批量验证
            </Button>
            <Button
              variant="danger"
              onClick={onBatchDelete}
            >
              删除选中 ({selectedCount})
            </Button>
          </>
        )}
        <Button
          variant="outline-success"
          onClick={onImportEvents}
        >
          导入Excel
        </Button>
        <Button
          variant="primary"
          onClick={onCreateEvent}
          data-testid="add-event-button"
        >
          新增事件
        </Button>
      </div>
    </div>
  );
});

EventsListHeader.displayName = 'EventsListHeader';

export default EventsListHeader;
