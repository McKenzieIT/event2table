/**
 * useEventConfig Hook
 *
 * Fetches a single event node config by config ID using React Query
 *
 * @param {number} configId - The config ID to fetch
 * @returns {UseQueryResult} React Query result object
 */
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';

/**
 * Fetches a single event node config from the API
 * @param {number} configId - The config ID
 * @returns {Promise<Object>} Event config object
 */
async function fetchEventConfig(configId) {
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
 * @param {number|undefined|null} configId - The config ID to fetch, or undefined/null/0 to disable query
 * @returns {UseQueryResult} React Query result object with data, error, isLoading, etc.
 */
export function useEventConfig(configId) {
  return useQuery({
    queryKey: queryKeys.eventConfigs.detail(configId),
    queryFn: () => fetchEventConfig(configId),
    enabled: configId !== undefined && configId !== null && configId !== 0, // Disable query if configId is undefined, null, or 0
  });
}
