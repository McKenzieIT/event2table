import React from 'react';

/**
 * Props for TableFooter component
 */
export interface TableFooterProps {
  /** Table footer class name */
  className?: string;
  /** Footer content */
  children?: React.ReactNode;
}

/**
 * TableFooter Component
 */
export const TableFooter: React.FC<TableFooterProps> = ({
  className = '',
  children,
}) => {
  return (
    <tfoot className={className}>
      {children && (
        <tr>
          <td colSpan={100}>{children}</td>
        </tr>
      )}
    </tfoot>
  );
};

TableFooter.displayName = 'TableFooter';
