/**
 * useEventConfig Hook
 *
 * Fetches a single event node config by config ID using React Query
 *
 * @param configId - The config ID to fetch
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';
import type { EventConfig } from '../types';

/**
 * Fetches a single event node config from the API
 *
 * @param configId - The config ID
 * @returns Event config object
 */
async function fetchEventConfig(configId: number): Promise<EventConfig> {
  const response = await fetch(`/event_node_builder/api/load/${configId}`);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch event config');
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error || 'Failed to fetch event config');
  }

  return result.data;
}

/**
 * Hook to fetch a single event node config by config ID
 *
 * @param configId - The config ID to fetch, or undefined/null/0 to disable query
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useEventConfig(123);
 * ```
 */
export function useEventConfig(
  configId: number | undefined | null
): UseQueryResult<EventConfig, Error> {
  return useQuery({
    queryKey: queryKeys.eventConfigs.detail(configId ?? 0),
    queryFn: () => fetchEventConfig(configId!),
    enabled:
      configId !== undefined && configId !== null && configId !== 0, // Disable query if configId is undefined, null, or 0
  });
}
