/**
 * Cyberpunk Lab Theme - Table Component
 *
 * Glassmorphism table with subtle hover states and striped rows
 * Optimized with React.memo and functional setState patterns
 */

import React from 'react';
import './Table.css';

const Table = React.forwardRef(({
  children,
  className = '',
  variant = 'default',      // default, bordered, compact
  striped = true,           // Zebra striping
  hoverable = true,         // Row hover effect (subtle)
  size = 'md',              // sm, md, lg
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

// Memoized sub-components
MemoizedTable.Header = React.memo(function TableHeader({ children, className = '', ...props }) {
  return <thead className={['cyber-table__header', className].filter(Boolean).join(' ')} {...props}>{children}</thead>;
});

MemoizedTable.Body = React.memo(function TableBody({ children, className = '', ...props }) {
  return <tbody className={['cyber-table__body', className].filter(Boolean).join(' ')} {...props}>{children}</tbody>;
});

MemoizedTable.Footer = React.memo(function TableFooter({ children, className = '', ...props }) {
  return <tfoot className={['cyber-table__footer', className].filter(Boolean).join(' ')} {...props}>{children}</tfoot>;
});

MemoizedTable.Row = React.memo(function TableRow({ children, className = '', onClick, ...props }) {
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
MemoizedTable.Head = React.memo(function TableHead({
  children,
  className = '',
  align = 'left',
  sortable = false,
  sorted = null,
  onSort,
  ...props
}) {
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

MemoizedTable.Cell = React.memo(function TableCell({ children, className = '', align = 'left', ...props }) {
  return (
    <td className={['cyber-table__cell', `cyber-table__cell--${align}`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </td>
  );
});

export default MemoizedTable;
