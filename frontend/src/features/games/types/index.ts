/**
 * Games Module Types
 *
 * Type definitions for game-related data structures
 *
 * ⚠️ IMPORTANT: Game interface is now imported from @/shared/types/game-types
 * Do not define Game interface here - use the unified definition
 */

// Import Game type from shared types
import type { Game, GameStatus } from '@/shared/types/game-types';

// Re-export for convenience
export type { Game, GameStatus } from '@/shared/types/game-types';

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
