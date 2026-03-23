/**
 * usePerformanceMetrics Hook
 *
 * Fetches performance metrics using React Query
 *
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';

import { getPerformanceMetrics } from '../api/monitoringApi';
import type { PerformanceMetrics } from '../types';

/**
 * Hook to fetch performance metrics
 *
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = usePerformanceMetrics();
 * ```
 */
export function usePerformanceMetrics(): UseQueryResult<PerformanceMetrics, Error> {
  return useQuery({
    queryKey: ['monitoring', 'performance-metrics'],
    queryFn: getPerformanceMetrics,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  });
}
