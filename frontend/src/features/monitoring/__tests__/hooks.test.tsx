/**
 * Monitoring Hooks Unit Tests
 *
 * Tests for monitoring React Query hooks
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import * as monitoringApi from '../api/monitoringApi';
import { useCacheStats, useApiLatency, usePerformanceMetrics } from '../hooks/index';

// Mock API functions
vi.mock('../api/monitoringApi');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('Monitoring Hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useCacheStats', () => {
    it('should fetch cache statistics successfully', async () => {
      const mockData = {
        hit_rate: 0.85,
        miss_rate: 0.15,
        total_requests: 10000,
        cache_size: 512,
        eviction_count: 50,
        timestamp: '2026-03-20T00:00:00Z',
      };

      vi.mocked(monitoringApi.getCacheStats).mockResolvedValueOnce(mockData);

      const { result } = renderHook(() => useCacheStats(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockData);
      expect(monitoringApi.getCacheStats).toHaveBeenCalledOnce();
    });

    it('should handle errors', async () => {
      const mockError = new Error('Failed to fetch cache stats');
      vi.mocked(monitoringApi.getCacheStats).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => useCacheStats(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isError).toBe(true));

      expect(result.current.error).toEqual(mockError);
    });
  });

  describe('useApiLatency', () => {
    it('should fetch API latency data successfully', async () => {
      const mockData = {
        endpoints: [],
        summary: {
          overall_avg_latency_ms: 150,
          total_requests: 1000,
          slowest_endpoint: '/api/events',
        },
        timestamp: '2026-03-20T00:00:00Z',
      };

      vi.mocked(monitoringApi.getApiLatency).mockResolvedValueOnce(mockData);

      const { result } = renderHook(() => useApiLatency(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockData);
      expect(monitoringApi.getApiLatency).toHaveBeenCalledOnce();
    });

    it('should handle errors', async () => {
      const mockError = new Error('Failed to fetch API latency');
      vi.mocked(monitoringApi.getApiLatency).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => useApiLatency(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isError).toBe(true));

      expect(result.current.error).toEqual(mockError);
    });
  });

  describe('usePerformanceMetrics', () => {
    it('should fetch performance metrics successfully', async () => {
      const mockData = {
        cpu_usage_percent: 45.5,
        memory_usage_mb: 1024,
        memory_usage_percent: 25.0,
        disk_usage_mb: 2048,
        disk_usage_percent: 10.0,
        active_connections: 50,
        uptime_seconds: 86400,
        timestamp: '2026-03-20T00:00:00Z',
      };

      vi.mocked(monitoringApi.getPerformanceMetrics).mockResolvedValueOnce(mockData);

      const { result } = renderHook(() => usePerformanceMetrics(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockData);
      expect(monitoringApi.getPerformanceMetrics).toHaveBeenCalledOnce();
    });

    it('should handle errors', async () => {
      const mockError = new Error('Failed to fetch performance metrics');
      vi.mocked(monitoringApi.getPerformanceMetrics).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => usePerformanceMetrics(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isError).toBe(true));

      expect(result.current.error).toEqual(mockError);
    });
  });
});
