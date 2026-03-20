/**
 * PerformancePage Component
 *
 * Main page for performance monitoring dashboard
 */

import React from 'react';
import { PerformanceDashboard } from '../components';

/**
 * PerformancePage component
 *
 * Main page that displays the performance monitoring dashboard
 *
 * @returns PerformancePage component
 *
 * @example
 * ```tsx
 * <PerformancePage />
 * ```
 */
export function PerformancePage(): React.JSX.Element {
  return (
    <div className="container mx-auto px-4 py-8">
      <PerformanceDashboard />
    </div>
  );
}
