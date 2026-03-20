/**
 * Cache Utilities for Event2Table
 *
 * Provides helper functions for cache management including:
 * - Cache key generation
 * - Cache invalidation
 * - Cache prefetching
 * - Cache statistics tracking
 */

import { useQueryClient, QueryClient, QueryKey, QueryFunction } from '@tanstack/react-query';
import {
  getInvalidationKeys,
  PREFETCH_CONFIG,
  ApiType,
  getCacheStrategy,
  CacheStats,
} from '@/config/cacheConfig';

/**
 * Generate a cache key for queries
 * Ensures consistent key generation across the application
 */
export function generateCacheKey(
  resource: string,
  params?: Record<string, unknown>
): QueryKey {
  if (!params || Object.keys(params).length === 0) {
    return [resource];
  }
  
  // Sort params to ensure consistent keys
  const sortedParams = Object.keys(params)
    .sort()
    .reduce((acc, key) => {
      acc[key] = params[key];
      return acc;
    }, {} as Record<string, unknown>);
  
  return [resource, sortedParams];
}

/**
 * Invalidate cache entries based on mutation type
 */
export function invalidateCache(
  queryClient: QueryClient,
  mutationType: keyof typeof getInvalidationKeys,
  exact?: boolean
): void {
  const keys = getInvalidationKeys(mutationType);
  
  keys.forEach((key) => {
    if (exact) {
      queryClient.invalidateQueries({ queryKey: [key] });
    } else {
      queryClient.invalidateQueries({ queryKey: [key], refetchType: 'active' });
    }
  });
}

/**
 * Invalidate specific cache entry
 */
export function invalidateQuery(
  queryClient: QueryClient,
  queryKey: QueryKey
): void {
  queryClient.invalidateQueries({ queryKey });
}

/**
 * Clear all cache entries
 */
export function clearCache(queryClient: QueryClient): void {
  queryClient.clear();
}

/**
 * Prefetch a query with delay
 */
export function prefetchQuery<T = unknown>(
  queryClient: QueryClient,
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  delay: number = PREFETCH_CONFIG.HOVER_DELAY
): void {
  setTimeout(() => {
    queryClient.prefetchQuery({
      queryKey,
      queryFn,
      staleTime: PREFETCH_CONFIG.PREFETCH_STALE_TIME,
    });
  }, delay);
}

/**
 * Prefetch multiple queries
 */
export function prefetchQueries<T = unknown>(
  queryClient: QueryClient,
  queries: Array<{ queryKey: QueryKey; queryFn: QueryFunction<T> }>,
  delay: number = PREFETCH_CONFIG.HOVER_DELAY
): void {
  setTimeout(() => {
    queries.forEach(({ queryKey, queryFn }) => {
      queryClient.prefetchQuery({
        queryKey,
        queryFn,
        staleTime: PREFETCH_CONFIG.PREFETCH_STALE_TIME,
      });
    });
  }, delay);
}

/**
 * Get cache data without refetching
 */
export function getCacheData<T = unknown>(
  queryClient: QueryClient,
  queryKey: QueryKey
): T | undefined {
  return queryClient.getQueryData<T>(queryKey);
}

/**
 * Set cache data directly
 */
export function setCacheData<T = unknown>(
  queryClient: QueryClient,
  queryKey: QueryKey,
  data: T,
  updatedAt?: Date
): void {
  queryClient.setQueryData(queryKey, data, { updatedAt });
}

/**
 * Remove cache entry
 */
export function removeCacheData(
  queryClient: QueryClient,
  queryKey: QueryKey
): void {
  queryClient.removeQueries({ queryKey });
}

/**
 * Cache statistics tracker
 */
class CacheStatsTracker {
  private stats: CacheStats = {
    hits: 0,
    misses: 0,
    prefetches: 0,
    invalidations: 0,
  };

  recordHit(): void {
    this.stats.hits++;
  }

  recordMiss(): void {
    this.stats.misses++;
  }

  recordPrefetch(): void {
    this.stats.prefetches++;
  }

  recordInvalidation(): void {
    this.stats.invalidations++;
    this.stats.lastInvalidation = new Date();
  }

