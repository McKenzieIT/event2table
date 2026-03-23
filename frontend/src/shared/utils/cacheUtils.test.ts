import { QueryClient } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import {
  generateCacheKey,
  invalidateCache,
  invalidateQuery,
  clearCache,
  prefetchQuery,
  prefetchQueries,
  getCacheData,
  setCacheData,
  removeCacheData,
  getCacheStats,
  getCacheHitRate,
  resetCacheStats,
  createQueryOptions,
  batchInvalidate,
} from './cacheUtils';

// Mock cache config
vi.mock('@/config/cacheConfig', () => ({
  getInvalidationKeys: () => ['events', 'games'],
  PREFETCH_CONFIG: {
    HOVER_DELAY: 100,
    PREFETCH_STALE_TIME: 30000,
    INTERSECTION_DELAY: 200,
  },
  getCacheStrategy: () => ({
    staleTime: 30000,
    gcTime: 300000,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    refetchOnMount: true,
  }),
}));

describe('cacheUtils', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    resetCacheStats();
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe('generateCacheKey', () => {
    it('should generate key without params', () => {
      const key = generateCacheKey('events');
      expect(key).toEqual(['events']);
    });

    it('should generate key with params', () => {
      const key = generateCacheKey('events', { page: 1, limit: 10 });
      expect(key).toEqual(['events', { limit: 10, page: 1 }]);
    });

    it('should sort params for consistency', () => {
      const key1 = generateCacheKey('events', { limit: 10, page: 1 });
      const key2 = generateCacheKey('events', { page: 1, limit: 10 });
      expect(key1).toEqual(key2);
    });

    it('should handle empty params', () => {
      const key = generateCacheKey('events', {});
      expect(key).toEqual(['events']);
    });
  });

  describe('invalidateCache', () => {
    it('should invalidate cache entries', () => {
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
      invalidateCache(queryClient, 'events');
      expect(invalidateSpy).toHaveBeenCalled();
    });

    it('should invalidate with exact option', () => {
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
      invalidateCache(queryClient, 'events', true);
      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ['events'],
      });
    });
  });

  describe('invalidateQuery', () => {
    it('should invalidate specific query', () => {
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
      invalidateQuery(queryClient, ['events', 1]);
      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ['events', 1],
      });
    });
  });

  describe('clearCache', () => {
    it('should clear all cache', () => {
      const clearSpy = vi.spyOn(queryClient, 'clear');
      clearCache(queryClient);
      expect(clearSpy).toHaveBeenCalled();
    });
  });

  describe('getCacheData and setCacheData', () => {
    it('should set and get cache data', () => {
      const data = { id: 1, name: 'test' };
      setCacheData(queryClient, ['events'], data);
      const cached = getCacheData(queryClient, ['events']);
      expect(cached).toEqual(data);
    });

    it('should return undefined for non-existent cache', () => {
      const cached = getCacheData(queryClient, ['nonexistent']);
      expect(cached).toBeUndefined();
    });
  });

  describe('removeCacheData', () => {
    it('should remove cache entry', () => {
      setCacheData(queryClient, ['events'], { id: 1 });
      const removeSpy = vi.spyOn(queryClient, 'removeQueries');
      removeCacheData(queryClient, ['events']);
      expect(removeSpy).toHaveBeenCalledWith({
        queryKey: ['events'],
      });
    });
  });

  describe('prefetchQuery', () => {
    it('should prefetch query with delay', () => {
      vi.useFakeTimers();
      const prefetchSpy = vi.spyOn(queryClient, 'prefetchQuery');
      const queryFn = () => Promise.resolve({ data: 'test' });

      prefetchQuery(queryClient, ['events'], queryFn, 100);
      
      expect(prefetchSpy).not.toHaveBeenCalled();
      vi.advanceTimersByTime(100);
      expect(prefetchSpy).toHaveBeenCalled();
      
      vi.useRealTimers();
    });
  });

  describe('prefetchQueries', () => {
    it('should prefetch multiple queries', () => {
      vi.useFakeTimers();
      const prefetchSpy = vi.spyOn(queryClient, 'prefetchQuery');
      const queries = [
        { queryKey: ['events'], queryFn: () => Promise.resolve({ data: 'events' }) },
        { queryKey: ['games'], queryFn: () => Promise.resolve({ data: 'games' }) },
      ];

      prefetchQueries(queryClient, queries, 100);
      
      expect(prefetchSpy).not.toHaveBeenCalled();
      vi.advanceTimersByTime(100);
      expect(prefetchSpy).toHaveBeenCalledTimes(2);
      
      vi.useRealTimers();
    });
  });

  describe('cacheStats', () => {
    it('should track cache statistics', () => {
      const stats = getCacheStats();
      expect(stats).toHaveProperty('hits');
      expect(stats).toHaveProperty('misses');
      expect(stats).toHaveProperty('prefetches');
      expect(stats).toHaveProperty('invalidations');
    });

    it('should calculate hit rate', () => {
      const rate = getCacheHitRate();
      expect(typeof rate).toBe('number');
      expect(rate).toBeGreaterThanOrEqual(0);
      expect(rate).toBeLessThanOrEqual(1);
    });

    it('should reset stats', () => {
      resetCacheStats();
      const stats = getCacheStats();
      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(0);
    });
  });

  describe('createQueryOptions', () => {
    it('should create query options with strategy', () => {
      const options = createQueryOptions(['events'], () => Promise.resolve({}), 'events');
      expect(options).toHaveProperty('queryKey');
      expect(options).toHaveProperty('queryFn');
      expect(options).toHaveProperty('staleTime');
      expect(options).toHaveProperty('gcTime');
    });
  });

  describe('batchInvalidate', () => {
    it('should invalidate multiple mutation types', () => {
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
      batchInvalidate(queryClient, ['events', 'games']);
      expect(invalidateSpy).toHaveBeenCalledTimes(2);
    });
  });
});
