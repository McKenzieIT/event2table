import React from 'react';

interface TableEmptyStateProps {
  colSpan: number;
  emptyComponent?: React.ReactNode;
}

/**
 * TableEmptyState Component
 * 
 * Displays empty state for the table
 */
export const TableEmptyState = React.memo(({
  colSpan,
  emptyComponent,
}: TableEmptyStateProps) => {
  return (
    <tr>
      <td colSpan={colSpan} className="table-empty">
        {emptyComponent || <div className="table-empty-message">No data available</div>}
      </td>
    </tr>
  );
}) as (props: TableEmptyStateProps) => React.JSX.Element;

TableEmptyState.displayName = 'TableEmptyState';
