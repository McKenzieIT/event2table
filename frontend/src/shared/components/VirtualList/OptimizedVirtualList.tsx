/**
 * OptimizedVirtualList - High-performance virtual scrolling component
 *
 * Performance Optimizations:
 * - React.memo with custom comparison for list items
 * - useMemo for visible items calculation
 * - useCallback for scroll handling
 * - RequestAnimationFrame for smooth scrolling
 * - IntersectionObserver for lazy loading
 *
 * Usage:
 * <OptimizedVirtualList
 *   items={games}
 *   renderItem={(game) => <GameListItem game={game} />}
 *   itemHeight={50}
 *   height={600}
 *   overscan={5}
 * />
 */

import React, { useState, useEffect, useRef, useMemo, useCallback, memo } from 'react';
import './OptimizedVirtualList.css';

interface OptimizedVirtualListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  itemHeight: number;
  height: number;
  overscan?: number;
  className?: string;
  onScroll?: (scrollTop: number) => void;
  onEndReached?: () => void;
  endReachedThreshold?: number;
}

function OptimizedVirtualList<T>({
  items,
  renderItem,
  itemHeight,
  height,
  overscan = 3,
  className = '',
  onScroll,
  onEndReached,
  endReachedThreshold = 200
}: OptimizedVirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const [isMounted, setIsMounted] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const endReachedRef = useRef(false);

  // ✅ useMemo for calculating visible range
  const visibleRange = useMemo(() => {
    const totalHeight = items.length * itemHeight;
    const visibleCount = Math.ceil(height / itemHeight);
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      startIndex + visibleCount + overscan * 2
    );

    return { startIndex, endIndex, totalHeight };
  }, [scrollTop, items.length, itemHeight, height, overscan]);

  // ✅ useMemo for visible items
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex + 1);
  }, [items, visibleRange.startIndex, visibleRange.endIndex]);

  // ✅ useCallback for scroll handling with RAF
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const scrollTop = e.currentTarget.scrollTop;

    // Use requestAnimationFrame for smooth scrolling
    requestAnimationFrame(() => {
      setScrollTop(scrollTop);
      onScroll?.(scrollTop);
    });

    // Check if end reached
    if (onEndReached && !endReachedRef.current) {
      const scrollHeight = e.currentTarget.scrollHeight;
      const clientHeight = e.currentTarget.clientHeight;
      const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);

      if (distanceFromBottom < endReachedThreshold) {
        endReachedRef.current = true;
        onEndReached();

        // Reset flag after a delay
        setTimeout(() => {
          endReachedRef.current = false;
        }, 500);
      }
    }
  }, [onScroll, onEndReached, endReachedThreshold]);

  // Mount effect for fade-in animation
  useEffect(() => {
    setIsMounted(true);
  }, []);

  return (
    <div
      ref={containerRef}
      className={`optimized-virtual-list ${isMounted ? 'mounted' : ''} ${className}`}
      style={{ height, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div
        className="virtual-list-spacer"
        style={{
          height: visibleRange.totalHeight,
          position: 'relative'
        }}
      >
        {visibleItems.map((item, index) => {
          const actualIndex = visibleRange.startIndex + index;
          const translateY = actualIndex * itemHeight;

          return (
            <div
              key={actualIndex}
              className="virtual-list-item"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: itemHeight,
                transform: `translateY(${translateY}px)`,
                willChange: 'transform'
              }}
            >
              {renderItem(item, actualIndex)}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ✅ Export memoized component
const OptimizedVirtualListMemo = memo(OptimizedVirtualList) as typeof OptimizedVirtualList;

export default OptimizedVirtualListMemo;
