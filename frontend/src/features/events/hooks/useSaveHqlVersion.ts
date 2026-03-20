/**
 * useSaveHqlVersion Hook
 *
 * Saves a new HQL version using React Query
 *
 * @returns React Query mutation object
 * @returns mutate - Function to trigger version save (callback-based)
 * @returns mutateAsync - Function to trigger version save (promise-based)
 * @returns isLoading - True if save is in progress
 * @returns isSuccess - True if save completed successfully
 * @returns isError - True if save failed
 * @returns error - Error object if save failed
 * @returns data - Saved version data
 *
 * @example
 * ```ts
 * const { mutate, isLoading, isSuccess } = useSaveHqlVersion();
 * mutate({
 *   event_id: 123,
 *   hql_content: 'SELECT * FROM table',
 *   change_description: 'Initial version'
 * });
 * ```
 */

import { useMutation, type UseMutationResult } from '@tanstack/react-query';
import { saveVersion, type SaveVersionRequest, type SaveVersionResponse } from '../api/hqlVersionApi';

/**
 * Hook to save a new HQL version
 *
 * @param options - Optional React Query mutation options
 * @returns React Query mutation object
 */
export function useSaveHqlVersion(
  options?: Partial<Parameters<typeof useMutation<SaveVersionResponse, Error, SaveVersionRequest>>[0]>
): UseMutationResult<SaveVersionResponse, Error, SaveVersionRequest> {
  return useMutation({
    mutationFn: (request: SaveVersionRequest) => saveVersion(request),
    ...options,
  });
}
