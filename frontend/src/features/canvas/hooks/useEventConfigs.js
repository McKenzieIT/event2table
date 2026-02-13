/**
 * useEventConfigs Hook
 *
 * Fetches all event node configs for a game using React Query
 *
 * @param {number} gameGid - The game GID to fetch event configs for
 * @returns {UseQueryResult} React Query result object
 */
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';

/**
 * Fetches event node configs from the API
 * @param {number} gameGid - The game GID
 * @returns {Promise<Array>} Event configs array
 */
async function fetchEventConfigs(gameGid) {
  const response = await fetch(`/event_node_builder/api/list?game_gid=${gameGid}`);

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
 * @param {number|undefined|null} gameGid - The game GID to fetch, or undefined/null to disable query
 * @returns {UseQueryResult} React Query result object with data, error, isLoading, etc.
 */
export function useEventConfigs(gameGid) {
  return useQuery({
    queryKey: queryKeys.eventConfigs.list(gameGid),
    queryFn: () => fetchEventConfigs(gameGid),
    enabled: gameGid !== undefined && gameGid !== null, // Disable query if gameGid is undefined or null (but allow 0)
  });
}
