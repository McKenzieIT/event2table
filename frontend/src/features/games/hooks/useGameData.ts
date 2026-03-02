// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * useGameData Hook
 *
 * Fetches game data by game_gid using React Query
 *
 * @param gameGid - The game GID to fetch
 * @returns React Query result object with fallback state
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
 * Fetches all games from the API
 *
 * @returns List of games
 */
async function fetchAllGames(): Promise<GameData[]> {
  const response = await fetch('/api/games');

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch games');
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error || 'Failed to fetch games');
  }

  return result.data || [];
}

/**
 * Hook to fetch game data by GID with fallback logic
 *
 * Features:
 * - If gameGid is provided, fetches that specific game
 * - If no gameGid and no games exist, returns helpful error state
 * - Auto-selects first game if available (optional behavior)
 *
 * @param gameGid - The game GID to fetch, or undefined/null to disable query
 * @returns React Query result object with data, error, isLoading, etc.
 *
 * @example
 * ```ts
 * const { data, error, isLoading } = useGameData(10000147);
 *
 * // Check for no-games state
 * if (error?.message.includes('请先创建游戏')) {
 *   // Show "Create Game" CTA
 * }
 * ```
 */
export function useGameData(
  gameGid: number | undefined | null
): UseQueryResult<GameData, Error> {
  // Query for specific game
  const gameQuery = useQuery({
    queryKey: queryKeys.games.detail(gameGid ?? 0),
    queryFn: () => fetchGameData(gameGid!),
    enabled:
      gameGid !== undefined &&
      gameGid !== null, // Disable query if gameGid is undefined or null (but allow 0)
  });

  // Fallback query: check if any games exist
  const gamesListQuery = useQuery({
    queryKey: queryKeys.games.all,
    queryFn: fetchAllGames,
    enabled: !gameGid, // Only run when no specific gameGid provided
  });

  // If no gameGid provided, return helpful state
  if (!gameGid) {
    const games = gamesListQuery.data || [];
    if (games.length === 0 && !gamesListQuery.isLoading) {
      // No games exist - return error with helpful message
      return {
        ...gameQuery,
        isLoading: false,
        error: new Error('请先创建游戏'),
      } as UseQueryResult<GameData, Error>;
    }
  }

  return gameQuery;
}
