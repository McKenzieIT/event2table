/**
 * useFieldTypeInference Hook
 *
 * Infers field type using React Query
 *
 * @returns React Query mutation object
 * @returns mutate - Function to trigger field type inference (callback-based)
 * @returns mutateAsync - Function to trigger field type inference (promise-based)
 * @returns isLoading - True if inference is in progress
 * @returns isSuccess - True if inference completed successfully
 * @returns isError - True if inference failed
 * @returns error - Error object if inference failed
 * @returns data - Returned inference data from successful request
 *
 * @example
 * ```ts
 * const { mutate, isLoading, data } = useFieldTypeInference();
 * mutate({ paramName: 'user_id', gameGid: 10000147, sampleValues: ['123', '456'] });
 * ```
 */

import { useMutation, type UseMutationResult } from '@tanstack/react-query';

import { inferFieldType, type FieldTypeInferenceRequest, type FieldTypeInferenceData } from '../api/fieldRecommendationApi';

/**
 * Hook to infer field type
 *
 * @param options - Optional React Query mutation options
 * @returns React Query mutation object
 */
export function useFieldTypeInference(
  options?: Partial<Parameters<typeof useMutation<FieldTypeInferenceData, Error, FieldTypeInferenceRequest>>[0]>
): UseMutationResult<FieldTypeInferenceData, Error, FieldTypeInferenceRequest> {
  return useMutation({
    mutationFn: (request: FieldTypeInferenceRequest) => inferFieldType(request),
    ...options,
  });
}
