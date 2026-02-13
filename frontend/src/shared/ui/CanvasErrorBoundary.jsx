import React from 'react';
import PropTypes from 'prop-types';
import './CanvasErrorBoundary.css';

/**
 * Canvas错误边界组件
 * 捕获Canvas子组件的错误并显示友好提示
 */
class CanvasErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null
        };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('[CanvasErrorBoundary]', error, errorInfo);

        this.setState({
            error: error,
            errorInfo: errorInfo
        });

        // 可选：发送错误到监控服务
        // this.props.onError?.(error, errorInfo);
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    handleReload = () => {
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
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
                            <button onClick={() => window.history.back()} className="btn btn-secondary">
                                返回
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

CanvasErrorBoundary.propTypes = {
    children: PropTypes.node.isRequired,
    onError: PropTypes.func
};

export default CanvasErrorBoundary;
