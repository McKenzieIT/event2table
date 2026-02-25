/**
 * TextArea Component Tests
 * 测试文本域组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TextArea from './TextArea';

describe('TextArea Component', () => {
  describe('Rendering', () => {
    it('should render textarea element', () => {
      const { container } = render(<TextArea />);
      expect(container.querySelector('textarea.cyber-textarea')).toBeInTheDocument();
    });

    it('should render with label', () => {
      render(<TextArea label="Description" />);
      expect(screen.getByLabelText('Description')).toBeInTheDocument();
    });

    it('should render with placeholder', () => {
      render(<TextArea placeholder="Enter description" />);
      expect(screen.getByPlaceholderText('Enter description')).toBeInTheDocument();
    });
  });

  describe('Value Handling', () => {
    it('should display value', () => {
      render(<TextArea value="test value" onChange={() => {}} />);
      expect(screen.getByDisplayValue('test value')).toBeInTheDocument();
    });

    it('should call onChange when value changes', async () => {
      const handleChange = vi.fn();
      render(<TextArea onChange={handleChange} />);
      
      const textarea = screen.getByRole('textbox');
      await userEvent.type(textarea, 'test');
      
      expect(handleChange).toHaveBeenCalled();
    });

    it('should update value on change', async () => {
      render(<TextArea />);
      
      const textarea = screen.getByRole('textbox');
      await userEvent.type(textarea, 'hello world');
      
      expect(textarea).toHaveValue('hello world');
    });
  });

  describe('Rows', () => {
    it('should have default rows of 4', () => {
      render(<TextArea />);
      expect(screen.getByRole('textbox')).toHaveAttribute('rows', '4');
    });

    it('should support custom rows', () => {
      render(<TextArea rows={6} />);
      expect(screen.getByRole('textbox')).toHaveAttribute('rows', '6');
    });
  });

  describe('Resize', () => {
    it('should have vertical resize by default', () => {
      const { container } = render(<TextArea />);
      const textarea = container.querySelector('textarea');
      expect(textarea).toHaveStyle({ resize: 'vertical' });
    });

    it('should support horizontal resize', () => {
      const { container } = render(<TextArea resize="horizontal" />);
      const textarea = container.querySelector('textarea');
      expect(textarea).toHaveStyle({ resize: 'horizontal' });
    });

    it('should support both resize', () => {
      const { container } = render(<TextArea resize="both" />);
      const textarea = container.querySelector('textarea');
      expect(textarea).toHaveStyle({ resize: 'both' });
    });

    it('should support no resize', () => {
      const { container } = render(<TextArea resize="none" />);
      const textarea = container.querySelector('textarea');
      expect(textarea).toHaveStyle({ resize: 'none' });
    });
  });

  describe('MaxLength and Character Count', () => {
    it('should support maxLength attribute', () => {
      render(<TextArea maxLength={100} />);
      expect(screen.getByRole('textbox')).toHaveAttribute('maxLength', '100');
    });

    it('should show character count when showCount and maxLength are set', () => {
      render(<TextArea maxLength={100} value="test" onChange={() => {}} showCount />);
      expect(screen.getByText('4/100')).toBeInTheDocument();
    });

    it('should not show character count when showCount is false', () => {
      const { container } = render(<TextArea maxLength={100} value="test" onChange={() => {}} />);
      expect(container.querySelector('.cyber-textarea__count')).not.toBeInTheDocument();
    });

    it('should update character count as value changes', async () => {
      render(<TextArea maxLength={100} showCount />);
      
      const textarea = screen.getByRole('textbox');
      await userEvent.type(textarea, 'hello');
      
      expect(screen.getByText('5/100')).toBeInTheDocument();
    });
  });

  describe('Label and Required', () => {
    it('should render label with required indicator', () => {
      const { container } = render(<TextArea label="Message" required />);
      expect(container.querySelector('.cyber-textarea__required')).toBeInTheDocument();
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should not show required indicator when not required', () => {
      const { container } = render(<TextArea label="Message" />);
      expect(container.querySelector('.cyber-textarea__required')).not.toBeInTheDocument();
    });

    it('should associate label with textarea', () => {
      render(<TextArea label="Description" />);
      const textarea = screen.getByLabelText('Description');
      expect(textarea).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    it('should display error message', () => {
      render(<TextArea error="This field is required" />);
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('should have error class when error is present', () => {
      const { container } = render(<TextArea error="Error message" />);
      expect(container.querySelector('.cyber-textarea-wrapper--invalid')).toBeInTheDocument();
      expect(container.querySelector('.cyber-textarea--invalid')).toBeInTheDocument();
    });

    it('should set aria-invalid when error is present', () => {
      render(<TextArea error="Error" />);
      expect(screen.getByRole('textbox')).toHaveAttribute('aria-invalid', 'true');
    });

    it('should associate error message with textarea via aria-describedby', () => {
      render(<TextArea error="Error message" />);
      const textarea = screen.getByRole('textbox');
      const errorId = textarea.getAttribute('aria-describedby');
      expect(errorId).toBeTruthy();
      expect(document.getElementById(errorId)).toHaveTextContent('Error message');
    });
  });

  describe('Helper Text', () => {
    it('should display helper text', () => {
      render(<TextArea helperText="Enter your message" />);
      expect(screen.getByText('Enter your message')).toBeInTheDocument();
    });

    it('should not display helper text when error is present', () => {
      render(<TextArea helperText="Helper text" error="Error message" />);
      expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
    });

    it('should associate helper text with textarea via aria-describedby', () => {
      render(<TextArea helperText="Helper text" />);
      const textarea = screen.getByRole('textbox');
      const helperId = textarea.getAttribute('aria-describedby');
      expect(helperId).toBeTruthy();
      expect(document.getElementById(helperId)).toHaveTextContent('Helper text');
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<TextArea disabled />);
      expect(screen.getByRole('textbox')).toBeDisabled();
    });

    it('should have disabled class when disabled', () => {
      const { container } = render(<TextArea disabled />);
      expect(container.querySelector('.cyber-textarea-wrapper--disabled')).toBeInTheDocument();
      expect(container.querySelector('.cyber-textarea--disabled')).toBeInTheDocument();
    });

    it('should not allow input when disabled', async () => {
      render(<TextArea disabled />);
      const textarea = screen.getByRole('textbox');
      
      await userEvent.type(textarea, 'test');
      expect(textarea).toHaveValue('');
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<TextArea className="custom-textarea" />);
      expect(container.querySelector('.custom-textarea')).toBeInTheDocument();
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to textarea element', () => {
      const ref = { current: null };
      render(<TextArea ref={ref} />);
      expect(ref.current).toBeInstanceOf(HTMLTextAreaElement);
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria attributes', () => {
      render(<TextArea label="Message" required error="Invalid message" />);
      const textarea = screen.getByRole('textbox');
      
      expect(textarea).toHaveAttribute('aria-invalid', 'true');
      expect(textarea).toHaveAttribute('aria-required', 'true');
    });

    it('should generate unique id for textarea', () => {
      render(
        <>
          <TextArea label="TextArea 1" />
          <TextArea label="TextArea 2" />
        </>
      );
      
      const textarea1 = screen.getByLabelText('TextArea 1');
      const textarea2 = screen.getByLabelText('TextArea 2');
      
      expect(textarea1.id).not.toBe(textarea2.id);
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<TextArea label="Test" value="" onChange={() => {}} />);
      const initialElement = screen.getByLabelText('Test');

      rerender(<TextArea label="Test" value="" onChange={() => {}} />);
      const afterRerenderElement = screen.getByLabelText('Test');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
