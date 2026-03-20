/**
 * Performance Utilities for Event2Table
 * Collection of utility functions for performance optimization
 */

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

// Throttle utility
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

// Virtual Scroll utility
export interface VirtualScrollOptions {
  containerHeight: number;
  itemHeight: number;
  totalItems: number;
  overscan?: number;
}

export interface VirtualScrollResult {
  visibleStart: number;
  visibleEnd: number;
  offsetY: number;
  totalHeight: number;
}

export function calculateVirtualScroll(
  scrollTop: number,
  options: VirtualScrollOptions
): VirtualScrollResult {
  const { containerHeight, itemHeight, totalItems, overscan = 3 } = options;
  
  const totalHeight = totalItems * itemHeight;
  const visibleStart = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const visibleEnd = Math.min(
    totalItems,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );
  const offsetY = visibleStart * itemHeight;
  
  return {
    visibleStart,
    visibleEnd,
    offsetY,
    totalHeight,
  };
}

// Image Lazy Load utility
export interface LazyImageOptions {
  rootMargin?: string;
  threshold?: number;
  placeholder?: string;
}

export class LazyImageLoader {
  private observer: IntersectionObserver | null = null;
  private imageElements: Map<HTMLImageElement, string> = new Map();
  
  constructor(options: LazyImageOptions = {}) {
    if (typeof IntersectionObserver !== 'undefined') {
      this.observer = new IntersectionObserver(
        this.handleIntersection.bind(this),
        {
          rootMargin: options.rootMargin || '50px',
          threshold: options.threshold || 0.01,
        }
      );
    }
  }
  
  private handleIntersection(entries: IntersectionObserverEntry[]): void {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        const src = this.imageElements.get(img);
        
        if (src) {
          img.src = src;
          img.classList.add('loaded');
          this.imageElements.delete(img);
          
          if (this.observer) {
            this.observer.unobserve(img);
          }
        }
      }
    });
  }
  
  observe(img: HTMLImageElement, src: string): void {
    this.imageElements.set(img, src);
    
    if (this.observer) {
      this.observer.observe(img);
    } else {
      img.src = src;
    }
  }
  
  disconnect(): void {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    this.imageElements.clear();
  }
}

// Performance Monitor utility
export interface PerformanceMetrics {
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
  domContentLoaded: number;
  loadComplete: number;
}

export class PerformanceMonitor {
  private metrics: Partial<PerformanceMetrics> = {};
  private observers: Array<() => void> = [];
  
  constructor() {
    this.initializeObservers();
  }
  
  private initializeObservers(): void {
    if (typeof window === 'undefined' || !window.performance) {
      return;
    }
    
    // Navigation timing
    window.addEventListener('load', () => {
      const timing = performance.timing;
      if (timing) {
        this.metrics.ttfb = timing.responseStart - timing.navigationStart;
        this.metrics.domContentLoaded = timing.domContentLoadedEventEnd - timing.navigationStart;
        this.metrics.loadComplete = timing.loadEventEnd - timing.navigationStart;
      }
    });
    
    // First Contentful Paint
    if ('PerformanceObserver' in window) {
      try {
        const paintObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              this.metrics.fcp = entry.startTime;
            }
          }
        });
        paintObserver.observe({ entryTypes: ['paint'] });
        this.observers.push(() => paintObserver.disconnect());
      } catch (e) {
        console.warn('Paint observer not supported');
      }
      
      // Largest Contentful Paint
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          this.metrics.lcp = lastEntry.startTime;
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        this.observers.push(() => lcpObserver.disconnect());
      } catch (e) {
        console.warn('LCP observer not supported');
      }
      
      // First Input Delay
      try {
        const fidObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            this.metrics.fid = (entry as any).processingStart - entry.startTime;
          }
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
        this.observers.push(() => fidObserver.disconnect());
      } catch (e) {
        console.warn('FID observer not supported');
      }
      
      // Cumulative Layout Shift
      try {
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!(entry as any).hadRecentInput) {
              clsValue += (entry as any).value;
            }
          }
          this.metrics.cls = clsValue;
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
        this.observers.push(() => clsObserver.disconnect());
      } catch (e) {
        console.warn('CLS observer not supported');
      }
    }
  }
  
  getMetrics(): Partial<PerformanceMetrics> {
    return { ...this.metrics };
  }
  
  getScore(): number {
    const metrics = this.metrics;
    let score = 100;
    
    if (metrics.fcp && metrics.fcp > 1800) score -= 10;
    if (metrics.lcp && metrics.lcp > 2500) score -= 10;
    if (metrics.fid && metrics.fid > 100) score -= 10;
    if (metrics.cls && metrics.cls > 0.1) score -= 10;
    if (metrics.ttfb && metrics.ttfb > 600) score -= 10;
    
    return Math.max(0, score);
  }
  
  destroy(): void {
    this.observers.forEach(cleanup => cleanup());
    this.observers = [];
  }
}

// Request Animation Frame utility
export function rafThrottle<T extends (...args: any[]) => any>(
  func: T
): (...args: Parameters<T>) => void {
  let rafId: number | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
    }
    
    rafId = requestAnimationFrame(() => {
      func(...args);
      rafId = null;
    });
  };
}

// Idle Callback utility
export function runWhenIdle(callback: () => void, timeout: number = 2000): void {
  if ('requestIdleCallback' in window) {
    (window as any).requestIdleCallback(
      () => callback(),
      { timeout }
    );
  } else {
    setTimeout(callback, 1);
  }
}

// Memoization utility
export function memoize<T extends (...args: any[]) => any>(
  func: T,
  keyGenerator?: (...args: Parameters<T>) => string
): T {
  const cache = new Map<string, ReturnType<T>>();
  
  return ((...args: Parameters<T>) => {
    const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = func(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

// Batch updates utility
export function batchUpdates<T>(
  items: T[],
  batchSize: number,
  processor: (batch: T[]) => void
): void {
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    processor(batch);
  }
}
