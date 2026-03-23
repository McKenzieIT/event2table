/**
 * useCommonPatterns Hook
 *
 * Fetches common field patterns using React Query
 *
 * @returns React Query result object
 * @returns data - Array of common field patterns
 * @returns error - Error object if request failed
 * @returns isLoading - True if request is in progress
 * @returns isError - True if request failed
 * @returns isSuccess - True if request completed successfully
 * @returns refetch - Function to manually refetch the data
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useCommonPatterns();
 * ```
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query';

import { getCommonPatterns, type FieldPattern } from '../api/fieldRecommendationApi';

/**
 * Hook to fetch common field patterns
 *
 * @param options - Optional React Query query options
 * @returns React Query result object with data, error, isLoading, etc.
 */
export function useCommonPatterns(
  options?: Partial<Parameters<typeof useQuery<FieldPattern[], Error>>[0]>
): UseQueryResult<FieldPattern[], Error> {
  return useQuery({
    queryKey: ['field-recommendations', 'patterns'],
    queryFn: getCommonPatterns,
    staleTime: 60000, // Consider data fresh for 1 minute
    gcTime: 300000, // Keep in cache for 5 minutes
    ...options,
  });
}
