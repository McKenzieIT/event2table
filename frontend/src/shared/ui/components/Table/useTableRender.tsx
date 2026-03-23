import { flexRender } from '@tanstack/react-table';
import { useCallback } from 'react';

import type { TableColumn, CellContext } from './Table.types';

/**
 * Props for useTableRender hook
 */
export interface UseTableRenderProps<TData> {
  /** Enable editing */
  editable: boolean;
  /** Edit callback */
  onEdit?: (row: TData, columnId: string, value: unknown) => void;
}

/**
 * Result of useTableRender hook
 */
export interface UseTableRenderResult<TData> {
  /** Render cell */
  renderCell: (cell: any, rowIndex: number, editingCell: { rowIndex: number; columnId: string } | null, setEditingCell: (cell: { rowIndex: number; columnId: string } | null) => void) => React.ReactNode;
  /** Render header */
  renderHeader: (header: any) => React.ReactNode;
}

/**
 * Hook for table rendering helpers
 */
export function useTableRender<TData extends Record<string, unknown>>({
  editable,
  onEdit,
}: UseTableRenderProps<TData>): UseTableRenderResult<TData> {
  const renderCell = useCallback(
    (cell: any, rowIndex: number, editingCell: { rowIndex: number; columnId: string } | null, setEditingCell: (cell: { rowIndex: number; columnId: string } | null) => void) => {
      const column = cell.column;
      const isEditing = editingCell?.rowIndex === rowIndex && editingCell?.columnId === column.id;
      const columnDef = column.columnDef as TableColumn<TData>;

      if (editable && columnDef.editable && isEditing) {
        return (
          <div className="table-cell-edit">
            {columnDef.editComponent ? (
              columnDef.editComponent({
                value: cell.getValue(),
                row: cell.row,
                column,
                onChange: (value) => cell.setValue(value),
                onSave: () => {
                  onEdit?.(cell.row.original, column.id, cell.getValue());
                  setEditingCell(null);
                },
                onCancel: () => setEditingCell(null),
              })
            ) : (
              <input
                type="text"
                defaultValue={cell.getValue() as string}
                onBlur={() => {
                  onEdit?.(cell.row.original, column.id, cell.getValue());
                  setEditingCell(null);
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    onEdit?.(cell.row.original, column.id, cell.getValue());
                    setEditingCell(null);
                  } else if (e.key === 'Escape') {
                    setEditingCell(null);
                  }
                }}
                autoFocus
                className="table-input"
              />
            )}
          </div>
        );
      }

      if (columnDef.cellRenderer) {
        return columnDef.cellRenderer({
          cell,
          row: cell.row,
          column,
          value: cell.getValue(),
        });
      }

      return flexRender(column.columnDef.cell, cell.getContext());
    },
    [editable, onEdit]
  );

  const renderHeader = useCallback(
    (header: any) => {
      const column = header.column;
      const columnDef = column.columnDef as TableColumn<TData>;

      if (columnDef.headerRenderer) {
        return columnDef.headerRenderer({
          column,
          header: columnDef.header || '',
        });
      }

      return flexRender(column.columnDef.header, header.getContext());
    },
    []
  );

  return {
    renderCell,
    renderHeader,
  };
}
