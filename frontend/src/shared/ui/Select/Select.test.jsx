/**
 * Select Component Tests
 * 测试下拉选择组件的所有功能
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Select from './Select';

describe('Select Component', () => {
  const mockOptions = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' }
  ];

  describe('Rendering', () => {
    it('should render select trigger', () => {
      render(<Select options={mockOptions} />);
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    it('should render with label', () => {
      render(<Select label="Select Option" options={mockOptions} />);
      expect(screen.getByLabelText('Select Option')).toBeInTheDocument();
    });

    it('should render placeholder', () => {
      render(<Select options={mockOptions} placeholder="Choose..." />);
      expect(screen.getByText('Choose...')).toBeInTheDocument();
    });

    it('should display selected option label', () => {
      render(<Select options={mockOptions} value="option2" />);
      expect(screen.getByText('Option 2')).toBeInTheDocument();
    });
  });

  describe('Opening/Closing Dropdown', () => {
    it('should open dropdown when trigger is clicked', async () => {
      render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should close dropdown when clicking outside', async () => {
      render(
        <div>
          <Select options={mockOptions} />
          <div data-testid="outside">Outside</div>
        </div>
      );
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      
      await userEvent.click(screen.getByTestId('outside'));
      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });

    it('should toggle dropdown on trigger click', async () => {
      render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      
      await userEvent.click(screen.getByRole('combobox'));
      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });

    it('should have open class when dropdown is open', async () => {
      const { container } = render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(container.querySelector('.cyber-select-wrapper--open')).toBeInTheDocument();
    });
  });

  describe('Option Selection', () => {
    it('should display options when dropdown is open', async () => {
      render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      
      expect(screen.getByText('Option 1')).toBeInTheDocument();
      expect(screen.getByText('Option 2')).toBeInTheDocument();
      expect(screen.getByText('Option 3')).toBeInTheDocument();
    });

    it('should call onChange when option is selected', async () => {
      const handleChange = vi.fn();
      render(<Select options={mockOptions} onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      await userEvent.click(screen.getByText('Option 2'));
      
      expect(handleChange).toHaveBeenCalledWith('option2');
    });

    it('should close dropdown after selection', async () => {
      render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      await userEvent.click(screen.getByText('Option 1'));
      
      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });

    it('should highlight selected option', async () => {
      render(<Select options={mockOptions} value="option2" />);
      
      await userEvent.click(screen.getByRole('combobox'));
      
      const selectedOption = screen.getByRole('option', { selected: true });
      expect(selectedOption).toHaveTextContent('Option 2');
    });

    it('should show checkmark for selected option', async () => {
      const { container } = render(<Select options={mockOptions} value="option1" />);
      
      await userEvent.click(screen.getByRole('combobox'));
      
      expect(container.querySelector('.cyber-select-check')).toBeInTheDocument();
    });
  });

  describe('Disabled Options', () => {
    const optionsWithDisabled = [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2', disabled: true },
      { value: 'option3', label: 'Option 3' }
    ];

    it('should render disabled option with disabled class', async () => {
      const { container } = render(<Select options={optionsWithDisabled} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(container.querySelector('.cyber-select-option--disabled')).toBeInTheDocument();
    });

    it('should not select disabled option', async () => {
      const handleChange = vi.fn();
      render(<Select options={optionsWithDisabled} onChange={handleChange} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      await userEvent.click(screen.getByText('Option 2'));
      
      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Searchable', () => {
    it('should render search input when searchable', async () => {
      render(<Select options={mockOptions} searchable />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
    });

    it('should filter options based on search term', async () => {
      render(<Select options={mockOptions} searchable />);
      
      await userEvent.click(screen.getByRole('combobox'));
      const searchInput = screen.getByPlaceholderText('Search...');
      await userEvent.type(searchInput, 'Option 1');
      
      expect(screen.getByText('Option 1')).toBeInTheDocument();
      expect(screen.queryByText('Option 2')).not.toBeInTheDocument();
      expect(screen.queryByText('Option 3')).not.toBeInTheDocument();
    });

    it('should show "No options found" when no matches', async () => {
      render(<Select options={mockOptions} searchable />);
      
      await userEvent.click(screen.getByRole('combobox'));
      const searchInput = screen.getByPlaceholderText('Search...');
      await userEvent.type(searchInput, 'xyz');
      
      expect(screen.getByText('No options found')).toBeInTheDocument();
    });

    it('should not render search input when not searchable', async () => {
      render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(screen.queryByPlaceholderText('Search...')).not.toBeInTheDocument();
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<Select options={mockOptions} disabled />);
      expect(screen.getByRole('combobox')).toHaveAttribute('aria-disabled', 'true');
    });

    it('should have disabled class when disabled', () => {
      const { container } = render(<Select options={mockOptions} disabled />);
      expect(container.querySelector('.cyber-select-wrapper--disabled')).toBeInTheDocument();
    });

    it('should not open dropdown when disabled', async () => {
      render(<Select options={mockOptions} disabled />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should have tabIndex -1 when disabled', () => {
      render(<Select options={mockOptions} disabled />);
      expect(screen.getByRole('combobox')).toHaveAttribute('tabIndex', '-1');
    });
  });

  describe('Required', () => {
    it('should show required indicator when required', () => {
      const { container } = render(<Select label="Required" options={mockOptions} required />);
      expect(container.querySelector('.cyber-select__required')).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    it('should display error message', () => {
      render(<Select options={mockOptions} error="Selection is required" />);
      expect(screen.getByText('Selection is required')).toBeInTheDocument();
    });

    it('should have error class when error is present', () => {
      const { container } = render(<Select options={mockOptions} error="Error" />);
      expect(container.querySelector('.cyber-select-wrapper--invalid')).toBeInTheDocument();
    });

    it('should set aria-invalid when error is present', () => {
      render(<Select options={mockOptions} error="Error" />);
      expect(screen.getByRole('combobox')).toHaveAttribute('aria-invalid', 'true');
    });
  });

  describe('Helper Text', () => {
    it('should display helper text', () => {
      render(<Select options={mockOptions} helperText="Select an option" />);
      expect(screen.getByText('Select an option')).toBeInTheDocument();
    });

    it('should not display helper text when error is present', () => {
      render(<Select options={mockOptions} helperText="Helper" error="Error" />);
      expect(screen.queryByText('Helper')).not.toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
    });
  });

  describe('Keyboard Navigation', () => {
    it('should open dropdown on Enter key', async () => {
      render(<Select options={mockOptions} />);
      
      const combobox = screen.getByRole('combobox');
      combobox.focus();
      await userEvent.keyboard('{Enter}');
      
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should open dropdown on Space key', async () => {
      render(<Select options={mockOptions} />);
      
      const combobox = screen.getByRole('combobox');
      combobox.focus();
      await userEvent.keyboard(' ');
      
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should open dropdown on ArrowDown key', async () => {
      render(<Select options={mockOptions} />);
      
      const combobox = screen.getByRole('combobox');
      combobox.focus();
      await userEvent.keyboard('{ArrowDown}');
      
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should close dropdown on Escape key', async () => {
      render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      
      await userEvent.keyboard('{Escape}');
      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Select options={mockOptions} className="custom-select" />);
      expect(container.querySelector('.custom-select')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<Select options={mockOptions} />);
      const combobox = screen.getByRole('combobox');
      
      expect(combobox).toHaveAttribute('aria-expanded', 'false');
      expect(combobox).toHaveAttribute('aria-haspopup', 'listbox');
    });

    it('should update aria-expanded when dropdown opens', async () => {
      render(<Select options={mockOptions} />);
      const combobox = screen.getByRole('combobox');
      
      await userEvent.click(combobox);
      expect(combobox).toHaveAttribute('aria-expanded', 'true');
    });

    it('should have role="listbox" for dropdown', async () => {
      render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should have role="option" for each option', async () => {
      render(<Select options={mockOptions} />);
      
      await userEvent.click(screen.getByRole('combobox'));
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(3);
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Select options={mockOptions} value="option1" />);
      const initialElement = screen.getByRole('combobox');

      rerender(<Select options={mockOptions} value="option1" />);
      const afterRerenderElement = screen.getByRole('combobox');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
