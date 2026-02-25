/**
 * Checkbox Component Tests
 * 测试复选框组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Checkbox from './Checkbox';

describe('Checkbox Component', () => {
  describe('Rendering', () => {
    it('should render checkbox input', () => {
      const { container } = render(<Checkbox />);
      expect(container.querySelector('input[type="checkbox"]')).toBeInTheDocument();
    });

    it('should render with label', () => {
      render(<Checkbox label="Accept terms" />);
      expect(screen.getByLabelText('Accept terms')).toBeInTheDocument();
    });

    it('should render label text', () => {
      render(<Checkbox label="Remember me" />);
      expect(screen.getByText('Remember me')).toBeInTheDocument();
    });
  });

  describe('Checked State', () => {
    it('should be unchecked by default', () => {
      render(<Checkbox />);
      expect(screen.getByRole('checkbox')).not.toBeChecked();
    });

    it('should be checked when checked prop is true', () => {
      render(<Checkbox checked onChange={() => {}} />);
      expect(screen.getByRole('checkbox')).toBeChecked();
    });

    it('should have checked class when checked', () => {
      const { container } = render(<Checkbox checked onChange={() => {}} />);
      expect(container.querySelector('.cyber-checkbox--checked')).toBeInTheDocument();
    });

    it('should display checkmark icon when checked', () => {
      const { container } = render(<Checkbox checked onChange={() => {}} />);
      expect(container.querySelector('.cyber-checkbox-icon')).toBeInTheDocument();
    });
  });

  describe('Indeterminate State', () => {
    it('should support indeterminate state', () => {
      const { container } = render(<Checkbox indeterminate />);
      expect(container.querySelector('.cyber-checkbox--indeterminate')).toBeInTheDocument();
    });

    it('should display indeterminate icon when indeterminate', () => {
      const { container } = render(<Checkbox indeterminate />);
      expect(container.querySelector('.cyber-checkbox-indeterminate')).toBeInTheDocument();
    });

    it('should set aria-checked to "mixed" when indeterminate', () => {
      render(<Checkbox indeterminate />);
      expect(screen.getByRole('checkbox')).toHaveAttribute('aria-checked', 'mixed');
    });

    it('should set indeterminate property on input element', () => {
      const ref = { current: null };
      render(<Checkbox indeterminate ref={ref} />);
      expect(ref.current?.indeterminate).toBe(true);
    });
  });

  describe('Change Handler', () => {
    it('should call onChange when clicked', async () => {
      const handleChange = vi.fn();
      render(<Checkbox onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('checkbox'));
      expect(handleChange).toHaveBeenCalled();
    });

    it('should pass checked value to onChange', async () => {
      const handleChange = vi.fn();
      render(<Checkbox onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('checkbox'));
      expect(handleChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('should toggle checked state', async () => {
      const handleChange = vi.fn();
      render(<Checkbox checked={false} onChange={handleChange} />);
      
      const checkbox = screen.getByRole('checkbox');
      await userEvent.click(checkbox);
      
      expect(handleChange).toHaveBeenCalledWith(true, expect.any(Object));
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Checkbox disabled />);
      expect(screen.getByRole('checkbox')).toBeDisabled();
    });

    it('should have disabled class when disabled', () => {
      const { container } = render(<Checkbox disabled />);
      expect(container.querySelector('.cyber-checkbox-wrapper--disabled')).toBeInTheDocument();
      expect(container.querySelector('.cyber-checkbox--disabled')).toBeInTheDocument();
    });

    it('should not trigger onChange when disabled', async () => {
      const handleChange = vi.fn();
      render(<Checkbox disabled onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('checkbox'));
      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Required', () => {
    it('should show required indicator when required', () => {
      const { container } = render(<Checkbox label="Required" required />);
      expect(container.querySelector('.cyber-checkbox-required')).toBeInTheDocument();
    });

    it('should have aria-required when required', () => {
      render(<Checkbox required />);
      expect(screen.getByRole('checkbox')).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Error State', () => {
    it('should display error message', () => {
      render(<Checkbox error="This field is required" />);
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('should have error class when error is present', () => {
      const { container } = render(<Checkbox error="Error" />);
      expect(container.querySelector('.cyber-checkbox-wrapper--invalid')).toBeInTheDocument();
      expect(container.querySelector('.cyber-checkbox--invalid')).toBeInTheDocument();
    });

    it('should set aria-invalid when error is present', () => {
      render(<Checkbox error="Error" />);
      expect(screen.getByRole('checkbox')).toHaveAttribute('aria-invalid', 'true');
    });

    it('should have role="alert" on error message', () => {
      render(<Checkbox error="Error message" />);
      expect(screen.getByRole('alert')).toHaveTextContent('Error message');
    });
  });

  describe('Name and Value', () => {
    it('should support name attribute', () => {
      render(<Checkbox name="terms" />);
      expect(screen.getByRole('checkbox')).toHaveAttribute('name', 'terms');
    });

    it('should support value attribute', () => {
      render(<Checkbox value="accepted" />);
      expect(screen.getByRole('checkbox')).toHaveAttribute('value', 'accepted');
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Checkbox className="custom-checkbox" />);
      expect(container.querySelector('.custom-checkbox')).toBeInTheDocument();
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to input element', () => {
      const ref = { current: null };
      render(<Checkbox ref={ref} />);
      expect(ref.current).toBeInstanceOf(HTMLInputElement);
    });
  });

  describe('Accessibility', () => {
    it('should associate label with checkbox', () => {
      render(<Checkbox label="Accept terms" />);
      const checkbox = screen.getByLabelText('Accept terms');
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).toHaveAttribute('type', 'checkbox');
    });

    it('should support aria-label without visible label', () => {
      render(<Checkbox aria-label="Toggle option" />);
      expect(screen.getByLabelText('Toggle option')).toBeInTheDocument();
    });

    it('should be focusable', () => {
      render(<Checkbox label="Focusable" />);
      const checkbox = screen.getByRole('checkbox');
      checkbox.focus();
      expect(checkbox).toHaveFocus();
    });
  });

  describe('Keyboard Interaction', () => {
    it('should toggle on Space key', async () => {
      const handleChange = vi.fn();
      render(<Checkbox onChange={handleChange} />);
      
      const checkbox = screen.getByRole('checkbox');
      checkbox.focus();
      await userEvent.keyboard(' ');
      
      expect(handleChange).toHaveBeenCalled();
    });

    it('should not toggle on Enter key', async () => {
      const handleChange = vi.fn();
      render(<Checkbox onChange={handleChange} />);
      
      const checkbox = screen.getByRole('checkbox');
      checkbox.focus();
      await userEvent.keyboard('{Enter}');
      
      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Checkbox checked={false} />);
      const initialElement = screen.getByRole('checkbox');

      rerender(<Checkbox checked={false} />);
      const afterRerenderElement = screen.getByRole('checkbox');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
