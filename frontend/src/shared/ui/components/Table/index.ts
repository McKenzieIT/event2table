/**
 * Unified Table Component - Entry Point
 * 
 * Exports all Table components and types for easy import
 */

export { Table, TableHeader, TableBody, TableFooter, TablePagination } from './Table';
export type {
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
  SortingState,
  FilterState,
  SelectionState,
  TableVariant,
  TableSize,
  TextAlign,
  SortDirection,
  CellRenderProps,
  HeaderRenderProps,
  CellEditProps,
} from './Table.types';

export { default } from './Table';