  getStats(): CacheStats {
    return { ...this.stats };
  }

  reset(): void {
    this.stats = {
      hits: 0,
      misses: 0,
      prefetches: 0,
      invalidations: 0,
    };
  }

  getHitRate(): number {
    const total = this.stats.hits + this.stats.misses;
    return total > 0 ? this.stats.hits / total : 0;
  }
}

// Global cache stats tracker instance
const globalCacheStats = new CacheStatsTracker();

/**
 * Get global cache statistics
 */
export function getCacheStats(): CacheStats {
  return globalCacheStats.getStats();
}

/**
 * Get cache hit rate
 */
export function getCacheHitRate(): number {
  return globalCacheStats.getHitRate();
}

/**
 * Reset cache statistics
 */
export function resetCacheStats(): void {
  globalCacheStats.reset();
}

/**
 * React hook for cache management
 */
export function useCacheManager() {
  const queryClient = useQueryClient();

  return {
    invalidate: (mutationType: keyof typeof getInvalidationKeys) =>
      invalidateCache(queryClient, mutationType),
    invalidateQuery: (queryKey: QueryKey) =>
      invalidateQuery(queryClient, queryKey),
    clear: () => clearCache(queryClient),
    prefetch: <T = unknown>(
      queryKey: QueryKey,
      queryFn: QueryFunction<T>,
      delay?: number
    ) => prefetchQuery(queryClient, queryKey, queryFn, delay),
    get: <T = unknown>(queryKey: QueryKey) =>
      getCacheData<T>(queryClient, queryKey),
    set: <T = unknown>(queryKey: QueryKey, data: T) =>
      setCacheData(queryClient, queryKey, data),
    remove: (queryKey: QueryKey) => removeCacheData(queryClient, queryKey),
    getStats: () => getCacheStats(),
    getHitRate: () => getCacheHitRate(),
  };
}

/**
 * Create a query with cache strategy
 */
export function createQueryOptions<T = unknown>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  apiType: ApiType
) {
  const strategy = getCacheStrategy(apiType);
  
  return {
    queryKey,
    queryFn,
    staleTime: strategy.staleTime,
    gcTime: strategy.gcTime,
    refetchOnWindowFocus: strategy.refetchOnWindowFocus,
    refetchOnReconnect: strategy.refetchOnReconnect,
    refetchOnMount: strategy.refetchOnMount,
  };
}

/**
 * Batch invalidate multiple mutation types
 */
export function batchInvalidate(
  queryClient: QueryClient,
  mutationTypes: Array<keyof typeof getInvalidationKeys>
): void {
  mutationTypes.forEach((type) => {
    invalidateCache(queryClient, type);
  });
}

/**
 * Prefetch on hover hook
 */
export function usePrefetchOnHover<T = unknown>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  delay: number = PREFETCH_CONFIG.HOVER_DELAY
) {
  const queryClient = useQueryClient();
  
  const handleMouseEnter = () => {
    prefetchQuery(queryClient, queryKey, queryFn, delay);
    globalCacheStats.recordPrefetch();
  };

  return {
    onMouseEnter: handleMouseEnter,
  };
}

/**
 * Prefetch on visibility hook
 */
export function usePrefetchOnVisibility<T = unknown>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  delay: number = PREFETCH_CONFIG.INTERSECTION_DELAY
) {
  const queryClient = useQueryClient();
  
  const handleIntersection = (entries: IntersectionObserverEntry[]) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        prefetchQuery(queryClient, queryKey, queryFn, delay);
        globalCacheStats.recordPrefetch();
      }
    });
  };

  return {
    onIntersection: handleIntersection,
  };
}

export default {
  generateCacheKey,
  invalidateCache,
  invalidateQuery,
  clearCache,
  prefetchQuery,
  prefetchQueries,
  getCacheData,
  setCacheData,
  removeCacheData,
  getCacheStats,
  getCacheHitRate,
  resetCacheStats,
  useCacheManager,
  createQueryOptions,
  batchInvalidate,
  usePrefetchOnHover,
  usePrefetchOnVisibility,
};
