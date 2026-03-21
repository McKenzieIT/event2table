import { TableColumn, RowData } from './Table.types';

// ============================================================================
// Column Utilities
// ============================================================================

/**
 * Get column width or default value
 */
export function getColumnWidth<T extends RowData>(
  column: TableColumn<T>,
  defaultWidth: number = 150
): number | string {
  return column.width || defaultWidth;
}

/**
 * Check if column is fixed
 */
export function isColumnFixed<T extends RowData>(
  column: TableColumn<T>
): boolean {
  return column.fixed === 'left' || column.fixed === 'right';
}

/**
 * Get column fixed position
 */
export function getColumnFixedPosition<T extends RowData>(
  column: TableColumn<T>
): 'left' | 'right' | undefined {
  return column.fixed;
}

/**
 * Check if column is sortable
 */
export function isColumnSortable<T extends RowData>(
  column: TableColumn<T>,
  globalSortable: boolean = true
): boolean {
  return column.sortable !== false && globalSortable;
}

/**
 * Check if column is filterable
 */
export function isColumnFilterable<T extends RowData>(
  column: TableColumn<T>,
  globalFilterable: boolean = true
): boolean {
  return column.filterable !== false && globalFilterable;
}

/**
 * Check if column is editable
 */
export function isColumnEditable<T extends RowData>(
  column: TableColumn<T>,
  globalEditable: boolean = false
): boolean {
  return column.editable !== false && globalEditable;
}

// ============================================================================
// Row Utilities
// ============================================================================

/**
 * Generate unique row key
 */
export function getRowKey<T extends RowData>(
  row: T,
  keyField: keyof T | string = 'id'
): string {
  const keyValue = row[keyField];
  return keyValue != null ? String(keyValue) : Math.random().toString(36).substr(2, 9);
}

/**
 * Check if row is selected
 */
export function isRowSelected(
  rowId: string | number,
  selectedIds: Set<string | number>
): boolean {
  return selectedIds.has(rowId);
}

/**
 * Toggle row selection
 */
export function toggleRowSelection(
  rowId: string | number,
  selectedIds: Set<string | number>,
  multiSelect: boolean = true
): Set<string | number> {
  const newSelection = new Set(selectedIds);
  
  if (newSelection.has(rowId)) {
    newSelection.delete(rowId);
  } else {
    if (multiSelect) {
      newSelection.add(rowId);
    } else {
      newSelection.clear();
      newSelection.add(rowId);
    }
  }
  
  return newSelection;
}

/**
 * Select all rows
 */
export function selectAllRows(
  rowIds: (string | number)[],
  selectedIds: Set<string | number>
): Set<string | number> {
  return new Set(rowIds);
}

/**
 * Clear all selections
 */
export function clearSelection(): Set<string | number> {
  return new Set();
}

// ============================================================================
// Pagination Utilities
// ============================================================================

/**
 * Calculate total pages
 */
export function getTotalPages(total: number, pageSize: number): number {
  return Math.ceil(total / pageSize);
}

/**
 * Calculate page range (start and end item indices)
 */
export function getPageRange(
  currentPage: number,
  pageSize: number,
  total: number
): [number, number] {
  const start = total === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const end = Math.min(currentPage * pageSize, total);
  return [start, end];
}

/**
 * Generate page numbers for pagination display
 */
export function generatePageNumbers(
  currentPage: number,
  totalPages: number,
  maxVisible: number = 7
): Array<number | string> {
  if (totalPages <= maxVisible) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const pages: Array<number | string> = [];
  const halfVisible = Math.floor(maxVisible / 2);

  // Always show first page
  pages.push(1);

  // Calculate start and end of visible range
  let start = Math.max(2, currentPage - halfVisible + 1);
  let end = Math.min(totalPages - 1, currentPage + halfVisible - 1);

  // Adjust if we're near the beginning
  if (currentPage <= halfVisible) {
    end = Math.min(totalPages - 1, maxVisible - 1);
  }

  // Adjust if we're near the end
  if (currentPage > totalPages - halfVisible) {
    start = Math.max(2, totalPages - maxVisible + 2);
  }

  // Add ellipsis if there's a gap after first page
  if (start > 2) {
    pages.push('...');
  }

  // Add visible pages
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  // Add ellipsis if there's a gap before last page
  if (end < totalPages - 1) {
    pages.push('...');
  }

  // Always show last page
  pages.push(totalPages);

  return pages;
}

/**
 * Validate page number
 */
export function validatePageNumber(
  page: number,
  totalPages: number
): number {
  return Math.max(1, Math.min(page, totalPages));
}

/**
 * Validate page size
 */
export function validatePageSize(
  pageSize: number,
  options: number[]
): number {
  if (options.includes(pageSize)) {
    return pageSize;
  }
  return options[0];
}

// ============================================================================
// Sorting Utilities
// ============================================================================

/**
 * Sort data array by column
 */
export function sortData<T extends RowData>(
  data: T[],
  sortColumn: keyof T | string,
  direction: 'asc' | 'desc'
): T[] {
  return [...data].sort((a, b) => {
    const aValue = a[sortColumn];
    const bValue = b[sortColumn];

    if (aValue == null && bValue == null) return 0;
    if (aValue == null) return direction === 'asc' ? 1 : -1;
    if (bValue == null) return direction === 'asc' ? -1 : 1;

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      const comparison = aValue.localeCompare(bValue);
      return direction === 'asc' ? comparison : -comparison;
    }

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return direction === 'asc' ? aValue - bValue : bValue - aValue;
    }

    return 0;
  });
}

