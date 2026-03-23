// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import { ThemeProvider } from '@shared/ui';
import { ErrorBoundary } from '@shared/ui/ErrorBoundary';
import React from 'react';
import { useRoutes, Navigate } from 'react-router-dom';

import { routes } from './routes/routes';

/**
 * App Component
 *
 * Root component that sets up routing and error boundaries
 * NOTE: Suspense boundary removed - all components are now direct imports
 * to fix Playwright test timeout issues caused by double Suspense nesting.
 *
 * ThemeProvider wraps the app to provide theme context with:
 * - localStorage persistence
 * - data-theme attribute on document.documentElement
 * - Dark mode default (Cyberpunk Lab Theme)
 */
function App(): React.JSX.Element {
  const element = useRoutes(routes);

  return (
    <ThemeProvider>
      <ErrorBoundary>
        {element || <Navigate to="/" replace />}
      </ErrorBoundary>
    </ThemeProvider>
  );
}

export default App;
