/**
 * PerformanceMonitor 单元测试
 * 遵循TDD开发模式：先写测试，看测试失败，再编写实现
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { PerformanceMonitor } from '../PerformanceMonitor';

describe('PerformanceMonitor', () => {
  beforeEach(() => {
    // Mock console.log to avoid cluttering test output
    vi.spyOn(console, 'log').mockImplementation(() => {});
    // Clear metrics before each test
    PerformanceMonitor.clearMetrics();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    PerformanceMonitor.clearMetrics();
  });

  describe('trackAPICall', () => {
    it('should log API call with correct format', () => {
      PerformanceMonitor.trackAPICall('/api/games', 150);

      expect(console.log).toHaveBeenCalledWith(
        '[API] /api/games: 150ms'
      );
    });

    it('should handle slow API calls (>1000ms)', () => {
      PerformanceMonitor.trackAPICall('/api/events', 1500);

      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[API] /api/events: 1500ms')
      );
    });

    it('should handle zero duration', () => {
      PerformanceMonitor.trackAPICall('/api/parameters', 0);

      expect(console.log).toHaveBeenCalledWith(
        '[API] /api/parameters: 0ms'
      );
    });
  });

  describe('trackCacheHit', () => {
    it('should log cache hit correctly', () => {
      PerformanceMonitor.trackCacheHit('games:list', true);

      expect(console.log).toHaveBeenCalledWith(
        '[Cache] games:list: HIT'
      );
    });

    it('should log cache miss correctly', () => {
      PerformanceMonitor.trackCacheHit('games:list', false);

      expect(console.log).toHaveBeenCalledWith(
        '[Cache] games:list: MISS'
      );
    });

    it('should handle different cache keys', () => {
      PerformanceMonitor.trackCacheHit('events:detail:123', true);
      PerformanceMonitor.trackCacheHit('parameters:all', false);

      expect(console.log).toHaveBeenCalledWith(
        '[Cache] events:detail:123: HIT'
      );
      expect(console.log).toHaveBeenCalledWith(
        '[Cache] parameters:all: MISS'
      );
    });
  });

  describe('trackPageLoad', () => {
    it('should track page load metrics', () => {
      const metrics = {
        fcp: 1234,
        lcp: 2456,
        cls: 0.05,
        tbt: 150
      };

      PerformanceMonitor.trackPageLoad('/', metrics);

      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[PageLoad] /')
      );
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('FCP: 1234ms')
      );
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('LCP: 2456ms')
      );
    });

    it('should handle missing metrics gracefully', () => {
      const partialMetrics = {
        fcp: 1000
      };

      PerformanceMonitor.trackPageLoad('/games', partialMetrics as any);

      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[PageLoad] /games')
      );
    });
  });

  describe('getMetricsSummary', () => {
    it('should return empty summary initially', () => {
      const summary = PerformanceMonitor.getMetricsSummary();

      expect(summary).toEqual({
        totalAPICalls: 0,
        averageAPIDuration: 0,
        cacheHitRate: 0,
        totalPageLoads: 0
      });
    });

    it('should calculate correct summary after tracking', () => {
      PerformanceMonitor.trackAPICall('/api/games', 100);
      PerformanceMonitor.trackAPICall('/api/events', 200);
      PerformanceMonitor.trackCacheHit('test', true);
      PerformanceMonitor.trackCacheHit('test', false);
      PerformanceMonitor.trackPageLoad('/', {} as any);

      const summary = PerformanceMonitor.getMetricsSummary();

      expect(summary.totalAPICalls).toBe(2);
      expect(summary.averageAPIDuration).toBe(150);
      expect(summary.cacheHitRate).toBe(0.5);
      expect(summary.totalPageLoads).toBe(1);
    });
  });
});
