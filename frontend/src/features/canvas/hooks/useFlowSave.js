import { useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';

/**
 * Mutation hook for saving flow data (create or update)
 *
 * @returns {Object} React Query mutation object
 * @returns {Function} returns.mutate - Function to trigger mutation (callback-based)
 * @returns {Function} returns.mutateAsync - Function to trigger mutation (promise-based)
 * @returns {boolean} returns.isLoading - True if mutation is in progress
 * @returns {boolean} returns.isSuccess - True if mutation completed successfully
 * @returns {boolean} returns.isError - True if mutation failed
 * @returns {Error|null} returns.error - Error object if mutation failed
 * @returns {Object|null} returns.data - Returned data from successful mutation
 *
 * @example
 * const { mutate, isLoading, error } = useFlowSave();
 * mutate({ name: 'My Flow', game_gid: 10000147, nodes: [], edges: [] });
 */
export function useFlowSave() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (flowData) => {
      // Determine if create or update based on flowData.id
      const isUpdate = flowData.id != null;
      const url = isUpdate
        ? `/api/flows/${flowData.id}`
        : '/api/flows';
      const method = isUpdate ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(flowData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to save flow: ${response.statusText}`);
      }

      const result = await response.json();

      // Validate result.success before accessing data (consistent with query hooks)
      if (!result.success) {
        throw new Error(result.error || 'Failed to save flow');
      }

      return result.data;
    },
    onSuccess: (data) => {
      // Invalidate queries to refresh flow list
      // TODO: Optimize to invalidate only specific game's flows when game_gid is available
      queryClient.invalidateQueries({ queryKey: queryKeys.flows.lists() });
    },
  });
}
