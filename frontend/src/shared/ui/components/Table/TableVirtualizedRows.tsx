import React, { useCallback } from 'react';
import { flexRender } from '@tanstack/react-table';
import { Row, RowData } from '@tanstack/react-table';
import { TableColumn, CellContext } from './Table.types';

interface TableVirtualizedRowsProps<TData extends RowData> {
  rows: Row<TData>[];
  virtualRows: any[];
  totalSize: number;
  rowVirtualizer: any;
  dynamicRowHeight: boolean;
  editable: boolean;
  editingCell: { rowIndex: number; columnId: string } | null;
  setEditingCell: React.Dispatch<React.SetStateAction<{ rowIndex: number; columnId: string } | null>>;
  renderCell: (cell: any, rowIndex: number) => React.ReactNode;
  onRowClick?: (row: TData, event: React.MouseEvent) => void;
  onRowDoubleClick?: (row: TData, event: React.MouseEvent) => void;
  onCellClick?: (cell: CellContext<TData>, event: React.MouseEvent) => void;
  onCellEdit?: (row: TData, columnId: string, value: unknown) => void;
}

/**
 * TableVirtualizedRows Component
 * 
 * Renders table rows using virtual scrolling for optimal performance
 * with large datasets. Handles:
 * - Virtualized row rendering
 * - Dynamic row height measurement
 * - Cell editing
 * - Row selection
 * - Fixed columns
 */
export const TableVirtualizedRows = React.memo(<TData extends RowData>({
  rows,
  virtualRows,
  totalSize,
  rowVirtualizer,
  dynamicRowHeight,
  editable,
  editingCell,
  setEditingCell,
  renderCell,
  onRowClick,
  onRowDoubleClick,
  onCellClick,
  onCellEdit,
}: TableVirtualizedRowsProps<TData>) => {
  const handleCellDoubleClick = useCallback((cell: any, virtualRow: any, columnDef: TableColumn<TData>) => {
    if (editable && columnDef.editable) {
      setEditingCell({
        rowIndex: virtualRow.index,
        columnId: cell.column.id,
      });
    }
  }, [editable, setEditingCell]);

  return (
    <>
      {/* Spacer for virtualized rows above viewport */}
      {virtualRows.length > 0 && virtualRows[0].start > 0 && (
        <tr style={{ height: virtualRows[0].start }} />
      )}
      {virtualRows.map((virtualRow, index) => {
        const row = rows[virtualRow.index];
        return (
          <tr
            key={row.id}
            data-index={virtualRow.index}
            data-virtualizer={index === 0 ? "true" : undefined}
            ref={dynamicRowHeight ? rowVirtualizer.measureElement : undefined}
            className={[
              'table-tr',
              'table-tr--virtual',
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
                  onDoubleClick={() => handleCellDoubleClick(cell, virtualRow, columnDef)}
                >
                  {renderCell(cell, virtualRow.index)}
                </td>
              );
            })}
          </tr>
        );
      })}
      {/* Spacer for virtualized rows below viewport */}
      {virtualRows.length > 0 && (
        <tr style={{ height: totalSize - virtualRows[virtualRows.length - 1].end }} />
      )}
    </>
  );
}) as <TData extends RowData>(props: TableVirtualizedRowsProps<TData>) => React.JSX.Element;

TableVirtualizedRows.displayName = 'TableVirtualizedRows';