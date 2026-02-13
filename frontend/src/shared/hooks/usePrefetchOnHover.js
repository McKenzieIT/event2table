import { useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

/**
 * Hook for prefetching query data on hover
 * Improves perceived performance by loading data before user clicks
 *
 * @param {string} queryKey - React Query key
 * @param {Function} queryFn - Query function to fetch data
 * @param {Object} options - Options
 * @param {number} options.delay - Delay in ms before prefetch (default: 200)
 * @param {boolean} options.enabled - Enable prefetch (default: true)
 * @returns {Object} - Event handlers for hover events
 */
export function usePrefetchOnHover(queryKey, queryFn, options = {}) {
  const {
    delay = 200,
    enabled = true,
  } = options;

  const queryClient = useQueryClient();
  const timeoutRef = useRef(null);
  const hasPrefetchedRef = useRef(false);

  const prefetch = useCallback(() => {
    if (!enabled || hasPrefetchedRef.current) return;

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      queryClient.prefetchQuery({
        queryKey,
        queryFn,
        staleTime: 5 * 60 * 1000, // 5 minutes
      });
      hasPrefetchedRef.current = true;
    }, delay);
  }, [queryClient, queryKey, queryFn, delay, enabled]);

  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    hasPrefetchedRef.current = false;
  }, []);

  // Event handlers for React elements
  const onMouseEnter = useCallback(() => {
    prefetch();
  }, [prefetch]);

  const onMouseLeave = useCallback(() => {
    cancel();
  }, [cancel]);

  const onFocus = useCallback(() => {
    prefetch();
  }, [prefetch]);

  const onBlur = useCallback(() => {
    cancel();
  }, [cancel]);

  // Cleanup on unmount
  const cleanup = useCallback(() => {
    cancel();
  }, [cancel]);

  return {
    prefetch,
    cancel,
    reset,
    onMouseEnter,
    onMouseLeave,
    onFocus,
    onBlur,
    cleanup,
  };
}

/**
 * Hook for prefetching multiple queries on hover
 * Useful for links that navigate to pages with multiple data needs
 *
 * @param {Array} queries - Array of {queryKey, queryFn} objects
 * @param {Object} options - Options
 * @returns {Object} - Event handlers
 */
export function usePrefetchMultipleOnHover(queries, options = {}) {
  const {
    delay = 200,
    enabled = true,
  } = options;

  const queryClient = useQueryClient();
  const timeoutRef = useRef(null);
  const hasPrefetchedRef = useRef(false);

  const prefetch = useCallback(() => {
    if (!enabled || hasPrefetchedRef.current) return;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      queries.forEach(({ queryKey, queryFn }) => {
        queryClient.prefetchQuery({
          queryKey,
          queryFn,
          staleTime: 5 * 60 * 1000,
        });
      });
      hasPrefetchedRef.current = true;
    }, delay);
  }, [queryClient, queries, delay, enabled]);

  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const onMouseEnter = useCallback(() => {
    prefetch();
  }, [prefetch]);

  const onMouseLeave = useCallback(() => {
    cancel();
  }, [cancel]);

  return {
    prefetch,
    cancel,
    onMouseEnter,
    onMouseLeave,
  };
}

/**
 * Hook for prefetching on viewport intersection
 * Useful for prefetching data when link becomes visible
 *
 * @param {string} queryKey - React Query key
 * @param {Function} queryFn - Query function
 * @param {Object} options - Options
 * @param {number} options.threshold - Intersection threshold (default: 0.1)
 * @returns {Object} - Ref and cleanup function
 */
export function usePrefetchOnIntersection(queryKey, queryFn, options = {}) {
  const {
    threshold = 0.1,
    enabled = true,
  } = options;

  const queryClient = useQueryClient();
  const elementRef = useRef(null);
  const hasPrefetchedRef = useRef(false);

  const observerRef = useRef(null);

  const startObserving = useCallback(() => {
    if (!enabled || hasPrefetchedRef.current || !elementRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasPrefetchedRef.current) {
            queryClient.prefetchQuery({
              queryKey,
              queryFn,
              staleTime: 5 * 60 * 1000,
            });
            hasPrefetchedRef.current = true;

            // Stop observing after prefetch
            if (observerRef.current) {
              observerRef.current.disconnect();
            }
          }
        });
      },
      { threshold }
    );

    if (elementRef.current) {
      observerRef.current.observe(elementRef.current);
    }
  }, [queryClient, queryKey, threshold, enabled]);

  const stopObserving = useCallback(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
      observerRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    hasPrefetchedRef.current = false;
  }, []);

  return {
    ref: elementRef,
    startObserving,
    stopObserving,
    reset,
  };
}

export default usePrefetchOnHover;
