/**
 * useHqlVersionCompare Hook
 *
 * Compares two HQL versions using React Query
 *
 * @param versionId1 - The first version ID to compare
 * @param versionId2 - The second version ID to compare
 * @returns React Query mutation object
 * @returns mutate - Function to trigger version comparison (callback-based)
 * @returns mutateAsync - Function to trigger version comparison (promise-based)
 * @returns isLoading - True if comparison is in progress
 * @returns isSuccess - True if comparison completed successfully
 * @returns isError - True if comparison failed
 * @returns error - Error object if comparison failed
 * @returns data - Comparison result with diff and summary
 *
 * @example
 * ```ts
 * const { mutate, isLoading, data } = useHqlVersionCompare();
 * mutate({ version_id_1: 1, version_id_2: 2 });
 * if (data) {
 *   console.log(`Diff: ${data.diff}`);
 *   console.log(`Changes: ${data.summary.changes}`);
 * }
 * ```
 */

import { useMutation, type UseMutationResult } from '@tanstack/react-query';

import { compareVersions, type CompareVersionsRequest, type VersionDiff } from '../api/hqlVersionApi';

/**
 * Hook to compare two HQL versions
 *
 * @param options - Optional React Query mutation options
 * @returns React Query mutation object
 */
export function useHqlVersionCompare(
  options?: Partial<Parameters<typeof useMutation<VersionDiff, Error, CompareVersionsRequest>>[0]>
): UseMutationResult<VersionDiff, Error, CompareVersionsRequest> {
  return useMutation({
    mutationFn: (request: CompareVersionsRequest) => compareVersions(request),
    ...options,
  });
}
