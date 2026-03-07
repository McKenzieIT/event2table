// @ts-nocheck - TypeScript检查暂禁用
import React from 'react';
import { Button } from '@shared/ui';
import './ErrorState.css';

interface ErrorStateProps {
  title?: string;
  message?: string;
  error?: Error | string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = '加载失败',
  message,
  error,
  onRetry,
  className = ''
}) => {
  const errorMessage = message || (error instanceof Error ? error.message : String(error || '未知错误'));

  return (
    <div className={`error-state-component ${className}`}>
      <div className="error-state-icon">
        <i className="bi bi-exclamation-triangle"></i>
      </div>
      <h3 className="error-state-title">{title}</h3>
      <p className="error-state-message">{errorMessage}</p>
      {onRetry && (
        <Button variant="primary" onClick={onRetry}>
          <i className="bi bi-arrow-clockwise"></i>
          重试
        </Button>
      )}
    </div>
  );
};

// Memoize ErrorState to prevent unnecessary re-renders
const MemoizedErrorState = React.memo(ErrorState);
MemoizedErrorState.displayName = 'MemoizedErrorState';

export default MemoizedErrorState;
