import React from 'react';
import { useRoutes, Navigate } from 'react-router-dom';
import { routes } from './routes/routes';

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
    <>
      {element || <Navigate to="/" replace />}
    </>
  );
}

export default App;
