/**
 * Card Component Tests
 * 测试卡片组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Card from './Card';

describe('Card Component', () => {
  describe('Rendering', () => {
    it('should render with children', () => {
      render(<Card>Card Content</Card>);
      expect(screen.getByText('Card Content')).toBeInTheDocument();
    });

    it('should render as div by default', () => {
      const { container } = render(<Card>Card</Card>);
      expect(container.querySelector('div.cyber-card')).toBeInTheDocument();
    });

    it('should render as custom element when as prop is provided', () => {
      const { container } = render(<Card as="article">Article Card</Card>);
      expect(container.querySelector('article.cyber-card')).toBeInTheDocument();
    });

    it('should render as custom component', () => {
      const CustomComponent = vi.fn(({ children, ...props }) => (
        <section {...props}>{children}</section>
      ));
      
      render(<Card as={CustomComponent}>Custom Card</Card>);
      expect(CustomComponent).toHaveBeenCalled();
    });
  });

  describe('Variants', () => {
    it('should render default variant', () => {
      const { container } = render(<Card>Default</Card>);
      expect(container.querySelector('.cyber-card--default')).toBeInTheDocument();
    });

    it('should apply custom variant', () => {
      const { container } = render(<Card variant="custom">Custom Variant</Card>);
      expect(container.querySelector('.cyber-card--custom')).toBeInTheDocument();
    });
  });

  describe('Hoverable', () => {
    it('should have hoverable class when hoverable prop is true', () => {
      const { container } = render(<Card hoverable>Hoverable Card</Card>);
      expect(container.querySelector('.cyber-card--hoverable')).toBeInTheDocument();
    });

    it('should have hoverable class when hover prop is true (alias)', () => {
      const { container } = render(<Card hover>Hover Card</Card>);
      expect(container.querySelector('.cyber-card--hoverable')).toBeInTheDocument();
    });

    it('should not have hoverable class by default', () => {
      const { container } = render(<Card>Normal Card</Card>);
      expect(container.querySelector('.cyber-card--hoverable')).not.toBeInTheDocument();
    });
  });

  describe('Glowing', () => {
    it('should have glowing class when glowing prop is true', () => {
      const { container } = render(<Card glowing>Glowing Card</Card>);
      expect(container.querySelector('.cyber-card--glowing')).toBeInTheDocument();
    });

    it('should not have glowing class by default', () => {
      const { container } = render(<Card>Normal Card</Card>);
      expect(container.querySelector('.cyber-card--glowing')).not.toBeInTheDocument();
    });
  });

  describe('Padding', () => {
    it('should have medium padding by default', () => {
      const { container } = render(<Card>Default Padding</Card>);
      expect(container.querySelector('.cyber-card--padding-md')).toBeInTheDocument();
    });

    it('should apply small padding', () => {
      const { container } = render(<Card padding="sm">Small Padding</Card>);
      expect(container.querySelector('.cyber-card--padding-sm')).toBeInTheDocument();
    });

    it('should apply large padding', () => {
      const { container } = render(<Card padding="lg">Large Padding</Card>);
      expect(container.querySelector('.cyber-card--padding-lg')).toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Card className="custom-card">Custom</Card>);
      expect(container.querySelector('.custom-card')).toBeInTheDocument();
    });

    it('should combine multiple classes', () => {
      const { container } = render(
        <Card variant="default" hoverable glowing className="custom-card">
          Combined
        </Card>
      );
      const card = container.querySelector('.cyber-card');
      expect(card).toHaveClass('cyber-card');
      expect(card).toHaveClass('cyber-card--default');
      expect(card).toHaveClass('cyber-card--hoverable');
      expect(card).toHaveClass('cyber-card--glowing');
      expect(card).toHaveClass('custom-card');
    });
  });

  describe('Sub-components', () => {
    describe('Card.Header', () => {
      it('should render header', () => {
        render(<Card.Header>Header Content</Card.Header>);
        expect(screen.getByText('Header Content')).toBeInTheDocument();
      });

      it('should have header class', () => {
        const { container } = render(<Card.Header>Header</Card.Header>);
        expect(container.querySelector('.cyber-card__header')).toBeInTheDocument();
      });

      it('should accept custom className', () => {
        const { container } = render(<Card.Header className="custom-header">Header</Card.Header>);
        expect(container.querySelector('.custom-header')).toBeInTheDocument();
      });
    });

    describe('Card.Body', () => {
      it('should render body', () => {
        render(<Card.Body>Body Content</Card.Body>);
        expect(screen.getByText('Body Content')).toBeInTheDocument();
      });

      it('should have body class', () => {
        const { container } = render(<Card.Body>Body</Card.Body>);
        expect(container.querySelector('.cyber-card__body')).toBeInTheDocument();
      });

      it('should accept custom className', () => {
        const { container } = render(<Card.Body className="custom-body">Body</Card.Body>);
        expect(container.querySelector('.custom-body')).toBeInTheDocument();
      });
    });

    describe('Card.Content (alias for Body)', () => {
      it('should render content', () => {
        render(<Card.Content>Content</Card.Content>);
        expect(screen.getByText('Content')).toBeInTheDocument();
      });

      it('should have body class (same as Card.Body)', () => {
        const { container } = render(<Card.Content>Content</Card.Content>);
        expect(container.querySelector('.cyber-card__body')).toBeInTheDocument();
      });
    });

    describe('Card.Footer', () => {
      it('should render footer', () => {
        render(<Card.Footer>Footer Content</Card.Footer>);
        expect(screen.getByText('Footer Content')).toBeInTheDocument();
      });

      it('should have footer class', () => {
        const { container } = render(<Card.Footer>Footer</Card.Footer>);
        expect(container.querySelector('.cyber-card__footer')).toBeInTheDocument();
      });

      it('should accept custom className', () => {
        const { container } = render(<Card.Footer className="custom-footer">Footer</Card.Footer>);
        expect(container.querySelector('.custom-footer')).toBeInTheDocument();
      });
    });

    describe('Card.Title', () => {
      it('should render title', () => {
        render(<Card.Title>Card Title</Card.Title>);
        expect(screen.getByText('Card Title')).toBeInTheDocument();
      });

      it('should render as h3 element', () => {
        const { container } = render(<Card.Title>Title</Card.Title>);
        expect(container.querySelector('h3.cyber-card__title')).toBeInTheDocument();
      });

      it('should accept custom className', () => {
        const { container } = render(<Card.Title className="custom-title">Title</Card.Title>);
        expect(container.querySelector('.custom-title')).toBeInTheDocument();
      });
    });
  });

  describe('Composed Card', () => {
    it('should render complete card with all sub-components', () => {
      render(
        <Card>
          <Card.Header>
            <Card.Title>Card Title</Card.Title>
          </Card.Header>
          <Card.Body>Card Body</Card.Body>
          <Card.Footer>Card Footer</Card.Footer>
        </Card>
      );

      expect(screen.getByText('Card Title')).toBeInTheDocument();
      expect(screen.getByText('Card Body')).toBeInTheDocument();
      expect(screen.getByText('Card Footer')).toBeInTheDocument();
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to div element', () => {
      const ref = { current: null };
      render(<Card ref={ref}>Ref Test</Card>);
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('Accessibility', () => {
    it('should support additional props', () => {
      render(<Card data-testid="test-card">Accessible Card</Card>);
      expect(screen.getByTestId('test-card')).toBeInTheDocument();
    });

    it('should support aria attributes', () => {
      render(
        <Card role="region" aria-label="Information card">
          Card Content
        </Card>
      );
      expect(screen.getByRole('region')).toBeInTheDocument();
      expect(screen.getByLabelText('Information card')).toBeInTheDocument();
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Card variant="default">Memoized</Card>);
      const initialElement = screen.getByText('Memoized');

      rerender(<Card variant="default">Memoized</Card>);
      const afterRerenderElement = screen.getByText('Memoized');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
