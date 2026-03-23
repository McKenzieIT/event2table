/**
 * useTasks Hook
 *
 * Fetches task list using React Query
 *
 * @param filters - Task filters
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';

import { getTasks } from '../api/taskApi';
import type { Task, TaskFilters } from '../api/taskApi';

/**
 * Hook to fetch task list with optional filters
 *
 * @param filters - Optional filters for task list
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useTasks({ status: 'running' });
 * ```
 */
export function useTasks(
  filters?: TaskFilters
): UseQueryResult<Task[], Error> {
  return useQuery({
    queryKey: ['async-tasks', 'list', filters],
    queryFn: () => getTasks(filters),
    staleTime: 10000, // 10 seconds
  });
}
