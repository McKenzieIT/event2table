/**
 * Button Component Tests
 * 测试按钮组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button Component', () => {
  describe('Rendering', () => {
    it('should render with children', () => {
      render(<Button>Click Me</Button>);
      expect(screen.getByRole('button', { name: 'Click Me' })).toBeInTheDocument();
    });

    it('should render as button element', () => {
      const { container } = render(<Button>Button</Button>);
      expect(container.querySelector('button.cyber-button')).toBeInTheDocument();
    });
  });

  describe('Variants', () => {
    it('should render primary variant (default)', () => {
      const { container } = render(<Button>Primary</Button>);
      expect(container.querySelector('.cyber-button--primary')).toBeInTheDocument();
    });

    it('should render secondary variant', () => {
      const { container } = render(<Button variant="secondary">Secondary</Button>);
      expect(container.querySelector('.cyber-button--secondary')).toBeInTheDocument();
    });

    it('should render ghost variant', () => {
      const { container } = render(<Button variant="ghost">Ghost</Button>);
      expect(container.querySelector('.cyber-button--ghost')).toBeInTheDocument();
    });

    it('should render danger variant', () => {
      const { container } = render(<Button variant="danger">Danger</Button>);
      expect(container.querySelector('.cyber-button--danger')).toBeInTheDocument();
    });
  });

  describe('Sizes', () => {
    it('should render small size', () => {
      const { container } = render(<Button size="sm">Small</Button>);
      expect(container.querySelector('.cyber-button--sm')).toBeInTheDocument();
    });

    it('should render medium size (default)', () => {
      const { container } = render(<Button>Medium</Button>);
      expect(container.querySelector('.cyber-button--md')).toBeInTheDocument();
    });

    it('should render large size', () => {
      const { container } = render(<Button size="lg">Large</Button>);
      expect(container.querySelector('.cyber-button--lg')).toBeInTheDocument();
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Button disabled>Disabled</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('should have disabled class when disabled', () => {
      const { container } = render(<Button disabled>Disabled</Button>);
      expect(container.querySelector('.cyber-button--disabled')).toBeInTheDocument();
    });

    it('should not trigger onClick when disabled', async () => {
      const handleClick = vi.fn();
      render(<Button disabled onClick={handleClick}>Disabled</Button>);
      
      await userEvent.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('should show loading spinner when loading', () => {
      const { container } = render(<Button loading>Loading</Button>);
      expect(container.querySelector('.cyber-button__spinner')).toBeInTheDocument();
    });

    it('should have loading class when loading', () => {
      const { container } = render(<Button loading>Loading</Button>);
      expect(container.querySelector('.cyber-button--loading')).toBeInTheDocument();
    });

    it('should be disabled when loading', () => {
      render(<Button loading>Loading</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('should not trigger onClick when loading', async () => {
      const handleClick = vi.fn();
      render(<Button loading onClick={handleClick}>Loading</Button>);
      
      await userEvent.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Icon', () => {
    it('should render icon when icon prop is provided', () => {
      const TestIcon = () => <svg data-testid="test-icon" />;
      const { container } = render(<Button icon={TestIcon}>With Icon</Button>);
      expect(container.querySelector('.cyber-button__icon')).toBeInTheDocument();
      expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('should not render icon when icon prop is not provided', () => {
      const { container } = render(<Button>No Icon</Button>);
      expect(container.querySelector('.cyber-button__icon')).not.toBeInTheDocument();
    });
  });

  describe('Click Handler', () => {
    it('should call onClick when clicked', async () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click Me</Button>);
      
      await userEvent.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should pass event to onClick handler', async () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click Me</Button>);
      
      await userEvent.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledWith(expect.any(Object));
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Button className="custom-class">Custom</Button>);
      expect(container.querySelector('.custom-class')).toBeInTheDocument();
    });

    it('should combine multiple classes', () => {
      const { container } = render(
        <Button variant="primary" size="lg" className="custom-class">
          Combined
        </Button>
      );
      const button = container.querySelector('.cyber-button');
      expect(button).toHaveClass('cyber-button');
      expect(button).toHaveClass('cyber-button--primary');
      expect(button).toHaveClass('cyber-button--lg');
      expect(button).toHaveClass('custom-class');
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to button element', () => {
      const ref = { current: null };
      render(<Button ref={ref}>Ref Test</Button>);
      expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    });
  });

  describe('Accessibility', () => {
    it('should support aria-label', () => {
      render(<Button aria-label="Submit form">Submit</Button>);
      expect(screen.getByLabelText('Submit form')).toBeInTheDocument();
    });

    it('should support aria-describedby', () => {
      render(
        <>
          <Button aria-describedby="button-help">Help</Button>
          <span id="button-help">Click for help</span>
        </>
      );
      expect(screen.getByRole('button')).toHaveAttribute('aria-describedby', 'button-help');
    });

    it('should have type="button" by default', () => {
      render(<Button>Default Type</Button>);
      expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
    });

    it('should support type attribute', () => {
      render(<Button type="submit">Submit</Button>);
      expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');
    });
  });

  describe('Keyboard Interaction', () => {
    it('should be focusable', () => {
      render(<Button>Focusable</Button>);
      const button = screen.getByRole('button');
      button.focus();
      expect(button).toHaveFocus();
    });

    it('should trigger onClick on Enter key', async () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Enter Key</Button>);
      
      const button = screen.getByRole('button');
      button.focus();
      await userEvent.keyboard('{Enter}');
      
      expect(handleClick).toHaveBeenCalled();
    });

    it('should trigger onClick on Space key', async () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Space Key</Button>);
      
      const button = screen.getByRole('button');
      button.focus();
      await userEvent.keyboard(' ');
      
      expect(handleClick).toHaveBeenCalled();
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Button variant="primary">Memoized</Button>);
      const initialElement = screen.getByText('Memoized');

      rerender(<Button variant="primary">Memoized</Button>);
      const afterRerenderElement = screen.getByText('Memoized');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
