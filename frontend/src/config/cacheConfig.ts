
/**
 * Cache Configuration for Event2Table
 *
 * Centralized cache strategy configuration for React Query and Apollo Client
 * Defines cache policies, invalidation strategies, and optimization rules
 */

import { QueryCache, MutationCache } from '@tanstack/react-query';

/**
 * Cache time constants (in milliseconds)
 */
export const CACHE_TIMES = {
  /** 5 minutes - frequently accessed data */
  SHORT: 5 * 60 * 1000,
  /** 15 minutes - moderately changing data */
  MEDIUM: 15 * 60 * 1000,
  /** 30 minutes - rarely changing data */
  LONG: 30 * 60 * 1000,
  /** 1 hour - configuration data */
  VERY_LONG: 60 * 60 * 1000,
} as const;

/**
 * API type categories for cache strategy
 */
export enum ApiType {
  /** Real-time data that changes frequently */
  REALTIME = 'realtime',
  /** User-specific data that changes on user actions */
  USER_DATA = 'user_data',
  /** Configuration and metadata */
  CONFIG = 'config',
  /** Reference data (categories, parameters, etc.) */
  REFERENCE = 'reference',
  /** Dashboard and analytics data */
  ANALYTICS = 'analytics',
}

/**
 * Cache strategy configuration for each API type
 */
export const CACHE_STRATEGIES = {
  [ApiType.REALTIME]: {
    staleTime: 0,
    gcTime: CACHE_TIMES.SHORT,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    refetchOnMount: true,
  },
  [ApiType.USER_DATA]: {
    staleTime: CACHE_TIMES.SHORT,
    gcTime: CACHE_TIMES.MEDIUM,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    refetchOnMount: false,
  },
  [ApiType.CONFIG]: {
    staleTime: CACHE_TIMES.VERY_LONG,
    gcTime: CACHE_TIMES.VERY_LONG,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
    refetchOnMount: false,
  },
  [ApiType.REFERENCE]: {
    staleTime: CACHE_TIMES.LONG,
    gcTime: CACHE_TIMES.LONG,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
    refetchOnMount: false,
  },
  [ApiType.ANALYTICS]: {
    staleTime: CACHE_TIMES.MEDIUM,
    gcTime: CACHE_TIMES.MEDIUM,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
    refetchOnMount: false,
  },
} as const;

/**
 * Cache invalidation patterns
 * Maps mutation types to cache keys that should be invalidated
 */
export const CACHE_INVALIDATION_PATTERNS = {
  /** Invalidate all game-related caches */
  GAME_MUTATION: ['games', 'event-configs', 'flows'],
  /** Invalidate event-related caches */
  EVENT_MUTATION: ['events', 'event-configs', 'parameters'],
  /** Invalidate parameter-related caches */
  PARAMETER_MUTATION: ['parameters', 'filtered-parameters', 'common-parameters'],
  /** Invalidate category-related caches */
  CATEGORY_MUTATION: ['categories'],
  /** Invalidate all caches (for major changes) */
  GLOBAL_INVALIDATION: ['games', 'events', 'parameters', 'categories', 'event-configs', 'flows'],
} as const;

/**
 * Prefetch configuration
 */
export const PREFETCH_CONFIG = {
  /** Delay before prefetching on hover (ms) */
  HOVER_DELAY: 200,
  /** Delay before prefetching on intersection (ms) */
  INTERSECTION_DELAY: 300,
  /** Maximum number of prefetch requests at once */
  MAX_CONCURRENT_PREFETCH: 3,
  /** Stale time for prefetched data (ms) */
  PREFETCH_STALE_TIME: 5 * 60 * 1000,
} as const;

/**
 * Cache statistics tracking
 */
export interface CacheStats {
  hits: number;
  misses: number;
  prefetches: number;
  invalidations: number;
  lastInvalidation?: Date;
}

/**
 * Get cache strategy for a specific API type
 */
export function getCacheStrategy(apiType: ApiType) {
  return CACHE_STRATEGIES[apiType];
}

/**
 * Get cache keys to invalidate for a mutation type
 */
export function getInvalidationKeys(mutationType: keyof typeof CACHE_INVALIDATION_PATTERNS) {
  return CACHE_INVALIDATION_PATTERNS[mutationType];
}

/**
 * Default React Query cache configuration
 * Note: QueryCache and MutationCache don't support onError/onSuccess in v5
 * Error handling is done at the query/mutation level instead
 */
export const DEFAULT_QUERY_CACHE_CONFIG: QueryCache = new QueryCache({});

/**
 * Default React Query mutation cache configuration
 */
export const DEFAULT_MUTATION_CACHE_CONFIG: MutationCache = new MutationCache({});

/**
 * Cache configuration for specific query keys
 */
export const QUERY_KEY_CACHE_CONFIG = {
  // Games
  games: {
    all: { ...CACHE_STRATEGIES[ApiType.REFERENCE] },
    detail: { ...CACHE_STRATEGIES[ApiType.REFERENCE] },
  },
  // Events
  events: {
    all: { ...CACHE_STRATEGIES[ApiType.USER_DATA] },
    detail: { ...CACHE_STRATEGIES[ApiType.USER_DATA] },
  },
  // Event Configs
  eventConfigs: {
    all: { ...CACHE_STRATEGIES[ApiType.USER_DATA] },
    detail: { ...CACHE_STRATEGIES[ApiType.USER_DATA] },
  },
  // Parameters
  parameters: {
    all: { ...CACHE_STRATEGIES[ApiType.REFERENCE] },
    detail: { ...CACHE_STRATEGIES[ApiType.REFERENCE] },
    filtered: { ...CACHE_STRATEGIES[ApiType.USER_DATA] },
    common: { ...CACHE_STRATEGIES[ApiType.REFERENCE] },
  },
  // Categories
  categories: {
    all: { ...CACHE_STRATEGIES[ApiType.REFERENCE] },
    detail: { ...CACHE_STRATEGIES[ApiType.REFERENCE] },
  },
  // Flows
  flows: {
    all: { ...CACHE_STRATEGIES[ApiType.USER_DATA] },
    detail: { ...CACHE_STRATEGIES[ApiType.USER_DATA] },
  },
  // Analytics
  analytics: {
    dashboard: { ...CACHE_STRATEGIES[ApiType.ANALYTICS] },
    stats: { ...CACHE_STRATEGIES[ApiType.ANALYTICS] },
  },
} as const;
