/**
 * Game Types - 统一游戏类型定义
 * Unified Game Type Definitions
 *
 * ⚠️ IMPORTANT: This is the ONLY place where the Game interface should be defined
 * All other files should import from here
 */

/**
 * Game status enum
 */
export type GameStatus = 'active' | 'inactive' | 'archived';

/**
 * Game - 游戏实体
 * Unified Game interface used across the entire application
 */
export interface Game {
  /** Database ID */
  id: number;

  /** Game business GID (should be number, not string) */
  gid: number;

  /** Game display name */
  name: string;
  gameName?: string; // Deprecated: use name

  /** Game Chinese name */
  gameNameCn?: string;
  game_name_cn?: string; // Deprecated: use gameNameCn

  /** ODS database name */
  odsDb: string;
  ods_db?: string; // Deprecated: use odsDb

  /** DWD table prefix */
  dwdPrefix?: string;
  dwd_prefix?: string; // Deprecated: use dwdPrefix

  /** Game description */
  description?: string;

  /** Game status */
  status?: GameStatus;

  /** Event count (derived) */
  eventCount?: number;

  /** Creation timestamp */
  createdAt?: string;
  created_at?: string; // Deprecated: use createdAt

  /** Update timestamp */
  updatedAt?: string;
  updated_at?: string; // Deprecated: use updatedAt
}

/**
 * Game creation request
 */
export interface GameCreateRequest {
  gid: number;
  name: string;
  gameNameCn?: string;
  odsDb: string;
  dwdPrefix?: string;
  description?: string;
}

/**
 * Game update request
 */
export interface GameUpdateRequest {
  id: number;
  name?: string;
  gameNameCn?: string;
  description?: string;
  status?: GameStatus;
}

/**
 * Game list query options
 */
export interface GameListOptions {
  page?: number;
  limit?: number;
  search?: string;
  status?: GameStatus;
}

/**
 * Game list response
 */
export interface GameListResponse {
  success: boolean;
  data: Game[];
  total?: number;
  page?: number;
  pageSize?: number;
}

/**
 * Game details response
 */
export interface GameDetailsResponse {
  success: boolean;
  data: Game;
}

/**
 * Game context (for sidebar/menu)
 */
export interface GameContext {
  gid: number;
  name: string;
  odsDb: string;
  dwdPrefix?: string;
}
