/**
 * Parameters API Client
 * 参数管理API客户端
 *
 * @module parameters
 */

/**
 * @typedef {Object} Parameter
 * @property {number} id - 参数ID
 * @property {string} param_name - 参数名（英文）
 * @property {string} param_name_cn - 参数名（中文）
 * @property {'string'|'int'|'float'|'boolean'|'json'} param_type - 参数类型
 * @property {number|null} game_gid - 所属游戏GID（null表示公共参数）
 * @property {string} [description] - 参数描述
 */

/**
 * @typedef {Object} ParameterResponse
 * @property {Parameter[]} data - 参数列表
 * @property {boolean} success - 是否成功
 * @property {string} [message] - 错误消息
 * @property {number} [total] - 总数量
 * @property {number} [page] - 当前页码
 * @property {number} [page_size] - 每页数量
 */

/**
 * @typedef {Object} FetchParametersOptions
 * @property {number} [page=1] - 页码
 * @property {number} [limit=50] - 每页数量
 * @property {string} [search=''] - 搜索关键词
 * @property {string} [type=''] - 参数类型过滤
 */

/**
 * 获取游戏的所有唯一参数(去重)
 *
 * @param {number} gameGid - 游戏GID
 * @param {FetchParametersOptions} options - 查询选项
 * @returns {Promise<ParameterResponse>} 参数响应对象 (包含 data.parameters, data.total 等)
 * @throws {Error} 当API响应无效或请求失败时
 *
 * @example
 * // 获取游戏的第一个参数
 * const response = await fetchAllParameters(10000147, { page: 1, limit: 20 });
 * const paramName = response.parameters[0].param_name;
 * const total = response.total;
 */
export async function fetchAllParameters(gameGid, options = {}) {
  const {
    page = 1,
    limit = 50,
    search = '',
    type = ''
  } = options;

  const params = new URLSearchParams({
    game_gid: gameGid,
    page: page.toString(),
    limit: limit.toString()
  });

  if (search) params.append('search', search);
  if (type) params.append('type', type);

  const response = await fetch(`/api/parameters/all?${params}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch parameters: ${response.statusText}`);
  }

  const result = /** @type {ParameterResponse} */ (await response.json());

  // 显式验证响应结构
  if (!result.success) {
    throw new Error(result.message || 'Parameters API request failed');
  }

  // API返回结构: { success: true, data: { parameters: [...], total, page, has_more } }
  if (!result.data || !Array.isArray(result.data.parameters)) {
    throw new Error('Invalid API response: data.data.parameters is not an array');
  }

  // 返回完整响应对象，包含 data.parameters, data.total, data.page, data.has_more
  return result.data;
}

/**
 * @typedef {Object} ParameterUsage
 * @property {number} event_id - 事件ID
 * @property {string} event_name - 事件名称
 * @property {string} event_display_name - 事件显示名称
 * @property {number} usage_count - 使用次数
 */

/**
 * @typedef {Object} ParameterDetails
 * @property {Parameter} parameter - 参数基本信息
 * @property {ParameterUsage[]} usage_in_events - 在哪些事件中使用
 * @property {boolean} is_public - 是否为公共参数
 * @property {number} total_usage - 总使用次数
 */

/**
 * 获取参数详情(跨事件使用情况)
 *
 * @param {string} paramName - 参数名
 * @param {number} gameGid - 游戏GID
 * @returns {Promise<ParameterDetails>} 参数详情
 * @throws {Error} 当参数不存在（404）或请求失败时
 *
 * @example
 * // 获取参数详情
 * const details = await fetchParameterDetails('zone_id', 10000147);
 * const usage = details.total_usage;
 * const eventCount = details.usage_in_events.length;
 */
export async function fetchParameterDetails(paramName, gameGid) {
  const response = await fetch(
    `/api/parameters/${encodeURIComponent(paramName)}/details?game_gid=${gameGid}`
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Parameter not found: ${paramName}`);
    }
    throw new Error(`Failed to fetch parameter details: ${response.statusText}`);
  }

  const data = await response.json();

  // 显式验证响应结构
  if (!data.success) {
    throw new Error(data.message || 'Parameter details API request failed');
  }

  if (!data.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return data.data;
}
