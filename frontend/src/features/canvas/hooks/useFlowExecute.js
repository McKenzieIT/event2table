import { useMutation } from '@tanstack/react-query';

/**
 * Mutation hook for executing a flow and generating HQL
 *
 * @returns {Object} React Query mutation object
 * @returns {Function} returns.mutate - Function to trigger mutation (callback-based)
 * @returns {Function} returns.mutateAsync - Function to trigger mutation (promise-based)
 * @returns {boolean} returns.isLoading - True if mutation is in progress
 * @returns {boolean} returns.isSuccess - True if mutation completed successfully
 * @returns {boolean} returns.isError - True if mutation failed
 * @returns {Error|null} returns.error - Error object if mutation failed
 * @returns {Object|null} returns.data - Returned data from successful mutation (contains HQL)
 *
 * @example
 * const { mutateAsync, isLoading, error } = useFlowExecute();
 * const result = await mutateAsync({ flowId: 1 });
 * console.log(result.hql); // "CREATE OR REPLACE VIEW..."
 * console.log(result.execution_time); // 1.23
 */
export function useFlowExecute() {
  return useMutation({
    mutationFn: async ({ flowId }) => {
      // Validate flowId
      if (flowId == null) {
        throw new Error('flowId is required');
      }

      const response = await fetch('/api/flows/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ flow_id: flowId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to execute flow: ${response.statusText}`);
      }

      const result = await response.json();

      // Validate result.success before accessing data (consistent with other hooks)
      if (!result.success) {
        throw new Error(result.error || 'Failed to execute flow');
      }

      return result.data;
    },
  });
}
