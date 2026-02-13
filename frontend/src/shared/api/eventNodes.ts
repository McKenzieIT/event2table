/**
 * 事件节点管理 - API客户端
 * Event Nodes Management - API Client
 */

import type {
  EventNode,
  EventNodeFilters,
  EventNodeStats,
  EventNodeField,
  EventNodeFormData,
  ApiResponse,
  EventNodesListResponse,
} from '@shared/types/eventNodes';

const API_BASE = '/event_node_builder/api';
const LEGACY_API_BASE = '/api/event-nodes';

/**
 * 事件节点API客户端
 */
export const eventNodesApi = {
  /**
   * 获取事件节点列表（带搜索和筛选）
   */
  list: async (params: {
    game_gid: number;
    keyword?: string;
    today_modified?: boolean;
    event_id?: string;
    field_count_min?: string;
    field_count_max?: string;
    page?: number;
    per_page?: number;
  }): Promise<ApiResponse<EventNodesListResponse>> => {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        queryParams.append(key, String(value));
      }
    });

    const response = await fetch(`${API_BASE}/search?${queryParams}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch event nodes: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 获取统计信息
   */
  stats: async (gameGid: number): Promise<ApiResponse<EventNodeStats>> => {
    const response = await fetch(`${API_BASE}/stats?game_gid=${gameGid}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 获取单个节点详情
   */
  get: async (id: number): Promise<ApiResponse<EventNode>> => {
    const response = await fetch(`${LEGACY_API_BASE}/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch event node: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 创建新节点
   */
  create: async (data: EventNodeFormData): Promise<ApiResponse<EventNode>> => {
    const response = await fetch(LEGACY_API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`Failed to create event node: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 快速更新节点（仅名称和描述）
   */
  quickUpdate: async (id: number, data: { name_en?: string; name_cn: string; description?: string }): Promise<ApiResponse<EventNode>> => {
    const response = await fetch(`${API_BASE}/quick-update/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`Failed to quick update event node: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 更新节点
   */
  update: async (id: number, data: Partial<EventNodeFormData>): Promise<ApiResponse<EventNode>> => {
    const response = await fetch(`${LEGACY_API_BASE}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`Failed to update event node: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 删除节点
   */
  delete: async (id: number): Promise<ApiResponse<void>> => {
    const response = await fetch(`${LEGACY_API_BASE}/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete event node: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 批量删除节点
   */
  bulkDelete: async (ids: number[]): Promise<ApiResponse<void>> => {
    const response = await fetch(`${API_BASE}/bulk-delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node_ids: ids }),
    });
    if (!response.ok) {
      throw new Error(`Failed to bulk delete event nodes: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 获取节点的HQL代码
   */
  getHql: async (id: number): Promise<ApiResponse<{ hql: string }>> => {
    const response = await fetch(`${API_BASE}/node/${id}/hql`);
    if (!response.ok) {
      throw new Error(`Failed to fetch HQL: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 获取节点的字段列表
   */
  getFields: async (id: number): Promise<ApiResponse<{ fields: EventNodeField[] }>> => {
    const response = await fetch(`${API_BASE}/node/${id}/fields`);
    if (!response.ok) {
      throw new Error(`Failed to fetch fields: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 复制节点配置
   */
  copy: async (id: number, newName: string): Promise<ApiResponse<EventNode>> => {
    const response = await fetch(`${API_BASE}/node/${id}/copy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newName }),
    });
    if (!response.ok) {
      throw new Error(`Failed to copy event node: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * 获取事件列表（用于筛选下拉框）
   */
  getEvents: async (gameGid: number): Promise<ApiResponse<{ events: Array<{ id: number; event_name: string; event_name_cn: string }> }>> => {
    const response = await fetch(`${API_BASE}/events?game_gid=${gameGid}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch events: ${response.statusText}`);
    }
    return response.json();
  },
};
