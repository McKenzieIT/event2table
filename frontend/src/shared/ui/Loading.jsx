import React from 'react';
import { Spinner } from '@shared/ui';
import './Loading.css';

/**
 * Loading Component
 *
 * Displayed during lazy loading and suspense
 * Uses the shared Spinner component for consistency
 */
function Loading() {
  return (
    <div className="loading-container" data-testid="loading-spinner">
      <div className="loading-spinner">
        <Spinner size="lg" />
        <p className="loading-text">加载中...</p>
      </div>
    </div>
  );
}

export default Loading;
