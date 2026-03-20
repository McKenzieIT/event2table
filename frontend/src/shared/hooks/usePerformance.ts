/**
 * Performance Hooks for Event2Table
 * Collection of React hooks for performance optimization
 */

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import {
  debounce,
  throttle,
  LazyImageLoader,
  PerformanceMonitor,
  PerformanceMetrics,
} from '../utils/performanceUtils';

/**
 * useDebounce - Debounce value changes
 * @param value - Value to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced value
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * useDebouncedCallback - Create a debounced callback function
 * @param callback - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced callback function
 */
export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const callbackRef = useRef(callback);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  return useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callbackRef.current(...args);
      }, delay);
    },
    [delay]
  ) as T;
}

/**
 * useThrottle - Throttle value changes
 * @param value - Value to throttle
 * @param limit - Time limit in milliseconds
 * @returns Throttled value
 */
export function useThrottle<T>(value: T, limit: number): T {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastRan = useRef(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);

  return throttledValue;
}

/**
 * useThrottledCallback - Create a throttled callback function
 * @param callback - Function to throttle
 * @param limit - Time limit in milliseconds
 * @returns Throttled callback function
 */
export function useThrottledCallback<T extends (...args: any[]) => any>(
  callback: T,
  limit: number
): T {
  const callbackRef = useRef(callback);
  const lastRan = useRef(Date.now());

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  return useCallback(
    (...args: Parameters<T>) => {
      if (Date.now() - lastRan.current >= limit) {
        callbackRef.current(...args);
        lastRan.current = Date.now();
      }
    },
    [limit]
  ) as T;
}

/**
 * useLazyLoad - Lazy load images using Intersection Observer
 * @param src - Image source URL
 * @param options - Lazy load options
 * @returns Object with ref and loading state
 */
export function useLazyLoad(
  src: string,
  options: { rootMargin?: string; threshold?: number } = {}
) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const imgRef = useRef<HTMLImageElement>(null);
  const loaderRef = useRef<LazyImageLoader | null>(null);

  useEffect(() => {
    if (!imgRef.current) return;

    loaderRef.current = new LazyImageLoader(options);
    const img = imgRef.current;

    const handleLoad = () => {
      setIsLoaded(true);
      setIsLoading(false);
    };

    const handleError = () => {
      setIsLoading(false);
    };

    img.addEventListener('load', handleLoad);
    img.addEventListener('error', handleError);

    loaderRef.current.observe(img, src);

    return () => {
      img.removeEventListener('load', handleLoad);
      img.removeEventListener('error', handleError);
      if (loaderRef.current) {
        loaderRef.current.disconnect();
      }
    };
  }, [src, options]);

  return { imgRef, isLoaded, isLoading };
}

/**
 * useLazyLoadComponent - Lazy load a component
 * @param importFn - Function that imports the component
 * @param fallback - Fallback component while loading
 * @returns Lazy loaded component
 */
export function useLazyLoadComponent<T extends React.ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  fallback?: React.ComponentType
): T | null {
  const [Component, setComponent] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    importFn()
      .then((module) => {
        setComponent(() => module.default);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Failed to lazy load component:', error);
        setIsLoading(false);
      });
  }, [importFn]);

  if (isLoading && fallback) {
    const FallbackComponent = fallback as React.ComponentType;
    return FallbackComponent as any;
  }

  return Component;
}

/**
 * usePerformanceMonitor - Monitor performance metrics
 * @returns Object with metrics and performance score
 */
export function usePerformanceMonitor() {
  const [metrics, setMetrics] = useState<Partial<PerformanceMetrics>>({});
  const [score, setScore] = useState<number>(100);
  const monitorRef = useRef<PerformanceMonitor | null>(null);

  useEffect(() => {
    monitorRef.current = new PerformanceMonitor();

    const interval = setInterval(() => {
      if (monitorRef.current) {
        const currentMetrics = monitorRef.current.getMetrics();
        const currentScore = monitorRef.current.getScore();
        
        setMetrics(currentMetrics);
        setScore(currentScore);
      }
    }, 1000);

    return () => {
      clearInterval(interval);
      if (monitorRef.current) {
        monitorRef.current.destroy();
      }
    };
  }, []);

  return { metrics, score };
}

/**
 * useVirtualScroll - Virtual scrolling for large lists
 * @param items - Array of items to render
 * @param itemHeight - Height of each item
 * @param containerHeight - Height of the container
 * @param overscan - Number of items to render outside viewport
 * @returns Object with virtual scroll properties
 */
export function useVirtualScroll<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan: number = 3
) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const { visibleStart, visibleEnd, offsetY, totalHeight } = useMemo(() => {
    const visibleStart = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const visibleEnd = Math.min(
      items.length,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    const offsetY = visibleStart * itemHeight;
    const totalHeight = items.length * itemHeight;

    return { visibleStart, visibleEnd, offsetY, totalHeight };
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan]);

  const visibleItems = useMemo(() => {
    return items.slice(visibleStart, visibleEnd);
  }, [items, visibleStart, visibleEnd]);

  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(event.currentTarget.scrollTop);
  }, []);

  return {
    containerRef,
    visibleItems,
    offsetY,
    totalHeight,
    handleScroll,
    startIndex: visibleStart,
  };
}

/**
 * useMemoizedValue - Memoize a value with custom key generator
 * @param factory - Function that creates the value
 * @param deps - Dependencies
 * @param keyGenerator - Optional key generator
 * @returns Memoized value
 */
export function useMemoizedValue<T>(
  factory: () => T,
  deps: any[],
  keyGenerator?: (...args: any[]) => string
): T {
  return useMemo(factory, deps);
}

/**
 * useRafCallback - Throttle callback using requestAnimationFrame
 * @param callback - Function to throttle
 * @returns Throttled callback function
 */
export function useRafCallback<T extends (...args: any[]) => any>(
  callback: T
): T {
  const callbackRef = useRef(callback);
  const rafIdRef = useRef<number | null>(null);

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  return useCallback(
    (...args: Parameters<T>) => {
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
      }

      rafIdRef.current = requestAnimationFrame(() => {
        callbackRef.current(...args);
        rafIdRef.current = null;
      });
    },
    []
  ) as T;
}

/**
 * useIdleCallback - Run callback when browser is idle
 * @param callback - Function to run
 * @param timeout - Maximum time to wait
 */
export function useIdleCallback(
  callback: () => void,
  timeout: number = 2000
) {
  useEffect(() => {
    if ('requestIdleCallback' in window) {
      const id = (window as any).requestIdleCallback(callback, { timeout });
      return () => (window as any).cancelIdleCallback(id);
    } else {
      const id = setTimeout(callback, 1);
      return () => clearTimeout(id);
    }
  }, [callback, timeout]);
}

/**
 * useWindowSize - Get window size with debouncing
 * @param delay - Debounce delay in milliseconds
 * @returns Window size object
 */
export function useWindowSize(delay: number = 250) {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = debounce(() => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }, delay);

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [delay]);

  return windowSize;
}

/**
 * usePrevious - Get previous value
 * @param value - Current value
 * @returns Previous value
 */
export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

/**
 * useMountedState - Check if component is mounted
 * @returns Function that returns true if mounted
 */
export function useMountedState(): () => boolean {
  const mountedRef = useRef<boolean>(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return useCallback(() => mountedRef.current, []);
}
