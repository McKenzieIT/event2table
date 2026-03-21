/**
 * Performance Monitoring Utility
 *
 * Tracks React component performance metrics:
 * - Render time
 * - Re-render count
 * - Memory usage
 * - FPS (frames per second)
 *
 * Usage:
 * import { usePerformanceMonitor } from '@shared/utils/performanceMonitor';
 *
 * function MyComponent() {
 *   usePerformanceMonitor('MyComponent');
 *   return <div>...</div>;
 * }
 */

import { useEffect, useRef } from 'react';

export interface PerformanceMetrics {
  componentName: string;
  renderCount: number;
  totalRenderTime: number;
  averageRenderTime: number;
  lastRenderTime: number;
  memoryUsage?: number;
}

class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, PerformanceMetrics> = new Map();
  private observers: PerformanceObserver[] = [];
  private fps: number = 60;
  private lastFrameTime: number = performance.now();

  private constructor() {
    this.setupPerformanceObserver();
    this.startFPSMonitoring();
  }

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  private setupPerformanceObserver() {
    if (typeof window === 'undefined' || !window.PerformanceObserver) {
      return;
    }

    // Observe render performance
    const renderObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'measure') {
          const componentName = entry.name.replace('render-', '');
          this.updateRenderMetrics(componentName, entry.duration);
        }
      }
    });

    renderObserver.observe({ entryTypes: ['measure'] });
    this.observers.push(renderObserver);
  }

  private startFPSMonitoring() {
    if (typeof window === 'undefined') return;

    const measureFPS = () => {
      const now = performance.now();
      const delta = now - this.lastFrameTime;
      this.fps = 1000 / delta;
      this.lastFrameTime = now;
      requestAnimationFrame(measureFPS);
    };

    requestAnimationFrame(measureFPS);
  }

  private updateRenderMetrics(componentName: string, renderTime: number) {
    const existing = this.metrics.get(componentName);

    if (existing) {
      existing.renderCount++;
      existing.totalRenderTime += renderTime;
      existing.averageRenderTime = existing.totalRenderTime / existing.renderCount;
      existing.lastRenderTime = renderTime;
      existing.memoryUsage = this.getMemoryUsage();
    } else {
      this.metrics.set(componentName, {
        componentName,
        renderCount: 1,
        totalRenderTime: renderTime,
        averageRenderTime: renderTime,
        lastRenderTime: renderTime,
        memoryUsage: this.getMemoryUsage()
      });
    }
  }

  private getMemoryUsage(): number | undefined {
    if (
      typeof window !== 'undefined' &&
      'memory' in performance &&
      (performance as any).memory
    ) {
      return (performance as any).memory.usedJSHeapSize / 1048576; // Convert to MB
    }
    return undefined;
  }

  recordRender(componentName: string) {
    if (typeof window === 'undefined' || !window.performance) {
      return;
    }

    const startTime = performance.now();

    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      performance.mark(`render-start-${componentName}`);
      performance.mark(`render-end-${componentName}`);
      performance.measure(
        `render-${componentName}`,
        `render-start-${componentName}`,
        `render-end-${componentName}`
      );

      // Clean up marks
      performance.clearMarks(`render-start-${componentName}`);
      performance.clearMarks(`render-end-${componentName}`);
    };
  }

  getMetrics(componentName?: string): PerformanceMetrics | PerformanceMetrics[] {
    if (componentName) {
      return this.metrics.get(componentName)!;
    }
    return Array.from(this.metrics.values());
  }

  getFPS(): number {
    return this.fps;
  }

  getSystemMemoryUsage(): number | undefined {
    return this.getMemoryUsage();
  }

  reset() {
    this.metrics.clear();
  }

  logMetrics(componentName?: string) {
    const metrics = componentName
      ? [this.getMetrics(componentName) as PerformanceMetrics]
      : (this.getMetrics() as PerformanceMetrics[]);

    console.group('🚀 Performance Metrics');

    metrics.forEach((metric) => {
      console.log(`📊 ${metric.componentName}:`, {
        'Render Count': metric.renderCount,
        'Avg Render Time': `${metric.averageRenderTime.toFixed(2)}ms`,
        'Last Render Time': `${metric.lastRenderTime.toFixed(2)}ms`,
        'Total Render Time': `${metric.totalRenderTime.toFixed(2)}ms`,
        'Memory Usage': metric.memoryUsage
          ? `${metric.memoryUsage.toFixed(2)}MB`
          : 'N/A'
      });
    });

    console.log(`🎯 FPS: ${this.fps.toFixed(1)}`);

    console.groupEnd();
  }

  warnOnSlowRender(componentName: string, threshold: number = 16.67) {
    const metrics = this.metrics.get(componentName);
    if (metrics && metrics.lastRenderTime > threshold) {
      console.warn(
        `⚠️ Slow render detected in ${componentName}: ${metrics.lastRenderTime.toFixed(2)}ms`
      );
    }
  }
}

// React Hook for performance monitoring
export function usePerformanceMonitor(componentName: string, threshold?: number) {
  const monitor = useRef<PerformanceMonitor>(PerformanceMonitor.getInstance());

  useEffect(() => {
    if (typeof window === 'undefined' || !window.performance) {
      return;
    }

    const stopRecording = monitor.current.recordRender(componentName);

    return () => {
      if (threshold) {
        monitor.current.warnOnSlowRender(componentName, threshold);
      }
    };
  }, [componentName, threshold]);
}

// Export singleton instance
export const performanceMonitor = PerformanceMonitor.getInstance();

// Export utility functions
export function logPerformanceMetrics(componentName?: string) {
  performanceMonitor.logMetrics(componentName);
}

export function getPerformanceMetrics(componentName?: string) {
  return performanceMonitor.getMetrics(componentName);
}

export function getFPS() {
  return performanceMonitor.getFPS();
}

export function getMemoryUsage() {
  return performanceMonitor.getSystemMemoryUsage();
}

export function resetPerformanceMetrics() {
  performanceMonitor.reset();
}
