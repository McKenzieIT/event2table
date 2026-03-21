import React from 'react';
import { TableCellProps, RowData } from './Table.types';

/**
 * TableCell Component
 * 
 * Renders a single table cell with support for:
 * - Custom rendering
 * - Editing
 * - Click events
 * - Double-click events
 * - Fixed columns
 * - Alignment
 */
export const TableCell = <TData extends RowData, TValue = unknown>({
  className = '',
  children,
  align = 'left',
  onClick,
  onDoubleClick,
  pinned = false,
  pinnedLeft = false,
  pinnedRight = false,
  style,
}: TableCellProps<TData, TValue>) => {
  const cellClasses = [
    'table-td',
    align && `table-td--${align}`,
    pinned && 'table-td--pinned',
    pinnedLeft && 'table-td--pinned-left',
    pinnedRight && 'table-td--pinned-right',
    className,
  ].filter(Boolean).join(' ');

  return (
    <td
      className={cellClasses}
      style={style}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
    >
      {children}
    </td>
  );
};

TableCell.displayName = 'TableCell';
