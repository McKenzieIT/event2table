# Cache Strategy Guide for Event2Table

This guide provides comprehensive documentation for the API caching strategy in Event2Table, including configuration, usage examples, and best practices.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Cache Configuration](#cache-configuration)
- [API Types](#api-types)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Cache Invalidation](#cache-invalidation)
- [Prefetching](#prefetching)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Overview

Event2Table uses a sophisticated caching strategy built on top of React Query (TanStack Query) to optimize data loading performance and reduce unnecessary network requests. The caching system is designed to:

- **Reduce network latency** by serving data from cache when possible
- **Improve user experience** with instant data display
- **Optimize bandwidth usage** by minimizing API calls
- **Maintain data consistency** through intelligent invalidation

### Key Features

- **Typed cache strategies** for different API types
- **Automatic cache invalidation** based on mutations
- **Prefetching** for proactive data loading
- **Cache statistics** for monitoring performance
- **Flexible configuration** for fine-tuning cache behavior

## Architecture

The caching system consists of three main components:

### 1. Cache Configuration (`cacheConfig.ts`)

Defines cache strategies, invalidation patterns, and prefetching configuration.

### 2. Cache Utilities (`cacheUtils.ts`)

Provides helper functions for cache management, including:
- Cache key generation
- Cache invalidation
- Prefetching utilities
- Statistics tracking

### 3. Query Client (`queryClient.ts`)

Configures the React Query client with optimized defaults and integrates with the cache configuration.

## Cache Configuration

### Cache Time Constants

```typescript
import { CACHE_TIMES } from '@/config/cacheConfig';

// Available cache times
CACHE_TIMES.SHORT    // 5 minutes
CACHE_TIMES.MEDIUM   // 15 minutes
CACHE_TIMES.LONG     // 30 minutes
CACHE_TIMES.VERY_LONG // 1 hour
```

### API Types

The system categorizes APIs into five types, each with its own caching strategy:

| API Type | Description | Stale Time | GC Time |
|----------|-------------|------------|---------|
| `REALTIME` | Data that changes frequently | 0ms | 5 min |
| `USER_DATA` | User-specific data | 5 min | 15 min |
| `CONFIG` | Configuration and metadata | 1 hour | 1 hour |
| `REFERENCE` | Reference data (categories, parameters) | 30 min | 30 min |
| `ANALYTICS` | Dashboard and analytics data | 15 min | 15 min |

### Cache Strategies

Each API type has a predefined strategy:

```typescript
import { ApiType, getCacheStrategy } from '@/config/cacheConfig';

const strategy = getCacheStrategy(ApiType.CONFIG);
// Returns: { staleTime, gcTime, refetchOnWindowFocus, ... }
```

## Usage Examples

### Basic Query with Cache Strategy

```typescript
import { useQuery } from '@tanstack/react-query';
import { createQueryOptions, ApiType } from '@/config/cacheConfig';

function useGames() {
  return useQuery(
    createQueryOptions(
      ['games'],
      fetchGames,
      ApiType.REFERENCE
    )
  );
}
```

### Custom Query with Cache Configuration

```typescript
import { useQuery } from '@tanstack/react-query';
import { QUERY_KEY_CACHE_CONFIG } from '@/config/cacheConfig';

function useEvents(gameGid: number) {
  return useQuery({
    queryKey: ['events', { gameGid }],
    queryFn: () => fetchEvents(gameGid),
    ...QUERY_KEY_CACHE_CONFIG.events.all,
  });
}
```

### Cache Invalidation

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { invalidateCache } from '@/shared/utils/cacheUtils';

function useUpdateGame() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: updateGame,
    onSuccess: () => {
      // Invalidate all game-related caches
      invalidateCache(queryClient, 'GAME_MUTATION');
    },
  });
}
```

### Manual Cache Management

```typescript
import { useCacheManager } from '@/shared/utils/cacheUtils';

function MyComponent() {
  const cache = useCacheManager();
  
  const handleUpdate = async () => {
    await updateData();
    // Invalidate specific cache
    cache.invalidateQuery(['events', { id: 123 }]);
  };
  
  return <button onClick={handleUpdate}>Update</button>;
}
```

### Prefetching on Hover

```typescript
import { usePrefetchOnHover } from '@/shared/utils/cacheUtils';

