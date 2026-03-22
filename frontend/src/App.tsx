// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React from 'react';
import { useRoutes, Navigate } from 'react-router-dom';
import { routes } from './routes/routes';
import { ErrorBoundary } from '@shared/ui/ErrorBoundary';

/**
 * App Component
 *
 * Root component that sets up routing and error boundaries
 * NOTE: Suspense boundary removed - all components are now direct imports
 * to fix Playwright test timeout issues caused by double Suspense nesting.
 */
function App(): React.JSX.Element {
  const element = useRoutes(routes);

  return (
    <ErrorBoundary>
      {element || <Navigate to="/" replace />}
    </ErrorBoundary>
  );
}

export default App;
