// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * GraphQL Performance Monitor
 *
 * 性能监控工具,用于对比GraphQL和REST API的性能差异
 * 提供实时监控、数据收集和性能报告生成功能
 */

import type {
  RequestMetric,
  CacheStats,
  PerformanceReport as BasePerformanceReport,
  Recommendation,
  EventHandler,
} from '@/types/common';

/**
 * GraphQL请求指标 - 扩展基础请求指标
 */
interface GraphQLRequestMetric extends RequestMetric {
  /** 查询名称 */
  queryName: string;
  /** 查询变量JSON字符串 */
  variables: string;
  /** 时间戳 */
  timestamp: number;
  /** 查询名称 (别名) */
  name: string;
}

/**
 * REST API请求指标 - 使用基础请求指标
 */
type RESTRequestMetric = RequestMetric;

/**
 * GraphQL统计指标
 */
interface GraphQLMetrics {
  requests: GraphQLRequestMetric[];
  totalRequests: number;
  totalDuration: number;
  averageDuration: number;
  cacheHits: number;
  cacheMisses: number;
  cacheHitRate?: string;
}

/**
 * REST API统计指标
 */
interface RESTMetrics {
  requests: RESTRequestMetric[];
  totalRequests: number;
  totalDuration: number;
  averageDuration: number;
}

/**
 * 性能统计信息
 */
interface PerformanceStats {
  graphql: GraphQLMetrics;
  rest: RESTMetrics;
  comparison: {
    requestReduction: string;
    durationImprovement: string;
  };
}

/**
 * 性能报告 - 扩展基础性能报告
 */
interface PerformanceReport extends Omit<BasePerformanceReport, 'cacheStats' | 'recommendations'> {
  summary: {
    graphqlRequests: number;
    restRequests: number;
    requestReduction: string;
    averageGraphQLDuration: string;
    averageRESTDuration: string;
    durationImprovement: string;
    cacheHitRate: string;
  };
  details: {
    graphql: GraphQLMetrics;
    rest: RESTMetrics;
  };
}

/**
 * 监听器回调函数类型
 */
type MetricsListener = EventHandler<{
  type: 'graphql' | 'rest';
  metric: GraphQLRequestMetric | RESTRequestMetric;
}>;

/**
 * 内部指标数据结构
 */
interface InternalMetrics {
  graphql: {
    requests: GraphQLRequestMetric[];
    totalRequests: number;
    totalDuration: number;
    averageDuration: number;
    cacheHits: number;
    cacheMisses: number;
  };
  rest: {
    requests: RESTRequestMetric[];
    totalRequests: number;
    totalDuration: number;
    averageDuration: number;
  };
}

/**
 * GraphQL Performance Monitor类
 */
class GraphQLPerformanceMonitor {
  private metrics: InternalMetrics;
  private isEnabled: boolean;
  private listeners: MetricsListener[];

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
   * @param queryName - 查询名称
   * @param variables - 查询变量
   * @param duration - 请求持续时间(毫秒)
   * @param fromCache - 是否来自缓存
   */
  trackGraphQLRequest(
    queryName: string,
    variables: Record<string, unknown>,
    duration: number,
    fromCache: boolean = false
  ): void {
    if (!this.isEnabled) return;

    const metric: GraphQLRequestMetric = {
      name: queryName,
      duration,
      fromCache,
      queryName,
      variables: JSON.stringify(variables),
      timestamp: Date.now(),
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

    this.notifyListeners({ type: 'graphql', metric });
  }

  /**
   * 记录REST API请求
   * @param endpoint - API端点
   * @param method - HTTP方法
   * @param duration - 请求持续时间(毫秒)
   */
  trackRESTRequest(endpoint: string, method: string, duration: number): void {
    if (!this.isEnabled) return;

    const metric: RESTRequestMetric = {
      timestamp: Date.now(),
      name: endpoint,
      method,
      duration,
    };

    this.metrics.rest.requests.push(metric);
    this.metrics.rest.totalRequests++;
    this.metrics.rest.totalDuration += duration;
    this.metrics.rest.averageDuration =
      this.metrics.rest.totalDuration / this.metrics.rest.totalRequests;

    this.notifyListeners({ type: 'rest', metric });
  }

  /**
   * 获取性能统计
   * @returns 性能统计信息
   */
  getStats(): PerformanceStats {
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
   * @returns 性能报告
   */
  generateReport(): PerformanceReport {
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
   * @param stats - 性能统计信息
   * @returns 优化建议列表
   */
  generateRecommendations(stats: PerformanceStats): Recommendation[] {
    const recommendations: Recommendation[] = [];

    if (parseFloat(stats.graphql.cacheHitRate) < 50) {
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
   * @param callback - 监听器回调函数
   */
  addListener(callback: MetricsListener): void {
    this.listeners.push(callback);
  }

  /**
   * 通知监听器
   * @param event - 包含类型和指标的事件对象
   */
  private notifyListeners(event: { type: 'graphql' | 'rest'; metric: GraphQLRequestMetric | RESTRequestMetric }): void {
    this.listeners.forEach(callback => callback(event));
  }

  /**
   * 清除数据
   */
  clear(): void {
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
   * @param enabled - 是否启用
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }
}

// 创建单例实例
const performanceMonitor = new GraphQLPerformanceMonitor();

// 导出实例和类
export { GraphQLPerformanceMonitor, performanceMonitor };
export type {
  GraphQLRequestMetric,
  RESTRequestMetric,
  GraphQLMetrics,
  RESTMetrics,
  PerformanceStats,
  PerformanceReport,
  Recommendation,
  MetricsListener,
};
export default performanceMonitor;
