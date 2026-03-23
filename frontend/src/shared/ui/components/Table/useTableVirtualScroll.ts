import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef, useEffect, useCallback } from 'react';

import type { VirtualScrollMetrics } from './Table.types';

/**
 * Props for useTableVirtualScroll hook
 */
export interface UseTableVirtualScrollProps<TData> {
  /** Enable virtual scrolling */
  virtual: boolean;
  /** Row height */
  rowHeight: number;
  /** Max height */
  maxHeight: number;
  /** Overscan */
  overscan: number;
  /** Dynamic row height */
  dynamicRowHeight: boolean;
  /** Callback for virtual scroll metrics */
  onVirtualScrollMetrics?: (metrics: VirtualScrollMetrics) => void;
  /** Table rows */
  rows: TData[];
}

/**
 * Result of useTableVirtualScroll hook
 */
export interface UseTableVirtualScrollResult {
  /** Container ref */
  tableContainerRef: React.RefObject<HTMLDivElement>;
  /** Virtual rows */
  virtualRows: ReturnType<typeof useVirtualizer>['getVirtualItems'];
  /** Total size */
  totalSize: number;
  /** Row virtualizer */
  rowVirtualizer: ReturnType<typeof useVirtualizer>;
}

/**
 * Hook for table virtual scrolling
 */
export function useTableVirtualScroll<TData>({
  virtual,
  rowHeight,
  maxHeight,
  overscan,
  dynamicRowHeight,
  onVirtualScrollMetrics,
  rows,
}: UseTableVirtualScrollProps<TData>): UseTableVirtualScrollResult {
  const tableContainerRef = useRef<HTMLDivElement>(null);
  const renderStartTimeRef = useRef<number>(0);
  
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
            const cellCount = Object.keys(row).length;
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

  return {
    tableContainerRef,
    virtualRows,
    totalSize,
    rowVirtualizer,
  };
}
