/**
 * useCacheStats Hook
 *
 * Fetches cache statistics using React Query
 *
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { getCacheStats } from '../api/monitoringApi';
import type { CacheStats } from '../types';

/**
 * Hook to fetch cache statistics
 *
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useCacheStats();
 * ```
 */
export function useCacheStats(): UseQueryResult<CacheStats, Error> {
  return useQuery({
    queryKey: ['monitoring', 'cache-stats'],
    queryFn: getCacheStats,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  });
}
