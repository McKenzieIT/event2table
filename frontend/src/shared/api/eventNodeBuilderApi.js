/**
 * Event Node Builder API Client
 * 事件节点构建器API客户端
 *
 * @module eventNodeBuilder
 */

/**
 * @typedef {Object} Event
 * @property {number} id - 事件ID
 * @property {string} event_name - 事件名称（英文标识）
 * @property {string} display_name - 事件显示名称（中文）
 * @property {number} game_gid - 所属游戏GID
 * @property {'user'|'system'|'auto'} event_type - 事件类型
 * @property {string} created_at - 创建时间
 */

/**
 * @typedef {Object} FieldConfig
 * @property {string} field_name - 字段名称
 * @property {string} display_name - 显示名称
 * @property {string} data_type - 数据类型
 * @property {boolean} is_required - 是否必填
 */

/**
 * @typedef {Object} WhereCondition
 * @property {string} field - 字段名
 * @property {string} operator - 操作符
 * @property {string} value - 值
 * @property {string} logical_operator - 逻辑操作符（AND/OR）
 */

/**
 * @typedef {Object} EventConfig
 * @property {number} id - 配置ID
 * @property {number} game_gid - 游戏GID
 * @property {number} event_id - 事件ID
 * @property {string} name_en - 英文名称
 * @property {string} name_cn - 中文名称
 * @property {string} description - 描述
 * @property {FieldConfig[]} fields - 字段列表
 * @property {WhereCondition[]} where_conditions - WHERE条件
 * @property {string} created_at - 创建时间
 * @property {string} updated_at - 更新时间
 */

/**
 * @typedef {Object} APIResponse
 * @property {boolean} success - 是否成功
 * @property {string} [message] - 消息
 * @property {*} [data] - 响应数据
 * @property {string} [error] - 错误消息
 */

/**
 * 获取事件列表（分页+搜索）
 *
 * @param {number} gameGid - 游戏GID
 * @param {number} [page=1] - 页码
 * @param {string} [search=''] - 搜索关键词
 * @returns {Promise<Event[]>} 事件列表
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 获取第一页事件列表
 * const events = await fetchEvents(10000147, 1, '');
 * console.log(events[0].display_name); // "登录事件"
 */
export const fetchEvents = (gameGid, page = 1, search = '') => {
  const params = new URLSearchParams({
    game_gid: gameGid,
    page: page.toString(),
    limit: '50',
  });

  if (search) {
    params.append('search', search);
  }

  return fetch(`/event_node_builder/api/events?${params}`)
    .then(r => {
      if (!r.ok) {
        throw new Error(`Failed to fetch events: ${r.statusText}`);
      }
      return r.json();
    })
    .then(data => {
      // 显式验证响应结构
      if (!data.success) {
        throw new Error(data.message || 'Events API request failed');
      }
      // 返回完整响应对象，包含 success、data.events、has_more、page
      // EventSelector 需要 lastPage.success 来判断是否继续分页
      return data;
    })
    .catch(error => {
      console.error('[API] Failed to fetch events:', error);
      throw error; // 重新抛出错误，让调用者处理
    });
};

/**
 * @typedef {Object} EventParameter
 * @property {number} id - 参数ID
 * @property {string} param_name - 参数名称
 * @property {string} param_name_cn - 参数中文名
 * @property {string} param_type - 参数类型
 * @property {string} [default_value] - 默认值
 * @property {string} [description] - 描述
 */

/**
 * 获取参数字段列表
 *
 * @param {number} eventId - 事件ID
 * @returns {Promise<EventParameter[]>} 参数字段列表
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 获取事件的参数列表
 * const params = await fetchParams(123);
 * console.log(params[0].param_name); // "zone_id"
 */
export const fetchParams = (eventId) => {
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
      // 返回完整响应对象，包含 success、data
      // ParamSelector 期望 data.data 是参数数组
      return data;
    })
    .catch(error => {
      console.error('[API] Failed to fetch params:', error);
      throw error;
    });
};

/**
 * @typedef {Object} HQLPreviewRequest
 * @property {number} event_id - 事件ID
 * @property {FieldConfig[]} fields - 字段列表
 * @property {WhereCondition[]} where_conditions - WHERE条件
 */

/**
 * @typedef {Object} HQLPreviewResponse
 * @property {string} hql - 生成的HQL语句
 * @property {FieldConfig[]} fields - 字段信息
 * @property {number} preview_count - 预览行数
 */

/**
 * 预览HQL
 *
 * @param {HQLPreviewRequest} data - 请求数据
 * @returns {Promise<HQLPreviewResponse>} HQL预览结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 预览HQL
 * const preview = await previewHQL({
 *   event_id: 123,
 *   fields: [{ field_name: 'zone_id', display_name: '区服ID', data_type: 'int', is_required: true }],
 *   where_conditions: []
 * });
 * console.log(preview.hql); // "CREATE OR REPLACE VIEW..."
 */
export const previewHQL = (data) => {
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
 * @typedef {Object} SaveConfigRequest
 * @property {number} game_gid - 游戏GID
 * @property {number} event_id - 事件ID
 * @property {string} name_en - 英文名称
 * @property {string} name_cn - 中文名称
 * @property {string} description - 描述
 * @property {FieldConfig[]} fields - 字段列表
 * @property {WhereCondition[]} where_conditions - WHERE条件
 */

/**
 * 保存配置
 *
 * @param {SaveConfigRequest} configData - 配置数据
 * @returns {Promise<EventConfig>} 保存后的配置
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 保存新配置
 * const config = await saveConfig({
 *   game_gid: 10000147,
 *   event_id: 123,
 *   name_en: 'login_event',
 *   name_cn: '登录事件',
 *   description: '用户登录事件',
 *   fields: [],
 *   where_conditions: []
 * });
 * console.log(config.id); // 新配置ID
 */
export const saveConfig = (configData) => {
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
 * @param {number} configId - 配置ID
 * @param {Partial<SaveConfigRequest>} configData - 配置数据
 * @returns {Promise<EventConfig>} 更新后的配置
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 更新配置
 * const updated = await updateConfig(456, { name_cn: '新名称' });
 * console.log(updated.name_cn); // "新名称"
 */
export const updateConfig = (configId, configData) => {
  // configId应该作为node_id放在请求体中，而不是路径参数
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
 * @param {number} configId - 配置ID
 * @returns {Promise<EventConfig>} 配置数据
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 加载配置
 * const config = await loadConfig(456);
 * console.log(config.name_cn); // "登录事件"
 */
export const loadConfig = (configId) => {
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
 * @param {number} gameGid - 游戏GID
 * @param {number} [page=1] - 页码
 * @param {number} [limit=20] - 每页数量
 * @returns {Promise<EventConfig[]>} 配置列表
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 获取第一页配置列表
 * const configs = await fetchConfigList(10000147, 1, 20);
 * console.log(configs.length); // 20
 */
export const fetchConfigList = (gameGid, page = 1, limit = 20) => {
  return fetch(`/event_node_builder/api/list?game_gid=${gameGid}&page=${page}&limit=${limit}`)
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
 * @param {number} configId - 配置ID
 * @returns {Promise<{message: string}>} 删除结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 删除配置
 * const result = await deleteConfig(456);
 * console.log(result.message); // "Config deleted successfully"
 */
export const deleteConfig = (configId) => {
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
 * @param {number} nodeId - 节点ID
 * @returns {Promise<EventConfig>} 复制后的新节点配置
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 复制节点
 * const newNode = await copyNode(456);
 * console.log(newNode.id); // 新节点ID（不同于456）
 */
export const copyNode = (nodeId) => {
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
