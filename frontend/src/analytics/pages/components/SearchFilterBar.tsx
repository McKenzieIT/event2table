import { useDebounce } from "@shared/hooks/useDebounce";
import type { EventNodeFilters } from "@shared/types/eventNodes";
import { Button } from "@shared/ui";
import React, { useState, useEffect, useCallback } from "react";

/**
 * 搜索和筛选栏组件
 * 提供基础搜索和高级筛选入口
 */
function SearchFilterBar({
  filters,
  updateFilters,
  selectedCount,
  onClearSelection,
  onBulkDelete,
  onToggleAdvanced,
  showAdvanced,
}: {
  filters: EventNodeFilters;
  updateFilters: (updates: Partial<EventNodeFilters>) => void;
  selectedCount: number;
  onClearSelection: () => void;
  onBulkDelete: () => void;
  onToggleAdvanced: () => void;
  showAdvanced: boolean;
}) {
  const [input, setInput] = useState(filters.keyword);
  const debouncedInput = useDebounce(input, 300);

  useEffect(() => {
    updateFilters({ keyword: debouncedInput });
  }, [debouncedInput, updateFilters]);

  return (
    <div className="glass-card filter-bar">
      <div className="filter-bar__main">
        {/* 基础搜索 */}
        <div className="search-input-wrapper">
          <i className="bi bi-search search-icon"></i>
          <input
            type="text"
            className="input-cyber"
            placeholder="搜索节点名称、别名..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
        </div>

        {/* 右侧操作区 */}
        <div className="filter-actions">
          {selectedCount > 0 && (
            <div className="bulk-actions">
              <span className="selection-count">
                已选择 <strong>{selectedCount}</strong> 个节点
              </span>
              <Button variant="outline-danger" onClick={onBulkDelete}>
                <i className="bi bi-trash me-2"></i>
                批量删除
              </Button>
            </div>
          )}
          <Button
            variant={showAdvanced ? "primary" : "outline-primary"}
            onClick={onToggleAdvanced}
          >
            <i className="bi bi-funnel me-2"></i>
            高级筛选
            {showAdvanced ? <i className="bi bi-chevron-up ms-2"></i> : <i className="bi bi-chevron-down ms-2"></i>}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default React.memo(SearchFilterBar);
