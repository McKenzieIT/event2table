/**
 * useFlowExecute Hook
 *
 * Mutation hook for executing a flow and generating HQL
 *
 * @returns React Query mutation object
 * @returns mutate - Function to trigger mutation (callback-based)
 * @returns mutateAsync - Function to trigger mutation (promise-based)
 * @returns isLoading - True if mutation is in progress
 * @returns isSuccess - True if mutation completed successfully
 * @returns isError - True if mutation failed
 * @returns error - Error object if mutation failed
 * @returns data - Returned data from successful mutation (contains HQL)
 *
 * @example
 * ```ts
 * const { mutateAsync, isLoading, error } = useFlowExecute();
 * const result = await mutateAsync({ flowId: 1 });
 * const hql = result.hql;
 * const execTime = result.execution_time;
 * ```
 */

import { useMutation } from '@tanstack/react-query';
import type { UseMutationResult } from '@tanstack/react-query';

interface ExecuteFlowVariables {
  flowId: number;
}

interface ExecutionResult {
  hql: string;
  execution_time?: number;
  metadata?: Record<string, unknown>;
}

export function useFlowExecute(): UseMutationResult<
  ExecutionResult,
  Error,
  ExecuteFlowVariables,
  unknown
> {
  return useMutation({
    mutationFn: async ({ flowId }: ExecuteFlowVariables) => {
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
        throw new Error(
          errorData.error || `Failed to execute flow: ${response.statusText}`
        );
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
