/**
 * SQL Optimizer API 客户端
 *
 * 提供 SQL 优化分析相关的 API 交互方法
 */

/**
 * SQL 分析结果接口
 */
export interface SQLAnalysisResult {
  performance_score: number;
  issues: Array<{
    type: string;
    severity: 'high' | 'medium' | 'low';
    message: string;
    location?: string;
  }>;
}

/**
 * SQL 优化建议接口
 */
export interface SQLOptimizationSuggestion {
  id: string;
  type: 'partition' | 'index' | 'query' | 'other';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  code?: string;
}

/**
 * 分析 SQL 请求接口
 */
export interface AnalyzeSQLRequest {
  sql: string;
  options?: {
    include_suggestions?: boolean;
    max_issues?: number;
  };
}

/**
 * 分析 SQL 响应接口
 */
export interface AnalyzeSQLResponse {
  success: boolean;
  data: {
    analysis: SQLAnalysisResult;
    suggestions: SQLOptimizationSuggestion[];
    optimized_sql?: string;
  };
  error?: string;
}

/**
 * 应用优化建议请求接口
 */
export interface ApplySuggestionRequest {
  original_sql: string;
  suggestion: SQLOptimizationSuggestion;
}

/**
 * 应用优化建议响应接口
 */
export interface ApplySuggestionResponse {
  success: boolean;
  data: {
    optimized_sql: string;
    applied_suggestions: SQLOptimizationSuggestion[];
  };
  error?: string;
}

/**
 * SQL Optimizer API 客户端类
 *
 * @example
 * ```ts
 * const client = new SQLOptimizerApiClient();
 * const result = await client.analyzeSQL({
 *   sql: 'SELECT * FROM events WHERE user_id = 123'
 * });
 * console.log(result.data.analysis.performance_score);
 * ```
 */
class SQLOptimizerApiClient {
  private baseUrl: string;

  /**
   * 创建 SQL Optimizer API 客户端实例
   *
   * @param {string} baseUrl - API 基础路径，默认为 '/api'
   */
  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  /**
   * 分析 SQL 语句
   *
   * @param {AnalyzeSQLRequest} requestData - SQL 分析请求参数
   * @returns {Promise<AnalyzeSQLResponse>} SQL 分析结果
   * @throws {Error} 当分析失败时抛出错误
   *
   * @example
   * ```ts
   * const result = await client.analyzeSQL({
   *   sql: 'SELECT * FROM events WHERE user_id = 123',
   *   options: {
   *     include_suggestions: true,
   *     max_issues: 10
   *   }
   * });
   * ```
   */
  async analyzeSQL(requestData: AnalyzeSQLRequest): Promise<AnalyzeSQLResponse> {
    const url = `${this.baseUrl}/sql-optimizer/analyze`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || 'Failed to analyze SQL');
    }

    return response.json();
  }

  /**
   * 应用优化建议
   *
   * @param {ApplySuggestionRequest} requestData - 应用建议请求参数
   * @returns {Promise<ApplySuggestionResponse>} 应用建议结果
   * @throws {Error} 当应用失败时抛出错误
   *
   * @example
   * ```ts
   * const result = await client.applySuggestion({
   *   original_sql: 'SELECT * FROM events WHERE user_id = 123',
   *   suggestion: {
   *     id: '1',
   *     type: 'partition',
   *     title: '添加分区过滤',
   *     description: '在 WHERE 子句中添加 dt 分区过滤',
   *     impact: 'high',
   *     code: "AND dt = '2024-01-01'"
   *   }
   * });
   * ```
   */
  async applySuggestion(requestData: ApplySuggestionRequest): Promise<ApplySuggestionResponse> {
    const url = `${this.baseUrl}/sql-optimizer/apply-suggestion`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || 'Failed to apply suggestion');
    }

    return response.json();
  }

  /**
   * 获取优化历史记录
   *
   * @param {Object} params - 查询参数
   * @param {number} [params.limit] - 返回记录数量限制
   * @param {number} [params.offset] - 偏移量
   * @returns {Promise<any>} 优化历史记录
   * @throws {Error} 当获取失败时抛出错误
   */
  async getOptimizationHistory(params?: {
    limit?: number;
    offset?: number;
  }): Promise<any> {
    const url = new URL(`${this.baseUrl}/sql-optimizer/history`, window.location.origin);

    if (params?.limit) {
      url.searchParams.append('limit', params.limit.toString());
    }

    if (params?.offset) {
      url.searchParams.append('offset', params.offset.toString());
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || 'Failed to get optimization history');
    }

    return response.json();
  }

  /**
   * 批量分析多个 SQL 语句
   *
   * @param {Array<{sql: string, id?: string}>} sqlList - SQL 语句列表
   * @returns {Promise<Array<AnalyzeSQLResponse>>} 分析结果列表
   * @throws {Error} 当分析失败时抛出错误
   */
  async batchAnalyzeSQL(
    sqlList: Array<{ sql: string; id?: string }>
  ): Promise<Array<AnalyzeSQLResponse>> {
    const url = `${this.baseUrl}/sql-optimizer/batch-analyze`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ sql_list: sqlList }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || 'Failed to batch analyze SQL');
    }

    return response.json();
  }
}

// 导出单例实例
export const sqlOptimizerApi = new SQLOptimizerApiClient();

// 导出类型
export type {
  SQLAnalysisResult,
  SQLOptimizationSuggestion,
  AnalyzeSQLRequest,
  AnalyzeSQLResponse,
  ApplySuggestionRequest,
  ApplySuggestionResponse,
};

// 导出类（用于创建自定义实例）
export { SQLOptimizerApiClient };

export default sqlOptimizerApi;
