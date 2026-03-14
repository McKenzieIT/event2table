/**
 * Event Types - 统一事件类型定义
 * Unified Event Type Definitions
 *
 * ⚠️ IMPORTANT: This is the ONLY place where the Event interface should be defined
 * All other files should import from here
 */

import type { Field } from './hql-types';

/**
 * Event - 事件实体
 * Unified Event interface used across the entire application
 */
export interface Event {
  /** Database ID */
  id: number;

  /** Event unique code */
  eventCode?: string;
  event_code?: string; // Deprecated: use eventCode

  /** Event display name */
  eventName?: string;
  event_name?: string;
  name?: string; // Deprecated: use eventName

  /** Event Chinese name */
  eventNameCn?: string;
  event_name_cn?: string; // Deprecated: use eventNameCn

  /** Game database ID */
  gameId?: number;
  game_id?: number; // Deprecated: use gameId

  /** Game business GID */
  gameGid: number;
  game_gid?: number; // Deprecated: use gameGid

  /** ODS database name */
  odsDb?: string;
  ods_db?: string; // Deprecated: use odsDb

  /** Source table name */
  sourceTable?: string;
  source_table?: string; // Deprecated: use sourceTable

  /** Target table name */
  targetTable?: string;
  target_table?: string; // Deprecated: use targetTable

  /** Category ID */
  categoryId?: number;
  category_id?: number; // Deprecated: use categoryId

  /** Category name */
  categoryName?: string;
  category_name?: string; // Deprecated: use categoryName

  /** Include in common parameters */
  includeInCommonParams?: boolean;
  include_in_common_params?: boolean; // Deprecated: use includeInCommonParams

  /** Description */
  description?: string;

  /** Creation timestamp */
  createdAt?: string;
  created_at?: string; // Deprecated: use createdAt

  /** Update timestamp */
  updatedAt?: string;
  updated_at?: string; // Deprecated: use updatedAt

  /** Associated fields for this event */
  fields?: Field[];
}

/**
 * Event creation request
 */
export interface EventCreateRequest {
  eventCode: string;
  eventName: string;
  eventNameCn?: string;
  gameGid: number;
  sourceTable?: string;
  categoryId?: number;
  description?: string;
}

/**
 * Event update request
 */
export interface EventUpdateRequest {
  id: number;
  eventCode?: string;
  eventName?: string;
  eventNameCn?: string;
  categoryId?: number;
  description?: string;
}

/**
 * Event list query options
 */
export interface EventListOptions {
  gameGid?: number;
  categoryId?: number;
  search?: string;
  page?: number;
  limit?: number;
}

/**
 * Event list response
 */
export interface EventListResponse {
  success: boolean;
  data: Event[];
  total?: number;
  page?: number;
  pageSize?: number;
}

/**
 * Event details response
 */
export interface EventDetailsResponse {
  success: boolean;
  data: Event;
}
