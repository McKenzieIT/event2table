/**
 * PerformanceDashboard Component
 *
 * Main monitoring dashboard that aggregates all performance metrics
 */

import React from 'react';
import { CacheStats } from './CacheStats';
import { ApiLatencyChart } from './ApiLatencyChart';
import { usePerformanceMetrics } from '../hooks';
import { MetricCard } from './MetricCard';
import { Spinner } from '@shared/ui';

/**
 * PerformanceDashboard component for displaying all performance metrics
 *
 * @returns PerformanceDashboard component
 *
 * @example
 * ```tsx
 * <PerformanceDashboard />
 * ```
 */
export function PerformanceDashboard(): React.JSX.Element {
  const { data: performanceMetrics, isLoading: metricsLoading, error: metricsError } = usePerformanceMetrics();

  if (metricsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (metricsError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700 font-medium">Failed to load performance metrics</p>
        <p className="text-red-600 text-sm mt-1">{metricsError.message}</p>
      </div>
    );
  }

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    }
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Performance Dashboard</h2>
        <p className="text-gray-600">Real-time system performance monitoring</p>
      </div>

      {performanceMetrics && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">System Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="CPU Usage"
              value={performanceMetrics.cpu_usage_percent}
              unit="%"
            />
            <MetricCard
              label="Memory Usage"
              value={performanceMetrics.memory_usage_mb}
              unit="MB"
            />
            <MetricCard
              label="Memory %"
              value={performanceMetrics.memory_usage_percent}
              unit="%"
            />
            <MetricCard
              label="Active Connections"
              value={performanceMetrics.active_connections}
            />
            <MetricCard
              label="Disk Usage"
              value={performanceMetrics.disk_usage_mb}
              unit="MB"
            />
            <MetricCard
              label="Disk %"
              value={performanceMetrics.disk_usage_percent}
              unit="%"
            />
            <MetricCard
              label="Uptime"
              value={formatUptime(performanceMetrics.uptime_seconds)}
            />
          </div>
        </div>
      )}

      <div className="border-t border-gray-200 pt-8">
        <CacheStats />
      </div>

      <div className="border-t border-gray-200 pt-8">
        <ApiLatencyChart />
      </div>
    </div>
  );
}
