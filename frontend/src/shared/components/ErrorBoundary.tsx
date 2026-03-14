import React, { Component, ReactNode, MouseEvent } from 'react';

/**
 * Error Boundary Component
 *
 * 捕获组件树中的JavaScript错误，记录错误日志，并显示备用UI
 *
 * 使用方法:
 * <ErrorBoundary fallback={<ErrorFallback />}>
 *   <YourComponent />
 * </ErrorBoundary>
 */

export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

// 内联样式（避免依赖外部CSS文件）
const styles: Record<string, React.CSSProperties> = {
  errorContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    padding: '20px',
    backgroundColor: '#fef2f2',
  },
  errorCard: {
    maxWidth: '600px',
    width: '100%',
    padding: '48px',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    textAlign: 'center',
  },
  errorTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#dc2626',
    marginBottom: '16px',
  },
  errorMessage: {
    fontSize: '16px',
    color: '#4b5563',
    marginBottom: '24px',
    lineHeight: '1.5',
  },
  errorDetails: {
    marginTop: '24px',
    marginBottom: '24px',
    textAlign: 'left',
    backgroundColor: '#f9fafb',
    padding: '16px',
    borderRadius: '8px',
    border: '1px solid #e5e7eb',
  },
  errorSummary: {
    cursor: 'pointer',
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: '12px',
  },
  errorStack: {
    maxHeight: '300px',
    overflow: 'auto',
  },
  errorStackTitle: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#374151',
    marginTop: '12px',
    marginBottom: '8px',
  },
  errorCode: {
    backgroundColor: '#1f2937',
    color: '#f3f4f6',
    padding: '12px',
    borderRadius: '6px',
    fontSize: '12px',
    overflow: 'auto',
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-all' as const,
  },
  errorActions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
  },
  retryButton: {
    padding: '12px 24px',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  homeButton: {
    padding: '12px 24px',
    backgroundColor: '#9ca3af',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
};

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // 更新state使下一次渲染能够显示降级后的UI
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // 可以将错误日志上报给服务器
    console.error('Error Boundary caught an error:', error);
    console.error('Error Info:', errorInfo);

    // 保存错误信息到state
    this.setState({
      error,
      errorInfo,
    });

    // TODO: 发送错误到日志服务
    // logErrorToService(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });

    // 如果提供了onReset回调，调用它
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  handleRetryMouseEnter = (e: MouseEvent<HTMLButtonElement>): void => {
    e.currentTarget.style.backgroundColor = '#2563eb';
  };

  handleRetryMouseLeave = (e: MouseEvent<HTMLButtonElement>): void => {
    e.currentTarget.style.backgroundColor = '#3b82f6';
  };

  handleHomeMouseEnter = (e: MouseEvent<HTMLButtonElement>): void => {
    e.currentTarget.style.backgroundColor = '#6b7280';
  };

  handleHomeMouseLeave = (e: MouseEvent<HTMLButtonElement>): void => {
    e.currentTarget.style.backgroundColor = '#9ca3af';
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // 如果提供了自定义fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 否则使用默认错误UI
      return (
        <div style={styles.errorContainer}>
          <div style={styles.errorCard}>
            <h2 style={styles.errorTitle}>⚠️ 页面加载失败</h2>
            <p style={styles.errorMessage}>
              抱歉，页面遇到了一些问题。我们已经记录了这个问题，请稍后再试。
            </p>

            {/* 开发环境显示详细错误信息 */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details style={styles.errorDetails}>
                <summary style={styles.errorSummary}>查看错误详情（开发模式）</summary>
                <div style={styles.errorStack}>
                  <h4 style={styles.errorStackTitle}>Error:</h4>
                  <pre style={styles.errorCode}>
                    {this.state.error.toString()}
                  </pre>

                  {this.state.errorInfo && (
                    <>
                      <h4 style={styles.errorStackTitle}>Component Stack:</h4>
                      <pre style={styles.errorCode}>
                        {this.state.errorInfo.componentStack}
                      </pre>

                      <h4 style={styles.errorStackTitle}>Stack Trace:</h4>
                      <pre style={styles.errorCode}>
                        {this.state.error.stack}
                      </pre>
                    </>
                  )}
                </div>
              </details>
            )}

            <div style={styles.errorActions}>
              <button
                onClick={this.handleReset}
                style={styles.retryButton}
                onMouseEnter={this.handleRetryMouseEnter}
                onMouseLeave={this.handleRetryMouseLeave}
              >
                🔄 重试
              </button>
              <button
                onClick={() => window.location.href = '/'}
                style={styles.homeButton}
                onMouseEnter={this.handleHomeMouseEnter}
                onMouseLeave={this.handleHomeMouseLeave}
              >
                🏠 返回首页
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

/**
 * 使用示例:
 *
 * // 1. 基础使用
 * <ErrorBoundary>
 *   <MyComponent />
 * </ErrorBoundary>
 *
 * // 2. 自定义fallback
 * <ErrorBoundary fallback={<CustomErrorUI />}>
 *   <MyComponent />
 * </ErrorBoundary>
 *
 * // 3. 带重置回调
 * <ErrorBoundary onReset={() => }>
 *   <MyComponent />
 * </ErrorBoundary>
 *
 * // 4. 在App.tsx中包裹整个应用
 * <ErrorBoundary>
 *   <App />
 * </ErrorBoundary>
 */
