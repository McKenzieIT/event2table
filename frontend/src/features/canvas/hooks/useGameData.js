/**
 * useGameData Hook
 *
 * Fetches game data by game_gid using React Query
 *
 * @param {number} gameGid - The game GID to fetch
 * @returns {UseQueryResult} React Query result object
 */
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';

/**
 * Fetches game data from the API
 * @param {number} gameGid - The game GID
 * @returns {Promise<Object>} Game data
 */
async function fetchGameData(gameGid) {
  const response = await fetch(`/api/games/by-gid/${gameGid}`);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch game data');
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error || 'Failed to fetch game data');
  }

  return result.data;
}

/**
 * Hook to fetch game data by GID
 *
 * @param {number|undefined|null} gameGid - The game GID to fetch, or undefined/null to disable query
 * @returns {UseQueryResult} React Query result object with data, error, isLoading, etc.
 */
export function useGameData(gameGid) {
  return useQuery({
    queryKey: queryKeys.games.detail(gameGid),
    queryFn: () => fetchGameData(gameGid),
    enabled: gameGid !== undefined && gameGid !== null, // Disable query if gameGid is undefined or null (but allow 0)
  });
}
