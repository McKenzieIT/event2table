/**
 * Event Node Builder API Client
 * 事件节点构建器API客户端
 *
 * @module eventNodeBuilder
 */

// ============================================
// Type Definitions
// ============================================

export interface Event {
  id: number;
  event_name: string;
  display_name: string;
  game_gid: number;
  event_type: 'user' | 'system' | 'auto';
  created_at: string;
}

export interface FieldConfig {
  field_name: string;
  display_name: string;
  data_type: string;
  is_required: boolean;
}

export interface WhereCondition {
  field: string;
  operator: string;
  value: string;
  logical_operator: 'AND' | 'OR';
}

export interface EventConfig {
  id: number;
  game_gid: number;
  event_id: number;
  name_en: string;
  name_cn: string;
  description: string;
  fields: FieldConfig[];
  where_conditions: WhereCondition[];
  created_at: string;
  updated_at: string;
}

export interface APIResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface EventParameter {
  id: number;
  param_name: string;
  param_name_cn: string;
  param_type: string;
  default_value?: string;
  description?: string;
}

export interface HQLPreviewRequest {
  event_id: number;
  fields: FieldConfig[];
  where_conditions: WhereCondition[];
}

export interface HQLPreviewResponse {
  hql: string;
  fields: FieldConfig[];
  preview_count: number;
}

export interface SaveConfigRequest {
  game_gid: number;
  event_id: number;
  name_en: string;
  name_cn: string;
  description: string;
  fields: FieldConfig[];
  where_conditions: WhereCondition[];
}

export interface ConfigListResponse {
  configs: EventConfig[];
  has_more: boolean;
}

// ============================================
// API Functions
// ============================================

interface FetchEventsResponse {
  success: boolean;
  data: {
    events: Event[];
    has_more: boolean;
    page: number;
  };
  message?: string;
}

/**
 * 获取事件列表（分页+搜索）
 *
 * @param gameGid - 游戏GID
 * @param page - 页码
 * @param search - 搜索关键词
 * @returns 事件列表
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await fetchEvents(10000147, 1, '');
 * const events = response.data.events;
 */
export const fetchEvents = (
  gameGid: number,
  page: number = 1,
  search: string = ''
): Promise<FetchEventsResponse> => {
  const params = new URLSearchParams({
    game_gid: gameGid.toString(),
    page: page.toString(),
    limit: '50',
  });

  if (search) {
    params.append('search', search);
  }

  return fetch(`/api/events?${params}`)
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to fetch events: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.message || 'Events API request failed');
      }
      return data;
    })
    .catch(error => {
      console.error('[API] Failed to fetch events:', error);
      throw error;
    });
};

interface FetchParamsResponse {
  success: boolean;
  data: EventParameter[];
  message?: string;
}

/**
 * 获取参数字段列表
 *
 * @param eventId - 事件ID
 * @returns 参数字段列表
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await fetchParams(123);
 * const params = response.data;
 */
export const fetchParams = (eventId: number): Promise<FetchParamsResponse> => {
  return fetch(`/event_node_builder/api/params?event_id=${eventId}`)
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to fetch params: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.message || 'Params API request failed');
      }
      return data;
    })
    .catch(error => {
      console.error('[API] Failed to fetch params:', error);
      throw error;
    });
};

/**
 * 预览HQL
 *
 * @param data - 请求数据
 * @returns HQL预览结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await previewHQL({
 *   event_id: 123,
 *   fields: [{ field_name: 'zone_id', display_name: '区服ID', data_type: 'int', is_required: true }],
 *   where_conditions: []
 * });
 */
export const previewHQL = (data: HQLPreviewRequest): Promise<HQLPreviewResponse> => {
  return fetch('/event_node_builder/api/preview-hql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to preview HQL: ${r.statusText}`);
      }
      return r.json();
    })
    .then(response => {
      if (!response.success) {
        throw new Error(response.message || 'HQL preview request failed');
      }
      return response.data;
    })
    .catch(error => {
      console.error('[API] Failed to preview HQL:', error);
      throw error;
    });
};

/**
 * 保存配置
 *
 * @param configData - 配置数据
 * @returns 保存后的配置
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const config = await saveConfig({
 *   game_gid: 10000147,
 *   event_id: 123,
 *   name_en: 'login_event',
 *   name_cn: '登录事件',
 *   description: '用户登录事件',
 *   fields: [],
 *   where_conditions: []
 * });
 */
export const saveConfig = (configData: SaveConfigRequest): Promise<EventConfig> => {
  return fetch('/event_node_builder/api/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(configData),
  })
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to save config: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.message || 'Save config request failed');
      }
      return data.data;
    })
    .catch(error => {
      console.error('[API] Failed to save config:', error);
      throw error;
    });
};

/**
 * 更新配置
 *
 * @param configId - 配置ID
 * @param configData - 配置数据
 * @returns 更新后的配置
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const updated = await updateConfig(456, { name_cn: '新名称' });
 */
export const updateConfig = (
  configId: number,
  configData: Partial<SaveConfigRequest>
): Promise<EventConfig> => {
  const requestData = { ...configData, node_id: configId };

  return fetch(`/event_node_builder/api/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  })
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to update config: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.message || 'Update config request failed');
      }
      return data.data;
    })
    .catch(error => {
      console.error('[API] Failed to update config:', error);
      throw error;
    });
};

/**
 * 加载配置
 *
 * @param configId - 配置ID
 * @returns 配置数据
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const config = await loadConfig(456);
 */
export const loadConfig = (configId: number): Promise<EventConfig> => {
  return fetch(`/event_node_builder/api/load/${configId}`)
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to load config: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.message || 'Load config request failed');
      }
      return data.data;
    })
    .catch(error => {
      console.error('[API] Failed to load config:', error);
      throw error;
    });
};

/**
 * 获取配置列表
 *
 * @param gameGid - 游戏GID
 * @param page - 页码
 * @param limit - 每页数量
 * @returns 配置列表
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await fetchConfigList(10000147, 1, 20);
 * const configs = response.data.configs;
 */
export const fetchConfigList = (
  gameGid: number,
  page: number = 1,
  limit: number = 20
): Promise<ConfigListResponse> => {
  return fetch(
    `/event_node_builder/api/list?game_gid=${gameGid}&page=${page}&limit=${limit}`
  )
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to fetch config list: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.message || 'Fetch config list request failed');
      }
      if (!Array.isArray(data.data)) {
        throw new Error('Invalid API response: data.data is not an array');
      }
      return data.data;
    })
    .catch(error => {
      console.error('[API] Failed to fetch config list:', error);
      throw error;
    });
};

/**
 * 删除配置
 *
 * @param configId - 配置ID
 * @returns 删除结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * await deleteConfig(456);
 */
export const deleteConfig = (configId: number): Promise<{ message: string }> => {
  return fetch(`/event_node_builder/api/delete/${configId}`, {
    method: 'DELETE',
  })
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to delete config: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.message || 'Delete config request failed');
      }
      return { message: data.message || 'Config deleted successfully' };
    })
    .catch(error => {
      console.error('[API] Failed to delete config:', error);
      throw error;
    });
};

/**
 * 复制节点
 *
 * @param nodeId - 节点ID
 * @returns 复制后的新节点配置
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const newNode = await copyNode(456);
 */
export const copyNode = (nodeId: number): Promise<EventConfig> => {
  return fetch(`/event_node_builder/api/copy/${nodeId}`, {
    method: 'POST',
  })
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to copy node: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.message || 'Copy node request failed');
      }
      return data.data;
    })
    .catch(error => {
      console.error('[API] Failed to copy node:', error);
      throw error;
    });
};
