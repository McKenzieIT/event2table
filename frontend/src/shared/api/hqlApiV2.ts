/**
 * HQL V2 API客户端
 *
 * 提供与HQL V2 API交互的方法
 */

/**
 * HQL生成请求接口
 * Interface for HQL generation request
 */
interface GenerateRequest {
  events: Array<{
    game_gid: number;
    event_id: number;
  }>;
  fields: Array<{
    fieldName: string;
    fieldType: 'base' | 'param' | 'custom' | 'fixed';
    alias?: string;
    jsonPath?: string;
    customExpression?: string;
    fixedValue?: any;
    aggregateFunc?: string;
  }>;
  where_conditions?: Array<{
    field: string;
    operator: string;
    value?: any;
    logicalOp?: 'AND' | 'OR';
  }>;
  options?: {
    mode?: 'single' | 'join' | 'union';
    sql_mode?: 'VIEW' | 'PROCEDURE' | 'CUSTOM';
    include_comments?: boolean;
  };
  debug?: boolean;
}

/**
 * HQL生成响应接口
 * Interface for HQL generation response
 */
interface GenerateResponse {
  success: boolean;
  data: {
    hql: string;
    generated_at: string;
  };
}

/**
 * 调试跟踪响应接口
 * Interface for debug trace response
 */
interface DebugTraceResponse {
  success: boolean;
  data: {
    hql: string;
    steps: Array<{
      step: string;
      result: any;
      count?: number;
    }>;
    events: any[];
    fields: any[];
  };
}

/**
 * HQL验证请求接口
 * Interface for HQL validation request
 */
interface ValidateRequest {
  hql: string;
}

/**
 * HQL验证响应接口
 * Interface for HQL validation response
 */
interface ValidateResponse {
  success: boolean;
  data: {
    is_valid: boolean;
    syntax_errors: string[];
  };
}

/**
 * 推荐字段响应接口
 * Interface for field recommendations response
 */
interface RecommendFieldsResponse {
  success: boolean;
  data: {
    suggestions: Array<{
      name: string;
      type: string;
      description: string;
    }>;
    count: number;
  };
}

/**
 * API状态响应接口
 * Interface for API status response
 */
interface StatusResponse {
  success: boolean;
  data: {
    version: string;
    status: string;
    features: string[];
    coming_soon: string[];
  };
}

/**
 * 缓存统计响应接口
 * Interface for cache statistics response
 */
interface CacheStatsResponse {
  success: boolean;
  data: {
    cache_size: number;
    cache_maxsize: number;
    cache_hits: number;
    cache_misses: number;
    hit_rate: number;
  };
}

/**
 * 清除缓存响应接口
 * Interface for clear cache response
 */
interface ClearCacheResponse {
  success: boolean;
  data: {
    message: string;
  };
}

/**
 * HQL V2 API客户端类
 * HQL V2 API Client Class
 *
 * @example
 * ```ts
 * const client = new HQLApiV2Client('/hql-preview-v2');
 * const result = await client.generate({
 *   events: [{ game_gid: 1001, event_id: 1 }],
 *   fields: [{ fieldName: 'user_id', fieldType: 'base' }]
 * });
 * console.log(result.data.hql);
 * ```
 */
class HQLApiV2Client {
  private baseUrl: string;

  /**
   * 创建HQL API客户端实例
   * Create HQL API client instance
   *
   * @param {string} baseUrl - API基础路径，默认为 '/hql-preview-v2'
   */
  constructor(baseUrl: string = '/hql-preview-v2') {
    this.baseUrl = baseUrl;
  }

  /**
   * 生成HQL语句
   * Generate HQL statement
   *
   * @param {GenerateRequest} requestData - HQL生成请求参数
   * @param {string} [customBaseUrl] - 自定义API基础路径（可选）
   * @returns {Promise<GenerateResponse>} HQL生成结果
   * @throws {Error} 当生成失败时抛出错误
   *
   * @example
   * ```ts
   * const result = await client.generate({
   *   events: [{ game_gid: 1001, event_id: 1 }],
   *   fields: [
   *     { fieldName: 'user_id', fieldType: 'base', alias: 'userId' }
   *   ],
   *   options: { mode: 'single', sql_mode: 'VIEW' }
   * });
   * console.log(result.data.hql);
   * ```
   */
  async generate(
    requestData: GenerateRequest,
    customBaseUrl?: string
  ): Promise<GenerateResponse> {
    const baseUrl = customBaseUrl || this.baseUrl;
    const url = `${baseUrl}/api/generate`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to generate HQL');
    }

    return response.json();
  }

  /**
   * 生成HQL（调试模式）
   */
  async generateDebug(
    requestData: GenerateRequest,
    customBaseUrl?: string
  ): Promise<DebugTraceResponse> {
    const baseUrl = customBaseUrl || this.baseUrl;
    const url = `${baseUrl}/api/generate-debug`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to generate HQL (debug)');
    }

    return response.json();
  }

  /**
   * 验证HQL语法
   */
  async validate(
    requestData: ValidateRequest,
    customBaseUrl?: string
  ): Promise<ValidateResponse> {
    const baseUrl = customBaseUrl || this.baseUrl;
    const url = `${baseUrl}/api/validate`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to validate HQL');
    }

    return response.json();
  }

  /**
   * 推荐字段
   */
  async recommendFields(
    params?: {
      event_name?: string;
      partial?: string;
      limit?: number;
    },
    customBaseUrl?: string
  ): Promise<RecommendFieldsResponse> {
    const baseUrl = customBaseUrl || this.baseUrl;
    const url = new URL(`${baseUrl}/api/recommend-fields`, window.location.origin);

    if (params?.event_name) {
      url.searchParams.append('event_name', params.event_name);
    }

    if (params?.partial) {
      url.searchParams.append('partial', params.partial);
    }

    if (params?.limit) {
      url.searchParams.append('limit', params.limit.toString());
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get field recommendations');
    }

    return response.json();
  }

  /**
   * 获取API状态
   */
  async getStatus(customBaseUrl?: string): Promise<StatusResponse> {
    const baseUrl = customBaseUrl || this.baseUrl;
    const url = `${baseUrl}/api/status`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get API status');
    }

    return response.json();
  }

  /**
   * 获取缓存统计
   */
  async getCacheStats(customBaseUrl?: string): Promise<CacheStatsResponse> {
    const baseUrl = customBaseUrl || this.baseUrl;
    const url = `${baseUrl}/api/cache-stats`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get cache stats');
    }

    return response.json();
  }

  /**
   * 清空缓存
   */
  async clearCache(customBaseUrl?: string): Promise<ClearCacheResponse> {
    const baseUrl = customBaseUrl || this.baseUrl;
    const url = `${baseUrl}/api/cache-clear`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to clear cache');
    }

    return response.json();
  }
}

// 导出单例实例
export const hqlApiV2 = new HQLApiV2Client();

// 导出类型
export type {
  GenerateRequest,
  GenerateResponse,
  DebugTraceResponse,
  ValidateRequest,
  ValidateResponse,
  RecommendFieldsResponse,
  StatusResponse,
  CacheStatsResponse,
  ClearCacheResponse,
};

// 导出类（用于创建自定义实例）
export { HQLApiV2Client };

export default hqlApiV2;
