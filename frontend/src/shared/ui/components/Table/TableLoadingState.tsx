import React from 'react';

interface TableLoadingStateProps {
  colSpan: number;
  loadingComponent?: React.ReactNode;
}

/**
 * TableLoadingState Component
 * 
 * Displays loading state for the table
 */
export const TableLoadingState = React.memo(({
  colSpan,
  loadingComponent,
}: TableLoadingStateProps) => {
  return (
    <tr>
      <td colSpan={colSpan} className="table-loading">
        {loadingComponent || <div className="table-spinner" />}
      </td>
    </tr>
  );
}) as (props: TableLoadingStateProps) => React.JSX.Element;

TableLoadingState.displayName = 'TableLoadingState';
