/**
 * useCancelTask Hook
 *
 * Mutation hook for cancelling a task
 *
 * @returns React Query mutation object
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { UseMutationResult } from '@tanstack/react-query';
import { cancelTask } from '../api/taskApi';

/**
 * Hook to cancel a task
 *
 * Features:
 * - Automatically invalidates task list and task detail queries on success
 * - Provides loading, success, and error states
 *
 * @returns React Query mutation object with mutate, mutateAsync, isLoading, isSuccess, isError, error, etc.
 *
 * @example
 * ```ts
 * const { mutateAsync, isLoading, error } = useCancelTask();
 * await mutateAsync('550e8400-e29b-41d4-a716-446655440000');
 * ```
 */
export function useCancelTask(): UseMutationResult<void, Error, string, unknown> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: cancelTask,
    onSuccess: () => {
      // Invalidate task list query
      queryClient.invalidateQueries({ queryKey: ['async-tasks', 'list'] });
      // Invalidate all task detail queries
      queryClient.invalidateQueries({ queryKey: ['async-tasks', 'detail'] });
      // Invalidate statistics query
      queryClient.invalidateQueries({ queryKey: ['async-tasks', 'statistics'] });
    },
  });
}
