/**
 * API类型定义
 * API Type Definitions
 * 
 * 统一管理API响应类型和数据模型
 */

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

/** 事件基本信息 */
export interface Event {
  id: number;
  name: string;
  event_name: string;
  event_name_cn: string;
  game_id: number;
  game_gid: number;
  source_table: string;
  target_table: string;
  category_id?: number;
  include_in_common_params?: boolean;
  created_at?: string;
  updated_at?: string;
}

/** 事件列表响应 */
export interface EventsResponse extends PaginatedResponse<Event> {}

// ========== 字段相关类型 ==========

/** 字段基本信息 */
export interface Field {
  id: number;
  name: string;
  type: string;
  param_name?: string;
  param_name_cn?: string;
  json_path?: string;
  template_id?: number;
  is_active?: boolean;
  version?: number;
}

/** 字段列表响应 */
export interface FieldsResponse extends ApiResponse<Field[]> {}

// ========== 参数相关类型 ==========

/** 事件参数 */
export interface EventParam {
  id: number;
  event_id: number;
  param_name: string;
  param_name_cn: string;
  param_type?: string;
  template_id?: number;
  param_description?: string;
  is_active?: boolean;
  version?: number;
}

/** 参数列表响应 */
export interface ParamsResponse extends ApiResponse<EventParam[]> {}

// ========== 游戏相关类型 ==========

/** 游戏基本信息 */
export interface Game {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

/** 游戏列表响应 */
export interface GamesResponse extends ApiResponse<Game[]> {}

// ========== 错误类型 ==========

/** API错误 */
export interface ApiError {
  code?: string;
  message: string;
  details?: Record<string, unknown>;
}
