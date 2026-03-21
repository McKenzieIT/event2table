import React from 'react';
import { TableRowProps, RowData } from './Table.types';

/**
 * TableRow Component
 * 
 * Renders a single table row with support for:
 * - Selection
 * - Click events
 * - Double-click events
 * - Virtual scrolling
 * - Fixed columns
 */
export const TableRow = <TData extends RowData>({
  className = '',
  children,
  onClick,
  onDoubleClick,
  selected = false,
  virtual = false,
  dataIndex,
}: TableRowProps<TData>) => {
  const rowClasses = [
    'table-tr',
    virtual && 'table-tr--virtual',
    selected && 'table-tr--selected',
    className,
  ].filter(Boolean).join(' ');

  return (
    <tr
      className={rowClasses}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
      data-index={dataIndex}
    >
      {children}
    </tr>
  );
};

TableRow.displayName = 'TableRow';
