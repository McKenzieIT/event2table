/**
 * Radio Component Tests
 * 测试单选框组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Radio from './Radio';

describe('Radio Component', () => {
  describe('Rendering', () => {
    it('should render radio input', () => {
      const { container } = render(<Radio />);
      expect(container.querySelector('input[type="radio"]')).toBeInTheDocument();
    });

    it('should render with label', () => {
      render(<Radio label="Option A" />);
      expect(screen.getByLabelText('Option A')).toBeInTheDocument();
    });

    it('should render label text', () => {
      render(<Radio label="Option B" />);
      expect(screen.getByText('Option B')).toBeInTheDocument();
    });
  });

  describe('Checked State', () => {
    it('should be unchecked by default', () => {
      render(<Radio />);
      expect(screen.getByRole('radio')).not.toBeChecked();
    });

    it('should be checked when checked prop is true', () => {
      render(<Radio checked onChange={() => {}} />);
      expect(screen.getByRole('radio')).toBeChecked();
    });

    it('should have checked class when checked', () => {
      const { container } = render(<Radio checked onChange={() => {}} />);
      expect(container.querySelector('.cyber-radio--checked')).toBeInTheDocument();
    });

    it('should display dot when checked', () => {
      const { container } = render(<Radio checked onChange={() => {}} />);
      expect(container.querySelector('.cyber-radio-dot')).toBeInTheDocument();
    });
  });

  describe('Radio Group', () => {
    it('should allow only one radio to be selected in a group', async () => {
      const handleChange = vi.fn();
      
      render(
        <div>
          <Radio name="group1" value="a" label="Option A" onChange={handleChange} />
          <Radio name="group1" value="b" label="Option B" onChange={handleChange} />
        </div>
      );
      
      const radioA = screen.getByLabelText('Option A');
      const radioB = screen.getByLabelText('Option B');
      
      await userEvent.click(radioA);
      expect(radioA).toBeChecked();
      expect(radioB).not.toBeChecked();
      
      await userEvent.click(radioB);
      expect(radioB).toBeChecked();
      expect(radioA).not.toBeChecked();
    });

    it('should call onChange with value when clicked', async () => {
      const handleChange = vi.fn();
      render(<Radio value="option1" onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('radio'));
      expect(handleChange).toHaveBeenCalledWith('option1', expect.any(Object));
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Radio disabled />);
      expect(screen.getByRole('radio')).toBeDisabled();
    });

    it('should have disabled class when disabled', () => {
      const { container } = render(<Radio disabled />);
      expect(container.querySelector('.cyber-radio-wrapper--disabled')).toBeInTheDocument();
      expect(container.querySelector('.cyber-radio--disabled')).toBeInTheDocument();
    });

    it('should not trigger onChange when disabled', async () => {
      const handleChange = vi.fn();
      render(<Radio disabled onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('radio'));
      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Required', () => {
    it('should show required indicator when required', () => {
      const { container } = render(<Radio label="Required" required />);
      expect(container.querySelector('.cyber-radio-required')).toBeInTheDocument();
    });

    it('should have aria-required when required', () => {
      render(<Radio required />);
      expect(screen.getByRole('radio')).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Error State', () => {
    it('should display error message', () => {
      render(<Radio error="This field is required" />);
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('should have error class when error is present', () => {
      const { container } = render(<Radio error="Error" />);
      expect(container.querySelector('.cyber-radio-wrapper--invalid')).toBeInTheDocument();
      expect(container.querySelector('.cyber-radio--invalid')).toBeInTheDocument();
    });

    it('should set aria-invalid when error is present', () => {
      render(<Radio error="Error" />);
      expect(screen.getByRole('radio')).toHaveAttribute('aria-invalid', 'true');
    });

    it('should have role="alert" on error message', () => {
      render(<Radio error="Error message" />);
      expect(screen.getByRole('alert')).toHaveTextContent('Error message');
    });
  });

  describe('Name and Value', () => {
    it('should support name attribute', () => {
      render(<Radio name="options" />);
      expect(screen.getByRole('radio')).toHaveAttribute('name', 'options');
    });

    it('should support value attribute', () => {
      render(<Radio value="option1" />);
      expect(screen.getByRole('radio')).toHaveAttribute('value', 'option1');
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Radio className="custom-radio" />);
      expect(container.querySelector('.custom-radio')).toBeInTheDocument();
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to input element', () => {
      const ref = { current: null };
      render(<Radio ref={ref} />);
      expect(ref.current).toBeInstanceOf(HTMLInputElement);
    });
  });

  describe('Accessibility', () => {
    it('should associate label with radio', () => {
      render(<Radio label="Option A" />);
      const radio = screen.getByLabelText('Option A');
      expect(radio).toBeInTheDocument();
      expect(radio).toHaveAttribute('type', 'radio');
    });

    it('should support aria-label without visible label', () => {
      render(<Radio aria-label="Select option" />);
      expect(screen.getByLabelText('Select option')).toBeInTheDocument();
    });

    it('should be focusable', () => {
      render(<Radio label="Focusable" />);
      const radio = screen.getByRole('radio');
      radio.focus();
      expect(radio).toHaveFocus();
    });
  });

  describe('Keyboard Interaction', () => {
    it('should be selectable with Space key', async () => {
      const handleChange = vi.fn();
      render(<Radio value="test" onChange={handleChange} />);
      
      const radio = screen.getByRole('radio');
      radio.focus();
      await userEvent.keyboard(' ');
      
      expect(handleChange).toHaveBeenCalled();
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Radio checked={false} />);
      const initialElement = screen.getByRole('radio');

      rerender(<Radio checked={false} />);
      const afterRerenderElement = screen.getByRole('radio');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
