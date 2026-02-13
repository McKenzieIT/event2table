/**
 * HQL V2 API客户端
 *
 * 提供与HQL V2 API交互的方法
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

interface GenerateResponse {
  success: boolean;
  data: {
    hql: string;
    generated_at: string;
  };
}

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

interface ValidateRequest {
  hql: string;
}

interface ValidateResponse {
  success: boolean;
  data: {
    is_valid: boolean;
    syntax_errors: string[];
  };
}

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

interface StatusResponse {
  success: boolean;
  data: {
    version: string;
    status: string;
    features: string[];
    coming_soon: string[];
  };
}

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

interface ClearCacheResponse {
  success: boolean;
  data: {
    message: string;
  };
}

/**
 * HQL V2 API客户端类
 */
class HQLApiV2Client {
  private baseUrl: string;

  constructor(baseUrl: string = '/hql-preview-v2') {
    this.baseUrl = baseUrl;
  }

  /**
   * 生成HQL
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
