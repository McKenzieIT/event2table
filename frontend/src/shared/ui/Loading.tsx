// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import { Spinner } from '@shared/ui';
import React from 'react';
import './Loading.css';

/**
 * Loading Component
 *
 * Displayed during lazy loading and suspense
 * Uses the shared Spinner component for consistency
 */
function Loading(): React.JSX.Element {
  return (
    <div className="loading-container" data-testid="loading-spinner">
      <div className="loading-spinner">
        <Spinner size="lg" />
        <p className="loading-text">加载中...</p>
      </div>
    </div>
  );
}

// Memoize Loading - simple component with no props
const MemoizedLoading = React.memo(Loading);
MemoizedLoading.displayName = 'MemoizedLoading';

export default MemoizedLoading;
