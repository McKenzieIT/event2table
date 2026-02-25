import { useRef, useCallback } from 'react';
import { useQueryClient, QueryClient, QueryKey, QueryFunction } from '@tanstack/react-query';

interface PrefetchOptions {
  delay?: number;
  enabled?: boolean;
}

interface UsePrefetchOnHoverResult {
  prefetch: () => void;
  cancel: () => void;
  reset: () => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
  onFocus: () => void;
  onBlur: () => void;
  cleanup: () => void;
}

export function usePrefetchOnHover<T = unknown>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  options: PrefetchOptions = {}
): UsePrefetchOnHoverResult {
  const { delay = 200, enabled = true } = options;

  const queryClient = useQueryClient();
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hasPrefetchedRef = useRef(false);

  const prefetch = useCallback(() => {
    if (!enabled || hasPrefetchedRef.current) return;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      queryClient.prefetchQuery({
        queryKey,
        queryFn: queryFn as QueryFunction<T>,
        staleTime: 5 * 60 * 1000,
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

interface QueryItem<T = unknown> {
  queryKey: QueryKey;
  queryFn: QueryFunction<T>;
}

interface UsePrefetchMultipleOnHoverResult {
  prefetch: () => void;
  cancel: () => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}

export function usePrefetchMultipleOnHover<T = unknown>(
  queries: QueryItem<T>[],
  options: PrefetchOptions = {}
): UsePrefetchMultipleOnHoverResult {
  const { delay = 200, enabled = true } = options;

  const queryClient = useQueryClient();
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
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
          queryFn: queryFn as QueryFunction<T>,
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

interface IntersectionOptions {
  threshold?: number;
  enabled?: boolean;
}

interface UsePrefetchOnIntersectionResult {
  ref: React.RefObject<HTMLDivElement | null>;
  startObserving: () => void;
  stopObserving: () => void;
  reset: () => void;
}

export function usePrefetchOnIntersection<T = unknown>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  options: IntersectionOptions = {}
): UsePrefetchOnIntersectionResult {
  const { threshold = 0.1, enabled = true } = options;

  const queryClient = useQueryClient();
  const elementRef = useRef<HTMLDivElement | null>(null);
  const hasPrefetchedRef = useRef(false);
  const observerRef = useRef<IntersectionObserver | null>(null);

  const startObserving = useCallback(() => {
    if (!enabled || hasPrefetchedRef.current || !elementRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasPrefetchedRef.current) {
            queryClient.prefetchQuery({
              queryKey,
              queryFn: queryFn as QueryFunction<T>,
              staleTime: 5 * 60 * 1000,
            });
            hasPrefetchedRef.current = true;

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
  }, [queryClient, queryKey, queryFn, threshold, enabled]);

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
