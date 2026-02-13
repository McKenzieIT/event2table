/**
 * useFlowLoad Hook
 *
 * Fetches a single flow by flow ID using React Query
 *
 * @param flowId - The flow ID to fetch
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';
import type { SavedFlow } from '../types';

/**
 * Fetches a single flow from the API
 *
 * @param flowId - The flow ID
 * @returns Flow object
 */
async function fetchFlowData(flowId: number): Promise<SavedFlow> {
  const response = await fetch(`/api/flows/${flowId}`);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch flow');
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error || 'Failed to fetch flow');
  }

  return result.data;
}

/**
 * Hook to fetch a single flow by flow ID
 *
 * @param flowId - The flow ID to fetch, or undefined/null/0 to disable query
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useFlowLoad(123);
 * ```
 */
export function useFlowLoad(
  flowId: number | undefined | null
): UseQueryResult<SavedFlow, Error> {
  return useQuery({
    queryKey: queryKeys.flows.detail(flowId ?? 0),
    queryFn: () => fetchFlowData(flowId!),
    enabled:
      flowId !== undefined && flowId !== null && flowId !== 0, // Disable query if flowId is undefined, null, or 0
  });
}
