import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi } from 'vitest';

import Select from './Select';
import type { SelectOption } from './Select.types';

describe('Select Component', () => {
  const mockOptions: SelectOption[] = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' },
    { value: 'option4', label: 'Option 4', disabled: true },
  ];

  describe('Rendering', () => {
    it('should render without crashing', () => {
      render(<Select name="test" options={mockOptions} />);
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    it('should render with label', () => {
      render(<Select name="test" label="Test Label" options={mockOptions} />);
      expect(screen.getByText('Test Label')).toBeInTheDocument();
    });

    it('should render with placeholder', () => {
      render(<Select name="test" placeholder="Select an option" options={mockOptions} />);
      expect(screen.getByText('Select an option')).toBeInTheDocument();
    });

    it('should render with helper text', () => {
      render(<Select name="test" helperText="This is helper text" options={mockOptions} />);
      expect(screen.getByText('This is helper text')).toBeInTheDocument();
    });

    it('should render with error state', () => {
      render(<Select name="test" error="This is an error" options={mockOptions} />);
      expect(screen.getByText('This is an error')).toBeInTheDocument();
    });

    it('should render with required indicator', () => {
      render(<Select name="test" label="Test Label" required options={mockOptions} />);
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should render disabled state', () => {
      render(<Select name="test" disabled options={mockOptions} />);
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveAttribute('aria-disabled', 'true');
    });

    it('should render with different sizes', () => {
      const { container: smallContainer } = render(
        <Select name="test" size="small" options={mockOptions} />
      );
      const { container: mediumContainer } = render(
        <Select name="test" size="medium" options={mockOptions} />
      );
      const { container: largeContainer } = render(
        <Select name="test" size="large" options={mockOptions} />
      );

      expect(smallContainer.querySelector('.cyber-select-wrapper--small')).toBeInTheDocument();
      expect(mediumContainer.querySelector('.cyber-select-wrapper--medium')).toBeInTheDocument();
      expect(largeContainer.querySelector('.cyber-select-wrapper--large')).toBeInTheDocument();
    });
  });

  describe('Selection Functionality', () => {
    it('should open dropdown on click', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should select an option on click', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();
      render(<Select name="test" options={mockOptions} onChange={handleChange} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      const option = screen.getByText('Option 1');
      await user.click(option);

      expect(handleChange).toHaveBeenCalledWith('option1');
    });

    it('should display selected value', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} value="option1" />);

      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveTextContent('Option 1');
    });

    it('should close dropdown after selection', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      const option = screen.getByText('Option 1');
      await user.click(option);

      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });

    it('should not select disabled option', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();
      render(<Select name="test" options={mockOptions} onChange={handleChange} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      const disabledOption = screen.getByText('Option 4');
      await user.click(disabledOption);

      expect(handleChange).not.toHaveBeenCalled();
    });

    it('should handle multiple selection', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();
      render(
        <Select name="test" options={mockOptions} multiple onChange={handleChange} />
      );

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      const option1 = screen.getByText('Option 1');
      await user.click(option1);

      expect(handleChange).toHaveBeenCalledWith(['option1']);

      await user.click(trigger);
      const option2 = screen.getByText('Option 2');
      await user.click(option2);

      expect(handleChange).toHaveBeenCalledWith(['option1', 'option2']);
    });

    it('should display selected tags for multiple selection', async () => {
      const user = userEvent.setup();
      render(
        <Select name="test" options={mockOptions} multiple value={['option1', 'option2']} />
      );

      expect(screen.getByText('Option 1')).toBeInTheDocument();
      expect(screen.getByText('Option 2')).toBeInTheDocument();
    });

    it('should remove selected option in multiple mode', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();
      render(
        <Select name="test" options={mockOptions} multiple value={['option1']} onChange={handleChange} />
      );

      const removeButton = screen.getByLabelText('Remove Option 1');
      await user.click(removeButton);

      expect(handleChange).toHaveBeenCalledWith([]);
    });
  });

  describe('Search Functionality', () => {
    it('should show search input when searchable', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} searchable />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
    });

    it('should filter options based on search term', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} searchable />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      const searchInput = screen.getByPlaceholderText('Search...');
      await user.type(searchInput, 'Option 1');

      expect(screen.getByText('Option 1')).toBeInTheDocument();
      expect(screen.queryByText('Option 2')).not.toBeInTheDocument();
      expect(screen.queryByText('Option 3')).not.toBeInTheDocument();
    });

    it('should show empty state when no options match', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} searchable />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      const searchInput = screen.getByPlaceholderText('Search...');
      await user.type(searchInput, 'Non-existent option');

      expect(screen.getByText('No options found')).toBeInTheDocument();
    });
  });

  describe('Keyboard Navigation', () => {
    it('should open dropdown on Enter key', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} />);

      const trigger = screen.getByRole('combobox');
      trigger.focus();
      await user.keyboard('{Enter}');

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should open dropdown on Space key', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} />);

      const trigger = screen.getByRole('combobox');
      trigger.focus();
      await user.keyboard(' ');

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should close dropdown on Escape key', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      trigger.focus();
      await user.keyboard('{Escape}');

      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });

    it('should navigate options with ArrowDown key', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      trigger.focus();
      await user.keyboard('{ArrowDown}');

      const options = screen.getAllByRole('option');
      expect(options[0]).toHaveClass('cyber-select-option--focused');
    });

    it('should navigate options with ArrowUp key', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      trigger.focus();
      await user.keyboard('{ArrowDown}');
      await user.keyboard('{ArrowUp}');

      const options = screen.getAllByRole('option');
      // The last non-disabled option should have focused class
      const nonDisabledOptions = options.filter(opt => !opt.classList.contains('cyber-select-option--disabled'));
      expect(nonDisabledOptions[nonDisabledOptions.length - 1]).toHaveClass('cyber-select-option--focused');
    });

    it('should select focused option on Enter key', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();
      render(<Select name="test" options={mockOptions} onChange={handleChange} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      trigger.focus();
      await user.keyboard('{ArrowDown}');
      await user.keyboard('{Enter}');

      expect(handleChange).toHaveBeenCalledWith('option1');
    });

    it('should close dropdown on Tab key', async () => {
      const user = userEvent.setup();
      render(<Select name="test" options={mockOptions} />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      trigger.focus();
      await user.keyboard('{Tab}');

      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error States', () => {
    it('should display error message', () => {
      render(<Select name="test" error="Required field" options={mockOptions} />);
      expect(screen.getByText('Required field')).toBeInTheDocument();
    });

    it('should have invalid aria attribute when error is present', () => {
      render(<Select name="test" error="Error" options={mockOptions} />);
      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveAttribute('aria-invalid', 'true');
    });

    it('should not show helper text when error is present', () => {
      render(
        <Select
          name="test"
          error="Error"
          helperText="Helper text"
          options={mockOptions}
        />
      );
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
    });
  });

  describe('React Hook Form Integration', () => {
    it('should work with React Hook Form Controller', async () => {
      const user = userEvent.setup();
      const TestForm = () => {
        const { control } = useForm({
          defaultValues: {
            testField: '',
          },
        });

        return (
          <form>
            <Select
              name="testField"
              control={control}
              options={mockOptions}
              label="Test Field"
            />
          </form>
        );
      };

      render(<TestForm />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      const option = screen.getByText('Option 1');
      await user.click(option);

      expect(trigger).toHaveTextContent('Option 1');
    });

    it('should validate with React Hook Form rules', async () => {
      const user = userEvent.setup();
      const TestForm = () => {
        const { control, trigger, formState: { errors } } = useForm({
          defaultValues: {
            testField: '',
          },
          mode: 'onBlur',
        });

        return (
          <form>
            <Select
              name="testField"
              control={control}
              rules={{ required: 'This field is required' }}
              options={mockOptions}
              label="Test Field"
            />
          </form>
        );
      };

      render(<TestForm />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);
      await user.click(document.body); // Blur to trigger validation

      await waitFor(() => {
        expect(screen.getByText('This field is required')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(
        <Select
          name="test"
          label="Test Label"
          options={mockOptions}
          required
          error="Error"
        />
      );

      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveAttribute('aria-expanded', 'false');
      expect(trigger).toHaveAttribute('aria-haspopup', 'listbox');
      expect(trigger).toHaveAttribute('aria-invalid', 'true');
      expect(trigger).toHaveAttribute('aria-multiselectable', 'false');
    });

    it('should have aria-multiselectable for multiple select', () => {
      render(
        <Select
          name="test"
          options={mockOptions}
          multiple
        />
      );

      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveAttribute('aria-multiselectable', 'true');
    });

    it('should have proper label association', () => {
      render(
        <Select
          name="test"
          label="Test Label"
          options={mockOptions}
        />
      );

      const label = screen.getByText('Test Label');
      const trigger = screen.getByRole('combobox');
      expect(label).toHaveAttribute('id');
      expect(trigger).toHaveAttribute('aria-labelledby');
    });

    it('should have proper error description association', () => {
      render(
        <Select
          name="test"
          error="Error message"
          options={mockOptions}
        />
      );

      const trigger = screen.getByRole('combobox');
      expect(trigger).toHaveAttribute('aria-describedby');
    });
  });

  describe('Click Outside', () => {
    it('should close dropdown when clicking outside', async () => {
      const user = userEvent.setup();
      render(
        <div>
          <Select name="test" options={mockOptions} />
          <div data-testid="outside">Outside</div>
        </div>
      );

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      expect(screen.getByRole('listbox')).toBeInTheDocument();

      const outside = screen.getByTestId('outside');
      await user.click(outside);

      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });
  });

  describe('Controlled Component', () => {
    it('should update when value prop changes', () => {
      const { rerender } = render(
        <Select name="test" options={mockOptions} value="option1" />
      );

      expect(screen.getByRole('combobox')).toHaveTextContent('Option 1');

      rerender(<Select name="test" options={mockOptions} value="option2" />);

      expect(screen.getByRole('combobox')).toHaveTextContent('Option 2');
    });
  });
});
