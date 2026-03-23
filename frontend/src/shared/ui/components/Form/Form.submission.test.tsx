/**
 * Form Component - Submission Tests
 * 
 * Tests for Form component submission behavior.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Form from './Form';
import { FormInput } from './index';

// Test schema
const testSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type TestFormData = z.infer<typeof testSchema>;

// Test wrapper component
const TestForm = ({
  onSubmit,
  defaultValues,
}: {
  onSubmit: (data: TestFormData) => void;
  defaultValues?: Partial<TestFormData>;
}) => {
  const form = useForm<TestFormData>({
    resolver: zodResolver(testSchema),
    defaultValues: {
      email: defaultValues?.email || '',
      password: defaultValues?.password || '',
    },
  });

  return (
    <Form form={form} onSubmit={onSubmit}>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...form.register('email')}
          placeholder="Enter email"
        />
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          {...form.register('password')}
          placeholder="Enter password"
        />
      </div>
      <button type="submit" disabled={form.formState.isSubmitting}>
        Submit
      </button>
    </Form>
  );
};

describe('Form Component - Submission', () => {
  const mockSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call onSubmit with form data when valid', async () => {
    const user = userEvent.setup();
    render(<TestForm onSubmit={mockSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('should not call onSubmit when form is invalid', async () => {
    const user = userEvent.setup();
    render(<TestForm onSubmit={mockSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'invalid-email');
    await user.type(screen.getByLabelText(/password/i), 'short');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(mockSubmit).not.toHaveBeenCalled();
    });
  });

  it('should show validation errors on submit', async () => {
    const user = userEvent.setup();
    render(<TestForm onSubmit={mockSubmit} />);

    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
    });
  });

  it('should prevent default form submission', async () => {
    const user = userEvent.setup();
    const preventDefaultMock = vi.fn();

    render(<TestForm onSubmit={mockSubmit} />);

    const form = screen.getByRole('form');
    const submitEvent = new Event('submit', {
      bubbles: true,
      cancelable: true,
    });
    Object.defineProperty(submitEvent, 'preventDefault', {
      value: preventDefaultMock,
    });

    fireEvent(form, submitEvent);

    expect(preventDefaultMock).toHaveBeenCalled();
  });

  it('should reset form when resetAfterSubmit is true', async () => {
    const user = userEvent.setup();
    const form = useForm<TestFormData>({
      defaultValues: { email: '', password: '' },
    });

    render(
      <Form form={form} onSubmit={mockSubmit} resetAfterSubmit>
        <input {...form.register('email')} placeholder="email" />
        <input {...form.register('password')} placeholder="password" />
        <button type="submit">Submit</button>
      </Form>
    );

    await user.type(screen.getByPlaceholderText('email'), 'test@example.com');
    await user.type(screen.getByPlaceholderText('password'), 'password123');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByPlaceholderText('email')).toHaveValue('');
      expect(screen.getByPlaceholderText('password')).toHaveValue('');
    });
  });

  it('should not reset form when resetAfterSubmit is false', async () => {
    const user = userEvent.setup();
    const form = useForm<TestFormData>({
      defaultValues: { email: '', password: '' },
    });

    render(
      <Form form={form} onSubmit={mockSubmit} resetAfterSubmit={false}>
        <input {...form.register('email')} placeholder="email" />
        <input {...form.register('password')} placeholder="password" />
        <button type="submit">Submit</button>
      </Form>
    );

    await user.type(screen.getByPlaceholderText('email'), 'test@example.com');
    await user.type(screen.getByPlaceholderText('password'), 'password123');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalled();
    });

    expect(screen.getByPlaceholderText('email')).toHaveValue('test@example.com');
    expect(screen.getByPlaceholderText('password')).toHaveValue('password123');
  });

  it('should handle async submission', async () => {
    const user = userEvent.setup();
    const asyncSubmit = vi.fn().mockResolvedValue({ success: true });

    render(<TestForm onSubmit={asyncSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(asyncSubmit).toHaveBeenCalled();
    });
  });

  it('should disable submit button during submission', async () => {
    const user = userEvent.setup();
    let isSubmitting = false;

    const TestFormWithState = () => {
      const form = useForm<TestFormData>({
        resolver: zodResolver(testSchema),
        defaultValues: { email: '', password: '' },
      });

      isSubmitting = form.formState.isSubmitting;

      return (
        <Form form={form} onSubmit={async () => await new Promise(resolve => setTimeout(resolve, 100))}>
          <input {...form.register('email')} placeholder="email" />
          <input {...form.register('password')} placeholder="password" />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<TestFormWithState />);

    await user.type(screen.getByPlaceholderText('email'), 'test@example.com');
    await user.type(screen.getByPlaceholderText('password'), 'password123');
    
    const submitButton = screen.getByRole('button', { name: 'Submit' });
    await user.click(submitButton);

    await waitFor(() => {
      expect(isSubmitting).toBe(true);
      expect(submitButton).toBeDisabled();
    });

    await waitFor(() => {
      expect(isSubmitting).toBe(false);
      expect(submitButton).not.toBeDisabled();
    }, { timeout: 200 });
  });
});
