/**
 * ErrorState Component Tests
 * 测试错误状态组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorState } from './ErrorState';

describe('ErrorState Component', () => {
  describe('Rendering', () => {
    it('should render with default title', () => {
      render(<ErrorState />);
      expect(screen.getByText('加载失败')).toBeInTheDocument();
    });

    it('should render with custom title', () => {
      render(<ErrorState title="Custom Error" />);
      expect(screen.getByText('Custom Error')).toBeInTheDocument();
    });

    it('should render with error message', () => {
      render(<ErrorState message="Something went wrong" />);
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should render with error object', () => {
      const error = new Error('Test error');
      render(<ErrorState error={error} />);
      expect(screen.getByText('Test error')).toBeInTheDocument();
    });

    it('should render with error string', () => {
      render(<ErrorState error="Error string" />);
      expect(screen.getByText('Error string')).toBeInTheDocument();
    });

    it('should render error icon', () => {
      const { container } = render(<ErrorState />);
      expect(container.querySelector('.bi-exclamation-triangle')).toBeInTheDocument();
    });
  });

  describe('Error Message Priority', () => {
    it('should prioritize message over error object', () => {
      const error = new Error('Error from object');
      render(<ErrorState message="Message prop" error={error} />);
      expect(screen.getByText('Message prop')).toBeInTheDocument();
      expect(screen.queryByText('Error from object')).not.toBeInTheDocument();
    });

    it('should use error object message when message is not provided', () => {
      const error = new Error('Error from object');
      render(<ErrorState error={error} />);
      expect(screen.getByText('Error from object')).toBeInTheDocument();
    });

    it('should use default message when neither message nor error is provided', () => {
      render(<ErrorState />);
      expect(screen.getByText('未知错误')).toBeInTheDocument();
    });
  });

  describe('Retry Button', () => {
    it('should render retry button when onRetry is provided', () => {
      const handleRetry = vi.fn();
      render(<ErrorState onRetry={handleRetry} />);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should call onRetry when retry button is clicked', async () => {
      const handleRetry = vi.fn();
      render(<ErrorState onRetry={handleRetry} />);

      await userEvent.click(screen.getByRole('button'));
      expect(handleRetry).toHaveBeenCalledTimes(1);
    });

    it('should not render retry button when onRetry is not provided', () => {
      render(<ErrorState />);
      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });

    it('should render retry button with correct label', () => {
      render(<ErrorState onRetry={() => {}} />);
      expect(screen.getByText('重试')).toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<ErrorState className="custom-error" />);
      expect(container.querySelector('.custom-error')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should be accessible', () => {
      render(<ErrorState title="Error" message="Error occurred" />);
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Error occurred')).toBeInTheDocument();
    });

    it('should have error icon with proper class', () => {
      const { container } = render(<ErrorState />);
      expect(container.querySelector('.error-state-icon')).toBeInTheDocument();
    });
  });

  describe('Error Display', () => {
    it('should display error state title', () => {
      const { container } = render(<ErrorState />);
      expect(container.querySelector('.error-state-title')).toBeInTheDocument();
    });

    it('should display error state message', () => {
      const { container } = render(<ErrorState message="Error message" />);
      expect(container.querySelector('.error-state-message')).toBeInTheDocument();
    });
  });
});
