/**
 * FormCheckbox Component - Enhanced Test Suite
 * 
 * Comprehensive tests for FormCheckbox component including:
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
import FormCheckbox from './FormCheckbox';

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

describe('FormCheckbox Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render checkbox', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('checkbox')).toBeInTheDocument();
    });

    it('should render label', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );
      expect(screen.getByLabelText('I agree')).toBeInTheDocument();
    });

    it('should render label text', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="Remember me" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Remember me')).toBeInTheDocument();
    });

    it('should render required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" required />
        </TestFormWrapper>
      );
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" className="custom-checkbox" />
        </TestFormWrapper>
      );
      const wrapper = screen.getByRole('checkbox').closest('.form-checkbox-wrapper');
      expect(wrapper).toHaveClass('custom-checkbox');
    });
  });

  describe('interactions', () => {
    it('should be unchecked by default', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('checkbox')).not.toBeChecked();
    });

    it('should be checked when clicked', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );

      const checkbox = screen.getByRole('checkbox');
      await user.click(checkbox);

      expect(checkbox).toBeChecked();
    });

    it('should toggle when clicked multiple times', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );

      const checkbox = screen.getByRole('checkbox');
      
      await user.click(checkbox);
      expect(checkbox).toBeChecked();
      
      await user.click(checkbox);
      expect(checkbox).not.toBeChecked();
    });

    it('should handle default checked value', () => {
      render(
        <TestFormWrapper defaultValues={{ agree: true }}>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('checkbox')).toBeChecked();
    });

    it('should handle default unchecked value', () => {
      render(
        <TestFormWrapper defaultValues={{ agree: false }}>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('checkbox')).not.toBeChecked();
    });

    it('should handle keyboard navigation', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );

      const checkbox = screen.getByRole('checkbox');
      checkbox.focus();
      expect(checkbox).toHaveFocus();

      await user.keyboard(' ');
      expect(checkbox).toBeChecked();
    });
  });

  describe('edge cases', () => {
    it('should be disabled when disabled is true', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" disabled />
        </TestFormWrapper>
      );
      expect(screen.getByRole('checkbox')).toBeDisabled();
    });

    it('should handle null value', () => {
      render(
        <TestFormWrapper defaultValues={{ agree: null }}>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('checkbox')).not.toBeChecked();
    });

    it('should handle undefined value', () => {
      render(
        <TestFormWrapper defaultValues={{}}>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('checkbox')).not.toBeChecked();
    });

    it('should not render label when not provided', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" />
        </TestFormWrapper>
      );
      expect(screen.queryByRole('checkbox')).toBeInTheDocument();
    });

    it('should handle indeterminate state', () => {
      render(
        <TestFormWrapper defaultValues={{ agree: false }}>
          <FormCheckbox name="agree" label="I agree" indeterminate />
        </TestFormWrapper>
      );
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-checked', 'mixed');
    });
  });

  describe('error handling', () => {
    it('should display validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        agree: z.boolean().refine(val => val === true, 'You must agree to terms'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormCheckbox name="agree" label="I agree" required />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('You must agree to terms')).toBeInTheDocument();
      });
    });

    it('should display error with custom className', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        agree: z.boolean().refine(val => val === true, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormCheckbox name="agree" className="custom-checkbox" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const checkbox = screen.getByRole('checkbox');
        expect(checkbox).toHaveClass('form-checkbox--error');
      });
    });

    it('should clear error when checked', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        agree: z.boolean().refine(val => val === true, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormCheckbox name="agree" label="I agree" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Required')).toBeInTheDocument();
      });

      const checkbox = screen.getByRole('checkbox');
      await user.click(checkbox);

      await waitFor(() => {
        expect(screen.queryByText('Required')).not.toBeInTheDocument();
      });
    });
  });

  describe('accessibility', () => {
    it('should have correct ARIA attributes for required field', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" required />
        </TestFormWrapper>
      );

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-required', 'true');
    });

    it('should have correct ARIA attributes for disabled field', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" disabled />
        </TestFormWrapper>
      );

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('disabled');
    });

    it('should have correct ARIA attributes for invalid field', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        agree: z.boolean().refine(val => val === true, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormCheckbox name="agree" label="I agree" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const checkbox = screen.getByRole('checkbox');
        expect(checkbox).toHaveAttribute('aria-invalid', 'true');
      });
    });

    it('should associate label with checkbox', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );

      const checkbox = screen.getByLabelText('I agree');
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).toHaveAttribute('type', 'checkbox');
    });

    it('should have correct aria-checked attribute', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-checked', 'false');
    });
  });
});
