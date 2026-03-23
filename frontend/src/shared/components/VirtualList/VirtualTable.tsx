// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { memo, useMemo, ReactNode } from 'react';

import { VirtualList } from './VirtualList';
import './VirtualTable.css';

/**
 * 虚拟滚动表格组件
 *
 * @param items - 数据项数组
 * @param columns - 列配置 [{key, header, width, render}]
 * @param rowHeight - 行高（默认60px）
 * @param isLoading - 是否加载中
 * @param className - 表格类名
 * @param onRowClick - 行点击事件
 * @param onRowSelect - 行选择事件
 * @param selectedIds - 选中的ID数组
 */

export interface ColumnConfig<T> {
  key: string;
  header: string;
  width?: string | number;
  render?: (item: T, index: number) => ReactNode;
}

export interface VirtualTableProps<T> {
  items: T[];
  columns: ColumnConfig<T>[];
  rowHeight?: number;
  isLoading?: boolean;
  className?: string;
  onRowClick?: (item: T) => void;
  onRowSelect?: (item: T) => void;
  selectedIds?: (string | number)[];
}

const VirtualTable = memo(<T extends { id: string | number }>({
  items = [],
  columns = [],
  rowHeight = 60,
  isLoading = false,
  className = '',
  onRowClick,
  onRowSelect,
  selectedIds = [],
  ...props
}: VirtualTableProps<T>) => {
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
  const renderRow = useMemo(() => (item: T, index: number) => {
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
            {col.render ? col.render(item, index) : (item[col.key as keyof T] as ReactNode)}
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
}) as <T extends { id: string | number }>(props: VirtualTableProps<T>) => React.JSX.Element;

VirtualTable.displayName = 'VirtualTable';

export default VirtualTable;
