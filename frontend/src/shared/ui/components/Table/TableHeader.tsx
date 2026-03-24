import { flexRender } from '@tanstack/react-table';
import React from 'react';

import { TableHeaderProps, TableColumn, RowData } from './Table.types';

/**
 * Validates and parses a width value to ensure it's a valid CSS value
 * @param width - The width value from column definition (number | string | undefined)
 * @returns A valid CSS width value (number with px, string, or 'auto')
 */
const parseWidth = (width: number | string | undefined): string => {
  // Handle undefined/null
  if (width === undefined || width === null) {
    return 'auto';
  }

  // Handle string values (e.g., '100px', '10%', 'auto')
  if (typeof width === 'string') {
    // Validate it's not an empty string
    return width.trim() !== '' ? width : 'auto';
  }

  // Handle number values
  if (typeof width === 'number') {
    // Check for invalid number values
    if (!Number.isFinite(width) || Number.isNaN(width)) {
      console.warn(`Invalid width value: ${width}. Using 'auto' instead.`);
      return 'auto';
    }

    // Check for negative values
    if (width < 0) {
      console.warn(`Negative width value: ${width}. Using 'auto' instead.`);
      return 'auto';
    }

    // Convert number to px string
    return `${width}px`;
  }

  // Fallback for any other type
  console.warn(`Unsupported width type: ${typeof width}. Using 'auto' instead.`);
  return 'auto';
};

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
export const TableHeader = React.memo(<TData extends RowData>({
  className = '',
  children,
}: TableHeaderProps) => {
  return <thead className={`table-thead ${className}`}>{children}</thead>;
}) as <TData extends RowData>(props: TableHeaderProps) => React.JSX.Element;
/**
 * TableHead Component
 * 
 * Individual table header cell with sorting and resizing support
 */
export const TableHead = React.memo(<TData extends RowData>({
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
    width: parseWidth(header.getSize()),
    left: isPinnedLeft ? parseWidth(header.getStart()) : undefined,
    right: isPinnedRight ? parseWidth(header.getTotalRight()) : undefined,
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
}) as <TData extends RowData>(props: {
  header: any;
  column: TableColumn<TData>;
  sortable?: boolean;
  onSort?: (columnId: string) => void;
  renderHeader?: (header: any) => React.ReactNode;
  className?: string;
}) => React.JSX.Element;
