/**
 * GraphQL Query Optimizer
 * 
 * 查询优化工具,用于分析和优化GraphQL查询
 * 提供查询复杂度分析、字段去重、查询合并等功能
 */

class GraphQLQueryOptimizer {
  constructor() {
    this.queryCache = new Map();
    this.fieldUsageStats = new Map();
  }

  /**
   * 分析查询复杂度
   */
  analyzeQueryComplexity(query) {
    const complexity = {
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
   */
  isQueryTooComplex(query, maxScore = 1000) {
    const complexity = this.analyzeQueryComplexity(query);
    return complexity.score > maxScore;
  }

  /**
   * 优化查询 - 移除重复字段
   */
  optimizeQuery(query) {
    // 简单的字段去重
    const lines = query.split('\n');
    const seen = new Set();
    const optimized = [];

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
   */
  mergeQueries(queries) {
    const merged = {
      query: '',
      variables: {},
    };

    const queryParts = [];
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
   */
  trackFieldUsage(typeName, fieldName) {
    const key = `${typeName}.${fieldName}`;
    this.fieldUsageStats.set(key, (this.fieldUsageStats.get(key) || 0) + 1);
  }

  /**
   * 获取字段使用统计
   */
  getFieldUsageStats() {
    return Object.fromEntries(this.fieldUsageStats);
  }

  /**
   * 生成优化建议
   */
  generateOptimizationSuggestions(query) {
    const suggestions = [];
    const complexity = this.analyzeQueryComplexity(query);

    if (complexity.depth > 5) {
      suggestions.push({
        type: 'depth',
        severity: 'warning',
        message: `查询深度为${complexity.depth},建议拆分为多个查询`,
      });
    }

    if (complexity.fields > 20) {
      suggestions.push({
        type: 'breadth',
        severity: 'info',
        message: `查询字段数为${complexity.fields},考虑使用片段减少重复`,
      });
    }

    if (complexity.score > 500) {
      suggestions.push({
        type: 'complexity',
        severity: 'warning',
        message: `查询复杂度为${complexity.score},可能影响性能`,
      });
    }

    return suggestions;
  }

  /**
   * 缓存查询
   */
  cacheQuery(queryKey, query) {
    this.queryCache.set(queryKey, {
      query,
      timestamp: Date.now(),
    });
  }

  /**
   * 获取缓存的查询
   */
  getCachedQuery(queryKey) {
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
  clearCache() {
    this.queryCache.clear();
  }
}

// 创建单例实例
const queryOptimizer = new GraphQLQueryOptimizer();

// 导出实例和类
export { GraphQLQueryOptimizer, queryOptimizer };
export default queryOptimizer;
