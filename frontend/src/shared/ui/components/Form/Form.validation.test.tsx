/**
 * Form Component - Validation Tests
 * 
 * Tests for Form component validation behavior.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Form from './Form';
import { FormInput, FormSelect, FormCheckbox, FormRadio } from './index';

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

describe('Form Component - Validation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show validation errors on submit', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      email: z.string().email('Invalid email'),
    });

    render(
      <TestFormWrapper schema={schema} mode="onSubmit">
        <FormInput name="email" label="Email" />
        <button type="submit">Submit</button>
      </TestFormWrapper>
    );

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
    });
  });

  it('should validate on blur when mode is onBlur', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      email: z.string().email('Invalid email'),
    });

    render(
      <TestFormWrapper schema={schema} mode="onBlur">
        <FormInput name="email" label="Email" />
      </TestFormWrapper>
    );

    const input = screen.getByRole('textbox');
    await user.type(input, 'invalid');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
    });
  });

  it('should validate on change when mode is onChange', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      email: z.string().email('Invalid email'),
    });

    render(
      <TestFormWrapper schema={schema} mode="onChange">
        <FormInput name="email" label="Email" />
      </TestFormWrapper>
    );

    const input = screen.getByRole('textbox');
    await user.type(input, 'invalid');

    await waitFor(() => {
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
    });
  });

  it('should clear errors when valid input is provided', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      email: z.string().email('Invalid email'),
    });

    render(
      <TestFormWrapper schema={schema} mode="onSubmit">
        <FormInput name="email" label="Email" />
        <button type="submit">Submit</button>
      </TestFormWrapper>
    );

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
    });

    const input = screen.getByRole('textbox');
    await user.clear(input);
    await user.type(input, 'test@example.com');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.queryByText('Invalid email')).not.toBeInTheDocument();
    });
  });

  it('should show multiple validation errors', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      email: z.string().email('Invalid email'),
      password: z.string().min(8, 'Password too short'),
    });

    render(
      <TestFormWrapper schema={schema} mode="onSubmit">
        <FormInput name="email" label="Email" />
        <FormInput name="password" label="Password" />
        <button type="submit">Submit</button>
      </TestFormWrapper>
    );

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
      expect(screen.getByText('Password too short')).toBeInTheDocument();
    });
  });

  it('should validate select field', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      sport: z.string().min(1, 'Please select a sport'),
    });

    const options = [
      { value: 'football', label: 'Football' },
      { value: 'basketball', label: 'Basketball' },
    ];

    render(
      <TestFormWrapper schema={schema} mode="onBlur">
        <FormSelect name="sport" label="Sport" options={options} />
      </TestFormWrapper>
    );

    const select = screen.getByLabelText('Sport');
    await user.click(select);
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText('Please select a sport')).toBeInTheDocument();
    });
  });

  it('should validate checkbox field', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      agree: z.boolean().refine((val) => val === true, 'You must agree'),
    });

    render(
      <Form form={useForm({
        resolver: zodResolver(schema),
        defaultValues: { agree: false },
        mode: 'onSubmit',
      })} onSubmit={vi.fn()}>
        <FormCheckbox name="agree" label="I agree" />
        <button type="submit">Submit</button>
      </Form>
    );

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.getByText('You must agree')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('should validate radio field', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      sport: z.string().min(1, 'Please select a sport'),
    });

    const options = [
      { value: 'football', label: 'Football' },
      { value: 'basketball', label: 'Basketball' },
    ];

    render(
      <Form form={useForm({
        resolver: zodResolver(schema),
        mode: 'onSubmit',
      })} onSubmit={vi.fn()}>
        <FormRadio name="sport" label="Sport" options={options} />
        <button type="submit">Submit</button>
      </Form>
    );

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.getByText('Please select a sport')).toBeInTheDocument();
    });
  });

  it('should show required indicator when required is true', () => {
    render(
      <TestFormWrapper>
        <FormInput name="email" label="Email" required />
      </TestFormWrapper>
    );

    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('should have correct ARIA attributes when error is present', async () => {
    const user = userEvent.setup();
    const schema = z.object({
      email: z.string().email('Invalid email'),
    });

    render(
      <TestFormWrapper schema={schema} mode="all">
        <FormInput name="email" label="Email" required />
      </TestFormWrapper>
    );

    const input = screen.getByRole('textbox');
    await user.type(input, 'invalid');
    await user.tab();

    await waitFor(() => {
      expect(input).toHaveAttribute('aria-invalid', 'true');
      expect(input).toHaveAttribute('aria-required', 'true');
    });
  });
});
