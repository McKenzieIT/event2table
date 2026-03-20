/**
 * monitoringApi Unit Tests
 *
 * Tests for monitoring API client functions
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getCacheStats, getApiLatency, getPerformanceMetrics } from '../api/monitoringApi';

// Mock fetch
global.fetch = vi.fn();

describe('monitoringApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getCacheStats', () => {
    it('should fetch and return cache statistics', async () => {
      const mockResponse = {
        success: true,
        data: {
          hit_rate: 0.85,
          miss_rate: 0.15,
          total_requests: 10000,
          cache_size: 512,
          eviction_count: 50,
          timestamp: '2026-03-20T00:00:00Z',
        },
      };

      (global.fetch as vi.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await getCacheStats();

      expect(result).toEqual(mockResponse.data);
      expect(fetch).toHaveBeenCalledWith('/api/monitoring/cache-stats');
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as vi.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Internal Server Error',
      } as Response);

      await expect(getCacheStats()).rejects.toThrow('Failed to fetch cache stats: Internal Server Error');
    });

    it('should throw error when API returns failure', async () => {
      const mockResponse = {
        success: false,
        message: 'Cache server error',
      };

      (global.fetch as vi.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      await expect(getCacheStats()).rejects.toThrow('Cache server error');
    });
  });

  describe('getApiLatency', () => {
    it('should fetch and return API latency data', async () => {
      const mockResponse = {
        success: true,
        data: {
          endpoints: [
            {
              endpoint: '/api/events',
              method: 'GET',
              avg_latency_ms: 150,
              p50_latency_ms: 100,
              p95_latency_ms: 300,
              p99_latency_ms: 500,
              request_count: 1000,
              timestamp: '2026-03-20T00:00:00Z',
            },
          ],
          summary: {
            overall_avg_latency_ms: 150,
            total_requests: 1000,
            slowest_endpoint: '/api/events',
          },
          timestamp: '2026-03-20T00:00:00Z',
        },
      };

      (global.fetch as vi.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await getApiLatency();

      expect(result).toEqual(mockResponse.data);
      expect(fetch).toHaveBeenCalledWith('/api/monitoring/api-latency');
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as vi.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Service Unavailable',
      } as Response);

      await expect(getApiLatency()).rejects.toThrow('Failed to fetch API latency: Service Unavailable');
    });
  });

  describe('getPerformanceMetrics', () => {
    it('should fetch and return performance metrics', async () => {
      const mockResponse = {
        success: true,
        data: {
          cpu_usage_percent: 45.5,
          memory_usage_mb: 1024,
          memory_usage_percent: 25.0,
          disk_usage_mb: 2048,
          disk_usage_percent: 10.0,
          active_connections: 50,
          uptime_seconds: 86400,
          timestamp: '2026-03-20T00:00:00Z',
        },
      };

      (global.fetch as vi.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await getPerformanceMetrics();

      expect(result).toEqual(mockResponse.data);
      expect(fetch).toHaveBeenCalledWith('/api/monitoring/performance-metrics');
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as vi.MockedFunction<typeof fetch>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Bad Gateway',
      } as Response);

      await expect(getPerformanceMetrics()).rejects.toThrow('Failed to fetch performance metrics: Bad Gateway');
    });
  });
});
