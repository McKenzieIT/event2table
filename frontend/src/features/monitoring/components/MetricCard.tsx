/**
 * MetricCard Component
 *
 * Displays a single performance metric with label and value
 */

import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
  icon?: React.ReactNode;
  className?: string;
}

/**
 * MetricCard component for displaying performance metrics
 *
 * @param props - Component props
 * @returns MetricCard component
 *
 * @example
 * ```tsx
 * <MetricCard
 *   label="Cache Hit Rate"
 *   value={85.5}
 *   unit="%"
 *   trend="up"
 *   trendValue={2.3}
 * />
 * ```
 */
export function MetricCard({
  label,
  value,
  unit,
  trend,
  trendValue,
  icon,
  className = '',
}: MetricCardProps): React.JSX.Element {
  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-green-500';
      case 'down':
        return 'text-red-500';
      default:
        return 'text-gray-400';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '→';
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm p-6 border border-gray-200 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-2">{label}</p>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-gray-900">
              {typeof value === 'number' ? value.toFixed(2) : value}
            </span>
            {unit && <span className="text-sm text-gray-500">{unit}</span>}
          </div>
          {trend && trendValue !== undefined && (
            <div className={`mt-2 text-sm ${getTrendColor()}`}>
              {getTrendIcon()} {Math.abs(trendValue).toFixed(1)}% vs last period
            </div>
          )}
        </div>
        {icon && <div className="ml-4 text-gray-400">{icon}</div>}
      </div>
    </div>
  );
}
