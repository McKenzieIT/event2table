// PERF: React Performance Optimization - Phase 3
// - Class components cannot use hooks, but we can memoize the entire component
// - Arrow function handlers are stable references
// See: docs/reports/2026-03-06/REACT-PERFORMANCE-OPTIMIZATION-REPORT.md

import React, { Component, ReactNode, memo } from 'react';
import './CanvasErrorBoundary.css';

/**
 * Props for CanvasErrorBoundary component
 */
interface CanvasErrorBoundaryProps {
  children: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

/**
 * State for CanvasErrorBoundary component
 */
interface CanvasErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * Canvas错误边界组件
 * 捕获Canvas子组件的错误并显示友好提示
 *
 * PERF: Class component optimization
 * - Arrow function handlers are stable references (auto-bound)
 * - Component only re-renders when error state changes
 * - Early return when no error (conditional rendering)
 */
class CanvasErrorBoundaryInner extends Component<CanvasErrorBoundaryProps, CanvasErrorBoundaryState> {
  constructor(props: CanvasErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<CanvasErrorBoundaryState> {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('[CanvasErrorBoundary]', error, errorInfo);

    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // 可选：发送错误到监控服务
    this.props.onError?.(error, errorInfo);
  }

  // PERF: Arrow function handlers are stable references (auto-bound to instance)
  handleReset = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  // PERF: Arrow function handlers are stable references (auto-bound to instance)
  handleReload = (): void => {
    window.location.reload();
  };

  // PERF: Arrow function handlers are stable references (auto-bound to instance)
  handleGoBack = (): void => {
    window.history.back();
  };

  render(): ReactNode {
    // PERF: Conditional rendering - early return when no error
    if (!this.state.hasError) {
      return this.props.children;
    }

    // Only render error UI when hasError is true
    return (
      <div className="canvas-error-boundary">
          <div className="error-container">
            <i className="bi bi-bug-fill error-icon"></i>
            <h2>画布出现错误</h2>
            <p className="error-message">
              {this.state.error?.message || '未知错误'}
            </p>

            {process.env.NODE_ENV === 'development' && (
              <details className="error-details">
                <summary>错误详情（开发模式）</summary>
                <pre>{this.state.error?.stack}</pre>
                <pre>{this.state.errorInfo?.componentStack}</pre>
              </details>
            )}

            <div className="error-actions">
              <button onClick={this.handleReset} className="btn btn-primary">
                重试
              </button>
              <button onClick={this.handleReload} className="btn btn-secondary">
                重新加载页面
              </button>
              <button onClick={this.handleGoBack} className="btn btn-secondary">
                返回
              </button>
            </div>
          </div>
        </div>
      );
    }
}

// PERF: Memoize the ErrorBoundary to prevent unnecessary re-renders
const CanvasErrorBoundary = memo(CanvasErrorBoundaryInner);

CanvasErrorBoundary.displayName = 'CanvasErrorBoundary';

export default CanvasErrorBoundary;
