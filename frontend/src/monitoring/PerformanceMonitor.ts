/**
 * PerformanceMonitor - 性能监控类
 * 用于追踪API调用、缓存命中率和页面加载性能
 */

export interface PageLoadMetrics {
  fcp?: number; // First Contentful Paint (ms)
  lcp?: number; // Largest Contentful Paint (ms)
  cls?: number; // Cumulative Layout Shift
  tbt?: number; // Total Blocking Time (ms)
}

export interface MetricsSummary {
  totalAPICalls: number;
  averageAPIDuration: number;
  cacheHitRate: number;
  totalPageLoads: number;
}

interface APICallMetric {
  endpoint: string;
  duration: number;
  timestamp: number;
}

interface CacheMetric {
  key: string;
  hit: boolean;
  timestamp: number;
}

interface PageLoadMetric {
  path: string;
  metrics: PageLoadMetrics;
  timestamp: number;
}

export class PerformanceMonitor {
  private static apiCalls: APICallMetric[] = [];
  private static cacheMetrics: CacheMetric[] = [];
  private static pageLoads: PageLoadMetric[] = [];

  /**
   * Track an API call with its duration
   * @param endpoint - API endpoint URL
   * @param duration - Request duration in milliseconds
   */
  static trackAPICall(endpoint: string, duration: number): void {
    const metric: APICallMetric = {
      endpoint,
      duration,
      timestamp: Date.now()
    };

    PerformanceMonitor.apiCalls.push(metric);

    console.log(`[API] ${endpoint}: ${duration}ms`);

    // Warn about slow API calls
    if (duration > 1000) {
      console.warn(`[Performance Warning] Slow API call: ${endpoint} took ${duration}ms`);
    }
  }

  /**
   * Track a cache hit or miss
   * @param cacheKey - Cache key
   * @param hit - Whether the cache was hit
   */
  static trackCacheHit(cacheKey: string, hit: boolean): void {
    const metric: CacheMetric = {
      key: cacheKey,
      hit,
      timestamp: Date.now()
    };

    PerformanceMonitor.cacheMetrics.push(metric);

    console.log(`[Cache] ${cacheKey}: ${hit ? 'HIT' : 'MISS'}`);
  }

  /**
   * Track page load performance metrics
   * @param path - Page path
   * @param metrics - Performance metrics
   */
  static trackPageLoad(path: string, metrics: PageLoadMetrics): void {
    const metric: PageLoadMetric = {
      path,
      metrics,
      timestamp: Date.now()
    };

    PerformanceMonitor.pageLoads.push(metric);

    console.log(`[PageLoad] ${path}`);
    console.log(`  FCP: ${metrics.fcp || 'N/A'}ms`);
    console.log(`  LCP: ${metrics.lcp || 'N/A'}ms`);
    console.log(`  CLS: ${metrics.cls ?? 'N/A'}`);
    console.log(`  TBT: ${metrics.tbt || 'N/A'}ms`);

    // Warn about poor performance
    if (metrics.fcp && metrics.fcp > 2000) {
      console.warn(`[Performance Warning] Slow FCP: ${metrics.fcp}ms (target: <2000ms)`);
    }
    if (metrics.lcp && metrics.lcp > 2500) {
      console.warn(`[Performance Warning] Slow LCP: ${metrics.lcp}ms (target: <2500ms)`);
    }
    if (metrics.cls && metrics.cls > 0.1) {
      console.warn(`[Performance Warning] High CLS: ${metrics.cls} (target: <0.1)`);
    }
    if (metrics.tbt && metrics.tbt > 300) {
      console.warn(`[Performance Warning] High TBT: ${metrics.tbt}ms (target: <300ms)`);
    }
  }

  /**
   * Get metrics summary
   * @returns Summary of all tracked metrics
   */
  static getMetricsSummary(): MetricsSummary {
    const totalAPICalls = PerformanceMonitor.apiCalls.length;
    const averageAPIDuration = totalAPICalls > 0
      ? PerformanceMonitor.apiCalls.reduce((sum, call) => sum + call.duration, 0) / totalAPICalls
      : 0;

    const cacheHits = PerformanceMonitor.cacheMetrics.filter(m => m.hit).length;
    const totalCacheCalls = PerformanceMonitor.cacheMetrics.length;
    const cacheHitRate = totalCacheCalls > 0 ? cacheHits / totalCacheCalls : 0;

    const totalPageLoads = PerformanceMonitor.pageLoads.length;

    return {
      totalAPICalls,
      averageAPIDuration: Math.round(averageAPIDuration),
      cacheHitRate: Math.round(cacheHitRate * 100) / 100,
      totalPageLoads
    };
  }

  /**
   * Get all API call metrics
   * @returns Array of API call metrics
   */
  static getAPICallMetrics(): APICallMetric[] {
    return [...PerformanceMonitor.apiCalls];
  }

  /**
   * Get all cache metrics
   * @returns Array of cache metrics
   */
  static getCacheMetrics(): CacheMetric[] {
    return [...PerformanceMonitor.cacheMetrics];
  }

  /**
   * Get all page load metrics
   * @returns Array of page load metrics
   */
  static getPageLoadMetrics(): PageLoadMetric[] {
    return [...PerformanceMonitor.pageLoads];
  }

  /**
   * Clear all tracked metrics
   */
  static clearMetrics(): void {
    PerformanceMonitor.apiCalls = [];
    PerformanceMonitor.cacheMetrics = [];
    PerformanceMonitor.pageLoads = [];
    console.log('[PerformanceMonitor] All metrics cleared');
  }

  /**
   * Get detailed performance report
   * @returns Detailed report object
   */
  static getDetailedReport(): object {
    const summary = PerformanceMonitor.getMetricsSummary();
    const slowestAPICalls = [...PerformanceMonitor.apiCalls]
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 5);

    const worstCacheKeys = PerformanceMonitor.cacheMetrics
      .filter(m => !m.hit)
      .reduce((acc, metric) => {
        acc[metric.key] = (acc[metric.key] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

    return {
      summary,
      slowestAPICalls,
      worstCacheKeys,
      timestamp: new Date().toISOString()
    };
  }
}
