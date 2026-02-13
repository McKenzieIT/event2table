/**
 * Games Module Types
 *
 * Type definitions for game-related data structures
 */

/**
 * Game data structure
 */
export interface Game {
  id: number;
  game_gid: number;
  game_name: string;
  game_name_cn?: string;
  description?: string;
  status?: 'active' | 'inactive' | 'archived';
  created_at?: string;
  updated_at?: string;
}

/**
 * Game list response
 */
export interface GameListResponse {
  success: boolean;
  data: Game[];
  total?: number;
  page?: number;
  page_size?: number;
}

/**
 * Game details response
 */
export interface GameDetailsResponse {
  success: boolean;
  data: Game;
}

/**
 * Query options for fetching games
 */
export interface FetchGamesOptions {
  page?: number;
  limit?: number;
  search?: string;
  status?: string;
}
