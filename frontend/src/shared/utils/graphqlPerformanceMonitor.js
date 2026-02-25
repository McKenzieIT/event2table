/**
 * GraphQL Performance Monitor
 * 
 * 性能监控工具,用于对比GraphQL和REST API的性能差异
 * 提供实时监控、数据收集和性能报告生成功能
 */

class GraphQLPerformanceMonitor {
  constructor() {
    this.metrics = {
      graphql: {
        requests: [],
        totalRequests: 0,
        totalDuration: 0,
        averageDuration: 0,
        cacheHits: 0,
        cacheMisses: 0,
      },
      rest: {
        requests: [],
        totalRequests: 0,
        totalDuration: 0,
        averageDuration: 0,
      }
    };
    
    this.isEnabled = true;
    this.listeners = [];
  }

  /**
   * 记录GraphQL请求
   */
  trackGraphQLRequest(queryName, variables, duration, fromCache = false) {
    if (!this.isEnabled) return;

    const metric = {
      timestamp: Date.now(),
      queryName,
      variables: JSON.stringify(variables),
      duration,
      fromCache,
    };

    this.metrics.graphql.requests.push(metric);
    this.metrics.graphql.totalRequests++;
    this.metrics.graphql.totalDuration += duration;
    this.metrics.graphql.averageDuration = 
      this.metrics.graphql.totalDuration / this.metrics.graphql.totalRequests;

    if (fromCache) {
      this.metrics.graphql.cacheHits++;
    } else {
      this.metrics.graphql.cacheMisses++;
    }

    this.notifyListeners('graphql', metric);
  }

  /**
   * 记录REST API请求
   */
  trackRESTRequest(endpoint, method, duration) {
    if (!this.isEnabled) return;

    const metric = {
      timestamp: Date.now(),
      endpoint,
      method,
      duration,
    };

    this.metrics.rest.requests.push(metric);
    this.metrics.rest.totalRequests++;
    this.metrics.rest.totalDuration += duration;
    this.metrics.rest.averageDuration = 
      this.metrics.rest.totalDuration / this.metrics.rest.totalRequests;

    this.notifyListeners('rest', metric);
  }

  /**
   * 获取性能统计
   */
  getStats() {
    return {
      graphql: {
        ...this.metrics.graphql,
        cacheHitRate: this.metrics.graphql.totalRequests > 0 
          ? (this.metrics.graphql.cacheHits / this.metrics.graphql.totalRequests * 100).toFixed(2) + '%'
          : '0%',
      },
      rest: {
        ...this.metrics.rest,
      },
      comparison: {
        requestReduction: this.metrics.rest.totalRequests > 0
          ? ((this.metrics.rest.totalRequests - this.metrics.graphql.totalRequests) / this.metrics.rest.totalRequests * 100).toFixed(2) + '%'
          : '0%',
        durationImprovement: this.metrics.rest.averageDuration > 0
          ? ((this.metrics.rest.averageDuration - this.metrics.graphql.averageDuration) / this.metrics.rest.averageDuration * 100).toFixed(2) + '%'
          : '0%',
      }
    };
  }

  /**
   * 生成性能报告
   */
  generateReport() {
    const stats = this.getStats();
    
    return {
      timestamp: new Date().toISOString(),
      summary: {
        graphqlRequests: stats.graphql.totalRequests,
        restRequests: stats.rest.totalRequests,
        requestReduction: stats.comparison.requestReduction,
        averageGraphQLDuration: `${stats.graphql.averageDuration.toFixed(2)}ms`,
        averageRESTDuration: `${stats.rest.averageDuration.toFixed(2)}ms`,
        durationImprovement: stats.comparison.durationImprovement,
        cacheHitRate: stats.graphql.cacheHitRate,
      },
      details: {
        graphql: stats.graphql,
        rest: stats.rest,
      },
      recommendations: this.generateRecommendations(stats),
    };
  }

  /**
   * 生成优化建议
   */
  generateRecommendations(stats) {
    const recommendations = [];

    if (stats.graphql.cacheHitRate < '50%') {
      recommendations.push({
        type: 'caching',
        priority: 'high',
        message: 'GraphQL缓存命中率较低,建议优化缓存策略',
      });
    }

    if (stats.graphql.averageDuration > stats.rest.averageDuration) {
      recommendations.push({
        type: 'performance',
        priority: 'high',
        message: 'GraphQL平均响应时间高于REST API,建议优化查询',
      });
    }

    if (stats.graphql.totalRequests > stats.rest.totalRequests) {
      recommendations.push({
        type: 'requests',
        priority: 'medium',
        message: 'GraphQL请求数量多于REST API,建议合并查询',
      });
    }

    return recommendations;
  }

  /**
   * 添加监听器
   */
  addListener(callback) {
    this.listeners.push(callback);
  }

  /**
   * 通知监听器
   */
  notifyListeners(type, metric) {
    this.listeners.forEach(callback => callback(type, metric));
  }

  /**
   * 清除数据
   */
  clear() {
    this.metrics = {
      graphql: {
        requests: [],
        totalRequests: 0,
        totalDuration: 0,
        averageDuration: 0,
        cacheHits: 0,
        cacheMisses: 0,
      },
      rest: {
        requests: [],
        totalRequests: 0,
        totalDuration: 0,
        averageDuration: 0,
      }
    };
  }

  /**
   * 启用/禁用监控
   */
  setEnabled(enabled) {
    this.isEnabled = enabled;
  }
}

// 创建单例实例
const performanceMonitor = new GraphQLPerformanceMonitor();

// 导出实例和类
export { GraphQLPerformanceMonitor, performanceMonitor };
export default performanceMonitor;
