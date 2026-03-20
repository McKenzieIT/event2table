/**
 * Monitoring Feature Types
 *
 * Type definitions for performance monitoring data structures
 */

/**
 * Cache statistics response
 */
export interface CacheStatsResponse {
  success: boolean;
  data: CacheStats;
  message?: string;
}

/**
 * Cache statistics data
 */
export interface CacheStats {
  hit_rate: number;
  miss_rate: number;
  total_requests: number;
  cache_size: number;
  eviction_count: number;
  timestamp: string;
}

/**
 * API latency response
 */
export interface ApiLatencyResponse {
  success: boolean;
  data: ApiLatencyData;
  message?: string;
}

/**
 * API latency data point
 */
export interface ApiLatencyDataPoint {
  endpoint: string;
  method: string;
  avg_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  request_count: number;
  timestamp: string;
}

/**
 * API latency data
 */
export interface ApiLatencyData {
  endpoints: ApiLatencyDataPoint[];
  summary: {
    overall_avg_latency_ms: number;
    total_requests: number;
    slowest_endpoint: string;
  };
  timestamp: string;
}

/**
 * Performance metrics response
 */
export interface PerformanceMetricsResponse {
  success: boolean;
  data: PerformanceMetrics;
  message?: string;
}

/**
 * Performance metrics data
 */
export interface PerformanceMetrics {
  cpu_usage_percent: number;
  memory_usage_mb: number;
  memory_usage_percent: number;
  disk_usage_mb: number;
  disk_usage_percent: number;
  active_connections: number;
  uptime_seconds: number;
  timestamp: string;
}
