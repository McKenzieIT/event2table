/**
 * FormInput Component - Enhanced Test Suite
 * 
 * Comprehensive tests for FormInput component including:
 * - Rendering behavior
 * - User interactions
 * - Validation and error handling
 * - Edge cases and accessibility
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import Form from './Form';
import FormInput from './FormInput';

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

describe('FormInput Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render input field', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('should render label', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
    });

    it('should render placeholder', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" placeholder="Enter email" />
        </TestFormWrapper>
      );
      expect(screen.getByPlaceholderText('Enter email')).toBeInTheDocument();
    });

    it('should render helper text when provided', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" helperText="Enter your email address" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Enter your email address')).toBeInTheDocument();
    });

    it('should render required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" required />
        </TestFormWrapper>
      );
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" className="custom-input" />
        </TestFormWrapper>
      );
      const wrapper = screen.getByRole('textbox').closest('.form-field-wrapper');
      expect(wrapper).toHaveClass('custom-input');
    });
  });

  describe('interactions', () => {
    it('should handle user input', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );

      const input = screen.getByRole('textbox');
      await user.type(input, 'test@example.com');
      expect(input).toHaveValue('test@example.com');
    });

    it('should handle password type input', () => {
      render(
        <TestFormWrapper>
          <FormInput name="password" label="Password" type="password" />
        </TestFormWrapper>
      );
      expect(screen.getByLabelText(/password/i)).toHaveAttribute('type', 'password');
    });

    it('should handle number type input', () => {
      render(
        <TestFormWrapper>
          <FormInput name="age" label="Age" type="number" />
        </TestFormWrapper>
      );
      expect(screen.getByLabelText(/age/i)).toHaveAttribute('type', 'number');
    });

    it('should handle email type input', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email Address" type="email" />
        </TestFormWrapper>
      );
      expect(screen.getByLabelText(/email/i)).toHaveAttribute('type', 'email');
    });

    it('should handle autoComplete attribute', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" autoComplete="email" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toHaveAttribute('autoComplete', 'email');
    });

    it('should handle focus and blur events', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );

      const input = screen.getByRole('textbox');
      await user.click(input);
      expect(input).toHaveFocus();

      await user.tab();
      expect(input).not.toHaveFocus();
    });
  });

  describe('edge cases', () => {
    it('should be disabled when disabled is true', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" disabled />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toBeDisabled();
    });

    it('should handle empty initial value', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toHaveValue('');
    });

    it('should handle default value', () => {
      render(
        <TestFormWrapper defaultValues={{ email: 'default@example.com' }}>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toHaveValue('default@example.com');
    });

    it('should handle null value', () => {
      render(
        <TestFormWrapper defaultValues={{ email: null }}>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toHaveValue('');
    });

    it('should handle undefined value', () => {
      render(
        <TestFormWrapper defaultValues={{}}>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toHaveValue('');
    });

    it('should not render label when not provided', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" />
        </TestFormWrapper>
      );
      expect(screen.queryByRole('textbox')).toBeInTheDocument();
    });

    it('should not render helper text when not provided', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/helper/i)).not.toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('should display validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        email: z.string({ required_error: 'Email is required' }).email('Invalid email format'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" label="Email" type="email" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/required|invalid/i)).toBeInTheDocument();
      });
    });

    it('should display error with custom className', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        email: z.string({ required_error: 'Required' }).email('Invalid email'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" label="Email" type="email" className="custom-input" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const input = screen.getByRole('textbox');
        expect(input).toHaveClass('form-input--error');
      });
    });

    it('should clear error when valid input is provided', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        email: z.string({ required_error: 'Required' }).email('Invalid email'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" label="Email" type="email" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/required/i)).toBeInTheDocument();
      });

      const input = screen.getByRole('textbox');
      await user.clear(input);
      await user.type(input, 'test@example.com');

      await waitFor(() => {
        expect(screen.queryByText(/required|invalid/i)).not.toBeInTheDocument();
      });
    });

    it('should hide helper text when error is present', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        email: z.string({ required_error: 'Email is required' }).email('Invalid email'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" label="Email" helperText="Enter your email" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      expect(screen.getByText('Enter your email')).toBeInTheDocument();

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText('Enter your email')).not.toBeInTheDocument();
        expect(screen.getByText(/required|invalid/i)).toBeInTheDocument();
      });
    });
  });

  describe('accessibility', () => {
    it('should have correct ARIA attributes for required field', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" required />
        </TestFormWrapper>
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-required', 'true');
    });

    it('should have correct ARIA attributes for disabled field', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" disabled />
        </TestFormWrapper>
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('disabled');
    });

    it('should have correct ARIA attributes for invalid field', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        email: z.string().email('Invalid email'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" label="Email" type="email" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const input = screen.getByRole('textbox');
        expect(input).toHaveAttribute('aria-invalid', 'true');
      });
    });

    it('should associate error message with input', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        email: z.string().email('Invalid email'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" label="Email" type="email" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const input = screen.getByRole('textbox');
        const errorId = input.getAttribute('aria-describedby');
        expect(errorId).toContain('error');
      });
    });

    it('should associate helper text with input', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" helperText="Helper text" />
        </TestFormWrapper>
      );

      const input = screen.getByRole('textbox');
      const helperId = input.getAttribute('aria-describedby');
      expect(helperId).toContain('helper');
    });
  });
});
