/**
 * Input Component Tests
 * 测试输入框组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Input from './Input';

describe('Input Component', () => {
  describe('Rendering', () => {
    it('should render input element', () => {
      const { container } = render(<Input />);
      expect(container.querySelector('input.cyber-input')).toBeInTheDocument();
    });

    it('should render with label', () => {
      render(<Input label="Username" />);
      expect(screen.getByLabelText('Username')).toBeInTheDocument();
    });

    it('should render with placeholder', () => {
      render(<Input placeholder="Enter username" />);
      expect(screen.getByPlaceholderText('Enter username')).toBeInTheDocument();
    });
  });

  describe('Input Types', () => {
    it('should render text input by default', () => {
      const { container } = render(<Input />);
      expect(container.querySelector('input[type="text"]')).toBeInTheDocument();
    });

    it('should render password input', () => {
      const { container } = render(<Input type="password" />);
      expect(container.querySelector('input[type="password"]')).toBeInTheDocument();
    });

    it('should render number input', () => {
      const { container } = render(<Input type="number" />);
      expect(container.querySelector('input[type="number"]')).toBeInTheDocument();
    });

    it('should render email input', () => {
      const { container } = render(<Input type="email" />);
      expect(container.querySelector('input[type="email"]')).toBeInTheDocument();
    });
  });

  describe('Value Handling', () => {
    it('should display value', () => {
      render(<Input value="test value" onChange={() => {}} />);
      expect(screen.getByDisplayValue('test value')).toBeInTheDocument();
    });

    it('should call onChange when value changes', async () => {
      const handleChange = vi.fn();
      render(<Input onChange={handleChange} />);
      
      const input = screen.getByRole('textbox');
      await userEvent.type(input, 'test');
      
      expect(handleChange).toHaveBeenCalled();
    });

    it('should update value on change', async () => {
      render(<Input />);
      
      const input = screen.getByRole('textbox');
      await userEvent.type(input, 'hello');
      
      expect(input).toHaveValue('hello');
    });
  });

  describe('Label and Required', () => {
    it('should render label with required indicator', () => {
      const { container } = render(<Input label="Email" required />);
      expect(container.querySelector('.cyber-input__required')).toBeInTheDocument();
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should not show required indicator when not required', () => {
      const { container } = render(<Input label="Email" />);
      expect(container.querySelector('.cyber-input__required')).not.toBeInTheDocument();
    });

    it('should associate label with input', () => {
      render(<Input label="Username" />);
      const input = screen.getByLabelText('Username');
      expect(input).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    it('should display error message', () => {
      render(<Input error="This field is required" />);
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('should have error class when error is present', () => {
      const { container } = render(<Input error="Error message" />);
      expect(container.querySelector('.cyber-input-wrapper--invalid')).toBeInTheDocument();
      expect(container.querySelector('.cyber-input--invalid')).toBeInTheDocument();
    });

    it('should set aria-invalid when error is present', () => {
      render(<Input error="Error" />);
      expect(screen.getByRole('textbox')).toHaveAttribute('aria-invalid', 'true');
    });

    it('should associate error message with input via aria-describedby', () => {
      render(<Input error="Error message" />);
      const input = screen.getByRole('textbox');
      const errorId = input.getAttribute('aria-describedby');
      expect(errorId).toBeTruthy();
      expect(document.getElementById(errorId)).toHaveTextContent('Error message');
    });
  });

  describe('Helper Text', () => {
    it('should display helper text', () => {
      render(<Input helperText="Enter your username" />);
      expect(screen.getByText('Enter your username')).toBeInTheDocument();
    });

    it('should not display helper text when error is present', () => {
      render(<Input helperText="Helper text" error="Error message" />);
      expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
    });

    it('should associate helper text with input via aria-describedby', () => {
      render(<Input helperText="Helper text" />);
      const input = screen.getByRole('textbox');
      const helperId = input.getAttribute('aria-describedby');
      expect(helperId).toBeTruthy();
      expect(document.getElementById(helperId)).toHaveTextContent('Helper text');
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Input disabled />);
      expect(screen.getByRole('textbox')).toBeDisabled();
    });

    it('should have disabled class when disabled', () => {
      const { container } = render(<Input disabled />);
      expect(container.querySelector('.cyber-input-wrapper--disabled')).toBeInTheDocument();
      expect(container.querySelector('.cyber-input--disabled')).toBeInTheDocument();
    });

    it('should not allow input when disabled', async () => {
      render(<Input disabled />);
      const input = screen.getByRole('textbox');
      
      await userEvent.type(input, 'test');
      expect(input).toHaveValue('');
    });
  });

  describe('Icon', () => {
    it('should render icon when icon prop is provided', () => {
      const TestIcon = () => <svg data-testid="test-icon" />;
      const { container } = render(<Input icon={TestIcon} />);
      expect(container.querySelector('.cyber-input__icon')).toBeInTheDocument();
      expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('should have icon class when icon is present', () => {
      const TestIcon = () => <svg />;
      const { container } = render(<Input icon={TestIcon} />);
      expect(container.querySelector('.cyber-input-wrapper--with-icon')).toBeInTheDocument();
    });

    it('should not render icon when icon prop is not provided', () => {
      const { container } = render(<Input />);
      expect(container.querySelector('.cyber-input__icon')).not.toBeInTheDocument();
    });
  });

  describe('Blur Handler', () => {
    it('should call onBlur when input loses focus', async () => {
      const handleBlur = vi.fn();
      render(<Input onBlur={handleBlur} />);
      
      const input = screen.getByRole('textbox');
      await userEvent.click(input);
      await userEvent.tab();
      
      expect(handleBlur).toHaveBeenCalled();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Input className="custom-class" />);
      expect(container.querySelector('.custom-class')).toBeInTheDocument();
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to input element', () => {
      const ref = { current: null };
      render(<Input ref={ref} />);
      expect(ref.current).toBeInstanceOf(HTMLInputElement);
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria attributes', () => {
      render(<Input label="Email" required error="Invalid email" />);
      const input = screen.getByRole('textbox');
      
      expect(input).toHaveAttribute('aria-invalid', 'true');
      expect(input).toHaveAttribute('aria-required', 'true');
    });

    it('should generate unique id for input', () => {
      render(
        <>
          <Input label="Input 1" />
          <Input label="Input 2" />
        </>
      );
      
      const input1 = screen.getByLabelText('Input 1');
      const input2 = screen.getByLabelText('Input 2');
      
      expect(input1.id).not.toBe(input2.id);
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Input label="Test" value="" onChange={() => {}} />);
      const initialElement = screen.getByLabelText('Test');

      rerender(<Input label="Test" value="" onChange={() => {}} />);
      const afterRerenderElement = screen.getByLabelText('Test');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
