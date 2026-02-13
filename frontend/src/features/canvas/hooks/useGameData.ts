/**
 * useGameData Hook
 *
 * Fetches game data by game_gid using React Query
 *
 * @param gameGid - The game GID to fetch
 * @returns React Query result object
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { queryKeys } from '../api/queryKeys';

/**
 * Game data structure
 */
export interface GameData {
  id: number;
  game_gid: number;
  game_name: string;
  game_name_cn?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Fetches game data from the API
 *
 * @param gameGid - The game GID
 * @returns Game data
 */
async function fetchGameData(gameGid: number): Promise<GameData> {
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
 * @param gameGid - The game GID to fetch, or undefined/null to disable query
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useGameData(10000147);
 * ```
 */
export function useGameData(
  gameGid: number | undefined | null
): UseQueryResult<GameData, Error> {
  return useQuery({
    queryKey: queryKeys.games.detail(gameGid ?? 0),
    queryFn: () => fetchGameData(gameGid!),
    enabled:
      gameGid !== undefined &&
      gameGid !== null, // Disable query if gameGid is undefined or null (but allow 0)
  });
}
