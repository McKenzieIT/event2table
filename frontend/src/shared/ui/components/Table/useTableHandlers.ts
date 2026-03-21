import { useCallback } from 'react';

import type { CellContext } from './Table.types';

/**
 * Props for useTableHandlers hook
 */
export interface UseTableHandlersProps<TData> {
  /** Row click callback */
  onRowClick?: (row: TData, event: React.MouseEvent) => void;
  /** Row double click callback */
  onRowDoubleClick?: (row: TData, event: React.MouseEvent) => void;
  /** Cell click callback */
  onCellClick?: (cell: CellContext<TData>, event: React.MouseEvent) => void;
  /** Edit callback */
  onEdit?: (row: TData, columnId: string, value: unknown) => void;
}

/**
 * Result of useTableHandlers hook
 */
export interface UseTableHandlersResult<TData> {
  /** Handle row click */
  handleRowClick: (row: TData, event: React.MouseEvent) => void;
  /** Handle row double click */
  handleRowDoubleClick: (row: TData, event: React.MouseEvent) => void;
  /** Handle cell click */
  handleCellClick: (cell: CellContext<TData>, event: React.MouseEvent) => void;
  /** Handle cell edit */
  handleCellEdit: (row: TData, columnId: string, value: unknown, setEditingCell: (cell: { rowIndex: number; columnId: string } | null) => void) => void;
}

/**
 * Hook for table event handlers
 */
export function useTableHandlers<TData extends Record<string, unknown>>({
  onRowClick,
  onRowDoubleClick,
  onCellClick,
  onEdit,
}: UseTableHandlersProps<TData>): UseTableHandlersResult<TData> {
  const handleRowClick = useCallback(
    (row: TData, event: React.MouseEvent) => {
      onRowClick?.(row, event);
    },
    [onRowClick]
  );

  const handleRowDoubleClick = useCallback(
    (row: TData, event: React.MouseEvent) => {
      onRowDoubleClick?.(row, event);
    },
    [onRowDoubleClick]
  );

  const handleCellClick = useCallback(
    (cell: CellContext<TData>, event: React.MouseEvent) => {
      onCellClick?.(cell, event);
    },
    [onCellClick]
  );

  const handleCellEdit = useCallback(
    (row: TData, columnId: string, value: unknown, setEditingCell: (cell: { rowIndex: number; columnId: string } | null) => void) => {
      onEdit?.(row, columnId, value);
      setEditingCell(null);
    },
    [onEdit]
  );

  return {
    handleRowClick,
    handleRowDoubleClick,
    handleCellClick,
    handleCellEdit,
  };
}
