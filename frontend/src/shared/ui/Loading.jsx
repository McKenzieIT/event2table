import React from 'react';
import './Loading.css';

/**
 * Loading Component
 *
 * Displayed during lazy loading and suspense
 */
function Loading() {
  return (
    <div className="loading-container" data-testid="loading-spinner">
      <div className="loading-spinner">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="loading-text">加载中...</p>
      </div>
    </div>
  );
}

export default Loading;
