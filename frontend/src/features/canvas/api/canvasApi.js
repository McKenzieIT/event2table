/**
 * Canvas API 调用模块
 * 与Flask后端通信
 *
 * @module canvasApi
 */

/**
 * @typedef {Object} FlowNode
 * @property {string} id - 节点ID
 * @property {string} type - 节点类型（event/config/output等）
 * @property {number} x - X坐标
 * @property {number} y - Y坐标
 * @property {Object} data - 节点数据
 */

/**
 * @typedef {Object} FlowEdge
 * @property {string} id - 边ID
 * @property {string} source - 源节点ID
 * @property {string} target - 目标节点ID
 */

/**
 * @typedef {Object} FlowData
 * @property {FlowNode[]} nodes - 节点列表
 * @property {FlowEdge[]} edges - 边列表
 */

/**
 * @typedef {Object} SavedFlow
 * @property {number} id - 流程ID
 * @property {number} game_id - 游戏ID
 * @property {string} name - 流程名称
 * @property {FlowData} flow_data - 流程数据
 * @property {string} created_at - 创建时间
 * @property {string} updated_at - 更新时间
 */

/**
 * 获取已保存的事件节点配置列表
 *
 * @param {number} gameGid - 游戏GID
 * @returns {Promise<EventConfig[]>} 配置列表
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 获取配置列表
 * const configs = await listEventConfigs(10000147);
 * console.log(configs[0].name_cn); // "登录事件"
 */
export async function listEventConfigs(gameGid) {
  try {
    const response = await fetch(
      `/event_node_builder/api/list?game_gid=${gameGid}`,
    );

    if (!response.ok) {
      throw new Error(`Failed to list event configs: ${response.statusText}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'List event configs request failed');
    }

    if (!Array.isArray(result.data)) {
      throw new Error('Invalid API response: data.data is not an array');
    }

    return result.data;
  } catch (error) {
    console.error("[API] Failed to list event configs:", error);
    throw error;
  }
}

/**
 * 加载单个事件节点配置
 *
 * @param {number} configId - 配置ID
 * @param {number} gameGid - 游戏GID
 * @returns {Promise<EventConfig>} 配置数据
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 加载配置
 * const config = await loadEventConfig(456, 10000147);
 * console.log(config.fields); // 字段列表
 */
export async function loadEventConfig(configId, gameGid) {
  try {
    const response = await fetch(
      `/event_node_builder/api/load/${configId}?game_gid=${gameGid}`,
    );

    if (!response.ok) {
      throw new Error(`Failed to load event config: ${response.statusText}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Load event config request failed');
    }

    return result.data;
  } catch (error) {
    console.error("[API] Failed to load event config:", error);
    throw error;
  }
}

/**
 * 保存节点流程
 *
 * @param {number} gameId - 游戏ID
 * @param {FlowData} flowData - 流程数据
 * @returns {Promise<SavedFlow>} 保存后的流程
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 保存流程
 * const flow = await saveFlow(10000147, {
 *   nodes: [{ id: '1', type: 'event', x: 100, y: 100, data: {} }],
 *   edges: []
 * });
 * console.log(flow.id); // 新流程ID
 */
export async function saveFlow(gameId, flowData) {
  try {
    const response = await fetch("/canvas/api/flows/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        game_id: gameId,
        flow_data: flowData,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to save flow: ${response.statusText}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Save flow request failed');
    }

    return result.data;
  } catch (error) {
    console.error("[API] Failed to save flow:", error);
    throw error;
  }
}

/**
 * 加载已保存的流程
 *
 * @param {number} flowId - 流程ID
 * @returns {Promise<SavedFlow>} 流程数据
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 加载流程
 * const flow = await loadFlow(789);
 * console.log(flow.flow_data.nodes); // 节点列表
 */
export async function loadFlow(flowId) {
  try {
    const response = await fetch(`/canvas/api/flows/${flowId}`);

    if (!response.ok) {
      throw new Error(`Failed to load flow: ${response.statusText}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Load flow request failed');
    }

    return result.data;
  } catch (error) {
    console.error("[API] Failed to load flow:", error);
    throw error;
  }
}

/**
 * @typedef {Object} ExecutionResult
 * @property {boolean} success - 是否成功
 * @property {string} hql - 生成的HQL语句
 * @property {Object} metadata - 元数据
 * @property {string} [error] - 错误消息
 */

/**
 * 执行HQL生成
 *
 * @param {FlowData} flowData - 流程数据
 * @returns {Promise<ExecutionResult>} 执行结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 执行流程生成HQL
 * const result = await executeFlow({
 *   nodes: [...],
 *   edges: [...]
 * });
 * console.log(result.hql); // "CREATE OR REPLACE VIEW..."
 */
export async function executeFlow(flowData) {
  try {
    const response = await fetch("/canvas/api/execute", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(flowData),
    });

    if (!response.ok) {
      throw new Error(`Failed to execute flow: ${response.statusText}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Execute flow request failed');
    }

    return result.data || result;
  } catch (error) {
    console.error("[API] Failed to execute flow:", error);
    throw error;
  }
}

/**
 * @typedef {Object} HealthCheckResponse
 * @property {boolean} healthy - 健康状态
 * @property {string} version - 版本号
 * @property {string} timestamp - 时间戳
 */

/**
 * Canvas健康检查
 *
 * @returns {Promise<HealthCheckResponse>} 健康状态
 * @throws {Error} 当API请求失败时
 *
 * @example
 * // 检查健康状态
 * const health = await healthCheck();
 * console.log(health.healthy); // true
 */
export async function healthCheck() {
  try {
    const response = await fetch("/canvas/api/canvas/health");

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || 'Health check request failed');
    }

    return result.data || result;
  } catch (error) {
    console.error("[API] Health check failed:", error);
    throw error;
  }
}
