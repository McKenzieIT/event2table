/**
 * useTaskStatistics Hook
 *
 * Fetches task statistics using React Query
 *
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { getTaskStatistics } from '../api/taskApi';
import type { TaskStatisticsResponse } from '../api/taskApi';

/**
 * Hook to fetch task statistics
 *
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useTaskStatistics();
 * console.log(data?.total_tasks);
 * ```
 */
export function useTaskStatistics(): UseQueryResult<TaskStatisticsResponse['data'], Error> {
  return useQuery({
    queryKey: ['async-tasks', 'statistics'],
    queryFn: getTaskStatistics,
    staleTime: 30000, // 30 seconds
  });
}
