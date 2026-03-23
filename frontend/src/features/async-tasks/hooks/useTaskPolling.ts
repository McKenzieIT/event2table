/**
 * useTaskPolling Hook
 *
 * Polls a task for status updates using React Query
 *
 * @param taskId - The task ID to poll
 * @param interval - Polling interval in milliseconds (default: 2000ms)
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';

import { getTask } from '../api/taskApi';
import type { Task, TaskStatus } from '../api/taskApi';

/**
 * Hook to poll a task for status updates
 *
 * Features:
 * - Automatically polls the task at specified interval
 * - Stops polling when task reaches terminal state (completed, failed, cancelled)
 * - Can be disabled by passing undefined/null taskId
 *
 * @param taskId - The task ID to poll, or undefined/null to disable polling
 * @param interval - Polling interval in milliseconds (default: 2000ms)
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useTaskPolling('550e8400-e29b-41d4-a716-446655440000', 2000);
 * 
 * // Check if task is still running
 * if (data?.status === 'running') {
 *   console.log(`Progress: ${data.progress}%`);
 * }
 * ```
 */
export function useTaskPolling(
  taskId: string | undefined | null,
  interval: number = 2000
): UseQueryResult<Task, Error> {
  return useQuery({
    queryKey: ['async-tasks', 'detail', taskId],
    queryFn: () => getTask(taskId!),
    enabled: !!taskId, // Disable query if taskId is undefined or null
    refetchInterval: (data) => {
      // Stop polling if task is in terminal state
      if (!data) return false;
      const terminalStates: TaskStatus[] = ['completed', 'failed', 'cancelled'];
      return terminalStates.includes(data.status) ? false : interval;
    },
    refetchIntervalInBackground: true, // Continue polling when tab is in background
    staleTime: 0, // Always fetch fresh data during polling
  });
}
