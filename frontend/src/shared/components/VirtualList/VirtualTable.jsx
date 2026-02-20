import React, { memo, useMemo } from 'react';
import { VirtualList } from './VirtualList';
import './VirtualTable.css';

/**
 * 虚拟滚动表格组件
 * 
 * @param {Array} items - 数据项数组
 * @param {Array} columns - 列配置 [{key, header, width, render}]
 * @param {number} rowHeight - 行高（默认60px）
 * @param {boolean} isLoading - 是否加载中
 * @param {string} className - 表格类名
 * @param {Function} onRowClick - 行点击事件
 * @param {Function} onRowSelect - 行选择事件
 * @param {Array} selectedIds - 选中的ID数组
 */
const VirtualTable = memo(({
  items = [],
  columns = [],
  rowHeight = 60,
  isLoading = false,
  className = '',
  onRowClick,
  onRowSelect,
  selectedIds = [],
  ...props
}) => {
  // 渲染表头
  const renderHeader = useMemo(() => (
    <div className="virtual-table-header">
      {columns.map(col => (
        <div
          key={col.key}
          className="virtual-table-cell"
          style={{ width: col.width || 'auto' }}
        >
          {col.header}
        </div>
      ))}
    </div>
  ), [columns]);

  // 渲染每一行
  const renderRow = useMemo(() => (item, index) => {
    const isSelected = selectedIds.includes(item.id);
    
    return (
      <div
        className={`virtual-table-row ${isSelected ? 'selected' : ''}`}
        onClick={() => onRowClick?.(item)}
        style={{ height: `${rowHeight}px` }}
      >
        {columns.map(col => (
          <div
            key={col.key}
            className="virtual-table-cell"
            style={{ width: col.width || 'auto' }}
          >
            {col.render ? col.render(item, index) : item[col.key]}
          </div>
        ))}
      </div>
    );
  }, [columns, selectedIds, onRowClick, rowHeight]);

  // 骨架屏
  const skeleton = useMemo(() => (
    <div className="virtual-table-skeleton">
      {renderHeader}
      {Array.from({ length: 10 }).map((_, i) => (
        <div
          key={i}
          className="skeleton-row"
          style={{ height: `${rowHeight}px` }}
        >
          {columns.map(col => (
            <div
              key={col.key}
              className="skeleton-cell skeleton-animate"
              style={{ width: col.width || 'auto' }}
            />
          ))}
        </div>
      ))}
    </div>
  ), [renderHeader, columns, rowHeight]);

  return (
    <div className={`virtual-table-wrapper ${className}`}>
      {renderHeader}
      <VirtualList
        items={items}
        renderItem={renderRow}
        estimateSize={rowHeight}
        isLoading={isLoading}
        skeleton={skeleton}
        {...props}
      />
    </div>
  );
});

VirtualTable.displayName = 'VirtualTable';

export default VirtualTable;
