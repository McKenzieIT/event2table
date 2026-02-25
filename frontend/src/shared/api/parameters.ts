/**
 * Parameters API Client
 * 参数管理API客户端
 *
 * @module parameters
 */

// ============================================
// Type Definitions
// ============================================

export interface Parameter {
  id: number;
  param_name: string;
  param_name_cn: string;
  param_type: 'string' | 'int' | 'float' | 'boolean' | 'json';
  game_gid: number | null;
  description?: string;
}

export interface ParameterResponse {
  data: {
    parameters: Parameter[];
    total: number;
    page: number;
    page_size: number;
    has_more: boolean;
  };
  success: boolean;
  message?: string;
}

export interface FetchParametersOptions {
  page?: number;
  limit?: number;
  search?: string;
  type?: string;
}

export interface ParameterUsage {
  event_id: number;
  event_name: string;
  event_display_name: string;
  usage_count: number;
}

export interface ParameterDetails {
  parameter: Parameter;
  usage_in_events: ParameterUsage[];
  is_public: boolean;
  total_usage: number;
}

// ============================================
// API Functions
// ============================================

/**
 * 获取游戏的所有唯一参数(去重)
 *
 * @param gameGid - 游戏GID
 * @param options - 查询选项
 * @returns 参数响应对象 (包含 data.parameters, data.total 等)
 * @throws {Error} 当API响应无效或请求失败时
 *
 * @example
 * const response = await fetchAllParameters(10000147, { page: 1, limit: 20 });
 * const paramName = response.parameters[0].param_name;
 */
export async function fetchAllParameters(
  gameGid: number,
  options: FetchParametersOptions = {}
): Promise<ParameterResponse['data']> {
  const {
    page = 1,
    limit = 50,
    search = '',
    type = ''
  } = options;

  const params = new URLSearchParams({
    game_gid: gameGid.toString(),
    page: page.toString(),
    limit: limit.toString()
  });

  if (search) params.append('search', search);
  if (type) params.append('type', type);

  const response = await fetch(`/api/parameters/all?${params}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch parameters: ${response.statusText}`);
  }

  const result = await response.json() as ParameterResponse;

  if (!result.success) {
    throw new Error(result.message || 'Parameters API request failed');
  }

  if (!result.data || !Array.isArray(result.data.parameters)) {
    throw new Error('Invalid API response: data.data.parameters is not an array');
  }

  return result.data;
}

/**
 * 获取参数详情(跨事件使用情况)
 *
 * @param paramName - 参数名
 * @param gameGid - 游戏GID
 * @returns 参数详情
 * @throws {Error} 当参数不存在（404）或请求失败时
 *
 * @example
 * const details = await fetchParameterDetails('zone_id', 10000147);
 * const usage = details.total_usage;
 */
export async function fetchParameterDetails(
  paramName: string,
  gameGid: number
): Promise<ParameterDetails> {
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

  if (!data.success) {
    throw new Error(data.message || 'Parameter details API request failed');
  }

  if (!data.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return data.data as ParameterDetails;
}
