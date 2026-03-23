/**
 * ErrorBoundary component tests
 * 测试错误边界组件
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@test/test-utils';
import { ErrorBoundary, ErrorFallback } from './ErrorBoundary';

// 创建一个会抛出错误的组件
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary component', () => {
  describe('错误捕获', () => {
    it('应该在子组件抛出错误时捕获并显示错误 UI', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText(/出错了/i)).toBeInTheDocument();
      expect(screen.getByText(/Test error/i)).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });

    it('应该在子组件正常时渲染子组件', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();
      expect(screen.queryByText(/出错了/i)).not.toBeInTheDocument();
    });

    it('应该使用自定义 fallback', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const customFallback = <div>Custom Error UI</div>;
      
      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom Error UI')).toBeInTheDocument();
      expect(screen.queryByText(/Test error/i)).not.toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });

    it('应该在 componentDidCatch 中记录错误', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });
  });

  describe('错误恢复', () => {
    it('应该在点击刷新页面按钮时重新加载页面', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const reloadSpy = vi.spyOn(window.location, 'reload').mockImplementation(() => {});
      
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const reloadButton = screen.getByText(/刷新页面/i);
      fireEvent.click(reloadButton);

      expect(reloadSpy).toHaveBeenCalledTimes(1);
      
      reloadSpy.mockRestore();
      consoleSpy.mockRestore();
    });

    it('应该在点击返回上一页按钮时重置错误状态', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText(/出错了/i)).toBeInTheDocument();

      const resetButton = screen.getByText(/返回上一页/i);
      fireEvent.click(resetButton);

      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();
      expect(screen.queryByText(/出错了/i)).not.toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });
  });

  describe('可访问性', () => {
    it('应该为错误容器设置正确的 role 属性', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const alertElement = screen.getByRole('alert');
      expect(alertElement).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });

    it('应该显示错误图标', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const icon = screen.getByRole('img', { hidden: true });
      expect(icon).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });
  });

  describe('ErrorFallback 组件', () => {
    it('应该渲染错误信息', () => {
      const error = new Error('Test error message');
      const resetErrorBoundary = vi.fn();

      render(<ErrorFallback error={error} resetErrorBoundary={resetErrorBoundary} />);

      expect(screen.getByText('出错了')).toBeInTheDocument();
      expect(screen.getByText('Test error message')).toBeInTheDocument();
    });

    it('应该在点击刷新按钮时重新加载页面', () => {
      const error = new Error('Test error');
      const resetErrorBoundary = vi.fn();
      const reloadSpy = vi.spyOn(window.location, 'reload').mockImplementation(() => {});

      render(<ErrorFallback error={error} resetErrorBoundary={resetErrorBoundary} />);

      const reloadButton = screen.getByText('刷新页面');
      fireEvent.click(reloadButton);

      expect(reloadSpy).toHaveBeenCalledTimes(1);

      reloadSpy.mockRestore();
    });

    it('应该在点击重试按钮时调用 resetErrorBoundary', () => {
      const error = new Error('Test error');
      const resetErrorBoundary = vi.fn();

      render(<ErrorFallback error={error} resetErrorBoundary={resetErrorBoundary} />);

      const retryButton = screen.getByText('重试');
      fireEvent.click(retryButton);

      expect(resetErrorBoundary).toHaveBeenCalledTimes(1);
    });
  });

  describe('边界情况', () => {
    it('应该处理空错误消息', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      const EmptyError = () => {
        throw new Error('');
      };

      render(
        <ErrorBoundary>
          <EmptyError />
        </ErrorBoundary>
      );

      expect(screen.getByText(/出错了/i)).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });

    it('应该处理嵌套组件中的错误', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      const ParentComponent = () => (
        <div>
          <ThrowError shouldThrow={true} />
        </div>
      );

      render(
        <ErrorBoundary>
          <ParentComponent />
        </ErrorBoundary>
      );

      expect(screen.getByText(/出错了/i)).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });
  });
});
