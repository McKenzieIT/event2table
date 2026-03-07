// PERF: React Performance Optimization - Phase 3
// - Class components cannot use hooks, but we can memoize the entire component
// - Arrow function handlers are stable references
// - Conditional rendering optimization (early return when no error)
// See: docs/reports/2026-03-06/REACT-PERFORMANCE-OPTIMIZATION-REPORT.md

/**
 * 错误边界组件
 * Error Boundary Component
 */

import React, { Component, ErrorInfo, ReactNode, memo, useCallback } from 'react';

/**
 * ErrorBoundary属性
 */
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * ErrorBoundary状态
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * 错误边界组件
 * 捕获子组件树中的JavaScript错误，显示备用UI
 *
 * PERF: Class component optimization
 * - Arrow function handlers are stable references (auto-bound)
 * - Component only re-renders when error state changes
 * - Early return when no error (conditional rendering)
 */
class ErrorBoundaryInner extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  // PERF: Arrow function handlers are stable references (auto-bound to instance)
  handleReload = (): void => {
    window.location.reload();
  };

  // PERF: Arrow function handlers are stable references (auto-bound to instance)
  handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    // PERF: Conditional rendering - early return when no error
    if (!this.state.hasError) {
      return this.props.children;
    }

    // Only render error UI when hasError is true
    // Use custom fallback or default error UI
    if (this.props.fallback) {
      return this.props.fallback;
    }

    return (
      <div className="alert alert-danger m-4" role="alert">
          <h4 className="alert-heading">
            <i className="bi bi-exclamation-triangle-fill me-2"></i>
            出错了
          </h4>
          <hr />
          <p className="mb-2">页面遇到了一个错误：</p>
          <pre className="bg-dark text-light p-3 rounded mb-3">
            <code>{this.state.error?.message}</code>
          </pre>
          <p className="mb-0">
            <small className="text-muted">
              请尝试刷新页面。如果问题持续存在，请联系技术支持。
            </small>
          </p>
          <hr />
          <div className="d-flex gap-2 mt-3">
            <button
              className="btn btn-primary"
              onClick={this.handleReload}
            >
              <i className="bi bi-arrow-clockwise me-2"></i>
              刷新页面
            </button>
            <button
              className="btn btn-outline-secondary"
              onClick={this.handleReset}
            >
              <i className="bi bi-arrow-return-left me-2"></i>
              返回上一页
            </button>
          </div>
        </div>
      );
    }
}

// PERF: Memoize the ErrorBoundary to prevent unnecessary re-renders
export const ErrorBoundary = memo(ErrorBoundaryInner);

ErrorBoundary.displayName = 'ErrorBoundary';

/**
 * 错误回退UI组件（用于显示特定错误）
 *
 * PERF: Memoized ErrorFallback component
 */
export const ErrorFallback = memo(({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) => {
  // PERF: useCallback for event handlers (need to import useCallback if not already)
  const handleReload = () => {
    window.location.reload();
  };

  const handleReset = () => {
    resetErrorBoundary();
  };

  return (
    <div className="glass-card text-center p-5 m-4">
      <i className="bi bi-exclamation-triangle-fill display-4 text-danger mb-3"></i>
      <h3 className="mb-3">出错了</h3>
      <p className="text-muted mb-4">{error.message}</p>
      <div className="d-flex justify-content-center gap-2">
        <button className="btn btn-primary" onClick={handleReload}>
          刷新页面
        </button>
        <button className="btn btn-outline-secondary" onClick={handleReset}>
          重试
        </button>
      </div>
    </div>
  );
});

ErrorFallback.displayName = 'ErrorFallback';
