/**
 * Unified Table Component - Powered by TanStack Table
 * 
 * A high-performance, feature-rich table component that replaces multiple
 * existing table implementations with a unified API.
 * 
 * Key Features:
 * - TanStack Table for optimal performance
 * - Virtual scrolling for large datasets
 * - Column pinning (left/right fixed columns)
 * - Editable cells with custom components
 * - Advanced sorting and filtering
 * - Row selection with multi-select support
 * - Responsive design with theme customization
 */

import React, { 
  useMemo, 
  useCallback, 
  useState, 
  useRef, 
  useEffect,
  forwardRef 
} from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  ColumnFiltersState,
  SortingState,
  PaginationState,
  RowSelectionState,
  ColumnPinningState,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import type {
  TableProps,
  TableColumn,
  CellContext,
  TableHeaderProps,
  TableBodyProps,
  TableFooterProps,
  TableRowProps,
  TableCellProps,
  TableHeadProps,
  PaginationProps,
  VirtualScrollMetrics,
} from './Table.types';
import { TableHeader } from './TableHeader';
import { TableBody } from './TableBody';
import { TableFooter } from './TableFooter';
import { TablePagination } from './TablePagination';
import { TableRow } from './TableRow';
import { TableCell } from './TableCell';
import { TableFilter } from './TableFilter';
import { TableSort } from './TableSort';
import { useTableVirtualScroll } from './useTableVirtualScroll';
import { useTableHandlers } from './useTableHandlers';
import { useTableRender } from './useTableRender';
import { TableVirtualizedRows } from './TableVirtualizedRows';
import { TableRegularRows } from './TableRegularRows';
import { TableLoadingState } from './TableLoadingState';
import { TableEmptyState } from './TableEmptyState';
import './Table.css';

// ============================================================================
// Main Table Component
// ============================================================================
// ============================================================================
// Main Table Component
// ============================================================================

