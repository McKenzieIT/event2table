// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Cyberpunk Lab Theme - Table Component
 *
 * Glassmorphism table with subtle hover states and striped rows
 * Optimized with React.memo and functional setState patterns
 * 
 * @deprecated Use Table from '@/shared/ui/components/Table' instead.
 * Will be removed in v3.0.0
 */

import React from 'react';
import './Table.css';

type TableVariant = 'default' | 'bordered' | 'compact';
type TableSize = 'sm' | 'md' | 'lg';
type TextAlign = 'left' | 'center' | 'right';
type SortDirection = 'asc' | 'desc' | null;

interface BaseTableProps {
  children: React.ReactNode;
  className?: string;
}

interface TableProps extends BaseTableProps {
  variant?: TableVariant;
  striped?: boolean;
  hoverable?: boolean;
  size?: TableSize;
}

interface TableHeadProps extends BaseTableProps {
  align?: TextAlign;
  sortable?: boolean;
  sorted?: SortDirection;
  onSort?: (prevSort: SortDirection) => SortDirection | void;
}

interface TableCellProps extends BaseTableProps {
  align?: TextAlign;
}

interface TableRowProps extends BaseTableProps {
  onClick?: () => void;
}

const Table = React.forwardRef<HTMLTableElement, TableProps & React.HTMLAttributes<HTMLTableElement>>(({
  children,
  className = '',
  variant = 'default',
  striped = true,
  hoverable = true,
  size = 'md',
  ...props
}, ref) => {
  const tableClass = [
    'cyber-table',
    `cyber-table--${variant}`,
    `cyber-table--${size}`,
    striped && 'cyber-table--striped',
    hoverable && 'cyber-table--hoverable',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="cyber-table-wrapper">
      <table ref={ref} className={tableClass} {...props}>
        {children}
      </table>
    </div>
  );
});

Table.displayName = 'Table';

// Memoize Table component
const MemoizedTable = React.memo(Table, (prevProps, nextProps) => {
  return (
    prevProps.variant === nextProps.variant &&
    prevProps.striped === nextProps.striped &&
    prevProps.hoverable === nextProps.hoverable &&
    prevProps.size === nextProps.size &&
    prevProps.className === nextProps.className &&
    prevProps.children === nextProps.children
  );
});

MemoizedTable.displayName = 'MemoizedTable';

// Define sub-components separately
const TableHeader = React.memo(function TableHeader({ children, className = '', ...props }: BaseTableProps & React.HTMLAttributes<HTMLTableSectionElement>) {
  return <thead className={['cyber-table__header', className].filter(Boolean).join(' ')} {...props}>{children}</thead>;
});

const TableBody = React.memo(function TableBody({ children, className = '', ...props }: BaseTableProps & React.HTMLAttributes<HTMLTableSectionElement>) {
  return <tbody className={['cyber-table__body', className].filter(Boolean).join(' ')} {...props}>{children}</tbody>;
});

const TableFooter = React.memo(function TableFooter({ children, className = '', ...props }: BaseTableProps & React.HTMLAttributes<HTMLTableSectionElement>) {
  return <tfoot className={['cyber-table__footer', className].filter(Boolean).join(' ')} {...props}>{children}</tfoot>;
});

const TableRow = React.memo(function TableRow({ children, className = '', onClick, ...props }: TableRowProps & React.HTMLAttributes<HTMLTableRowElement>) {
  const rowClass = [
    'cyber-table__row',
    onClick && 'cyber-table__row--clickable',
    className
  ].filter(Boolean).join(' ');

  return (
    <tr className={rowClass} onClick={onClick} {...props}>
      {children}
    </tr>
  );
});

// Optimize Table.Head with useCallback-like pattern for stable handlers
const TableHead = React.memo(function TableHead({
  children,
  className = '',
  align = 'left',
  sortable = false,
  sorted = null,
  onSort,
  ...props
}: TableHeadProps & React.HTMLAttributes<HTMLTableCellElement>) {
  // Use functional update pattern for sort state (rerender-functional-setstate)
  // This prevents creating new functions on every render
  const handleClick = React.useCallback(() => {
    if (sortable && onSort) {
      // Functional setState pattern - more stable
      onSort((prevSort) => {
        if (prevSort === 'asc') return 'desc';
        if (prevSort === 'desc') return null;
        return 'asc';
      });
    }
  }, [sortable, onSort]);

  const headClass = [
    'cyber-table__head',
    `cyber-table__head--${align}`,
    sortable && 'cyber-table__head--sortable',
    sorted === 'asc' && 'cyber-table__head--sorted-asc',
    sorted === 'desc' && 'cyber-table__head--sorted-desc',
    className
  ].filter(Boolean).join(' ');

  return (
    <th className={headClass} onClick={handleClick} {...props}>
      <div className="cyber-table__head-content">
        <span>{children}</span>
        {sortable && (
          <span className="cyber-table__sort-indicator">
            {sorted === 'asc' && '↑'}
            {sorted === 'desc' && '↓'}
            {!sorted && '↕'}
          </span>
        )}
      </div>
    </th>
  );
});

const TableCell = React.memo(function TableCell({ children, className = '', align = 'left', ...props }: TableCellProps & React.HTMLAttributes<HTMLTableCellElement>) {
  return (
    <td className={['cyber-table__cell', `cyber-table__cell--${align}`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </td>
  );
});

// Define TableWithSubComponents type
interface TableWithSubComponents extends React.MemoExoticComponent<React.ForwardRefExoticComponent<TableProps & React.HTMLAttributes<HTMLTableElement> & React.RefAttributes<HTMLTableElement>>> {
  Header: typeof TableHeader;
  Body: typeof TableBody;
  Footer: typeof TableFooter;
  Row: typeof TableRow;
  Head: typeof TableHead;
  Cell: typeof TableCell;
}

// Cast to properly typed component and attach sub-components
const TableComponent = MemoizedTable as TableWithSubComponents;
TableComponent.Header = TableHeader;
TableComponent.Body = TableBody;
TableComponent.Footer = TableFooter;
TableComponent.Row = TableRow;
TableComponent.Head = TableHead;
TableComponent.Cell = TableCell;

export type { TableProps, TableHeadProps, TableCellProps, TableRowProps, SortDirection, TableVariant, TableSize, TextAlign };
export default TableComponent;
