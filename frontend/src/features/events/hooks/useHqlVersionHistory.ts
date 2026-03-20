/**
 * useHqlVersionHistory Hook
 *
 * Fetches HQL version history using React Query
 *
 * @param eventId - The event ID to fetch version history for
 * @returns React Query result object with version history data
 * @returns data - Version history response containing versions array and total count
 * @returns isLoading - True if fetching is in progress
 * @returns error - Error object if fetch failed
 * @returns refetch - Function to manually refetch the data
 *
 * @example
 * ```ts
 * const { data, isLoading, error, refetch } = useHqlVersionHistory(123);
 * if (data) {
 *   console.log(`Total versions: ${data.total}`);
 *   data.versions.forEach(version => {
 *     console.log(`Version ${version.version_number}: ${version.change_description}`);
 *   });
 * }
 * ```
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { getVersionHistory, type VersionHistoryResponse } from '../api/hqlVersionApi';

/**
 * Hook to fetch HQL version history
 *
 * @param eventId - The event ID to fetch version history for, or undefined/null to disable query
 * @returns React Query result object with version history data, error, isLoading, etc.
 */
export function useHqlVersionHistory(
  eventId: number | undefined | null
): UseQueryResult<VersionHistoryResponse, Error> {
  return useQuery({
    queryKey: ['hql-versions', 'history', eventId],
    queryFn: () => getVersionHistory(eventId!),
    enabled: !!eventId,
    staleTime: 30000, // 30 seconds
    gcTime: 300000, // 5 minutes (formerly cacheTime)
  });
}
