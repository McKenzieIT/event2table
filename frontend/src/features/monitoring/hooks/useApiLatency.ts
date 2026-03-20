/**
 * useApiLatency Hook
 *
 * Fetches API latency data using React Query
 *
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { getApiLatency } from '../api/monitoringApi';
import type { ApiLatencyData } from '../types';

/**
 * Hook to fetch API latency data
 *
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useApiLatency();
 * ```
 */
export function useApiLatency(): UseQueryResult<ApiLatencyData, Error> {
  return useQuery({
    queryKey: ['monitoring', 'api-latency'],
    queryFn: getApiLatency,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  });
}
