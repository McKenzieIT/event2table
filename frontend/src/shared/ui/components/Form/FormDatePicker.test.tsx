/**
 * FormDatePicker Component - Test Suite
 * 
 * Comprehensive tests for FormDatePicker component including:
 * - Rendering behavior
 * - User interactions
 * - Validation and error handling
 * - Edge cases and accessibility
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Form from './Form';
import FormDatePicker from './FormDatePicker';

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

describe('FormDatePicker Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render date input', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );
      // Date inputs don't have role="textbox", use getByLabelText instead
      expect(screen.getByLabelText('Birth Date')).toBeInTheDocument();
    });

    it('should render label', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Birth Date')).toBeInTheDocument();
    });

    it('should render calendar icon', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );
      // The calendar icon is in a span with class form-datepicker-icon
      const iconContainer = document.querySelector('.form-datepicker-icon');
      expect(iconContainer).toBeInTheDocument();
    });

    it('should render helper text when provided', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" helperText="Select your birth date" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Select your birth date')).toBeInTheDocument();
    });

    it('should render required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" required />
        </TestFormWrapper>
      );
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" className="custom-datepicker" />
        </TestFormWrapper>
      );
      const wrapper = screen.getByLabelText('Birth Date').closest('.form-field-wrapper');
      expect(wrapper).toHaveClass('custom-datepicker');
    });
  });

  describe('interactions', () => {
    it('should handle date input', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );

      const input = screen.getByLabelText('Birth Date');
      await user.type(input, '2024-01-15');
      expect(input).toHaveValue('2024-01-15');
    });

    it('should handle datetime input when showTime is true', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="meetingDate" label="Meeting Date" showTime />
        </TestFormWrapper>
      );
      const input = screen.getByLabelText('Meeting Date');
      expect(input).toHaveAttribute('type', 'datetime-local');
    });

    it('should handle default value', () => {
      const defaultDate = new Date('2024-01-15');
      render(
        <TestFormWrapper defaultValues={{ birthDate: defaultDate }}>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );
      const input = screen.getByLabelText('Birth Date');
      expect(input).toHaveValue('2024-01-15');
    });

    it('should handle null value', () => {
      render(
        <TestFormWrapper defaultValues={{ birthDate: null }}>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );
      const input = screen.getByLabelText('Birth Date');
      expect(input).toHaveValue('');
    });

    it('should handle undefined value', () => {
      render(
        <TestFormWrapper defaultValues={{}}>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );
      const input = screen.getByLabelText('Birth Date');
      expect(input).toHaveValue('');
    });
  });

  describe('edge cases', () => {
    it('should be disabled when disabled is true', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" disabled />
        </TestFormWrapper>
      );
      expect(screen.getByLabelText('Birth Date')).toBeDisabled();
    });

    it('should respect minDate constraint', () => {
      const minDate = new Date('2024-01-01');
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" minDate={minDate} />
        </TestFormWrapper>
      );
      const input = screen.getByLabelText('Birth Date');
      expect(input).toHaveAttribute('min', '2024-01-01');
    });

    it('should respect maxDate constraint', () => {
      const maxDate = new Date('2024-12-31');
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" maxDate={maxDate} />
        </TestFormWrapper>
      );
      const input = screen.getByLabelText('Birth Date');
      expect(input).toHaveAttribute('max', '2024-12-31');
    });

    it('should handle invalid date string', () => {
      render(
        <TestFormWrapper defaultValues={{ birthDate: 'invalid-date' }}>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );
      const input = screen.getByLabelText('Birth Date');
      expect(input).toHaveValue('');
    });

    it('should not render label when not provided', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/birth date/i)).not.toBeInTheDocument();
    });

    it('should not render helper text when not provided', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/helper/i)).not.toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('should display validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        birthDate: z.date({
          required_error: 'Birth date is required',
          invalid_type_error: 'Invalid date',
        }),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormDatePicker name="birthDate" label="Birth Date" required />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/birth date is required/i)).toBeInTheDocument();
      });
    });

    it('should display error with custom className', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        birthDate: z.date({
          required_error: 'Required',
        }),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormDatePicker name="birthDate" label="Birth Date" className="custom-datepicker" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const input = screen.getByLabelText('Birth Date');
        expect(input).toHaveClass('form-input--error');
      });
    });

    it('should clear error when valid date is selected', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        birthDate: z.date({
          required_error: 'Required',
        }),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormDatePicker name="birthDate" label="Birth Date" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/required/i)).toBeInTheDocument();
      });

      const input = screen.getByLabelText('Birth Date');
      await user.type(input, '2024-01-15');

      await waitFor(() => {
        expect(screen.queryByText(/required/i)).not.toBeInTheDocument();
      });
    });

    it('should hide helper text when error is present', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        birthDate: z.date({
          required_error: 'Required',
        }),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormDatePicker name="birthDate" label="Birth Date" helperText="Select your birth date" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      expect(screen.getByText('Select your birth date')).toBeInTheDocument();

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText('Select your birth date')).not.toBeInTheDocument();
        expect(screen.getByText(/required/i)).toBeInTheDocument();
      });
    });
  });

  describe('accessibility', () => {
    it('should have correct ARIA attributes for required field', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" required />
        </TestFormWrapper>
      );

      const input = screen.getByLabelText('Birth Date');
      expect(input).toHaveAttribute('aria-required', 'true');
    });

    it('should have correct ARIA attributes for disabled field', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" disabled />
        </TestFormWrapper>
      );

      const input = screen.getByLabelText('Birth Date');
      expect(input).toHaveAttribute('disabled');
    });

    it('should have correct ARIA attributes for invalid field', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        birthDate: z.date({
          required_error: 'Required',
        }),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormDatePicker name="birthDate" label="Birth Date" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const input = screen.getByLabelText('Birth Date');
        expect(input).toHaveAttribute('aria-invalid', 'true');
      });
    });

    it('should associate label with input', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" />
        </TestFormWrapper>
      );

      const input = screen.getByLabelText('Birth Date');
      expect(input).toBeInTheDocument();
    });

    it('should associate error message with input', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        birthDate: z.date({
          required_error: 'Required',
        }),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormDatePicker name="birthDate" label="Birth Date" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const input = screen.getByLabelText('Birth Date');
        const errorId = input.getAttribute('aria-describedby');
        expect(errorId).toContain('error');
      });
    });

    it('should associate helper text with input', () => {
      render(
        <TestFormWrapper>
          <FormDatePicker name="birthDate" label="Birth Date" helperText="Helper text" />
        </TestFormWrapper>
      );

      const input = screen.getByLabelText('Birth Date');
      const helperId = input.getAttribute('aria-describedby');
      expect(helperId).toContain('helper');
    });
  });
});
