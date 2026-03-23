import { SearchInput, Button, Checkbox, Badge } from '@shared/ui';
import React from 'react';

import { EventsFiltersProps } from './types';

/**
 * EventsFilters 组件
 * 筛选栏，包含搜索框和选择操作
 */
const EventsFilters: React.FC<EventsFiltersProps> = React.memo(({
  searchTerm,
  onSearchChange,
  selectedCount,
  totalCount,
  onSelectAll,
  onClearSelection
}) => {
  return (
    <div className="filters-bar">
      <SearchInput
        placeholder="搜索事件名、中文名或分类..."
        value={searchTerm}
        onChange={onSearchChange}
      />

      <div className="filter-actions">
        <label className="select-all-label">
          <Checkbox
            checked={selectedCount === totalCount && totalCount > 0}
            onChange={onSelectAll}
          />
          <Badge variant="primary">全选</Badge>
        </label>

        {selectedCount > 0 && (
          <>
            <div className="divider"></div>
            <span className="selected-count">
              已选择 <strong>{selectedCount}</strong> 个事件
            </span>
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={onClearSelection}
            >
              取消选择
            </Button>
          </>
        )}
      </div>
    </div>
  );
});

EventsFilters.displayName = 'EventsFilters';

export default EventsFilters;
