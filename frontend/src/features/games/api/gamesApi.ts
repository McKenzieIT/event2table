// @ts-nocheck - TypeScript检查暂禁用
/**
 * Games API Module
 *
 * API client for game-related operations
 *
 * @module gamesApi
 */

import type { Game, GameListResponse, GameDetailsResponse, FetchGamesOptions } from '../types';

/**
 * Fetches all games with optional filtering
 *
 * @param options - Query options for filtering games
 * @returns Promise resolving to array of games
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const games = await fetchGames({ search: 'poker', limit: 20 });
 * ```
 */
export async function fetchGames(
  options: FetchGamesOptions = {}
): Promise<Game[]> {
  const { page = 1, limit = 50, search = '', status = '' } = options;

  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });

  if (search) params.append('search', search);
  if (status) params.append('status', status);

  const response = await fetch(`/api/games?${params}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch games: ${response.statusText}`);
  }

  const result: GameListResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Games API request failed');
  }

  return result.data;
}

/**
 * Fetches a single game by GID
 *
 * @param gameGid - Game GID
 * @returns Promise resolving to game data
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const game = await fetchGameByGid(10000147);
 * const gameName = game.game_name;
 * ```
 */
export async function fetchGameByGid(gameGid: number): Promise<Game> {
  const response = await fetch(`/api/games/by-gid/${gameGid}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch game: ${response.statusText}`);
  }

  const result: GameDetailsResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Game API request failed');
  }

  return result.data;
}

/**
 * Fetches a single game by ID
 *
 * @param gameId - Game database ID
 * @returns Promise resolving to game data
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const game = await fetchGameById(1);
 * const gameName = game.game_name;
 * ```
 */
export async function fetchGameById(gameId: number): Promise<Game> {
  const response = await fetch(`/api/games/${gameId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch game: ${response.statusText}`);
  }

  const result: GameDetailsResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Game API request failed');
  }

  return result.data;
}
