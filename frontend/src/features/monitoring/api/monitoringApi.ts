/**
 * Monitoring API Module
 *
 * API client for performance monitoring operations
 *
 * @module monitoringApi
 */

import type {
  CacheStatsResponse,
  CacheStats,
  ApiLatencyResponse,
  ApiLatencyData,
  PerformanceMetricsResponse,
  PerformanceMetrics,
} from '../types';

/**
 * Fetches cache statistics
 *
 * @returns Promise resolving to cache statistics
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const stats = await getCacheStats();
 * console.log(stats.hit_rate);
 * ```
 */
export async function getCacheStats(): Promise<CacheStats> {
  const response = await fetch('/api/monitoring/cache-stats');

  if (!response.ok) {
    throw new Error(`Failed to fetch cache stats: ${response.statusText}`);
  }

  const result: CacheStatsResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Cache stats API request failed');
  }

  if (!result.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return result.data;
}

/**
 * Fetches API latency data
 *
 * @returns Promise resolving to API latency data
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const latency = await getApiLatency();
 * console.log(latency.summary.overall_avg_latency_ms);
 * ```
 */
export async function getApiLatency(): Promise<ApiLatencyData> {
  const response = await fetch('/api/monitoring/api-latency');

  if (!response.ok) {
    throw new Error(`Failed to fetch API latency: ${response.statusText}`);
  }

  const result: ApiLatencyResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'API latency API request failed');
  }

  if (!result.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return result.data;
}

/**
 * Fetches performance metrics
 *
 * @returns Promise resolving to performance metrics
 * @throws Error when API request fails
 *
 * @example
 * ```ts
 * const metrics = await getPerformanceMetrics();
 * console.log(metrics.cpu_usage_percent);
 * ```
 */
export async function getPerformanceMetrics(): Promise<PerformanceMetrics> {
  const response = await fetch('/api/monitoring/performance-metrics');

  if (!response.ok) {
    throw new Error(`Failed to fetch performance metrics: ${response.statusText}`);
  }

  const result: PerformanceMetricsResponse = await response.json();

  if (!result.success) {
    throw new Error(result.message || 'Performance metrics API request failed');
  }

  if (!result.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return result.data;
}
