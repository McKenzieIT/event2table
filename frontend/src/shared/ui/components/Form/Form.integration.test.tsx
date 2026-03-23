/**
 * Form Component - Integration and Edge Cases Tests
 * 
 * Tests for Form component integration scenarios and edge cases.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import Form, { useFormContextValue } from './Form';

import { FormInput, FormSelect, FormCheckbox } from './index';

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

describe('Form Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle multiple fields together', async () => {
    const user = userEvent.setup();
    const onSubmitData = vi.fn();
    const complexSchema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
      sport: z.string().min(1, 'Sport is required'),
      agree: z.boolean().refine((val) => val === true, 'You must agree'),
    });

    const TestForm = () => {
      const form = useForm({
        resolver: zodResolver(complexSchema),
        mode: 'onBlur',
      });

      const handleSubmit = form.handleSubmit(async (data) => {
        onSubmitData(data);
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <FormInput name="name" label="Name" />
          <FormInput name="email" label="Email" type="email" />
          <FormSelect
            name="sport"
            label="Sport"
            options={[
              { value: 'football', label: 'Football' },
              { value: 'basketball', label: 'Basketball' },
            ]}
          />
          <FormCheckbox name="agree" label="I agree" />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<TestForm />);

    await user.type(screen.getByRole('textbox', { name: /name/i }), 'John Doe');
    await user.type(screen.getByRole('textbox', { name: /email/i }), 'john@example.com');
    await user.selectOptions(screen.getByRole('combobox'), 'football');
    await user.click(screen.getByLabelText('I agree'));

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(onSubmitData).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'John Doe',
          email: 'john@example.com',
          sport: 'football',
          agree: true,
        })
      );
    });
  });

  it('should show multiple errors', async () => {
    const user = userEvent.setup();
    const complexSchema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
      sport: z.string().min(1, 'Sport is required'),
      agree: z.boolean().refine((val) => val === true, 'You must agree'),
    });

    const TestForm = () => {
      const form = useForm({
        resolver: zodResolver(complexSchema),
        mode: 'onTouched',
      });

      const handleSubmit = form.handleSubmit(async (data) => {
        // This will only be called if validation passes
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <FormInput name="name" label="Name" />
          <FormInput name="email" label="Email" type="email" />
          <FormSelect
            name="sport"
            label="Sport"
            options={[
              { value: 'football', label: 'Football' },
              { value: 'basketball', label: 'Basketball' },
            ]}
          />
          <FormCheckbox name="agree" label="I agree" />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<TestForm />);

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
    }, { timeout: 5000 });

    expect(screen.getByText('Invalid email')).toBeInTheDocument();
    expect(screen.getByText('Sport is required')).toBeInTheDocument();
    expect(screen.getByText('You must agree')).toBeInTheDocument();
  });

  it('should clear errors when valid input is provided', async () => {
    const user = userEvent.setup();
    const complexSchema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
    });

    const TestForm = () => {
      const form = useForm({
        resolver: zodResolver(complexSchema),
        mode: 'onSubmit',
      });

      const handleSubmit = form.handleSubmit(async (data) => {
        // This will only be called if validation passes
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <FormInput name="name" label="Name" />
          <FormInput name="email" label="Email" type="email" />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<TestForm />);

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
    }, { timeout: 3000 });

    const nameInput = screen.getByRole('textbox', { name: /name/i });
    await user.type(nameInput, 'John');
    const emailInput = screen.getByRole('textbox', { name: /email/i });
    await user.type(emailInput, 'john@example.com');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.queryByText('Name is required')).not.toBeInTheDocument();
    }, { timeout: 3000 });
  });
});

describe('Form Edge Cases', () => {
  it('should handle form without schema', () => {
    render(
      <TestFormWrapper>
        <FormInput name="field" />
        <button type="submit">Submit</button>
      </TestFormWrapper>
    );

    expect(screen.getByRole('form')).toBeInTheDocument();
  });

  it('should handle empty options array', () => {
    render(
      <TestFormWrapper>
        <FormSelect name="field" options={[]} />
      </TestFormWrapper>
    );

    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('should handle missing label', () => {
    render(
      <TestFormWrapper>
        <FormInput name="field" />
      </TestFormWrapper>
    );

    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('should handle undefined default values', () => {
    render(
      <TestFormWrapper defaultValues={undefined}>
        <FormInput name="field" />
      </TestFormWrapper>
    );

    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });
});

describe('Form State Tracking', () => {
  it('should track isSubmitting state', async () => {
    let isSubmittingState = false;

    const TestFormWithState = () => {
      const form = useForm();
      isSubmittingState = form.formState.isSubmitting;

      return (
        <Form form={form} onSubmit={async () => {}}>
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<TestFormWithState />);

    expect(isSubmittingState).toBe(false);
  });

  it('should track isValid state', () => {
    const testSchema = z.object({
      email: z.string().email('Invalid email'),
      password: z.string().min(8, 'Password must be at least 8 characters'),
    });

    const form = useForm({
      resolver: zodResolver(testSchema),
      defaultValues: { email: '', password: '' },
    });

    render(
      <Form form={form} onSubmit={() => {}}>
        <div data-testid="valid-state">{form.formState.isValid ? 'Valid' : 'Invalid'}</div>
      </Form>
    );

    expect(screen.getByTestId('valid-state')).toHaveTextContent('Invalid');
  });

  it('should track isDirty state', async () => {
    const user = userEvent.setup();
    const form = useForm({
      defaultValues: { email: '', password: '' },
    });

    render(
      <Form form={form} onSubmit={() => {}}>
        <input {...form.register('email')} placeholder="email" />
        <div data-testid="dirty-state">{form.formState.isDirty ? 'Dirty' : 'Clean'}</div>
      </Form>
    );

    expect(screen.getByTestId('dirty-state')).toHaveTextContent('Clean');

    await user.type(screen.getByPlaceholderText('email'), 'test@example.com');

    await waitFor(() => {
      expect(screen.getByTestId('dirty-state')).toHaveTextContent('Dirty');
    });
  });
});

describe('useFormContextValue Hook', () => {
  it('should throw error when used outside Form component', () => {
    const TestComponent = () => {
      useFormContextValue();
      return null;
    };

    expect(() => render(<TestComponent />)).toThrow(
      'useFormContextValue must be used within a Form component'
    );
  });

  it('should provide form context value when used within Form component', () => {
    let contextValue: any;

    const TestChild = () => {
      contextValue = useFormContextValue();
      return <div>Test</div>;
    };

    const form = useForm();

    render(
      <Form form={form} onSubmit={() => {}}>
        <TestChild />
      </Form>
    );

    expect(contextValue).toBeDefined();
    expect(contextValue.form).toBe(form);
    expect(contextValue.isSubmitting).toBe(false);
    expect(contextValue.isValid).toBe(true);
    expect(contextValue.isDirty).toBe(false);
  });
});

describe('Form Performance', () => {
  it('should not re-render unnecessarily', () => {
    const { rerender } = render(
      <TestFormWrapper>
        <FormInput name="field" />
      </TestFormWrapper>
    );

    const firstRender = screen.getByRole('textbox');
    
    rerender(
      <TestFormWrapper>
        <FormInput name="field" />
      </TestFormWrapper>
    );

    const secondRender = screen.getByRole('textbox');
    
    expect(firstRender).toBe(secondRender);
  });
});
