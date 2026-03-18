/**
 * React Performance Testing Utilities
 *
 * Provides tools to measure component render performance:
 * - Render count tracking
 * - Render time measurement
 * - Re-render detection
 * - Memory leak detection
 */

import { useEffect, useRef } from 'react';

/**
 * Hook to track component renders
 * @param componentName - Name of the component being tracked
 * @returns Object with render count and last render time
 */
export function useRenderTracker(componentName: string) {
  const renderCount = useRef(0);
  const lastRenderTime = useRef<number>(0);
  const renderTimes = useRef<number[]>([]);

  useEffect(() => {
    const now = performance.now();
    const timeSinceLastRender = lastRenderTime.current ? now - lastRenderTime.current : 0;

    renderCount.current += 1;
    renderTimes.current.push(timeSinceLastRender);
    lastRenderTime.current = now;

    // Log render info in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[RenderTracker] ${componentName} rendered:`, {
        renderCount: renderCount.current,
        timeSinceLastRender: `${timeSinceLastRender.toFixed(2)}ms`,
        averageRenderTime: `${(renderTimes.current.reduce((a, b) => a + b, 0) / renderTimes.current.length).toFixed(2)}ms`,
      });
    }

    // Cleanup function to report final stats
    return () => {
      if (process.env.NODE_ENV === 'development') {
        const totalRenders = renderCount.current;
        const avgTime = renderTimes.current.reduce((a, b) => a + b, 0) / renderTimes.current.length;
        console.log(`[RenderTracker] ${componentName} unmounted:`, {
          totalRenders,
          averageRenderTime: `${avgTime.toFixed(2)}ms`,
        });
      }
    };
  });

  return {
    renderCount: renderCount.current,
    lastRenderTime: lastRenderTime.current,
    averageRenderTime: renderTimes.current.length > 0
      ? renderTimes.current.reduce((a, b) => a + b, 0) / renderTimes.current.length
      : 0,
  };
}

/**
 * Hook to measure component render time
 * @param componentName - Name of the component being measured
 * @returns Object with current render duration
 */
export function useRenderTime(componentName: string) {
  const renderStartTime = useRef<number>(0);
  const renderDuration = useRef<number>(0);

  useEffect(() => {
    // Measure render time after paint
    requestAnimationFrame(() => {
      renderDuration.current = performance.now() - renderStartTime.current;

      if (process.env.NODE_ENV === 'development') {
        console.log(`[RenderTime] ${componentName}: ${renderDuration.current.toFixed(2)}ms`);
      }
    });
  });

  // Start timer at beginning of render
  renderStartTime.current = performance.now();

  return {
    renderDuration: renderDuration.current,
  };
}

/**
 * Performance metrics collector
 */
export class PerformanceMetrics {
  private metrics: Map<string, number[]> = new Map();

  /**
   * Record a metric
   * @param key - Metric name
   * @param value - Metric value (e.g., render time in ms)
   */
  record(key: string, value: number): void {
    if (!this.metrics.has(key)) {
      this.metrics.set(key, []);
    }
    this.metrics.get(key)!.push(value);
  }

  /**
   * Get statistics for a metric
   * @param key - Metric name
   * @returns Statistics object
   */
  getStats(key: string): { min: number; max: number; avg: number; count: number } | null {
    const values = this.metrics.get(key);
    if (!values || values.length === 0) return null;

    return {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: values.reduce((a, b) => a + b, 0) / values.length,
      count: values.length,
    };
  }

  /**
   * Get all metrics
   * @returns Object with all metrics and their statistics
   */
  getAllStats(): Record<string, ReturnType<PerformanceMetrics['getStats']>> {
    const stats: Record<string, ReturnType<PerformanceMetrics['getStats']>> = {};
    for (const key of this.metrics.keys()) {
      stats[key] = this.getStats(key);
    }
    return stats;
  }

  /**
   * Clear all metrics
   */
  clear(): void {
    this.metrics.clear();
  }

  /**
   * Generate a performance report
   * @returns Formatted report string
   */
  generateReport(): string {
    const stats = this.getAllStats();
    const lines: string[] = ['\n=== Performance Metrics Report ===\n'];

    for (const [key, stat] of Object.entries(stats)) {
      if (stat) {
        lines.push(`${key}:`);
        lines.push(`  Count: ${stat.count}`);
        lines.push(`  Min: ${stat.min.toFixed(2)}ms`);
        lines.push(`  Max: ${stat.max.toFixed(2)}ms`);
        lines.push(`  Avg: ${stat.avg.toFixed(2)}ms`);
        lines.push('');
      }
    }

    lines.push('===================================\n');
    return lines.join('\n');
  }
}

/**
 * Global performance metrics instance
 */
export const globalMetrics = new PerformanceMetrics();

/**
 * Utility to measure async function performance
 * @param fn - Async function to measure
 * @param label - Label for the measurement
 * @returns Result of the function
 */
export async function measurePerformance<T>(
  fn: () => Promise<T>,
  label: string
): Promise<T> {
  const start = performance.now();
  try {
    const result = await fn();
    const duration = performance.now() - start;

    globalMetrics.record(label, duration);

    if (process.env.NODE_ENV === 'development') {
      console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
    }

    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.error(`[Performance] ${label} failed after ${duration.toFixed(2)}ms:`, error);
    throw error;
  }
}

/**
 * Utility to measure synchronous function performance
 * @param fn - Function to measure
 * @param label - Label for the measurement
 * @returns Result of the function
 */
export function measureSyncPerformance<T>(
  fn: () => T,
  label: string
): T {
  const start = performance.now();
  try {
    const result = fn();
    const duration = performance.now() - start;

    globalMetrics.record(label, duration);

    if (process.env.NODE_ENV === 'development') {
      console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
    }

    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.error(`[Performance] ${label} failed after ${duration.toFixed(2)}ms:`, error);
    throw error;
  }
}
