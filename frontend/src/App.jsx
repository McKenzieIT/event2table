import React, { Suspense } from 'react';
import { useRoutes, Navigate } from 'react-router-dom';
import { routes } from './routes/routes';

/**
 * Global Loading Component
 * Shows during initial app load and route transitions
 */
function GlobalLoading() {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      gap: '16px',
      backgroundColor: '#f8fafc',
      zIndex: 9999
    }}>
      <div style={{
        width: '48px',
        height: '48px',
        border: '4px solid #e2e8f0',
        borderTop: '4px solid #3b82f6',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
      }} />
      <div style={{
        color: '#64748b',
        fontSize: '14px',
        fontWeight: '500'
      }}>
        Loading Event2Table...
      </div>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

/**
 * App Component
 *
 * Root component that sets up routing and error boundaries
 * Includes global Suspense boundary for lazy-loaded routes
 */
function App() {
  const element = useRoutes(routes);

  return (
    <Suspense fallback={<GlobalLoading />}>
      {element || <Navigate to="/" replace />}
    </Suspense>
  );
}

export default App;
