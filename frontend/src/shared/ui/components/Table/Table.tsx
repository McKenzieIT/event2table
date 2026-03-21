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
import './Table.css';

// ============================================================================
// Sub-components
// ============================================================================

const TableHeader = forwardRef<HTMLTableSectionElement, TableHeaderProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <thead ref={ref} className={`table-header ${className}`} {...props}>
        {children}
      </thead>
    );
  }
);

TableHeader.displayName = 'TableHeader';

const TableBody = forwardRef<HTMLTableSectionElement, TableBodyProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <tbody ref={ref} className={`table-body ${className}`} {...props}>
        {children}
      </tbody>
    );
  }
);

TableBody.displayName = 'TableBody';

const TableFooter = forwardRef<HTMLTableSectionElement, TableFooterProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <tfoot ref={ref} className={`table-footer ${className}`} {...props}>
        {children}
      </tfoot>
    );
  }
);

TableFooter.displayName = 'TableFooter';

// ============================================================================
// Pagination Component
// ============================================================================

const TablePagination: React.FC<PaginationProps> = ({
  currentPage,
  pageSize,
  total,
  pageSizeOptions = [10, 20, 50, 100],
  onPageChange,
  showSizeChanger = true,
  showQuickJumper = true,
  showTotal,
  className = '',
}) => {
  const totalPages = Math.ceil(total / pageSize);
  const [jumpPage, setJumpPage] = useState('');

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      onPageChange(page, pageSize);
    }
  };

  const handlePageSizeChange = (newPageSize: number) => {
    const newPage = Math.min(currentPage, Math.ceil(total / newPageSize));
    onPageChange(newPage, newPageSize);
  };

  const handleJump = () => {
    const page = parseInt(jumpPage, 10);
    if (!isNaN(page)) {
      handlePageChange(page);
      setJumpPage('');
    }
  };

  const renderPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);
      
      if (currentPage > 3) {
        pages.push('...');
      }
      
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      if (currentPage < totalPages - 2) {
        pages.push('...');
      }
      
      pages.push(totalPages);
    }

    return pages;
  };

  const startItem = total === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, total);

  return (
    <div className={`table-pagination ${className}`}>
      {showTotal && (
        <div className="pagination-total">
          {showTotal(total, [startItem, endItem])}
        </div>
      )}
      
      <div className="pagination-controls">
        <button
          className="pagination-button"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          aria-label="Previous page"
        >
          ‹
        </button>

        {renderPageNumbers().map((page, index) => (
          <button
            key={index}
            className={`pagination-button ${page === currentPage ? 'active' : ''}`}
            onClick={() => typeof page === 'number' && handlePageChange(page)}
            disabled={page === '...'}
          >
            {page}
          </button>
        ))}

        <button
          className="pagination-button"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          aria-label="Next page"
        >
          ›
        </button>
      </div>

      {showSizeChanger && (
        <div className="pagination-size-changer">
          <select
            value={pageSize}
            onChange={(e) => handlePageSizeChange(Number(e.target.value))}
            className="pagination-select"
          >
            {pageSizeOptions.map((size) => (
              <option key={size} value={size}>
                {size} / page
              </option>
            ))}
          </select>
        </div>
      )}

      {showQuickJumper && (
        <div className="pagination-jumper">
          <span>Go to</span>
          <input
            type="number"
            min={1}
            max={totalPages}
            value={jumpPage}
            onChange={(e) => setJumpPage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleJump()}
            className="pagination-input"
          />
          <button
            className="pagination-button pagination-go-button"
            onClick={handleJump}
            disabled={!jumpPage}
          >
            Go
          </button>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// Main Table Component
// ============================================================================

const Table = React.memo(<TData extends Record<string, unknown>>({
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
              <tr>
                <td colSpan={table.getAllColumns().length} className="table-loading">
                  {loadingComponent || <div className="table-spinner" />}
                </td>
              </tr>
            ) : displayRows.length === 0 ? (
              <tr>
                <td colSpan={table.getAllColumns().length} className="table-empty">
                  {emptyComponent || <div className="table-empty-message">No data available</div>}
                </td>
              </tr>
            ) : (
              <>
                {virtual ? (
                  <>
                    {/* Spacer for virtualized rows above viewport */}
                    {virtualRows.length > 0 && virtualRows[0].start > 0 && (
                      <tr style={{ height: virtualRows[0].start }} />
                    )}
                    {virtualRows.map((virtualRow) => {
                      const row = rows[virtualRow.index];
                      return (
                        <tr
                          key={row.id}
                          data-index={virtualRow.index}
                          ref={dynamicRowHeight ? rowVirtualizer.measureElement : undefined}
                          className={[
                            'table-tr',
                            'table-tr--virtual',
                            row.getIsSelected() && 'table-tr--selected',
                          ].filter(Boolean).join(' ')}
                          onClick={(e) => handleRowClick(row.original, e)}
                          onDoubleClick={(e) => handleRowDoubleClick(row.original, e)}
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
                                onClick={(e) => handleCellClick(cell, e)}
                                onDoubleClick={() => {
                                  if (editable && columnDef.editable) {
                                    setEditingCell({
                                      rowIndex: virtualRow.index,
                                      columnId: cell.column.id,
                                    });
                                  }
                                }}
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
                ) : (
                  displayRows.map((row) => (
                    <tr
                      key={row.id}
                      className={[
                        'table-tr',
                        row.getIsSelected() && 'table-tr--selected',
                      ].filter(Boolean).join(' ')}
                      onClick={(e) => handleRowClick(row.original, e)}
                      onDoubleClick={(e) => handleRowDoubleClick(row.original, e)}
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
                            onClick={(e) => handleCellClick(cell, e)}
                            onDoubleClick={() => {
                              if (editable && columnDef.editable) {
                                setEditingCell({
                                  rowIndex: row.index,
                                  columnId: cell.column.id,
                                });
                              }
                            }}
                          >
                            {renderCell(cell, row.index)}
                          </td>
                        );
                      })}
                    </tr>
                  ))
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
};

// ============================================================================
// Exports
// ============================================================================

Table.displayName = 'Table';

export { Table, TableHeader, TableBody, TableFooter, TablePagination, TableRow, TableCell, TableFilter, TableSort };
export type { TableProps, TableColumn, CellContext };
