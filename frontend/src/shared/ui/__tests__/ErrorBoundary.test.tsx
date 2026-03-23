/**
 * ErrorBoundary Component Tests
 * 
 * Tests for the error boundary component that catches JavaScript errors
 * in child component tree and displays a fallback UI.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@test/test-utils';
import React from 'react';
import { ErrorBoundary, ErrorFallback } from '../ErrorBoundary';

// Mock console.error to suppress error logs in tests
const originalError = console.error;
beforeEach(() => {
  console.error = vi.fn();
});

afterEach(() => {
  console.error = originalError;
});

// Component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  describe('Normal Rendering', () => {
    it('should render children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div>Test child</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Test child')).toBeInTheDocument();
    });

    it('should not display error UI when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div>Test child</div>
        </ErrorBoundary>
      );

      expect(screen.queryByText('出错了')).not.toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should catch errors and display error UI', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('出错了')).toBeInTheDocument();
      expect(screen.getByText('Test error')).toBeInTheDocument();
    });

    it('should display custom fallback when provided', () => {
      render(
        <ErrorBoundary fallback={<div>Custom error UI</div>}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom error UI')).toBeInTheDocument();
    });

    it('should log error to console', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(console.error).toHaveBeenCalled();
    });

    it('should display error message in code block', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const codeElement = screen.getByText('Test error');
      expect(codeElement.tagName).toBe('CODE');
    });
  });

  describe('User Actions', () => {
    it('should have a refresh button', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const refreshButton = screen.getByRole('button', { name: /刷新页面/i });
      expect(refreshButton).toBeInTheDocument();
    });

    it('should have a reset button', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const resetButton = screen.getByRole('button', { name: /返回上一页/i });
      expect(resetButton).toBeInTheDocument();
    });

    it('should reload page when refresh button clicked', () => {
      const reloadMock = vi.fn();
      Object.defineProperty(window.location, 'reload', {
        value: reloadMock,
        writable: true,
      });

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const refreshButton = screen.getByRole('button', { name: /刷新页面/i });
      fireEvent.click(refreshButton);

      expect(reloadMock).toHaveBeenCalled();
    });

    it('should reset error state when reset button clicked', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      // Verify error UI is shown
      expect(screen.getByText('出错了')).toBeInTheDocument();

      // Click reset button
      const resetButton = screen.getByRole('button', { name: /返回上一页/i });
      fireEvent.click(resetButton);

      // Rerender without error
      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      // Should show normal content
      expect(screen.getByText('No error')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper alert role', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });

    it('should have proper heading structure', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const heading = screen.getByRole('heading', { level: 4 });
      expect(heading).toHaveTextContent('出错了');
    });
  });
});

describe('ErrorFallback', () => {
  const mockError = new Error('Fallback test error');
  const mockReset = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render error message', () => {
    render(<ErrorFallback error={mockError} resetErrorBoundary={mockReset} />);

    expect(screen.getByText('Fallback test error')).toBeInTheDocument();
  });

  it('should have refresh button', () => {
    render(<ErrorFallback error={mockError} resetErrorBoundary={mockReset} />);

    expect(screen.getByRole('button', { name: '刷新页面' })).toBeInTheDocument();
  });

  it('should have retry button', () => {
    render(<ErrorFallback error={mockError} resetErrorBoundary={mockReset} />);

    expect(screen.getByRole('button', { name: '重试' })).toBeInTheDocument();
  });

  it('should reload page when refresh button clicked', () => {
    const reloadMock = vi.fn();
    Object.defineProperty(window.location, 'reload', {
      value: reloadMock,
      writable: true,
    });

    render(<ErrorFallback error={mockError} resetErrorBoundary={mockReset} />);

    const refreshButton = screen.getByRole('button', { name: '刷新页面' });
    fireEvent.click(refreshButton);

    expect(reloadMock).toHaveBeenCalled();
  });

  it('should call resetErrorBoundary when retry button clicked', () => {
    render(<ErrorFallback error={mockError} resetErrorBoundary={mockReset} />);

    const retryButton = screen.getByRole('button', { name: '重试' });
    fireEvent.click(retryButton);

    expect(mockReset).toHaveBeenCalled();
  });

  it('should have danger icon', () => {
    render(<ErrorFallback error={mockError} resetErrorBoundary={mockReset} />);

    const icon = screen.getByRole('img', { hidden: true });
    expect(icon).toHaveClass('bi-exclamation-triangle-fill');
  });
});
