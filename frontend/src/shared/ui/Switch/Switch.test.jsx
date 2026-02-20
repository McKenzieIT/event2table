/**
 * Switch Component Tests
 * 测试开关组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Switch from './Switch';

describe('Switch Component', () => {
  describe('Rendering', () => {
    it('should render switch input', () => {
      const { container } = render(<Switch />);
      expect(container.querySelector('input[type="checkbox"]')).toBeInTheDocument();
    });

    it('should render with label', () => {
      render(<Switch label="Enable notifications" />);
      expect(screen.getByLabelText('Enable notifications')).toBeInTheDocument();
    });

    it('should render label text', () => {
      render(<Switch label="Auto-save" />);
      expect(screen.getByText('Auto-save')).toBeInTheDocument();
    });

    it('should render description', () => {
      render(<Switch label="Auto-save" description="Save changes automatically" />);
      expect(screen.getByText('Save changes automatically')).toBeInTheDocument();
    });
  });

  describe('Checked State', () => {
    it('should be unchecked by default', () => {
      render(<Switch />);
      expect(screen.getByRole('switch')).not.toBeChecked();
    });

    it('should be checked when checked prop is true', () => {
      render(<Switch checked onChange={() => {}} />);
      expect(screen.getByRole('switch')).toBeChecked();
    });

    it('should have checked class when checked', () => {
      const { container } = render(<Switch checked onChange={() => {}} />);
      expect(container.querySelector('.cyber-switch--checked')).toBeInTheDocument();
    });

    it('should display checkmark icon when checked', () => {
      const { container } = render(<Switch checked onChange={() => {}} />);
      expect(container.querySelector('.cyber-switch-icon')).toBeInTheDocument();
    });

    it('should have aria-checked="true" when checked', () => {
      render(<Switch checked onChange={() => {}} />);
      expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true');
    });

    it('should have aria-checked="false" when unchecked', () => {
      render(<Switch />);
      expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'false');
    });
  });

  describe('Change Handler', () => {
    it('should call onChange when clicked', async () => {
      const handleChange = vi.fn();
      render(<Switch onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('switch'));
      expect(handleChange).toHaveBeenCalled();
    });

    it('should pass checked value to onChange', async () => {
      const handleChange = vi.fn();
      render(<Switch onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('switch'));
      expect(handleChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('should toggle checked state', async () => {
      const handleChange = vi.fn();
      render(<Switch checked={false} onChange={handleChange} />);
      
      const switchElement = screen.getByRole('switch');
      await userEvent.click(switchElement);
      
      expect(handleChange).toHaveBeenCalledWith(true, expect.any(Object));
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Switch disabled />);
      expect(screen.getByRole('switch')).toBeDisabled();
    });

    it('should have disabled class when disabled', () => {
      const { container } = render(<Switch disabled />);
      expect(container.querySelector('.cyber-switch-wrapper--disabled')).toBeInTheDocument();
      expect(container.querySelector('.cyber-switch--disabled')).toBeInTheDocument();
    });

    it('should not trigger onChange when disabled', async () => {
      const handleChange = vi.fn();
      render(<Switch disabled onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('switch'));
      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Required', () => {
    it('should show required indicator when required', () => {
      const { container } = render(<Switch label="Required" required />);
      expect(container.querySelector('.cyber-switch-required')).toBeInTheDocument();
    });

    it('should have aria-required when required', () => {
      render(<Switch required />);
      expect(screen.getByRole('switch')).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Error State', () => {
    it('should display error message', () => {
      render(<Switch error="This field is required" />);
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('should have error class when error is present', () => {
      const { container } = render(<Switch error="Error" />);
      expect(container.querySelector('.cyber-switch-wrapper--invalid')).toBeInTheDocument();
      expect(container.querySelector('.cyber-switch--invalid')).toBeInTheDocument();
    });

    it('should set aria-invalid when error is present', () => {
      render(<Switch error="Error" />);
      expect(screen.getByRole('switch')).toHaveAttribute('aria-invalid', 'true');
    });

    it('should have role="alert" on error message', () => {
      render(<Switch error="Error message" />);
      expect(screen.getByRole('alert')).toHaveTextContent('Error message');
    });
  });

  describe('Name and Value', () => {
    it('should support name attribute', () => {
      render(<Switch name="auto-save" />);
      expect(screen.getByRole('switch')).toHaveAttribute('name', 'auto-save');
    });

    it('should support value attribute', () => {
      render(<Switch value="enabled" />);
      expect(screen.getByRole('switch')).toHaveAttribute('value', 'enabled');
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Switch className="custom-switch" />);
      expect(container.querySelector('.custom-switch')).toBeInTheDocument();
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to input element', () => {
      const ref = { current: null };
      render(<Switch ref={ref} />);
      expect(ref.current).toBeInstanceOf(HTMLInputElement);
    });
  });

  describe('Accessibility', () => {
    it('should have role="switch"', () => {
      render(<Switch />);
      expect(screen.getByRole('switch')).toBeInTheDocument();
    });

    it('should associate label with switch', () => {
      render(<Switch label="Enable feature" />);
      const switchElement = screen.getByLabelText('Enable feature');
      expect(switchElement).toBeInTheDocument();
    });

    it('should support aria-label without visible label', () => {
      render(<Switch aria-label="Toggle option" />);
      expect(screen.getByLabelText('Toggle option')).toBeInTheDocument();
    });

    it('should be focusable', () => {
      render(<Switch label="Focusable" />);
      const switchElement = screen.getByRole('switch');
      switchElement.focus();
      expect(switchElement).toHaveFocus();
    });
  });

  describe('Keyboard Interaction', () => {
    it('should toggle on Space key', async () => {
      const handleChange = vi.fn();
      render(<Switch onChange={handleChange} />);
      
      const switchElement = screen.getByRole('switch');
      switchElement.focus();
      await userEvent.keyboard(' ');
      
      expect(handleChange).toHaveBeenCalled();
    });

    it('should toggle on Enter key', async () => {
      const handleChange = vi.fn();
      render(<Switch onChange={handleChange} />);
      
      const switchElement = screen.getByRole('switch');
      switchElement.focus();
      await userEvent.keyboard('{Enter}');
      
      expect(handleChange).toHaveBeenCalled();
    });
  });

  describe('Description', () => {
    it('should render description below label', () => {
      const { container } = render(
        <Switch label="Auto-save" description="Automatically save changes" />
      );
      expect(screen.getByText('Auto-save')).toBeInTheDocument();
      expect(screen.getByText('Automatically save changes')).toBeInTheDocument();
      expect(container.querySelector('.cyber-switch-description')).toBeInTheDocument();
    });

    it('should not render description element when not provided', () => {
      const { container } = render(<Switch label="Auto-save" />);
      expect(container.querySelector('.cyber-switch-description')).not.toBeInTheDocument();
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Switch checked={false} />);
      const initialElement = screen.getByRole('switch');

      rerender(<Switch checked={false} />);
      const afterRerenderElement = screen.getByRole('switch');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
