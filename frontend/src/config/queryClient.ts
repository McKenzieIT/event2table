/**
 * React Query Configuration for Event2Table
 *
 * Centralized QueryClient setup with optimized cache strategies
 * Integrates with cacheConfig.ts for consistent caching behavior
 */

import { QueryClient } from '@tanstack/react-query';
import {
  DEFAULT_QUERY_CACHE_CONFIG,
  DEFAULT_MUTATION_CACHE_CONFIG,
  QUERY_KEY_CACHE_CONFIG,
} from './cacheConfig';

/**
 * Create and configure the QueryClient instance
 */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    queryCache: DEFAULT_QUERY_CACHE_CONFIG,
    mutationCache: DEFAULT_MUTATION_CACHE_CONFIG,
    
    defaultOptions: {
      queries: {
        // Default stale time - data is fresh for 5 minutes
        staleTime: 5 * 60 * 1000,
        
        // Default cache time - keep data for 15 minutes
        gcTime: 15 * 60 * 1000,
        
        // Refetch on window focus (disabled for config/reference data)
        refetchOnWindowFocus: false,
        
        // Refetch on reconnect
        refetchOnReconnect: true,
        
        // Don't refetch on mount by default
        refetchOnMount: false,
        
        // Retry failed queries
        retry: 1,
        
        // Retry delay with exponential backoff
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        
        // Throw errors by default
        throwOnError: false,
      },
      
      mutations: {
        // Retry failed mutations
        retry: 0,
        
        // Throw errors by default
        throwOnError: false,
      },
    },
  });
}

/**
 * Global QueryClient instance
 * This is the singleton instance used throughout the application
 */
export const queryClient = createQueryClient();

/**
 * Get cache configuration for a specific query key pattern
 */
export function getQueryCacheConfig(queryKey: readonly unknown[]) {
  if (!queryKey || queryKey.length === 0) {
    return undefined;
  }
  
  const key = queryKey[0] as string;
  
  // Match query key to cache configuration
  if (key === 'games') {
    return QUERY_KEY_CACHE_CONFIG.games;
  }
  
  if (key === 'events') {
    return QUERY_KEY_CACHE_CONFIG.events;
  }
  
  if (key === 'event-configs') {
    return QUERY_KEY_CACHE_CONFIG.eventConfigs;
  }
  
  if (key === 'parameters') {
    return QUERY_KEY_CACHE_CONFIG.parameters;
  }
  
  if (key === 'categories') {
    return QUERY_KEY_CACHE_CONFIG.categories;
  }
  
  if (key === 'flows') {
    return QUERY_KEY_CACHE_CONFIG.flows;
  }
  
  if (key === 'analytics') {
    return QUERY_KEY_CACHE_CONFIG.analytics;
  }
  
  return undefined;
}

/**
 * Configure query with appropriate cache strategy
 */
export function configureQuery(queryKey: readonly unknown[]) {
  const cacheConfig = getQueryCacheConfig(queryKey);
  
  if (!cacheConfig) {
    return {};
  }
  
  return cacheConfig;
}

/**
 * Reset the QueryClient
 * Useful for testing or clearing all caches
 */
export function resetQueryClient(): void {
  queryClient.clear();
}

/**
 * Prefetch multiple queries with optimized batching
 */
export function batchPrefetch(queries: Array<{
  queryKey: readonly unknown[];
  queryFn: () => Promise<unknown>;
}>): void {
  queries.forEach(({ queryKey, queryFn }) => {
    queryClient.prefetchQuery({
      queryKey,
      queryFn,
      staleTime: 5 * 60 * 1000,
    });
  });
}

/**
 * Get all active queries
 */
export function getActiveQueries() {
  return queryClient.getQueryCache().findAll({
    active: true,
  });
}

/**
 * Get all cached data
 */
export function getAllCacheData() {
  const queries = queryClient.getQueryCache().findAll();
  return queries.map((query) => ({
    queryKey: query.queryKey,
    state: query.state,
  }));
}

/**
 * Monitor cache health
 */
export function getCacheHealth() {
  const cache = queryClient.getQueryCache();
  const queries = cache.findAll();
  
  const active = queries.filter((q) => q.state.fetchStatus === 'fetching').length;
  const stale = queries.filter((q) => q.isStale()).length;
  const inactive = queries.filter((q) => !q.hasObservers()).length;
  
  return {
    total: queries.length,
    active,
    stale,
    inactive,
  };
}

export default queryClient;
