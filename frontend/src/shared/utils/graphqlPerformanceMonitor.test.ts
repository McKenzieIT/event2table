// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * GraphQL Performance Monitor Tests
 * 测试GraphQL性能监控工具的所有功能
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { GraphQLPerformanceMonitor, performanceMonitor } from './graphqlPerformanceMonitor';

describe('GraphQLPerformanceMonitor', () => {
  let monitor: GraphQLPerformanceMonitor;

  beforeEach(() => {
    monitor = new GraphQLPerformanceMonitor();
  });

  afterEach(() => {
    monitor.clear();
  });

  describe('Initialization', () => {
    it('should initialize with empty metrics', () => {
      const stats = monitor.getStats();
      expect(stats.graphql.totalRequests).toBe(0);
      expect(stats.rest.totalRequests).toBe(0);
      expect(stats.graphql.requests).toEqual([]);
      expect(stats.rest.requests).toEqual([]);
    });

    it('should be enabled by default', () => {
      const newMonitor = new GraphQLPerformanceMonitor();
      // Monitor should track requests when enabled
      newMonitor.trackGraphQLRequest('testQuery', {}, 100);
      const stats = newMonitor.getStats();
      expect(stats.graphql.totalRequests).toBe(1);
    });
  });

  describe('GraphQL Request Tracking', () => {
    it('should track GraphQL request', () => {
      monitor.trackGraphQLRequest('GetGames', { limit: 10 }, 150);

      const stats = monitor.getStats();
      expect(stats.graphql.totalRequests).toBe(1);
      expect(stats.graphql.requests.length).toBe(1);
      expect(stats.graphql.requests[0].queryName).toBe('GetGames');
      expect(stats.graphql.requests[0].duration).toBe(150);
    });

    it('should track multiple GraphQL requests', () => {
      monitor.trackGraphQLRequest('GetGames', { limit: 10 }, 150);
      monitor.trackGraphQLRequest('GetEvents', { gameGid: 10000147 }, 200);
      monitor.trackGraphQLRequest('GetGames', { limit: 20 }, 180);

      const stats = monitor.getStats();
      expect(stats.graphql.totalRequests).toBe(3);
      expect(stats.graphql.requests.length).toBe(3);
    });

    it('should calculate average duration', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100);
      monitor.trackGraphQLRequest('Query2', {}, 200);
      monitor.trackGraphQLRequest('Query3', {}, 300);

      const stats = monitor.getStats();
      expect(stats.graphql.averageDuration).toBe(200);
    });

    it('should track cache hits', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100, true);
      monitor.trackGraphQLRequest('Query2', {}, 150, false);
      monitor.trackGraphQLRequest('Query3', {}, 120, true);

      const stats = monitor.getStats();
      expect(stats.graphql.cacheHits).toBe(2);
      expect(stats.graphql.cacheMisses).toBe(1);
    });

    it('should calculate cache hit rate', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100, true);
      monitor.trackGraphQLRequest('Query2', {}, 150, true);
      monitor.trackGraphQLRequest('Query3', {}, 120, false);

      const stats = monitor.getStats();
      expect(stats.graphql.cacheHitRate).toBe('66.67%');
    });

    it('should return 0% cache hit rate when no requests', () => {
      const stats = monitor.getStats();
      expect(stats.graphql.cacheHitRate).toBe('0%');
    });

    it('should store request timestamp', () => {
      const beforeTrack = Date.now();
      monitor.trackGraphQLRequest('Query1', {}, 100);
      const afterTrack = Date.now();

      const stats = monitor.getStats();
      expect(stats.graphql.requests[0].timestamp).toBeGreaterThanOrEqual(beforeTrack);
      expect(stats.graphql.requests[0].timestamp).toBeLessThanOrEqual(afterTrack);
    });

    it('should serialize variables to JSON', () => {
      const variables = { gameGid: 10000147, limit: 10, filters: { status: 'active' } };
      monitor.trackGraphQLRequest('Query1', variables, 100);

      const stats = monitor.getStats();
      expect(stats.graphql.requests[0].variables).toBe(JSON.stringify(variables));
    });

    it('should not track when disabled', () => {
      monitor.setEnabled(false);
      monitor.trackGraphQLRequest('Query1', {}, 100);

      const stats = monitor.getStats();
      expect(stats.graphql.totalRequests).toBe(0);
    });
  });

  describe('REST API Request Tracking', () => {
    it('should track REST API request', () => {
      monitor.trackRESTRequest('/api/games', 'GET', 120);

      const stats = monitor.getStats();
      expect(stats.rest.totalRequests).toBe(1);
      expect(stats.rest.requests.length).toBe(1);
      expect(stats.rest.requests[0].name).toBe('/api/games');
      expect(stats.rest.requests[0].method).toBe('GET');
      expect(stats.rest.requests[0].duration).toBe(120);
    });

    it('should track multiple REST requests', () => {
      monitor.trackRESTRequest('/api/games', 'GET', 120);
      monitor.trackRESTRequest('/api/events', 'GET', 180);
      monitor.trackRESTRequest('/api/games', 'POST', 250);

      const stats = monitor.getStats();
      expect(stats.rest.totalRequests).toBe(3);
      expect(stats.rest.requests.length).toBe(3);
    });

    it('should calculate average duration', () => {
      monitor.trackRESTRequest('/api/1', 'GET', 100);
      monitor.trackRESTRequest('/api/2', 'GET', 200);
      monitor.trackRESTRequest('/api/3', 'GET', 300);

      const stats = monitor.getStats();
      expect(stats.rest.averageDuration).toBe(200);
    });

    it('should store request timestamp', () => {
      const beforeTrack = Date.now();
      monitor.trackRESTRequest('/api/test', 'GET', 100);
      const afterTrack = Date.now();

      const stats = monitor.getStats();
      expect(stats.rest.requests[0].timestamp).toBeGreaterThanOrEqual(beforeTrack);
      expect(stats.rest.requests[0].timestamp).toBeLessThanOrEqual(afterTrack);
    });

    it('should not track when disabled', () => {
      monitor.setEnabled(false);
      monitor.trackRESTRequest('/api/test', 'GET', 100);

      const stats = monitor.getStats();
      expect(stats.rest.totalRequests).toBe(0);
    });
  });

  describe('Performance Statistics', () => {
    it('should calculate request reduction percentage', () => {
      monitor.trackRESTRequest('/api/1', 'GET', 100);
      monitor.trackRESTRequest('/api/2', 'GET', 100);
      monitor.trackRESTRequest('/api/3', 'GET', 100);
      monitor.trackGraphQLRequest('Query1', {}, 150);

      const stats = monitor.getStats();
      expect(stats.comparison.requestReduction).toBe('66.67%');
    });

    it('should return 0% request reduction when no REST requests', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100);

      const stats = monitor.getStats();
      expect(stats.comparison.requestReduction).toBe('0%');
    });

    it('should calculate duration improvement percentage', () => {
      monitor.trackRESTRequest('/api/test', 'GET', 200);
      monitor.trackGraphQLRequest('Query1', {}, 100);

      const stats = monitor.getStats();
      expect(stats.comparison.durationImprovement).toBe('50.00%');
    });

    it('should return 0% duration improvement when no REST requests', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100);

      const stats = monitor.getStats();
      expect(stats.comparison.durationImprovement).toBe('0%');
    });

    it('should show negative improvement when GraphQL is slower', () => {
      monitor.trackRESTRequest('/api/test', 'GET', 100);
      monitor.trackGraphQLRequest('Query1', {}, 200);

      const stats = monitor.getStats();
      expect(parseFloat(stats.comparison.durationImprovement)).toBeLessThan(0);
    });
  });

  describe('Performance Report Generation', () => {
    it('should generate comprehensive performance report', () => {
      monitor.trackGraphQLRequest('GetGames', { limit: 10 }, 150, true);
      monitor.trackRESTRequest('/api/games', 'GET', 200);

      const report = monitor.generateReport();

      expect(report.timestamp).toBeDefined();
      expect(report.summary.graphqlRequests).toBe(1);
      expect(report.summary.restRequests).toBe(1);
      expect(report.summary.cacheHitRate).toBe('100.00%');
      expect(report.details.graphql.requests.length).toBe(1);
      expect(report.details.rest.requests.length).toBe(1);
    });

    it('should include average durations in report', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100);
      monitor.trackGraphQLRequest('Query2', {}, 200);
      monitor.trackRESTRequest('/api/test', 'GET', 150);

      const report = monitor.generateReport();
      expect(report.summary.averageGraphQLDuration).toBe('150.00ms');
      expect(report.summary.averageRESTDuration).toBe('150.00ms');
    });

    it('should include recommendations in report', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100, false);
      monitor.trackGraphQLRequest('Query2', {}, 100, false);
      monitor.trackGraphQLRequest('Query3', {}, 100, false);

      const report = monitor.generateReport();
      expect(report.recommendations).toBeInstanceOf(Array);
    });
  });

  describe('Recommendations Generation', () => {
    it('should recommend caching improvement when hit rate < 50%', () => {
      // Cache hit rate: 33.33% (1 hit out of 3)
      monitor.trackGraphQLRequest('Query1', {}, 100, true);
      monitor.trackGraphQLRequest('Query2', {}, 100, false);
      monitor.trackGraphQLRequest('Query3', {}, 100, false);

      const report = monitor.generateReport();
      const cachingRec = report.recommendations.find(r => r.type === 'caching');
      expect(cachingRec).toBeDefined();
      expect(cachingRec?.priority).toBe('high');
    });

    it('should not recommend caching improvement when hit rate >= 50%', () => {
      // Cache hit rate: 66.67% (2 hits out of 3)
      monitor.trackGraphQLRequest('Query1', {}, 100, true);
      monitor.trackGraphQLRequest('Query2', {}, 100, true);
      monitor.trackGraphQLRequest('Query3', {}, 100, false);

      const report = monitor.generateReport();
      const cachingRec = report.recommendations.find(r => r.type === 'caching');
      expect(cachingRec).toBeUndefined();
    });

    it('should recommend query optimization when GraphQL slower than REST', () => {
      monitor.trackGraphQLRequest('Query1', {}, 200);
      monitor.trackRESTRequest('/api/test', 'GET', 100);

      const report = monitor.generateReport();
      const perfRec = report.recommendations.find(r => r.type === 'performance');
      expect(perfRec).toBeDefined();
      expect(perfRec?.priority).toBe('high');
    });

    it('should recommend query merging when GraphQL has more requests', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100);
      monitor.trackGraphQLRequest('Query2', {}, 100);
      monitor.trackGraphQLRequest('Query3', {}, 100);
      monitor.trackRESTRequest('/api/test', 'GET', 100);

      const report = monitor.generateReport();
      const reqRec = report.recommendations.find(r => r.type === 'requests');
      expect(reqRec).toBeDefined();
      expect(reqRec?.priority).toBe('medium');
    });

    it('should return empty recommendations when performance is good', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100, true);
      monitor.trackGraphQLRequest('Query2', {}, 100, true);
      monitor.trackRESTRequest('/api/test', 'GET', 200);

      const report = monitor.generateReport();
      expect(report.recommendations.length).toBe(0);
    });
  });

  describe('Event Listeners', () => {
    it('should notify listeners on GraphQL request', () => {
      const listener = vi.fn();
      monitor.addListener(listener);

      monitor.trackGraphQLRequest('Query1', {}, 100);

      expect(listener).toHaveBeenCalledTimes(1);
      expect(listener).toHaveBeenCalledWith({
        type: 'graphql',
        metric: expect.objectContaining({
          queryName: 'Query1',
          duration: 100,
        }),
      });
    });

    it('should notify listeners on REST request', () => {
      const listener = vi.fn();
      monitor.addListener(listener);

      monitor.trackRESTRequest('/api/test', 'GET', 100);

      expect(listener).toHaveBeenCalledTimes(1);
      expect(listener).toHaveBeenCalledWith({
        type: 'rest',
        metric: expect.objectContaining({
          name: '/api/test',
          method: 'GET',
          duration: 100,
        }),
      });
    });

    it('should support multiple listeners', () => {
      const listener1 = vi.fn();
      const listener2 = vi.fn();
      monitor.addListener(listener1);
      monitor.addListener(listener2);

      monitor.trackGraphQLRequest('Query1', {}, 100);

      expect(listener1).toHaveBeenCalledTimes(1);
      expect(listener2).toHaveBeenCalledTimes(1);
    });

    it('should not notify listeners when disabled', () => {
      const listener = vi.fn();
      monitor.addListener(listener);
      monitor.setEnabled(false);

      monitor.trackGraphQLRequest('Query1', {}, 100);

      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('Clear Functionality', () => {
    it('should clear all metrics', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100);
      monitor.trackRESTRequest('/api/test', 'GET', 100);

      monitor.clear();

      const stats = monitor.getStats();
      expect(stats.graphql.totalRequests).toBe(0);
      expect(stats.rest.totalRequests).toBe(0);
      expect(stats.graphql.requests).toEqual([]);
      expect(stats.rest.requests).toEqual([]);
    });

    it('should reset cache statistics', () => {
      monitor.trackGraphQLRequest('Query1', {}, 100, true);
      monitor.trackGraphQLRequest('Query2', {}, 100, false);

      monitor.clear();

      const stats = monitor.getStats();
      expect(stats.graphql.cacheHits).toBe(0);
      expect(stats.graphql.cacheMisses).toBe(0);
      expect(stats.graphql.cacheHitRate).toBe('0%');
    });
  });

  describe('Enable/Disable Functionality', () => {
    it('should disable tracking', () => {
      monitor.setEnabled(false);
      monitor.trackGraphQLRequest('Query1', {}, 100);

      const stats = monitor.getStats();
      expect(stats.graphql.totalRequests).toBe(0);
    });

    it('should re-enable tracking', () => {
      monitor.setEnabled(false);
      monitor.setEnabled(true);
      monitor.trackGraphQLRequest('Query1', {}, 100);

      const stats = monitor.getStats();
      expect(stats.graphql.totalRequests).toBe(1);
    });
  });
});

describe('Singleton Instance', () => {
  it('should export singleton instance', () => {
    expect(performanceMonitor).toBeInstanceOf(GraphQLPerformanceMonitor);
  });

  it('should maintain state across imports', () => {
    performanceMonitor.clear();
    performanceMonitor.trackGraphQLRequest('TestQuery', {}, 100);

    const stats = performanceMonitor.getStats();
    expect(stats.graphql.totalRequests).toBe(1);

    performanceMonitor.clear();
  });
});
