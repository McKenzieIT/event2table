/**
 * useEventConfigs Hook
 *
 * Fetches a list of event node configs by game GID using React Query
 *
 * @param gameGid - The game GID to fetch configs for
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';
import type { EventConfig } from '../types';

/**
 * Fetches event node configs from the API
 *
 * @param gameGid - The game GID
 * @returns Array of event config objects
 */
async function fetchEventConfigs(gameGid: number): Promise<EventConfig[]> {
  const response = await fetch(
    `/event_node_builder/api/list?game_gid=${gameGid}`
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch event configs');
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error || 'Failed to fetch event configs');
  }

  return result.data;
}

/**
 * Hook to fetch event node configs by game GID
 *
 * @param gameGid - The game GID to fetch configs for, or undefined/null to disable query
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useEventConfigs(10000147);
 * ```
 */
export function useEventConfigs(
  gameGid: number | undefined | null
): UseQueryResult<EventConfig[], Error> {
  return useQuery({
    queryKey: queryKeys.eventConfigs.list(gameGid ?? 0),
    queryFn: () => fetchEventConfigs(gameGid!),
    enabled:
      gameGid !== undefined &&
      gameGid !== null, // Disable query if gameGid is undefined or null (but allow 0)
  });
}