/**
 * Get sort direction icon
 */
export function getSortDirectionIcon(direction: 'asc' | 'desc' | false): string {
  if (direction === 'asc') return '↑';
  if (direction === 'desc') return '↓';
  return '';
}

// ============================================================================
// Filtering Utilities
// ============================================================================

/**
 * Filter data by column value
 */
export function filterData<T extends RowData>(
  data: T[],
  filterColumn: keyof T | string,
  filterValue: unknown
): T[] {
  if (filterValue == null || filterValue === '') {
    return data;
  }

  return data.filter((item) => {
    const itemValue = item[filterColumn];
    
    if (itemValue == null) return false;
    
    if (typeof filterValue === 'string' && typeof itemValue === 'string') {
      return itemValue.toLowerCase().includes(filterValue.toLowerCase());
    }
    
    return itemValue === filterValue;
  });
}

/**
 * Apply multiple filters
 */
export function applyFilters<T extends RowData>(
  data: T[],
  filters: Record<string, unknown>
): T[] {
  return data.filter((item) => {
    return Object.entries(filters).every(([key, value]) => {
      if (value == null || value === '') return true;
      const itemValue = item[key];
      
      if (itemValue == null) return false;
      
      if (typeof value === 'string' && typeof itemValue === 'string') {
        return itemValue.toLowerCase().includes(value.toLowerCase());
      }
      
      return itemValue === value;
    });
  });
}

// ============================================================================
// Virtual Scroll Utilities
// ============================================================================

/**
 * Estimate row height based on content
 */
export function estimateRowHeight(
  baseHeight: number,
  cellCount: number,
  contentLength?: number
): number {
  const estimatedHeight = baseHeight;
  
  if (contentLength && contentLength > 50) {
    return Math.min(estimatedHeight * 2, estimatedHeight + Math.ceil(contentLength / 20) * 10);
  }
  
  return estimatedHeight;
}

/**
 * Calculate virtual scroll metrics
 */
export function calculateVirtualScrollMetrics(
  totalRows: number,
  visibleRows: number,
  scrollOffset: number,
  rowHeight: number,
  renderTime?: number
): {
  totalRows: number;
  visibleRows: number;
  scrollOffset: number;
  estimatedRowHeight: number;
  renderTime?: number;
  memoryUsage?: number;
} {
  return {
    totalRows,
    visibleRows,
    scrollOffset,
    estimatedRowHeight: rowHeight,
    renderTime,
    memoryUsage: visibleRows * rowHeight * 0.001, // Rough estimate in MB
  };
}

// ============================================================================
// Style Utilities
// ============================================================================

/**
 * Build table className
 */
export function buildTableClassName(
  baseClass: string,
  variant?: string,
  size?: string,
  theme?: string,
  striped?: boolean,
  hoverable?: boolean,
  bordered?: boolean,
  additionalClass?: string
): string {
  const classes = [baseClass];
  
  if (variant) classes.push(`${baseClass}--${variant}`);
  if (size) classes.push(`${baseClass}--${size}`);
  if (theme) classes.push(`${baseClass}--${theme}`);
  if (striped) classes.push(`${baseClass}--striped`);
  if (hoverable) classes.push(`${baseClass}--hoverable`);
  if (bordered) classes.push(`${baseClass}--bordered`);
  if (additionalClass) classes.push(additionalClass);
  
  return classes.filter(Boolean).join(' ');
}

/**
 * Build cell className
 */
export function buildCellClassName(
  baseClass: string,
  align?: string,
  pinned?: boolean,
  pinnedLeft?: boolean,
  pinnedRight?: boolean,
  additionalClass?: string
): string {
  const classes = [baseClass];
  
  if (align) classes.push(`${baseClass}--${align}`);
  if (pinned) classes.push(`${baseClass}--pinned`);
  if (pinnedLeft) classes.push(`${baseClass}--pinned-left`);
  if (pinnedRight) classes.push(`${baseClass}--pinned-right`);
  if (additionalClass) classes.push(additionalClass);
  
  return classes.filter(Boolean).join(' ');
}

// ============================================================================
// Data Utilities
// ============================================================================

/**
 * Get nested property value
 */
export function getNestedValue<T extends RowData>(
  obj: T,
  path: string
): unknown {
  return path.split('.').reduce((current: any, key) => {
    return current?.[key];
  }, obj);
}

/**
 * Set nested property value
 */
export function setNestedValue<T extends RowData>(
  obj: T,
  path: string,
  value: unknown
): void {
  const keys = path.split('.');
  const lastKey = keys.pop()!;
  
  const target = keys.reduce((current: any, key) => {
    if (!(key in current)) {
      current[key] = {};
    }
    return current[key];
  }, obj as any);
  
  target[lastKey] = value;
}

/**
 * Deep clone data
 */
export function deepClone<T>(data: T): T {
  return JSON.parse(JSON.stringify(data));
}

/**
 * Flatten data for export
 */
export function flattenData<T extends RowData>(
  data: T[],
  columns: TableColumn<T>[]
): Record<string, unknown>[] {
  return data.map((row) => {
    const flattened: Record<string, unknown> = {};
    
    columns.forEach((column) => {
      const key = column.id || column.accessorKey as string;
      if (key) {
        flattened[key] = getNestedValue(row, key);
      }
    });
    
    return flattened;
  });
}
