import React, { useCallback } from 'react';
import { Row, RowData } from '@tanstack/react-table';
import { TableColumn, CellContext } from './Table.types';

interface TableRegularRowsProps<TData extends RowData> {
  rows: Row<TData>[];
  editable: boolean;
  editingCell: { rowIndex: number; columnId: string } | null;
  setEditingCell: React.Dispatch<React.SetStateAction<{ rowIndex: number; columnId: string } | null>>;
  renderCell: (cell: any, rowIndex: number) => React.ReactNode;
  onRowClick?: (row: TData, event: React.MouseEvent) => void;
  onRowDoubleClick?: (row: TData, event: React.MouseEvent) => void;
  onCellClick?: (cell: CellContext<TData>, event: React.MouseEvent) => void;
}

/**
 * TableRegularRows Component
 * 
 * Renders table rows without virtual scrolling.
 * Handles:
 * - Regular row rendering
 * - Cell editing
 * - Row selection
 * - Fixed columns
 */
export const TableRegularRows = React.memo(<TData extends RowData>({
  rows,
  editable,
  editingCell,
  setEditingCell,
  renderCell,
  onRowClick,
  onRowDoubleClick,
  onCellClick,
}: TableRegularRowsProps<TData>) => {
  const handleCellDoubleClick = useCallback((cell: any, row: Row<TData>, columnDef: TableColumn<TData>) => {
    if (editable && columnDef.editable) {
      setEditingCell({
        rowIndex: row.index,
        columnId: cell.column.id,
      });
    }
  }, [editable, setEditingCell]);

  return (
    <>
      {rows.map((row) => (
        <tr
          key={row.id}
          className={[
            'table-tr',
            row.getIsSelected() && 'table-tr--selected',
          ].filter(Boolean).join(' ')}
          onClick={(e) => onRowClick?.(row.original, e)}
          onDoubleClick={(e) => onRowDoubleClick?.(row.original, e)}
        >
          {row.getVisibleCells().map((cell: any) => {
            const columnDef = cell.column.columnDef as TableColumn<TData>;
            const isPinnedLeft = cell.column.getIsPinned() === 'left';
            const isPinnedRight = cell.column.getIsPinned() === 'right';
            const isPinned = isPinnedLeft || isPinnedRight;

            return (
              <td
                key={cell.id}
                className={[
                  'table-td',
                  columnDef.align && `table-td--${columnDef.align}`,
                  isPinned && 'table-td--pinned',
                  isPinnedLeft && 'table-td--pinned-left',
                  isPinnedRight && 'table-td--pinned-right',
                ].filter(Boolean).join(' ')}
                style={{
                  width: cell.column.getSize(),
                  left: isPinnedLeft ? cell.column.getStart() : undefined,
                  right: isPinnedRight ? cell.column.getTotalRight() : undefined,
                }}
                onClick={(e) => onCellClick?.(cell, e)}
                onDoubleClick={() => handleCellDoubleClick(cell, row, columnDef)}
              >
                {renderCell(cell, row.index)}
              </td>
            );
          })}
        </tr>
      ))}
    </>
  );
}) as <TData extends RowData>(props: TableRegularRowsProps<TData>) => React.JSX.Element;

TableRegularRows.displayName = 'TableRegularRows';
