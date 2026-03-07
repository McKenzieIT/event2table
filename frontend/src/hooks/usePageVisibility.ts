/**
 * usePageVisibility Hook
 *
 * ⚡ PERF: Phase 2 - Smart Polling Optimization
 *
 * Detects page visibility state to optimize polling intervals:
 * - Visible: 10s polling interval (real-time updates)
 * - Hidden: 60s polling interval (reduce unnecessary API calls by 83%)
 *
 * Usage:
 * ```tsx
 * const isVisible = usePageVisibility();
 * const pollingInterval = isVisible ? 10000 : 60000;
 *
 * useQuery(GET_DASHBOARD_STATS, {
 *   refetchInterval: pollingInterval,
 * });
 * ```
 *
 * Performance Impact:
 * - Reduces API calls by 83% when tab is hidden
 * - Saves bandwidth and server resources
 * - Maintains real-time updates when tab is visible
 */

import { useState, useEffect } from 'react';

/**
 * Hook to track page visibility state
 *
 * @returns boolean - true if page is visible, false if hidden
 */
export function usePageVisibility(): boolean {
  const [isVisible, setIsVisible] = useState<boolean>(() => {
    // Initialize with current visibility state
    return !document.hidden;
  });

  useEffect(() => {
    // Handle visibility change
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    // Listen for visibility change events
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Cleanup listener on unmount
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  return isVisible;
}

/**
 * Hook to get polling interval based on page visibility
 *
 * @param visibleInterval - Polling interval when visible (default: 10s)
 * @param hiddenInterval - Polling interval when hidden (default: 60s)
 * @returns number - Current polling interval in milliseconds
 *
 * Usage:
 * ```tsx
 * const pollingInterval = usePollingInterval(); // 10000 or 60000
 *
 * useQuery(GET_DASHBOARD_STATS, {
 *   refetchInterval: pollingInterval,
 * });
 * ```
 */
export function usePollingInterval(
  visibleInterval: number = 10000,  // 10 seconds
  hiddenInterval: number = 60000    // 60 seconds
): number {
  const isVisible = usePageVisibility();
  return isVisible ? visibleInterval : hiddenInterval;
}

/**
 * Higher-order hook for smart polling
 *
 * Automatically adjusts polling interval based on page visibility
 * while respecting a minimum interval.
 *
 * @param baseInterval - Base polling interval (default: 10s)
 * @param minInterval - Minimum interval (default: 5s)
 * @returns object - { pollingInterval, isVisible }
 *
 * Usage:
 * ```tsx
 * const { pollingInterval, isVisible } = useSmartPolling(10000, 5000);
 *
 * useQuery(GET_DASHBOARD_STATS, {
 *   refetchInterval: pollingInterval,
 * });
 *
 * return (
 *   <div>
 *     Status: {isVisible ? '🟢 Live' : '⚫ Paused'}
 *   </div>
 * );
 * ```
 */
export function useSmartPolling(
  baseInterval: number = 10000,  // 10 seconds
  minInterval: number = 5000      // 5 seconds
): {
  pollingInterval: number;
  isVisible: boolean;
  status: 'live' | 'paused';
} {
  const isVisible = usePageVisibility();

  // When hidden, use 6x interval (60s instead of 10s)
  const pollingInterval = isVisible
    ? baseInterval
    : Math.max(baseInterval * 6, minInterval);

  return {
    pollingInterval,
    isVisible,
    status: isVisible ? 'live' : 'paused',
  };
}

export default usePageVisibility;
