/**
 * GraphQL Query Optimizer
 *
 * 查询优化工具,用于分析和优化GraphQL查询
 * 提供查询复杂度分析、字段去重、查询合并等功能
 */

import type {
  Recommendation,
  Priority,
} from '@/types/common';

/**
 * 查询复杂度分析结果
 */
interface QueryComplexity {
  depth: number;
  breadth: number;
  fields: number;
  score: number;
}

/**
 * GraphQL查询对象
 */
interface GraphQLQuery {
  query: string;
  variables?: Record<string, unknown>;
}

/**
 * 合并后的查询结果
 */
interface MergedQuery {
  query: string;
  variables: Record<string, unknown>;
}

/**
 * 优化建议
 */
interface OptimizationSuggestion {
  type: 'depth' | 'breadth' | 'complexity';
  severity: Priority;
  message: string;
}

/**
 * 缓存的查询
 */
interface CachedQuery {
  query: string;
  timestamp: number;
}

/**
 * 字段使用统计
 */
type FieldUsageStats = Record<string, number>;

/**
 * GraphQL Query Optimizer类
 */
class GraphQLQueryOptimizer {
  private queryCache: Map<string, CachedQuery>;
  private fieldUsageStats: Map<string, number>;

  constructor() {
    this.queryCache = new Map();
    this.fieldUsageStats = new Map();
  }

  /**
   * 分析查询复杂度
   * @param query - GraphQL查询字符串
   * @returns 查询复杂度分析结果
   */
  analyzeQueryComplexity(query: string): QueryComplexity {
    const complexity: QueryComplexity = {
      depth: 0,
      breadth: 0,
      fields: 0,
      score: 0,
    };

    // 简单的复杂度计算
    const lines = query.split('\n');
    let maxDepth = 0;
    let currentDepth = 0;

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.endsWith('{')) {
        currentDepth++;
        maxDepth = Math.max(maxDepth, currentDepth);
      }
      if (trimmed === '}') {
        currentDepth--;
      }
      if (trimmed && !trimmed.startsWith('#') && !trimmed.endsWith('{') && trimmed !== '}') {
        complexity.fields++;
      }
    });

    complexity.depth = maxDepth;
    complexity.breadth = complexity.fields;
    complexity.score = complexity.depth * 10 + complexity.breadth;

    return complexity;
  }

  /**
   * 检查查询是否超过复杂度限制
   * @param query - GraphQL查询字符串
   * @param maxScore - 最大复杂度分数
   * @returns 是否超过限制
   */
  isQueryTooComplex(query: string, maxScore: number = 1000): boolean {
    const complexity = this.analyzeQueryComplexity(query);
    return complexity.score > maxScore;
  }

  /**
   * 优化查询 - 移除重复字段
   * @param query - GraphQL查询字符串
   * @returns 优化后的查询字符串
   */
  optimizeQuery(query: string): string {
    // 简单的字段去重
    const lines = query.split('\n');
    const seen = new Set<string>();
    const optimized: string[] = [];

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#') && !trimmed.endsWith('{') && trimmed !== '}') {
        if (!seen.has(trimmed)) {
          seen.add(trimmed);
          optimized.push(line);
        }
      } else {
        optimized.push(line);
      }
    });

    return optimized.join('\n');
  }

  /**
   * 合并多个查询
   * @param queries - GraphQL查询数组
   * @returns 合并后的查询对象
   */
  mergeQueries(queries: GraphQLQuery[]): MergedQuery {
    const merged: MergedQuery = {
      query: '',
      variables: {},
    };

    const queryParts: string[] = [];
    let queryIndex = 0;

    queries.forEach(({ query, variables }) => {
      // 提取查询名称和内容
      const queryMatch = query.match(/query\s+(\w+)?\s*(\([^)]*\))?\s*\{([\s\S]*)\}/);
      if (queryMatch) {
        const queryName = queryMatch[1] || `Query${queryIndex}`;
        const queryBody = queryMatch[3].trim();

        queryParts.push(`${queryName}: ${queryBody}`);

        // 合并变量
        if (variables) {
          Object.assign(merged.variables, variables);
        }

        queryIndex++;
      }
    });

    merged.query = `query MergedQuery {\n${queryParts.join('\n')}\n}`;
    return merged;
  }

  /**
   * 记录字段使用统计
   * @param typeName - 类型名称
   * @param fieldName - 字段名称
   */
  trackFieldUsage(typeName: string, fieldName: string): void {
    const key = `${typeName}.${fieldName}`;
    this.fieldUsageStats.set(key, (this.fieldUsageStats.get(key) || 0) + 1);
  }

  /**
   * 获取字段使用统计
   * @returns 字段使用统计对象
   */
  getFieldUsageStats(): FieldUsageStats {
    return Object.fromEntries(this.fieldUsageStats) as FieldUsageStats;
  }

  /**
   * 生成优化建议
   * @param query - GraphQL查询字符串
   * @returns 优化建议列表
   */
  generateOptimizationSuggestions(query: string): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];
    const complexity = this.analyzeQueryComplexity(query);

    if (complexity.depth > 5) {
      suggestions.push({
        type: 'depth',
        severity: 'medium',
        message: `查询深度为${complexity.depth},建议拆分为多个查询`,
      });
    }

    if (complexity.fields > 20) {
      suggestions.push({
        type: 'breadth',
        severity: 'low',
        message: `查询字段数为${complexity.fields},考虑使用片段减少重复`,
      });
    }

    if (complexity.score > 500) {
      suggestions.push({
        type: 'complexity',
        severity: 'medium',
        message: `查询复杂度为${complexity.score},可能影响性能`,
      });
    }

    return suggestions;
  }

  /**
   * 缓存查询
   * @param queryKey - 查询键
   * @param query - 查询字符串
   */
  cacheQuery(queryKey: string, query: string): void {
    this.queryCache.set(queryKey, {
      query,
      timestamp: Date.now(),
    });
  }

  /**
   * 获取缓存的查询
   * @param queryKey - 查询键
   * @returns 缓存的查询字符串,如果不存在或已过期则返回null
   */
  getCachedQuery(queryKey: string): string | null {
    const cached = this.queryCache.get(queryKey);
    if (cached) {
      // 缓存有效期5分钟
      if (Date.now() - cached.timestamp < 5 * 60 * 1000) {
        return cached.query;
      }
      this.queryCache.delete(queryKey);
    }
    return null;
  }

  /**
   * 清除缓存
   */
  clearCache(): void {
    this.queryCache.clear();
  }
}

// 创建单例实例
const queryOptimizer = new GraphQLQueryOptimizer();

// 导出实例和类
export { GraphQLQueryOptimizer, queryOptimizer };
export type {
  QueryComplexity,
  GraphQLQuery,
  MergedQuery,
  OptimizationSuggestion,
  CachedQuery,
  FieldUsageStats,
};
export default queryOptimizer;