function EventListItem({ eventId }) {
  const { onMouseEnter } = usePrefetchOnHover(
    ['events', eventId],
    () => fetchEventDetail(eventId)
  );
  
  return (
    <div onMouseEnter={onMouseEnter}>
      {event.name}
    </div>
  );
}
```

### Cache Statistics

```typescript
import { getCacheStats, getCacheHitRate } from '@/shared/utils/cacheUtils';

function CacheMonitor() {
  const stats = getCacheStats();
  const hitRate = getCacheHitRate();
  
  return (
    <div>
      <p>Cache Hits: {stats.hits}</p>
      <p>Cache Misses: {stats.misses}</p>
      <p>Hit Rate: {(hitRate * 100).toFixed(2)}%</p>
    </div>
  );
}
```

## Best Practices

### 1. Choose the Right API Type

Select the appropriate API type based on your data characteristics:

```typescript
// ✅ Good: Configuration data rarely changes
const configQuery = useQuery({
  queryKey: ['config'],
  queryFn: fetchConfig,
  ...getCacheStrategy(ApiType.CONFIG),
});

// ✅ Good: User data changes on user actions
const userDataQuery = useQuery({
  queryKey: ['user', userId],
  queryFn: fetchUserData,
  ...getCacheStrategy(ApiType.USER_DATA),
});

// ❌ Bad: Using CONFIG for frequently changing data
const realtimeQuery = useQuery({
  queryKey: ['realtime'],
  queryFn: fetchRealtimeData,
  ...getCacheStrategy(ApiType.CONFIG), // Wrong!
});
```

### 2. Use Consistent Cache Keys

Always use the cache utilities to generate consistent keys:

```typescript
import { generateCacheKey } from '@/shared/utils/cacheUtils';

// ✅ Good: Consistent key generation
const queryKey = generateCacheKey('events', { gameGid: 123, status: 'active' });

// ❌ Bad: Inconsistent key generation
const queryKey = ['events', { status: 'active', gameGid: 123 }]; // Different order!
```

### 3. Invalidate Related Caches

After mutations, invalidate all related caches:

```typescript
const updateEventMutation = useMutation({
  mutationFn: updateEvent,
  onSuccess: () => {
    // Invalidate all related caches
    batchInvalidate(queryClient, [
      'EVENT_MUTATION',
      'PARAMETER_MUTATION',
    ]);
  },
});
```

### 4. Prefetch Proactively

Use prefetching to improve perceived performance:

```typescript
function EventList() {
  const { data: events } = useEvents();
  
  useEffect(() => {
    // Prefetch first 10 events
    events?.slice(0, 10).forEach(event => {
      prefetchQuery(
        queryClient,
        ['events', event.id],
        () => fetchEventDetail(event.id)
      );
    });
  }, [events]);
  
  return <EventListItems events={events} />;
}
```

### 5. Monitor Cache Performance

Track cache statistics to identify optimization opportunities:

```typescript
useEffect(() => {
  const interval = setInterval(() => {
    const stats = getCacheStats();
    const hitRate = getCacheHitRate();
    
    if (hitRate < 0.7) {
      console.warn('Low cache hit rate:', hitRate);
    }
  }, 60000);
  
  return () => clearInterval(interval);
}, []);
```

## Cache Invalidation

### Automatic Invalidation

The system provides predefined invalidation patterns:

```typescript
import { CACHE_INVALIDATION_PATTERNS } from '@/config/cacheConfig';

// Available patterns
CACHE_INVALIDATION_PATTERNS.GAME_MUTATION       // games, event-configs, flows
CACHE_INVALIDATION_PATTERNS.EVENT_MUTATION      // events, event-configs, parameters
CACHE_INVALIDATION_PATTERNS.PARAMETER_MUTATION  // parameters, filtered-parameters, common-parameters
CACHE_INVALIDATION_PATTERNS.CATEGORY_MUTATION   // categories
CACHE_INVALIDATION_PATTERNS.GLOBAL_INVALIDATION // All caches
```

### Manual Invalidation

```typescript
import { invalidateQuery, removeCacheData } from '@/shared/utils/cacheUtils';

// Invalidate specific query
invalidateQuery(queryClient, ['events', { id: 123 }]);

// Remove cache entry
removeCacheData(queryClient, ['events', { id: 123 }]);

