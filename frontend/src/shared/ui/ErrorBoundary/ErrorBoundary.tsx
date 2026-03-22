/**
 * Enhanced Error Boundary Component
 * 增强版错误边界组件
 * 
 * Features:
 * - Error logging and recovery
 * - Custom fallback support (ReactNode or render function)
 * - onError callback for error reporting
 * - onReset callback for cleanup
 * - resetKeys for automatic reset on dependency changes
 */

import React, { Component, ReactNode, memo } from 'react';
import type { 
  ErrorBoundaryProps, 
  ErrorBoundaryState, 
  FallbackProps,
  ErrorInfo 
} from './types';

/**
 * Enhanced Error Boundary Component
 * 
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI.
 * 
 * @example
 * ```tsx
 * <ErrorBoundary
 *   fallback={<div>Something went wrong</div>}
 *   onError={(error, info) => logError(error, info)}
 *   onReset={() => clearState()}
 *   resetKeys={[userId]}
 * >
 *   <MyComponent />
 * </ErrorBoundary>
 * ```
 */
class ErrorBoundaryInner extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  static getDerivedStateFromProps(
    props: ErrorBoundaryProps,
    state: ErrorBoundaryState
  ): Partial<ErrorBoundaryState> | null {
    // Reset error state when resetKeys change
    if (state.hasError && props.resetKeys) {
      const { previousResetKeys } = state as ErrorBoundaryState & { previousResetKeys?: unknown[] };
      if (previousResetKeys && !shallowEqual(previousResetKeys, props.resetKeys)) {
        return { hasError: false, error: null, errorInfo: null };
      }
    }
    return null;
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    const customErrorInfo: ErrorInfo = {
      componentStack: errorInfo.componentStack || '',
      errorBoundary: 'ErrorBoundary',
    };

    // Log error to console
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Call external error handler
    this.props.onError?.(error, customErrorInfo);

    // Store error info and previous reset keys
    this.setState({ 
      errorInfo: customErrorInfo,
      previousResetKeys: this.props.resetKeys,
    } as ErrorBoundaryState & { previousResetKeys?: unknown[] });
  }

  handleReset = (): void => {
    this.props.onReset?.();
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    const { fallback } = this.props;

    // Support render function fallback
    if (typeof fallback === 'function') {
      return fallback({
        error: this.state.error!,
        errorInfo: this.state.errorInfo!,
        resetErrorBoundary: this.handleReset,
      });
    }

    // Support ReactNode fallback
    if (fallback) {
      return fallback;
    }

    // Default error UI
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
          <button className="btn btn-primary" onClick={this.handleReload}>
            <i className="bi bi-arrow-clockwise me-2"></i>
            刷新页面
          </button>
          <button className="btn btn-outline-secondary" onClick={this.handleReset}>
            <i className="bi bi-arrow-return-left me-2"></i>
            重试
          </button>
        </div>
      </div>
    );
  }
}

/**
 * Shallow equality check for resetKeys
 */
function shallowEqual(arr1: unknown[], arr2: unknown[]): boolean {
  if (arr1.length !== arr2.length) return false;
  return arr1.every((item, index) => item === arr2[index]);
}

// Memoize the component
const ErrorBoundary = memo(ErrorBoundaryInner);

ErrorBoundary.displayName = 'ErrorBoundary';

export { ErrorBoundary };
export type { ErrorBoundaryProps, FallbackProps, ErrorInfo };
