/**
 * useFieldRecommendations Hook
 *
 * Fetches field recommendations using React Query
 *
 * @returns React Query mutation object
 * @returns mutate - Function to trigger field recommendation (callback-based)
 * @returns mutateAsync - Function to trigger field recommendation (promise-based)
 * @returns isLoading - True if recommendation is in progress
 * @returns isSuccess - True if recommendation completed successfully
 * @returns isError - True if recommendation failed
 * @returns error - Error object if recommendation failed
 * @returns data - Returned recommendation data from successful request
 *
 * @example
 * ```ts
 * const { mutate, isLoading, data } = useFieldRecommendations();
 * mutate({ paramName: 'user_id', gameGid: 10000147 });
 * ```
 */

import { useMutation, type UseMutationResult } from '@tanstack/react-query';
import { getRecommendations, type FieldRecommendationRequest, type FieldRecommendationData } from '../api/fieldRecommendationApi';

/**
 * Hook to get field recommendations
 *
 * @param options - Optional React Query mutation options
 * @returns React Query mutation object
 */
export function useFieldRecommendations(
  options?: Partial<Parameters<typeof useMutation<FieldRecommendationData, Error, FieldRecommendationRequest>>[0]>
): UseMutationResult<FieldRecommendationData, Error, FieldRecommendationRequest> {
  return useMutation({
    mutationFn: (request: FieldRecommendationRequest) => getRecommendations(request),
    ...options,
  });
}
