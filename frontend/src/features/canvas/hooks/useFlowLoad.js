/**
 * useFlowLoad Hook
 *
 * Fetches a single flow by flow ID using React Query
 *
 * @param {number} flowId - The flow ID to fetch
 * @returns {UseQueryResult} React Query result object
 */
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';

/**
 * Fetches a single flow from the API
 * @param {number} flowId - The flow ID
 * @returns {Promise<Object>} Flow object
 */
async function fetchFlowData(flowId) {
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
 * @param {number|undefined|null} flowId - The flow ID to fetch, or undefined/null/0 to disable query
 * @returns {UseQueryResult} React Query result object with data, error, isLoading, etc.
 */
export function useFlowLoad(flowId) {
  return useQuery({
    queryKey: queryKeys.flows.detail(flowId),
    queryFn: () => fetchFlowData(flowId),
    enabled: flowId !== undefined && flowId !== null && flowId !== 0, // Disable query if flowId is undefined, null, or 0
  });
}
