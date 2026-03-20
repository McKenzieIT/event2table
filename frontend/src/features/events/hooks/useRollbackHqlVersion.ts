/**
 * useRollbackHqlVersion Hook
 *
 * Rolls back to a specific HQL version using React Query
 *
 * @returns React Query mutation object
 * @returns mutate - Function to trigger rollback (callback-based)
 * @returns mutateAsync - Function to trigger rollback (promise-based)
 * @returns isLoading - True if rollback is in progress
 * @returns isSuccess - True if rollback completed successfully
 * @returns isError - True if rollback failed
 * @returns error - Error object if rollback failed
 * @returns data - Rolled back version data
 *
 * @example
 * ```ts
 * const { mutate, isLoading, isSuccess } = useRollbackHqlVersion();
 * mutate({ version_id: 1 });
 * ```
 */

import { useMutation, type UseMutationResult } from '@tanstack/react-query';
import { rollbackToVersion, type RollbackVersionRequest, type RollbackVersionResponse } from '../api/hqlVersionApi';

/**
 * Hook to rollback to a specific HQL version
 *
 * @param options - Optional React Query mutation options
 * @returns React Query mutation object
 */
export function useRollbackHqlVersion(
  options?: Partial<Parameters<typeof useMutation<RollbackVersionResponse, Error, RollbackVersionRequest>>[0]>
): UseMutationResult<RollbackVersionResponse, Error, RollbackVersionRequest> {
  return useMutation({
    mutationFn: (request: RollbackVersionRequest) => rollbackToVersion(request),
    ...options,
  });
}
