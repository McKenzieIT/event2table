import React from 'react';
import { flexRender } from '@tanstack/react-table';
import { TableHeaderProps, TableColumn, RowData } from './Table.types';

/**
 * TableHeader Component
 * 
 * Renders the header section of the table with support for:
 * - Column grouping
 * - Sorting indicators
 * - Column resizing
 * - Fixed columns
 * - Custom header rendering
 */
export const TableHeader = <TData extends RowData>({
  className = '',
  children,
}: TableHeaderProps) => {
  return <thead className={`table-thead ${className}`}>{children}</thead>;
};

/**
 * TableHead Component
 * 
 * Individual table header cell with sorting and resizing support
 */
export const TableHead = <TData extends RowData>({
  header,
  column,
  sortable = false,
  onSort,
  renderHeader,
  className = '',
}: {
  header: any;
  column: TableColumn<TData>;
  sortable?: boolean;
  onSort?: (columnId: string) => void;
  renderHeader?: (header: any) => React.ReactNode;
  className?: string;
}) => {
  const columnDef = column as TableColumn<TData>;
  const isPinnedLeft = header.column.getIsPinned() === 'left';
  const isPinnedRight = header.column.getIsPinned() === 'right';
  const isPinned = isPinnedLeft || isPinnedRight;
  
  // Column grouping support
  const isGroupHeader = !header.isPlaceholder && header.colSpan > 1;
  const colSpan = header.colSpan;
  const rowSpan = header.rowSpan || 1;

  const handleClick = () => {
    if (sortable && header.column.getCanSort()) {
      onSort?.(header.column.id);
    }
  };

  const headClasses = [
    'table-th',
    columnDef.align && `table-th--${columnDef.align}`,
    header.column.getCanSort() && 'table-th--sortable',
    isPinned && 'table-th--pinned',
    isPinnedLeft && 'table-th--pinned-left',
    isPinnedRight && 'table-th--pinned-right',
    isGroupHeader && 'table-th--group',
    className,
  ].filter(Boolean).join(' ');

  const style: React.CSSProperties = {
    width: header.getSize() !== 150 ? header.getSize() : undefined,
    left: isPinnedLeft ? header.getStart() : undefined,
    right: isPinnedRight ? header.getTotalRight() : undefined,
  };

  return (
    <th
      className={headClasses}
      style={style}
      colSpan={colSpan}
      rowSpan={rowSpan}
      onClick={sortable ? handleClick : undefined}
    >
      <div className="table-th-content">
        {renderHeader ? renderHeader(header) : flexRender(column.header, header.getContext())}
        {header.column.getIsSorted() && (
          <span className="table-sort-indicator">
            {header.column.getIsSorted() === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </div>
      {!isGroupHeader && !header.isPlaceholder && (
        <div
          className="table-resizer"
          onMouseDown={header.getResizeHandler()}
          onClick={(e) => e.stopPropagation()}
        />
      )}
    </th>
  );
};

TableHead.displayName = 'TableHead';
