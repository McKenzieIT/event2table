/**
 * Spinner Component Tests
 * 测试加载动画组件的所有功能
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Spinner from './Spinner';

describe('Spinner Component', () => {
  describe('Rendering', () => {
    it('should render spinner element', () => {
      const { container } = render(<Spinner />);
      expect(container.querySelector('.cyber-spinner')).toBeInTheDocument();
    });

    it('should render spinner circles', () => {
      const { container } = render(<Spinner />);
      expect(container.querySelectorAll('.cyber-spinner-circle')).toHaveLength(3);
    });

    it('should have role="status"', () => {
      render(<Spinner />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should have aria-live="polite"', () => {
      render(<Spinner />);
      expect(screen.getByRole('status')).toHaveAttribute('aria-live', 'polite');
    });

    it('should have aria-busy="true"', () => {
      render(<Spinner />);
      expect(screen.getByRole('status')).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('Sizes', () => {
    it('should render small size', () => {
      const { container } = render(<Spinner size="sm" />);
      expect(container.querySelector('.cyber-spinner--sm')).toBeInTheDocument();
    });

    it('should render medium size (default)', () => {
      const { container } = render(<Spinner />);
      expect(container.querySelector('.cyber-spinner--md')).toBeInTheDocument();
    });

    it('should render large size', () => {
      const { container } = render(<Spinner size="lg" />);
      expect(container.querySelector('.cyber-spinner--lg')).toBeInTheDocument();
    });
  });

  describe('Label', () => {
    it('should render label when provided', () => {
      render(<Spinner label="Loading data..." />);
      expect(screen.getByText('Loading data...')).toBeInTheDocument();
    });

    it('should not render label when not provided', () => {
      const { container } = render(<Spinner />);
      expect(container.querySelector('.cyber-spinner-label')).not.toBeInTheDocument();
    });

    it('should render label with correct class', () => {
      const { container } = render(<Spinner label="Loading..." />);
      expect(container.querySelector('.cyber-spinner-label')).toBeInTheDocument();
    });
  });

  describe('Screen Reader Text', () => {
    it('should have screen reader text', () => {
      render(<Spinner />);
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should have sr-only class on screen reader text', () => {
      const { container } = render(<Spinner />);
      expect(container.querySelector('.sr-only')).toHaveTextContent('Loading...');
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Spinner className="custom-spinner" />);
      expect(container.querySelector('.custom-spinner')).toBeInTheDocument();
    });

    it('should combine multiple classes', () => {
      const { container } = render(<Spinner size="lg" className="custom-spinner" />);
      const spinner = container.querySelector('.cyber-spinner');
      expect(spinner).toHaveClass('cyber-spinner');
      expect(spinner).toHaveClass('cyber-spinner--lg');
      expect(spinner).toHaveClass('custom-spinner');
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to div element', () => {
      const ref = { current: null };
      render(<Spinner ref={ref} />);
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('Accessibility', () => {
    it('should be accessible for screen readers', () => {
      render(<Spinner label="Loading content" />);
      const spinner = screen.getByRole('status');
      
      expect(spinner).toHaveAttribute('aria-live', 'polite');
      expect(spinner).toHaveAttribute('aria-busy', 'true');
      expect(spinner).toHaveTextContent('Loading content');
    });

    it('should hide decorative circles from screen readers', () => {
      const { container } = render(<Spinner />);
      const circles = container.querySelectorAll('.cyber-spinner-circle');
      
      circles.forEach(circle => {
        expect(circle).toHaveAttribute('aria-hidden', 'true');
      });
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Spinner size="md" />);
      const initialElement = screen.getByRole('status');

      rerender(<Spinner size="md" />);
      const afterRerenderElement = screen.getByRole('status');

      expect(initialElement).toBe(afterRerenderElement);
    });

    it('should re-render when props change', () => {
      const { rerender, container } = render(<Spinner size="sm" />);
      expect(container.querySelector('.cyber-spinner--sm')).toBeInTheDocument();

      rerender(<Spinner size="lg" />);
      expect(container.querySelector('.cyber-spinner--lg')).toBeInTheDocument();
      expect(container.querySelector('.cyber-spinner--sm')).not.toBeInTheDocument();
    });
  });

  describe('Additional Props', () => {
    it('should support data-testid', () => {
      render(<Spinner data-testid="loading-spinner" />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('should support aria-label', () => {
      render(<Spinner aria-label="Content is loading" />);
      expect(screen.getByLabelText('Content is loading')).toBeInTheDocument();
    });
  });
});
