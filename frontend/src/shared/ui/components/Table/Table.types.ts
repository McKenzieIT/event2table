/**
 * Unified Table Component Type Definitions
 * Based on TanStack Table with enhanced features
 */

import { ColumnDef, RowData, TableOptions, Row, Column } from '@tanstack/react-table';

// ============================================================================
// Core Types
// ============================================================================

export type TableVariant = 'default' | 'bordered' | 'compact' | 'minimal';
export type TableSize = 'sm' | 'md' | 'lg';
export type TextAlign = 'left' | 'center' | 'right';
export type SortDirection = 'asc' | 'desc';

// ============================================================================
// Column Configuration
// ============================================================================

export interface TableColumn<TData extends RowData, TValue = unknown> extends ColumnDef<TData, TValue> {
  // Display properties
  header?: string | React.ReactNode;
  width?: number | string;
  minWidth?: number;
  maxWidth?: number;
  
  // Alignment
  align?: TextAlign;
  
  // Fixed columns
  fixed?: 'left' | 'right';
  
  // Sorting
  sortable?: boolean;
  sortDirection?: SortDirection;
  
  // Filtering
  filterable?: boolean;
  filterType?: 'text' | 'select' | 'date' | 'number';
  filterOptions?: Array<{ label: string; value: string | number }>;
  
  // Editing
  editable?: boolean;
  editComponent?: (props: CellEditProps<TData, TValue>) => React.ReactNode;
  
  // Custom rendering
  cellRenderer?: (props: CellRenderProps<TData, TValue>) => React.ReactNode;
  headerRenderer?: (props: HeaderRenderProps<TData, TValue>) => React.ReactNode;
}

// ============================================================================
// Table Props
// ============================================================================

export interface TableProps<TData extends RowData> {
  // Data
  data: TData[];
  columns: TableColumn<TData>[];
  
  // Display options
  variant?: TableVariant;
  size?: TableSize;
  striped?: boolean;
  hoverable?: boolean;
  bordered?: boolean;
  
  // Selection
  selectable?: boolean;
  onSelectionChange?: (selectedRows: TData[]) => void;
  initialSelectedIds?: (string | number)[];
  
  // Sorting
  sortable?: boolean;
  onSortChange?: (sorting: SortingState) => void;
  initialSorting?: SortingState;
  
  // Filtering
  filterable?: boolean;
  onFilterChange?: (filters: FilterState) => void;
  initialFilters?: FilterState;
  
  // Pagination
  pagination?: boolean;
  pageSize?: number;
  currentPage?: number;
  onPageChange?: (page: number, pageSize: number) => void;
  pageSizeOptions?: number[];
  
  // Virtualization
  virtual?: boolean;
  rowHeight?: number;
  maxHeight?: number;
  
  // Editing
  editable?: boolean;
  onEdit?: (row: TData, columnId: string, value: unknown) => void;
  
  // Events
  onRowClick?: (row: TData, event: React.MouseEvent) => void;
  onRowDoubleClick?: (row: TData, event: React.MouseEvent) => void;
  onCellClick?: (cell: CellContext<TData>, event: React.MouseEvent) => void;
  
  // Loading state
  loading?: boolean;
  loadingComponent?: React.ReactNode;
  
  // Empty state
  empty?: boolean;
  emptyComponent?: React.ReactNode;
  
  // Styling
  className?: string;
  style?: React.CSSProperties;
  tableClassName?: string;
  headerClassName?: string;
  bodyClassName?: string;
  
  // Theme
  theme?: 'light' | 'dark' | 'auto';
}

// ============================================================================
// State Types
// ============================================================================

export type SortingState = Array<{
  id: string;
  desc: boolean;
}>;

export type FilterState = Record<string, unknown>;

export type SelectionState = Set<string | number>;

// ============================================================================
// Context Types
// ============================================================================

export interface CellRenderProps<TData extends RowData, TValue> {
  cell: CellContext<TData>;
  row: Row<TData>;
  column: Column<TData, TValue>;
  value: TValue;
}

export interface HeaderRenderProps<TData extends RowData, TValue> {
  column: Column<TData, TValue>;
  header: string | React.ReactNode;
}

export interface CellEditProps<TData extends RowData, TValue> {
  value: TValue;
  row: Row<TData>;
  column: Column<TData, TValue>;
  onChange: (value: TValue) => void;
  onSave: () => void;
  onCancel: () => void;
}

export interface CellContext<TData extends RowData> {
  row: Row<TData>;
  column: Column<TData>;
  getValue: () => unknown;
  setValue: (value: unknown) => void;
}

// ============================================================================
// Sub-component Props
// ============================================================================

export interface TableHeaderProps {
  className?: string;
  children?: React.ReactNode;
}

export interface TableBodyProps {
  className?: string;
  children?: React.ReactNode;
}

export interface TableFooterProps {
  className?: string;
  children?: React.ReactNode;
}

export interface TableRowProps<TData extends RowData> {
  row: Row<TData>;
  className?: string;
  onClick?: (row: TData, event: React.MouseEvent) => void;
  onDoubleClick?: (row: TData, event: React.MouseEvent) => void;
  children?: React.ReactNode;
}

export interface TableCellProps<TData extends RowData, TValue = unknown> {
  cell: CellContext<TData>;
  column: Column<TData, TValue>;
  className?: string;
  onClick?: (cell: CellContext<TData>, event: React.MouseEvent) => void;
  children?: React.ReactNode;
}

export interface TableHeadProps<TData extends RowData, TValue = unknown> {
  column: Column<TData, TValue>;
  className?: string;
  sortable?: boolean;
  onClick?: (column: Column<TData, TValue>) => void;
  children?: React.ReactNode;
}

// ============================================================================
// Virtualization Props
// ============================================================================

export interface VirtualTableProps<TData extends RowData> extends TableProps<TData> {
  virtual: true;
  rowHeight: number;
  maxHeight: number;
  overscan?: number;
}

// ============================================================================
// Pagination Props
// ============================================================================

export interface PaginationProps {
  currentPage: number;
  pageSize: number;
  total: number;
  pageSizeOptions?: number[];
  onPageChange: (page: number, pageSize: number) => void;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: (total: number, range: [number, number]) => React.ReactNode;
  className?: string;
}

// ============================================================================
// Filter Props
// ============================================================================

export interface FilterProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  columns: TableColumn<unknown>[];
  className?: string;
}

// ============================================================================
// Export all types
// ============================================================================

export type {
  ColumnDef,
  TableOptions,
  Row,
  Column,
  RowData,
};
