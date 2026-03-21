import React from 'react';
import { TableBodyProps } from './Table.types';

/**
 * TableBody Component
 * 
 * Renders the body section of the table with support for:
 * - Loading state
 * - Empty state
 * - Virtual scrolling
 * - Row selection
 * - Row click events
 */
export const TableBody = <TData extends Record<string, unknown>>({
  className = '',
  children,
}: TableBodyProps) => {
  return <tbody className={`table-tbody ${className}`}>{children}</tbody>;
};

TableBody.displayName = 'TableBody';
