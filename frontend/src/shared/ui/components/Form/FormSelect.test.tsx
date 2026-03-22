/**
 * FormSelect Component - Enhanced Test Suite
 * 
 * Comprehensive tests for FormSelect component including:
 * - Rendering behavior
 * - User interactions
 * - Validation and error handling
 * - Edge cases and accessibility
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Form from './Form';
import FormSelect from './FormSelect';

// Test wrapper component
const TestFormWrapper = ({
  children,
  schema,
  mode = 'onTouched',
  defaultValues = {},
}: {
  children: React.ReactNode;
  schema?: any;
  mode?: any;
  defaultValues?: any;
}) => {
  const form = useForm({
    resolver: schema ? zodResolver(schema) : undefined,
    mode,
    defaultValues,
  });

  return (
    <Form form={form} onSubmit={vi.fn()}>
      {children}
    </Form>
  );
};

const options = [
  { value: 'football', label: 'Football' },
  { value: 'basketball', label: 'Basketball' },
  { value: 'tennis', label: 'Tennis' },
];

describe('FormSelect Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render select field', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" label="Sport" options={options} />
        </TestFormWrapper>
      );
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    it('should render label', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" label="Sport" options={options} />
        </TestFormWrapper>
      );
      expect(screen.getByText('Sport')).toBeInTheDocument();
    });

    it('should render all options', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={options} />
        </TestFormWrapper>
      );
      options.forEach((option) => {
        expect(screen.getByText(option.label)).toBeInTheDocument();
      });
    });

    it('should render placeholder option when provided', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={options} placeholder="Select a sport" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Select a sport')).toBeInTheDocument();
    });

    it('should render helper text when provided', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" helperText="Choose your favorite sport" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Choose your favorite sport')).toBeInTheDocument();
    });

    it('should render required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" label="Sport" required />
        </TestFormWrapper>
      );
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={options} className="custom-select" />
        </TestFormWrapper>
      );
      const wrapper = screen.getByRole('combobox').closest('.form-field-wrapper');
      expect(wrapper).toHaveClass('custom-select');
    });
  });

  describe('interactions', () => {
    it('should select option when clicked', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={options} />
        </TestFormWrapper>
      );

      const select = screen.getByRole('combobox');
      await user.selectOptions(select, 'football');

      expect(select).toHaveValue('football');
    });

    it('should switch between options', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={options} />
        </TestFormWrapper>
      );

      const select = screen.getByRole('combobox');
      await user.selectOptions(select, 'football');
      expect(select).toHaveValue('football');

      await user.selectOptions(select, 'basketball');
      expect(select).toHaveValue('basketball');
    });

    it('should handle default value', () => {
      render(
        <TestFormWrapper defaultValues={{ sport: 'basketball' }}>
          <FormSelect name="sport" options={options} />
        </TestFormWrapper>
      );
      const select = screen.getByRole('combobox');
      expect(select).toHaveValue('basketball');
    });

    it('should handle empty options array', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={[]} />
        </TestFormWrapper>
      );
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });
  });

  describe('edge cases', () => {
    it('should be disabled when disabled is true', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={options} disabled />
        </TestFormWrapper>
      );
      expect(screen.getByRole('combobox')).toBeDisabled();
    });

    it('should disable individual options', () => {
      const disabledOptions = [
        { value: 'football', label: 'Football' },
        { value: 'basketball', label: 'Basketball', disabled: true },
      ];

      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={disabledOptions} />
        </TestFormWrapper>
      );
      const basketballOption = screen.getByText('Basketball');
      expect(basketballOption).toBeDisabled();
    });

    it('should handle null value', () => {
      render(
        <TestFormWrapper defaultValues={{ sport: null }}>
          <FormSelect name="sport" options={options} />
        </TestFormWrapper>
      );
      const select = screen.getByRole('combobox');
      expect(select).toHaveValue('');
    });

    it('should handle undefined value', () => {
      render(
        <TestFormWrapper defaultValues={{}}>
          <FormSelect name="sport" options={options} />
        </TestFormWrapper>
      );
      const select = screen.getByRole('combobox');
      expect(select).toHaveValue('');
    });

    it('should not render label when not provided', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" options={options} />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/sport/i)).not.toBeInTheDocument();
    });

    it('should not render helper text when not provided', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" label="Sport" />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/helper/i)).not.toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('should display validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Please select a sport'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormSelect name="sport" label="Sport" options={options} />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Please select a sport')).toBeInTheDocument();
      });
    });

    it('should display error with custom className', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormSelect name="sport" options={options} className="custom-select" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const select = screen.getByRole('combobox');
        expect(select).toHaveClass('form-select--error');
      });
    });

    it('should clear error when valid option is selected', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema} mode="onSubmit" defaultValues={{ sport: '' }}>
          <FormSelect name="sport" options={options} />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Required')).toBeInTheDocument();
      });

      // Select a valid option to clear the error
      const select = screen.getByRole('combobox');
      await user.selectOptions(select, 'football');

      // Trigger form submission to validate the new value
      await user.click(screen.getByRole('button', { name: /submit/i }));

      // Wait for React Hook Form to update the validation state
      await waitFor(() => {
        expect(screen.queryByText('Required')).not.toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should hide helper text when error is present', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormSelect name="sport" helperText="Choose your sport" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      expect(screen.getByText('Choose your sport')).toBeInTheDocument();

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText('Choose your sport')).not.toBeInTheDocument();
        expect(screen.getByText('Required')).toBeInTheDocument();
      });
    });
  });

  describe('accessibility', () => {
    it('should have correct ARIA attributes for required field', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" label="Sport" required />
        </TestFormWrapper>
      );

      const select = screen.getByRole('combobox');
      expect(select).toHaveAttribute('aria-required', 'true');
    });

    it('should have correct ARIA attributes for disabled field', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" label="Sport" disabled />
        </TestFormWrapper>
      );

      const select = screen.getByRole('combobox');
      expect(select).toHaveAttribute('disabled');
    });

    it('should have correct ARIA attributes for invalid field', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormSelect name="sport" options={options} />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const select = screen.getByRole('combobox');
        expect(select).toHaveAttribute('aria-invalid', 'true');
      });
    });

    it('should associate error message with select', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormSelect name="sport" options={options} />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const select = screen.getByRole('combobox');
        const errorId = select.getAttribute('aria-describedby');
        expect(errorId).toContain('error');
      });
    });

    it('should associate helper text with select', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" helperText="Helper text" />
        </TestFormWrapper>
      );

      const select = screen.getByRole('combobox');
      const helperId = select.getAttribute('aria-describedby');
      expect(helperId).toContain('helper');
    });
  });
});
