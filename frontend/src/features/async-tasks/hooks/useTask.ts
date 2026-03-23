/**
 * useTask Hook
 *
 * Fetches a single task by task_id using React Query
 *
 * @param taskId - The task ID to fetch
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';

import { getTask } from '../api/taskApi';
import type { Task } from '../api/taskApi';

/**
 * Hook to fetch a single task by ID
 *
 * @param taskId - The task ID to fetch, or undefined/null to disable query
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useTask('550e8400-e29b-41d4-a716-446655440000');
 * ```
 */
export function useTask(
  taskId: string | undefined | null
): UseQueryResult<Task, Error> {
  return useQuery({
    queryKey: ['async-tasks', 'detail', taskId],
    queryFn: () => getTask(taskId!),
    enabled: !!taskId, // Disable query if taskId is undefined or null
    staleTime: 5000, // 5 seconds
  });
}