const Table = React.memo(<TData extends object = any>({
  data,
  columns,
  variant = 'default',
  size = 'md',
  striped = true,
  hoverable = true,
  bordered = false,
  selectable = false,
  onSelectionChange,
  initialSelectedIds = [],
  sortable = true,
  onSortChange,
  initialSorting = [],
  filterable = true,
  onFilterChange,
  initialFilters = [],
  pagination = true,
  pageSize = 10,
  currentPage = 1,
  onPageChange,
  pageSizeOptions = [10, 20, 50, 100],
  virtual = false,
  rowHeight = 50,
  maxHeight = 600,
  overscan = 10,
  dynamicRowHeight = false,
  onVirtualScrollMetrics,
  editable = false,
  onEdit,
  onRowClick,
  onRowDoubleClick,
  onCellClick,
  loading = false,
  loadingComponent,
  empty = false,
  emptyComponent,
  className = '',
  style,
  tableClassName = '',
  headerClassName = '',
  bodyClassName = '',
  theme = 'light',
}: TableProps<TData>) => {
  // ============================================================================
  // State Management
  // ============================================================================

  const [sorting, setSorting] = useState<SortingState>(initialSorting);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>(initialFilters);
  const [rowSelection, setRowSelection] = useState<RowSelectionState>(() => {
    const selection: RowSelectionState = {};
    initialSelectedIds.forEach((id) => {
      selection[String(id)] = true;
    });
    return selection;
  });
  const [columnPinning, setColumnPinning] = useState<ColumnPinningState>({ left: [], right: [] });
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: currentPage - 1,
    pageSize,
  });
  const [editingCell, setEditingCell] = useState<{ rowIndex: number; columnId: string } | null>(null);

  // ============================================================================
  // Column Definition
  // ============================================================================

  const tableColumns = useMemo(() => {
    const cols: TableColumn<TData>[] = [...columns];

    // Add selection column if selectable
    if (selectable) {
      cols.unshift({
        id: 'select',
        header: ({ table }) => (
          <input
            type="checkbox"
            checked={table.getIsAllRowsSelected()}
            onChange={table.getToggleAllRowsSelectedHandler()}
            className="table-checkbox"
            aria-label="Select all rows"
          />
        ),
        cell: ({ row }) => (
          <input
            type="checkbox"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
            className="table-checkbox"
            aria-label={`Select row ${row.index + 1}`}
          />
        ),
        enableSorting: false,
        enableFiltering: false,
        size: 40,
      } as TableColumn<TData>);
    }

    return cols.map((col) => ({
      ...col,
      enableSorting: col.sortable !== false && sortable,
      enableFiltering: col.filterable !== false && filterable,
      size: col.width || 'auto',
      minSize: col.minWidth || 40,
      maxSize: col.maxWidth || 1000,
    }));
  }, [columns, selectable, sortable, filterable]);

  // ============================================================================
  // Table Instance
  // ============================================================================

  const table = useReactTable({
    data,
    columns: tableColumns,
    state: {
      sorting,
      columnFilters,
      rowSelection,
      columnPinning,
      pagination: paginationState,
    },
    onSortingChange: (updater) => {
      const newSorting = typeof updater === 'function' ? updater(sorting) : updater;
      setSorting(newSorting);
      onSortChange?.(newSorting);
    },
    onColumnFiltersChange: (updater) => {
      const newFilters = typeof updater === 'function' ? updater(columnFilters) : updater;
      setColumnFilters(newFilters);
      onFilterChange?.(newFilters as unknown as Record<string, unknown>);
    },
    onRowSelectionChange: (updater) => {
      const newSelection = typeof updater === 'function' ? updater(rowSelection) : updater;
      setRowSelection(newSelection);
      
      // Notify parent of selection changes
      if (onSelectionChange) {
        const selectedRows = table
          .getSelectedRowModel()
          .rows.map((row) => row.original);
        onSelectionChange(selectedRows);
      }
    },
    onColumnPinningChange: setColumnPinning,
    onPaginationChange: (updater) => {
      const newPagination = typeof updater === 'function' ? updater(paginationState) : updater;
      setPaginationState(newPagination);
      onPageChange?.(newPagination.pageIndex + 1, newPagination.pageSize);
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: pagination ? getPaginationRowModel() : undefined,
    enableRowSelection: selectable,
    enableMultiRowSelection: true,
    enableSubRowSelection: false,
  });

  // ============================================================================
  // Virtual Scrolling
  // ============================================================================

  const tableContainerRef = useRef<HTMLDivElement>(null);
  const renderStartTimeRef = useRef<number>(0);
  
  const { rows } = table.getRowModel();
  
  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: useCallback(
      (index: number) => {
        // Support dynamic row height estimation based on content
        if (dynamicRowHeight) {
          const row = rows[index];
          if (row) {
            // Estimate based on content length (basic heuristic)
            const cellCount = row.getVisibleCells().length;
            return Math.max(rowHeight, Math.min(rowHeight * 2, cellCount * 20));
          }
        }
        return rowHeight;
      },
      [dynamicRowHeight, rows, rowHeight]
    ),
    overscan,
    measureElement: dynamicRowHeight
      ? (element) => element?.getBoundingClientRect().height
      : undefined,
  });

  const virtualRows = virtual ? rowVirtualizer.getVirtualItems() : [];
  const totalSize = virtual ? rowVirtualizer.getTotalSize() : 0;

  // Report virtual scroll metrics
  useEffect(() => {
    if (virtual && onVirtualScrollMetrics) {
      const metrics: VirtualScrollMetrics = {
        totalRows: rows.length,
        visibleRows: virtualRows.length,
        scrollOffset: rowVirtualizer.scrollOffset ?? 0,
        estimatedRowHeight: rowHeight,
        renderTime: renderStartTimeRef.current > 0 
          ? performance.now() - renderStartTimeRef.current 
          : undefined,
      };
      onVirtualScrollMetrics(metrics);
    }
  }, [virtual, onVirtualScrollMetrics, rows.length, virtualRows.length, rowVirtualizer.scrollOffset, rowHeight]);

  // Track render start time for performance measurement
  useEffect(() => {
    if (virtual) {
      renderStartTimeRef.current = performance.now();
    }
  }, [virtual, virtualRows]);

  // ============================================================================
  // Event Handlers
  // ============================================================================

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
    (row: TData, columnId: string, value: unknown) => {
      onEdit?.(row, columnId, value);
      setEditingCell(null);
    },
    [onEdit]
  );

  // ============================================================================
  // Render Helpers
  // ============================================================================

  const renderCell = useCallback(
    (cell: any, rowIndex: number) => {
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
                onSave: () => handleCellEdit(cell.row.original, column.id, cell.getValue()),
                onCancel: () => setEditingCell(null),
              })
            ) : (
              <input
                type="text"
                defaultValue={cell.getValue() as string}
                onBlur={() => handleCellEdit(cell.row.original, column.id, cell.getValue())}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleCellEdit(cell.row.original, column.id, cell.getValue());
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
    [editable, editingCell, handleCellEdit]
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

  // ============================================================================
  // Effects
  // ============================================================================

  // Sync external pagination state
  useEffect(() => {
    setPaginationState({
      pageIndex: currentPage - 1,
      pageSize,
    });
  }, [currentPage, pageSize]);

  // Setup column pinning
  useEffect(() => {
    const leftPins: string[] = [];
    const rightPins: string[] = [];

    tableColumns.forEach((col) => {
      if (col.fixed === 'left') {
        leftPins.push(col.id || col.accessorKey as string);
      } else if (col.fixed === 'right') {
        rightPins.push(col.id || col.accessorKey as string);
      }
    });

    setColumnPinning({ left: leftPins, right: rightPins });
  }, [tableColumns]);

  // ============================================================================
  // Render
  // ============================================================================

  const tableClasses = [
    'table',
    `table--${variant}`,
    `table--${size}`,
    `table--${theme}`,
    striped && 'table--striped',
    hoverable && 'table--hoverable',
    bordered && 'table--bordered',
    className,
  ].filter(Boolean).join(' ');

  const displayRows = virtual ? rows : table.getRowModel().rows;

  return (
    <div className={`table-wrapper ${className}`} style={style}>
      <div
        ref={tableContainerRef}
        className="table-container"
        style={{
          maxHeight: virtual ? maxHeight : undefined,
          overflow: virtual ? 'auto' : 'visible',
        }}
      >
        <table className={`${tableClasses} ${tableClassName}`}>
          <TableHeader className={headerClassName}>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  const columnDef = header.column.columnDef as TableColumn<TData>;
                  const isPinnedLeft = header.column.getIsPinned() === 'left';
                  const isPinnedRight = header.column.getIsPinned() === 'right';
                  const isPinned = isPinnedLeft || isPinnedRight;
                  
                  // Column grouping support - check if this is a group header
                  const isGroupHeader = !header.isPlaceholder && header.colSpan > 1;
                  const colSpan = header.colSpan;
                  const rowSpan = header.rowSpan || 1;

                  return (
                    <th
                      key={header.id}
                      className={[
                        'table-th',
                        columnDef.align && `table-th--${columnDef.align}`,
                        header.column.getCanSort() && 'table-th--sortable',
                        isPinned && 'table-th--pinned',
                        isPinnedLeft && 'table-th--pinned-left',
                        isPinnedRight && 'table-th--pinned-right',
                        isGroupHeader && 'table-th--group',
                      ].filter(Boolean).join(' ')}
                      style={{
                        width: header.getSize() !== 150 ? header.getSize() : undefined,
                        left: isPinnedLeft ? header.getStart() : undefined,
                        right: isPinnedRight ? header.getTotalRight() : undefined,
                      }}
                      colSpan={colSpan}
                      rowSpan={rowSpan}
                      onClick={
                        header.column.getCanSort()
                          ? header.column.getToggleSortingHandler()
                          : undefined
                      }
                    >
                      <div className="table-th-content">
                        {renderHeader(header)}
                        {header.column.getIsSorted() && (
                          <span className="table-sort-indicator">
                            {header.column.getIsSorted() === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                      {!isGroupHeader && !header.isPlaceholder && (
                        <div
                          className="table-resizer"
                          onMouseDown={header.getResizeHandler()}
                          onClick={(e) => e.stopPropagation()}
                        />
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
          </TableHeader>

          <TableBody className={bodyClassName}>
            {loading ? (
              <TableLoadingState
                colSpan={table.getAllColumns().length}
                loadingComponent={loadingComponent}
              />
            ) : displayRows.length === 0 ? (
              <TableEmptyState
                colSpan={table.getAllColumns().length}
                emptyComponent={emptyComponent}
              />
            ) : (
              <>
                {virtual ? (
                  <TableVirtualizedRows
                    rows={rows}
                    virtualRows={virtualRows}
                    totalSize={totalSize}
                    rowVirtualizer={rowVirtualizer}
                    dynamicRowHeight={dynamicRowHeight}
                    editable={editable}
                    editingCell={editingCell}
                    setEditingCell={setEditingCell}
                    renderCell={renderCell}
                    onRowClick={handleRowClick}
                    onRowDoubleClick={handleRowDoubleClick}
                    onCellClick={handleCellClick}
                  />
                ) : (
                  <TableRegularRows
                    rows={displayRows}
                    editable={editable}
                    editingCell={editingCell}
                    setEditingCell={setEditingCell}
                    renderCell={renderCell}
                    onRowClick={handleRowClick}
                    onRowDoubleClick={handleRowDoubleClick}
                    onCellClick={handleCellClick}
                  />
                )}
              </>
            )}
          </TableBody>
        </table>
      </div>

      {pagination && !loading && displayRows.length > 0 && (
        <TablePagination
          currentPage={paginationState.pageIndex + 1}
          pageSize={paginationState.pageSize}
          total={table.getFilteredRowModel().rows.length}
          pageSizeOptions={pageSizeOptions}
          onPageChange={(page, size) => {
            setPaginationState({ pageIndex: page - 1, pageSize: size });
            onPageChange?.(page, size);
          }}
          showTotal={(total, range) => (
            <span>
              {range[0]}-{range[1]} of {total} items
            </span>
          )}
        />
      )}
    </div>
  );
});

// ============================================================================
// Exports
// ============================================================================

Table.displayName = 'Table';

export { Table };
export type { TableProps, TableColumn, CellContext };
