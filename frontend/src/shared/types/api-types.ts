/**
 * API类型定义
 * API Type Definitions
 *
 * 统一管理API响应类型和数据模型
 *
 * ⚠️ IMPORTANT: Event, Game, Field, and Parameter interfaces are now imported from their respective type files
 * Do not redefine them here - use the unified definitions
 */

// Import unified type definitions
import type { Event } from './event-types';
import type { Game } from './game-types';
import type { Field } from './hql-types';
import type { Parameter, EventParam } from './parameter-types';

// Re-export types for external use
export type { Event, Game, Field, Parameter, EventParam };

// Export individual types for convenience
export type { Event as EventType } from './event-types';
export type { Game as GameType } from './game-types';
export type { Field as FieldType } from './hql-types';
export type { Parameter as ParameterType } from './parameter-types';

// Export individual types for convenience
export type { Event as EventType } from './event-types';
export type { Game as GameType } from './game-types';
export type { Field as FieldType } from './hql-types';
export type { Parameter as ParameterType } from './parameter-types';

// ========== 基础类型 ==========

/** 通用API响应 */
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp?: string;
}

/** 分页信息 */
export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

/** 带分页的API响应 */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: Pagination;
}

// ========== 条件值类型 ==========

/** WHERE条件的值类型 */
export type ConditionValue = string | number | boolean | string[] | number[];

// ========== HQL相关类型 ==========

/** HQL生成数据 */
export interface HQLGenerateData {
  result: string;
  mode: string;
  event_count: number;
  field_count: number;
  generated_at?: string;
}

/** HQL生成响应 */
export interface HQLGenerateResponse extends ApiResponse<HQLGenerateData> {}

// ========== 事件相关类型 ==========

/** 事件列表响应 */
export interface EventsResponse extends PaginatedResponse<Event> {}

// ========== 字段相关类型 ==========

/** 字段列表响应 */
export interface FieldsResponse extends ApiResponse<Field[]> {}

// ========== 参数相关类型 ==========

/** 参数列表响应 */
export interface ParamsResponse extends ApiResponse<EventParam[]> {}

// ========== 游戏相关类型 ==========

/** 游戏列表响应 */
export interface GamesResponse extends ApiResponse<Game[]> {}

// ========== 错误类型 ==========

/** API错误 */
export interface ApiError {
  code?: string;
  message: string;
  details?: Record<string, unknown>;
}
