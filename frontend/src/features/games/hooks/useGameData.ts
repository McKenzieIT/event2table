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
import { fetchGameByGid } from '../api';
import type { Game } from '../types';
import { queryKeys } from '../../canvas/api/queryKeys';

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
): UseQueryResult<Game, Error> {
  return useQuery({
    queryKey: queryKeys.games.detail(gameGid ?? 0),
    queryFn: () => fetchGameByGid(gameGid!),
    enabled:
      gameGid !== undefined &&
      gameGid !== null, // Disable query if gameGid is undefined or null (but allow 0)
  });
}
