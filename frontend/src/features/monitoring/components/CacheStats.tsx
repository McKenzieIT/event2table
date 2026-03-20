/**
 * CacheStats Component
 *
 * Displays cache statistics including hit rate, miss rate, and cache size
 */

import React from 'react';
import { useCacheStats } from '../hooks';
import { MetricCard } from './MetricCard';
import { Spinner } from '@shared/ui';
import type { CacheStats } from '../types';

/**
 * CacheStats component for displaying cache performance metrics
 *
 * @returns CacheStats component
 *
 * @example
 * ```tsx
 * <CacheStats />
 * ```
 */
export function CacheStats(): React.JSX.Element {
  const { data: cacheStats, isLoading, error } = useCacheStats();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700 font-medium">Failed to load cache statistics</p>
        <p className="text-red-600 text-sm mt-1">{error.message}</p>
      </div>
    );
  }

  if (!cacheStats) {
    return null;
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Cache Statistics</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          label="Hit Rate"
          value={cacheStats.hit_rate * 100}
          unit="%"
          trend="up"
          trendValue={2.5}
        />
        <MetricCard
          label="Miss Rate"
          value={cacheStats.miss_rate * 100}
          unit="%"
          trend="down"
          trendValue={1.2}
        />
        <MetricCard
          label="Total Requests"
          value={cacheStats.total_requests}
        />
        <MetricCard
          label="Cache Size"
          value={cacheStats.cache_size}
          unit="MB"
        />
        <MetricCard
          label="Eviction Count"
          value={cacheStats.eviction_count}
          trend="down"
          trendValue={5.0}
        />
      </div>
    </div>
  );
}
