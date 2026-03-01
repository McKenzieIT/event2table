/**
 * EventNodeBuilderErrorBoundary Component
 * 事件节点构造器错误边界组件
 *
 * 功能:
 * - 捕获子组件中的渲染错误
 * - 显示友好的错误提示界面
 * - 提供错误详情供开发者调试
 * - 提供刷新页面按钮
 *
 * @component EventNodeBuilderErrorBoundary
 *
 * @example
 * <EventNodeBuilderErrorBoundary>
 *   <EventNodeBuilder />
 * </EventNodeBuilderErrorBoundary>
 */

import React, { Component, ReactNode, ErrorInfo } from 'react';
import './ErrorBoundary.css';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
}

/**
 * 错误边界组件
 */
class EventNodeBuilderErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // 更新 state 使下一次渲染能够显示降级后的 UI
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // 可以将错误日志上报给服务器
    console.error('[EventNodeBuilderErrorBoundary] Caught error:', error);
    console.error('[EventNodeBuilderErrorBoundary] Error info:', errorInfo);

    this.setState({
      error,
      errorInfo
    });

    // 可以在这里添加错误上报逻辑
    // logErrorToService(error, errorInfo);
  }

  handleReload = (): void => {
    // 刷新页面
    window.location.reload();
  };

  handleReset = (): void => {
    // 重置错误状态，尝试重新渲染
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <div className="error-icon">⚠️</div>
            <h2 className="error-title">组件渲染错误</h2>
            <p className="error-message">
              事件节点构造器遇到问题，无法正常显示。您可以尝试刷新页面或联系技术支持。
            </p>

            <div className="error-actions">
              <button
                className="btn btn-primary"
                onClick={this.handleReload}
              >
                <i className="bi bi-arrow-clockwise"></i>
                刷新页面
              </button>
              <button
                className="btn btn-secondary"
                onClick={this.handleReset}
              >
                <i className="bi bi-arrow-counterclockwise"></i>
                重试
              </button>
            </div>

            <details className="error-details">
              <summary>错误详情（开发者）</summary>
              <div className="error-details-content">
                <div className="error-section">
                  <h4>错误消息</h4>
                  <pre>{this.state.error?.toString()}</pre>
                </div>
                <div className="error-section">
                  <h4>组件堆栈</h4>
                  <pre>{this.state.errorInfo?.componentStack}</pre>
                </div>
                {this.state.error?.stack && (
                  <div className="error-section">
                    <h4>错误堆栈</h4>
                    <pre>{this.state.error.stack}</pre>
                  </div>
                )}
              </div>
            </details>

            <div className="error-tips">
              <h4>💡 提示</h4>
              <ul>
                <li>尝试清除浏览器缓存和 localStorage 后刷新</li>
                <li>检查控制台是否有更多错误信息</li>
                <li>如果问题持续存在，请联系技术支持</li>
              </ul>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default EventNodeBuilderErrorBoundary;
