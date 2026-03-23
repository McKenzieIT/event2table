// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Toast Component Tests
 * 测试通知提示组件的所有功能
 */

import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import ToastProvider, { useToast } from './Toast';

describe('Toast Component', () => {
  beforeEach(() => {
    vi.clearAllTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const TestComponent = () => {
    const { success, error, warning, info, showToast, toasts } = useToast();

    return (
      <div>
        <button onClick={() => success('Success message')}>Success</button>
        <button onClick={() => error('Error message')}>Error</button>
        <button onClick={() => warning('Warning message')}>Warning</button>
        <button onClick={() => info('Info message')}>Info</button>
        <button onClick={() => showToast('custom', 'Custom message', 100)}>Custom Short</button>
        <button onClick={() => showToast('custom', 'Custom message', 10000)}>Custom Long</button>
        <div data-testid="toast-count">{toasts.length}</div>
      </div>
    );
  };

  const renderWithProvider = () => {
    return render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    );
  };

  describe('ToastProvider', () => {
    it('should render children', () => {
      render(
        <ToastProvider>
          <div>Child Content</div>
        </ToastProvider>
      );
      expect(screen.getByText('Child Content')).toBeInTheDocument();
    });
  });

  describe('Success Toast', () => {
    it('should show success toast', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));

      expect(screen.getByText('Success message')).toBeInTheDocument();
      expect(screen.getByTestId('toast-count')).toHaveTextContent('1');
    });

    it('should have success styling', async () => {
      const { container } = renderWithProvider();

      await userEvent.click(screen.getByText('Success'));

      expect(container.querySelector('.cyber-toast--success')).toBeInTheDocument();
    });

    it('should have success icon', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));

      expect(screen.getByText('✓')).toBeInTheDocument();
    });
  });

  describe('Error Toast', () => {
    it('should show error toast', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Error'));

      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByTestId('toast-count')).toHaveTextContent('1');
    });

    it('should have error styling', async () => {
      const { container } = renderWithProvider();

      await userEvent.click(screen.getByText('Error'));

      expect(container.querySelector('.cyber-toast--error')).toBeInTheDocument();
    });

    it('should have error icon', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Error'));

      expect(screen.getByText('✕')).toBeInTheDocument();
    });
  });

  describe('Warning Toast', () => {
    it('should show warning toast', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Warning'));

      expect(screen.getByText('Warning message')).toBeInTheDocument();
      expect(screen.getByTestId('toast-count')).toHaveTextContent('1');
    });

    it('should have warning styling', async () => {
      const { container } = renderWithProvider();

      await userEvent.click(screen.getByText('Warning'));

      expect(container.querySelector('.cyber-toast--warning')).toBeInTheDocument();
    });

    it('should have warning icon', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Warning'));

      expect(screen.getByText('⚠')).toBeInTheDocument();
    });
  });

  describe('Info Toast', () => {
    it('should show info toast', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Info'));

      expect(screen.getByText('Info message')).toBeInTheDocument();
      expect(screen.getByTestId('toast-count')).toHaveTextContent('1');
    });

    it('should have info styling', async () => {
      const { container } = renderWithProvider();

      await userEvent.click(screen.getByText('Info'));

      expect(container.querySelector('.cyber-toast--info')).toBeInTheDocument();
    });

    it('should have info icon', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Info'));

      expect(screen.getByText('ℹ')).toBeInTheDocument();
    });
  });

  describe('Custom Toast', () => {
    it('should show custom toast with custom type', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Custom Short'));

      expect(screen.getByText('Custom message')).toBeInTheDocument();
    });

    it('should support custom duration', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Custom Short'));

      expect(screen.getByText('Custom message')).toBeInTheDocument();

      // Wait for auto-dismiss (100ms)
      await new Promise(resolve => setTimeout(resolve, 150));
      await waitFor(() => {
        expect(screen.queryByText('Custom message')).not.toBeInTheDocument();
      });
    });
  });

  describe('Auto-dismiss', () => {
    it('should auto-dismiss after short duration (100ms)', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Custom Short'));

      expect(screen.getByText('Custom message')).toBeInTheDocument();

      // Wait for auto-dismiss
      await new Promise(resolve => setTimeout(resolve, 150));
      await waitFor(() => {
        expect(screen.queryByText('Custom message')).not.toBeInTheDocument();
      });
    });

    it('should not auto-dismiss quickly for long duration (10000ms)', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Custom Long'));

      expect(screen.getByText('Custom message')).toBeInTheDocument();

      // Should still be there after 200ms
      await new Promise(resolve => setTimeout(resolve, 200));
      expect(screen.getByText('Custom message')).toBeInTheDocument();
    });
  });

  describe('Manual Dismiss', () => {
    it('should dismiss toast when close button is clicked', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));
      expect(screen.getByText('Success message')).toBeInTheDocument();

      await userEvent.click(screen.getByLabelText('关闭通知'));

      await waitFor(() => {
        expect(screen.queryByText('Success message')).not.toBeInTheDocument();
      });
    });

    it('should update toast count when manually dismissed', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));
      expect(screen.getByTestId('toast-count')).toHaveTextContent('1');

      await userEvent.click(screen.getByLabelText('关闭通知'));

      await waitFor(() => {
        expect(screen.getByTestId('toast-count')).toHaveTextContent('0');
      });
    });
  });

  describe('Multiple Toasts', () => {
    it('should show multiple toasts', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));
      await userEvent.click(screen.getByText('Error'));
      await userEvent.click(screen.getByText('Warning'));

      expect(screen.getByText('Success message')).toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByText('Warning message')).toBeInTheDocument();
      expect(screen.getByTestId('toast-count')).toHaveTextContent('3');
    });

    it('should dismiss toasts independently', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));
      await userEvent.click(screen.getByText('Error'));

      const closeButtons = screen.getAllByLabelText('关闭通知');
      await userEvent.click(closeButtons[0]);

      await waitFor(() => {
        expect(screen.getByTestId('toast-count')).toHaveTextContent('1');
      });
    });
  });

  describe('useToast Hook', () => {
    it('should throw error when used outside ToastProvider', () => {
      const ComponentWithoutProvider = () => {
        const { success } = useToast();
        return <button onClick={() => success('test')}>Test</button>;
      };

      expect(() => {
        render(<ComponentWithoutProvider />);
      }).toThrow('useToast must be used within a ToastProvider');
    });

    it('should provide all toast methods', () => {
      const ComponentWithHooks = () => {
        const toast = useToast();
        return (
          <div>
            <span data-testid="has-success">{typeof toast.success === 'function' ? 'yes' : 'no'}</span>
            <span data-testid="has-error">{typeof toast.error === 'function' ? 'yes' : 'no'}</span>
            <span data-testid="has-warning">{typeof toast.warning === 'function' ? 'yes' : 'no'}</span>
            <span data-testid="has-info">{typeof toast.info === 'function' ? 'yes' : 'no'}</span>
            <span data-testid="has-showToast">{typeof toast.showToast === 'function' ? 'yes' : 'no'}</span>
            <span data-testid="has-removeToast">{typeof toast.removeToast === 'function' ? 'yes' : 'no'}</span>
          </div>
        );
      };

      render(
        <ToastProvider>
          <ComponentWithHooks />
        </ToastProvider>
      );

      expect(screen.getByTestId('has-success')).toHaveTextContent('yes');
      expect(screen.getByTestId('has-error')).toHaveTextContent('yes');
      expect(screen.getByTestId('has-warning')).toHaveTextContent('yes');
      expect(screen.getByTestId('has-info')).toHaveTextContent('yes');
      expect(screen.getByTestId('has-showToast')).toHaveTextContent('yes');
      expect(screen.getByTestId('has-removeToast')).toHaveTextContent('yes');
    });
  });

  describe('Accessibility', () => {
    it('should have role="alert" on toast', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));

      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should have aria-live="assertive"', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));

      expect(screen.getByRole('alert')).toHaveAttribute('aria-live', 'assertive');
    });

    it('should have aria-atomic="true"', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));

      expect(screen.getByRole('alert')).toHaveAttribute('aria-atomic', 'true');
    });

    it('should have accessible close button', async () => {
      renderWithProvider();

      await userEvent.click(screen.getByText('Success'));

      const closeButton = screen.getByLabelText('关闭通知');
      expect(closeButton).toBeInTheDocument();
    });
  });
});