// Clear all caches
clearCache(queryClient);
```

### Selective Invalidation

```typescript
// Invalidate only active queries
queryClient.invalidateQueries({
  queryKey: ['events'],
  refetchType: 'active',
});

// Invalidate without refetching
queryClient.invalidateQueries({
  queryKey: ['events'],
  refetchType: 'none',
});
```

## Prefetching

### Hover Prefetching

```typescript
import { usePrefetchOnHover } from '@/shared/utils/cacheUtils';

function Link({ to, children }) {
  const { onMouseEnter } = usePrefetchOnHover(
    ['page', to],
    () => fetchPageData(to),
    200 // delay in ms
  );
  
  return <a href={to} onMouseEnter={onMouseEnter}>{children}</a>;
}
```

### Intersection Prefetching

```typescript
import { usePrefetchOnVisibility } from '@/shared/utils/cacheUtils';

function LazyImage({ src, alt }) {
  const { onIntersection } = usePrefetchOnVisibility(
    ['image', src],
    () => prefetchImage(src)
  );
  
  return (
    <img 
      src={src} 
      alt={alt}
      ref={(ref) => {
        if (ref) {
          const observer = new IntersectionObserver(onIntersection);
          observer.observe(ref);
        }
      }}
    />
  );
}
```

### Batch Prefetching

```typescript
import { prefetchQueries } from '@/shared/utils/cacheUtils';

function Dashboard() {
  useEffect(() => {
    const queries = [
      { queryKey: ['stats'], queryFn: fetchStats },
      { queryKey: ['recent-events'], queryFn: fetchRecentEvents },
      { queryKey: ['alerts'], queryFn: fetchAlerts },
    ];
    
    prefetchQueries(queryClient, queries);
  }, []);
  
  return <DashboardContent />;
}
```

## Monitoring

### Cache Statistics

```typescript
import { getCacheStats, getCacheHitRate, resetCacheStats } from '@/shared/utils/cacheUtils';

// Get current statistics
const stats = getCacheStats();
// { hits: 100, misses: 20, prefetches: 50, invalidations: 10, lastInvalidation: Date }

// Calculate hit rate
const hitRate = getCacheHitRate();
// 0.8333 (83.33%)

// Reset statistics
resetCacheStats();
```

### Cache Health

```typescript
import { getCacheHealth } from '@/config/queryClient';

const health = getCacheHealth();
// { total: 50, active: 5, stale: 10, inactive: 35 }
```

### Debug Logging

Enable debug logging in development:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      onSuccess: (data) => {
        if (import.meta.env.DEV) {
          console.log('[Cache Hit]', data);
        }
      },
    },
  },
});
```

## Troubleshooting

### Issue: Stale Data Display

**Problem:** Data appears outdated even after updates.

**Solution:** Ensure proper cache invalidation:

```typescript
// After mutation
invalidateCache(queryClient, 'EVENT_MUTATION');

// Or force refetch
queryClient.refetchQueries({ queryKey: ['events'] });
```

### Issue: Too Many Network Requests

**Problem:** Excessive API calls despite caching.

**Solution:** Check cache configuration:

```typescript
// Increase stale time for reference data
const strategy = getCacheStrategy(ApiType.REFERENCE);
strategy.staleTime = CACHE_TIMES.VERY_LONG;
```

### Issue: Low Cache Hit Rate

**Problem:** Cache hit rate is below 70%.

**Solution:** Review cache key consistency:

```typescript
// Use consistent key generation
const queryKey = generateCacheKey('events', { gameGid: 123 });
```

### Issue: Memory Usage

**Problem:** High memory consumption from cache.

**Solution:** Adjust GC time:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 5 * 60 * 1000, // Reduce to 5 minutes
    },
  },
});
```

## Additional Resources

- [React Query Documentation](https://tanstack.com/query/latest)
- [Cache Configuration API](../frontend/src/config/cacheConfig.ts)
- [Cache Utilities](../frontend/src/shared/utils/cacheUtils.ts)
- [Query Client Setup](../frontend/src/config/queryClient.ts)

## Changelog

### Version 1.0.0 (2026-03-20)

- Initial release of cache strategy system
- Added cache configuration with API types
- Implemented cache utilities for management
- Created comprehensive documentation
