/**
 * 事件节点管理 - 类型定义
 * Event Nodes Management - Type Definitions
 */

/**
 * 事件节点接口
 */
export interface EventNode {
  id: number;
  game_id: number;
  game_gid: number;
  name_en: string;  // ✅ 使用与后端一致的字段名
  name_cn: string;
  description?: string;
  event_id: number | null;
  event_name?: string;
  event_name_cn?: string;
  config_json: string;
  field_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * 事件节点筛选条件
 */
export interface EventNodeFilters {
  keyword: string;
  todayModified: boolean;
  eventId: string;
  fieldCountMin: string;
  fieldCountMax: string;
}

/**
 * 事件节点统计信息
 */
export interface EventNodeStats {
  total_nodes: number;
  unique_events: number;
  avg_fields: number;
}

/**
 * 事件节点字段详情
 */
export interface EventNodeField {
  name: string;
  alias: string;
  dataType: string;
  baseType: string;
  mapping?: string;
}

/**
 * 创建/更新事件节点的表单数据
 */
export interface EventNodeFormData {
  name_en: string;
  name_cn: string;
  description?: string;
}

/**
 * API响应基础类型
 */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

/**
 * 事件节点列表响应
 */
export interface EventNodesListResponse {
  nodes: EventNode[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
