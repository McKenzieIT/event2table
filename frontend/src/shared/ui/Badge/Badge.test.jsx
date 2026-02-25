/**
 * Badge Component Tests
 * 测试徽章组件的所有功能
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Badge from './Badge';

describe('Badge Component', () => {
  describe('Rendering', () => {
    it('should render with children', () => {
      render(<Badge>Test Badge</Badge>);
      expect(screen.getByText('Test Badge')).toBeInTheDocument();
    });

    it('should render as span element', () => {
      const { container } = render(<Badge>Badge</Badge>);
      expect(container.querySelector('span.cyber-badge')).toBeInTheDocument();
    });
  });

  describe('Variants', () => {
    it('should render default variant', () => {
      const { container } = render(<Badge>Default</Badge>);
      expect(container.querySelector('.cyber-badge--default')).toBeInTheDocument();
    });

    it('should render primary variant', () => {
      const { container } = render(<Badge variant="primary">Primary</Badge>);
      expect(container.querySelector('.cyber-badge--primary')).toBeInTheDocument();
    });

    it('should render success variant', () => {
      const { container } = render(<Badge variant="success">Success</Badge>);
      expect(container.querySelector('.cyber-badge--success')).toBeInTheDocument();
    });

    it('should render warning variant', () => {
      const { container } = render(<Badge variant="warning">Warning</Badge>);
      expect(container.querySelector('.cyber-badge--warning')).toBeInTheDocument();
    });

    it('should render danger variant', () => {
      const { container } = render(<Badge variant="danger">Danger</Badge>);
      expect(container.querySelector('.cyber-badge--danger')).toBeInTheDocument();
    });

    it('should render info variant', () => {
      const { container } = render(<Badge variant="info">Info</Badge>);
      expect(container.querySelector('.cyber-badge--info')).toBeInTheDocument();
    });
  });

  describe('Sizes', () => {
    it('should render small size', () => {
      const { container } = render(<Badge size="sm">Small</Badge>);
      expect(container.querySelector('.cyber-badge--sm')).toBeInTheDocument();
    });

    it('should render medium size (default)', () => {
      const { container } = render(<Badge>Medium</Badge>);
      expect(container.querySelector('.cyber-badge--md')).toBeInTheDocument();
    });

    it('should render large size', () => {
      const { container } = render(<Badge size="lg">Large</Badge>);
      expect(container.querySelector('.cyber-badge--lg')).toBeInTheDocument();
    });
  });

  describe('Dot', () => {
    it('should render dot when dot prop is true', () => {
      const { container } = render(<Badge dot>With Dot</Badge>);
      expect(container.querySelector('.cyber-badge--dot')).toBeInTheDocument();
      expect(container.querySelector('.cyber-badge__dot')).toBeInTheDocument();
    });

    it('should not render dot by default', () => {
      const { container } = render(<Badge>No Dot</Badge>);
      expect(container.querySelector('.cyber-badge__dot')).not.toBeInTheDocument();
    });
  });

  describe('Pill Shape', () => {
    it('should render pill shape when pill prop is true', () => {
      const { container } = render(<Badge pill>Pill Badge</Badge>);
      expect(container.querySelector('.cyber-badge--pill')).toBeInTheDocument();
    });

    it('should not render pill shape by default', () => {
      const { container } = render(<Badge>Normal Badge</Badge>);
      expect(container.querySelector('.cyber-badge--pill')).not.toBeInTheDocument();
    });
  });

  describe('Icon', () => {
    it('should render icon when icon prop is provided', () => {
      const TestIcon = () => <svg data-testid="test-icon" />;
      const { container } = render(<Badge icon={TestIcon}>With Icon</Badge>);
      expect(container.querySelector('.cyber-badge__icon')).toBeInTheDocument();
      expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('should not render icon when icon prop is not provided', () => {
      const { container } = render(<Badge>No Icon</Badge>);
      expect(container.querySelector('.cyber-badge__icon')).not.toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Badge className="custom-class">Custom</Badge>);
      expect(container.querySelector('.custom-class')).toBeInTheDocument();
    });

    it('should combine multiple classes', () => {
      const { container } = render(
        <Badge variant="primary" size="lg" className="custom-class">
          Combined
        </Badge>
      );
      const badge = container.querySelector('.cyber-badge');
      expect(badge).toHaveClass('cyber-badge');
      expect(badge).toHaveClass('cyber-badge--primary');
      expect(badge).toHaveClass('cyber-badge--lg');
      expect(badge).toHaveClass('custom-class');
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to span element', () => {
      const ref = { current: null };
      render(<Badge ref={ref}>Ref Test</Badge>);
      expect(ref.current).toBeInstanceOf(HTMLSpanElement);
    });
  });

  describe('Accessibility', () => {
    it('should support additional props', () => {
      render(<Badge data-testid="badge-test">Accessible</Badge>);
      expect(screen.getByTestId('badge-test')).toBeInTheDocument();
    });

    it('should support aria attributes', () => {
      render(
        <Badge aria-label="Status badge" role="status">
          Status
        </Badge>
      );
      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByLabelText('Status badge')).toBeInTheDocument();
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Badge variant="primary">Memoized</Badge>);
      const initialElement = screen.getByText('Memoized');

      rerender(<Badge variant="primary">Memoized</Badge>);
      const afterRerenderElement = screen.getByText('Memoized');

      // Same element reference due to memoization
      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
