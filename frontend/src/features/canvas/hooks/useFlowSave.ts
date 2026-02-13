/**
 * useFlowSave Hook
 *
 * Mutation hook for saving flow data (create or update)
 *
 * @returns React Query mutation object
 * @returns mutate - Function to trigger mutation (callback-based)
 * @returns mutateAsync - Function to trigger mutation (promise-based)
 * @returns isLoading - True if mutation is in progress
 * @returns isSuccess - True if mutation completed successfully
 * @returns isError - True if mutation failed
 * @returns error - Error object if mutation failed
 * @returns data - Returned data from successful mutation
 *
 * @example
 * ```ts
 * const { mutate, isLoading, error } = useFlowSave();
 * mutate({ name: 'My Flow', game_gid: 10000147, nodes: [], edges: [] });
 * ```
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { UseMutationResult } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';
import type { SavedFlow, FlowData } from '../types';

interface SaveFlowVariables {
  id?: number;
  name: string;
  game_gid: number;
  flow_data: FlowData;
}

export function useFlowSave(): UseMutationResult<
  SavedFlow,
  Error,
  SaveFlowVariables,
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (flowData: SaveFlowVariables) => {
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
        throw new Error(
          errorData.error || `Failed to save flow: ${response.statusText}`
        );
      }

      const result = await response.json();

      // Validate result.success before accessing data (consistent with query hooks)
      if (!result.success) {
        throw new Error(result.error || 'Failed to save flow');
      }

      return result.data;
    },
    onSuccess: () => {
      // Invalidate queries to refresh flow list
      // TODO: Optimize to invalidate only specific game's flows when game_gid is available
      queryClient.invalidateQueries({ queryKey: queryKeys.flows.lists() });
    },
  });
}
