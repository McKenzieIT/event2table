/**
 * Form Component - Main Test Suite
 * 
 * Comprehensive tests for Form component including:
 * - Rendering behavior
 * - Form submission
 * - Validation
 * - Error handling
 * - Context management
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import Form, { useFormContextValue } from './Form';

import { FormInput, FormSelect, FormCheckbox, FormRadio } from './index';

// Test schema
const testSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  agree: z.boolean().refine(val => val === true, 'You must agree to terms'),
  sport: z.string().min(1, 'Please select a sport'),
});

type TestFormData = z.infer<typeof testSchema>;

// Test wrapper component
const TestFormWrapper = ({
  children,
  schema = testSchema,
  mode = 'onTouched',
  defaultValues = { email: '', password: '', agree: false, sport: '' },
}: {
  children: React.ReactNode;
  schema?: any;
  mode?: any;
  defaultValues?: any;
}) => {
  const form = useForm<TestFormData>({
    resolver: zodResolver(schema),
    mode,
    defaultValues,
  });

  return (
    <Form form={form} onSubmit={vi.fn()}>
      {children}
    </Form>
  );
};

describe('Form Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render form element with role', () => {
      render(<TestFormWrapper><div>Test</div></TestFormWrapper>);
      expect(screen.getByRole('form')).toBeInTheDocument();
    });

    it('should render children components', () => {
      render(
        <TestFormWrapper>
          <div>Child 1</div>
          <div>Child 2</div>
        </TestFormWrapper>
      );
      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();
    });

    it('should have noValidate attribute', () => {
      render(<TestFormWrapper><div>Test</div></TestFormWrapper>);
      const form = screen.getByRole('form');
      expect(form).toHaveAttribute('noValidate');
    });

    it('should apply custom className', () => {
      const TestFormWithClassName = () => {
        const form = useForm();
        return (
          <Form form={form} onSubmit={() => {}} className="custom-class">
            <div>Test</div>
          </Form>
        );
      };

      render(<TestFormWithClassName />);
      const formElement = screen.getByRole('form');
      expect(formElement).toHaveClass('custom-class');
    });

    it('should apply custom id', () => {
      const TestFormWithId = () => {
        const form = useForm();
        return (
          <Form form={form} onSubmit={() => {}} id="test-form">
            <div>Test</div>
          </Form>
        );
      };

      render(<TestFormWithId />);
      const formElement = screen.getByRole('form');
      expect(formElement).toHaveAttribute('id', 'test-form');
    });
  });

  describe('interactions', () => {
    it('should call onSubmit with valid data', async () => {
      const user = userEvent.setup();
      const handleSubmit = vi.fn();

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(testSchema),
          defaultValues: { email: '', password: '', agree: false, sport: '' },
        });

        return (
          <Form form={form} onSubmit={handleSubmit}>
            <FormInput name="email" label="Email" type="email" />
            <FormInput name="password" label="Password" type="password" />
            <FormCheckbox name="agree" label="I agree" />
            <FormRadio 
              name="sport" 
              label="Sport"
              options={[
                { value: 'football', label: 'Football' },
                { value: 'basketball', label: 'Basketball' }
              ]}
            />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByLabelText(/i agree/i));
      await user.click(screen.getByLabelText(/football/i));
      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(handleSubmit).toHaveBeenCalledTimes(1);
        expect(handleSubmit).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
          agree: true,
          sport: 'football',
        });
      });
    });

    it('should not call onSubmit with invalid data', async () => {
      const user = userEvent.setup();
      const handleSubmit = vi.fn();

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(testSchema),
          defaultValues: { email: '', password: '', agree: false, sport: '' },
        });

        return (
          <Form form={form} onSubmit={handleSubmit}>
            <FormInput name="email" label="Email" type="email" />
            <FormInput name="password" label="Password" type="password" />
            <FormCheckbox name="agree" label="I agree" />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(handleSubmit).not.toHaveBeenCalled();
      });
    });

    it('should prevent default form submission', async () => {
      const user = userEvent.setup();
      const handleSubmit = vi.fn();

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(testSchema),
          defaultValues: { email: 'test@example.com', password: 'password123', agree: true, sport: 'football' },
        });

        return (
          <Form form={form} onSubmit={handleSubmit}>
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(handleSubmit).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('edge cases', () => {
    it('should handle empty children', () => {
      const TestFormWithEmptyChildren = () => {
        const form = useForm();
        return <Form form={form} onSubmit={() => {}} />;
      };

      render(<TestFormWithEmptyChildren />);
      expect(screen.getByRole('form')).toBeInTheDocument();
    });

    it('should handle resetAfterSubmit option', async () => {
      const user = userEvent.setup();
      const handleSubmit = vi.fn();

      const TestForm = () => {
        const form = useForm({
          defaultValues: { email: '', password: '', agree: false, sport: '' },
        });

        return (
          <Form form={form} onSubmit={handleSubmit} resetAfterSubmit>
            <FormInput name="email" label="Email" />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'test@example.com');
      expect(emailInput).toHaveValue('test@example.com');

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(emailInput).toHaveValue('');
      });
    });

    it('should handle async onSubmit', async () => {
      const user = userEvent.setup();
      const handleSubmit = vi.fn(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });

      const TestForm = () => {
        const form = useForm({
          defaultValues: { email: 'test@example.com', password: 'password123', agree: true, sport: 'football' },
        });

        return (
          <Form form={form} onSubmit={handleSubmit}>
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(handleSubmit).toHaveBeenCalledTimes(1);
      }, { timeout: 1000 });
    });

    it('should handle form with only optional fields', async () => {
      const user = userEvent.setup();
      const handleSubmit = vi.fn();

      const optionalSchema = z.object({
        name: z.string().optional(),
      });

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(optionalSchema),
          defaultValues: { name: '' },
        });

        return (
          <Form form={form} onSubmit={handleSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(handleSubmit).toHaveBeenCalledWith({ name: '' });
      });
    });
  });

  describe('error handling', () => {
    it('should display validation errors', async () => {
      const user = userEvent.setup();

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(testSchema),
          defaultValues: { email: '', password: '', agree: false, sport: '' },
        });

        return (
          <Form form={form} onSubmit={() => {}}>
            <FormInput name="email" label="Email" type="email" />
            <FormInput name="password" label="Password" type="password" />
            <FormCheckbox name="agree" label="I agree" required />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
        expect(screen.getByText(/you must agree to terms/i)).toBeInTheDocument();
      });
    });

    it('should clear errors when valid input is provided', async () => {
      const user = userEvent.setup();

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(testSchema),
          defaultValues: { email: '', password: '', agree: false, sport: '' },
          mode: 'onSubmit',
        });

        return (
          <Form form={form} onSubmit={() => {}}>
            <FormInput name="email" label="Email" type="email" />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
      });

      const emailInput = screen.getByLabelText(/email/i);
      await user.clear(emailInput);
      await user.type(emailInput, 'test@example.com');
      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText(/invalid email/i)).not.toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should handle submission errors gracefully', async () => {
      const user = userEvent.setup();
      const handleSubmit = vi.fn(() => {
        throw new Error('Submission failed');
      });

      const TestForm = () => {
        const form = useForm({
          defaultValues: { email: 'test@example.com', password: 'password123', agree: true, sport: 'football' },
        });

        return (
          <Form form={form} onSubmit={handleSubmit}>
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(handleSubmit).toHaveBeenCalled();
      });
    });
  });

  describe('context management', () => {
    it('should provide form context to children', () => {
      let contextValue: any;

      const TestChild = () => {
        contextValue = useFormContextValue();
        return <div>Test</div>;
      };

      const TestFormWithContext = () => {
        const form = useForm({
          defaultValues: { email: '', password: '', agree: false, sport: '' },
        });

        return (
          <Form form={form} onSubmit={() => {}}>
            <TestChild />
          </Form>
        );
      };

      render(<TestFormWithContext />);

      expect(contextValue).toBeDefined();
      expect(contextValue.form).toBeDefined();
      expect(contextValue.isSubmitting).toBe(false);
      expect(contextValue.isDirty).toBe(false);
    });

    it('should update context when form state changes', async () => {
      const user = userEvent.setup();
      let contextValue: any;

      const TestChild = () => {
        contextValue = useFormContextValue();
        return <div>Test</div>;
      };

      const TestForm = () => {
        const form = useForm({
          defaultValues: { email: '' },
        });

        return (
          <Form form={form} onSubmit={() => {}}>
            <FormInput name="email" label="Email" />
            <TestChild />
          </Form>
        );
      };

      render(<TestForm />);

      expect(contextValue.isDirty).toBe(false);

      await user.type(screen.getByLabelText(/email/i), 'test');

      expect(contextValue.isDirty).toBe(true);
    });

    it('should throw error when useFormContextValue is used outside Form', () => {
      const TestChild = () => {
        expect(() => useFormContextValue()).toThrow('useFormContextValue must be used within a Form component');
        return <div>Test</div>;
      };

      render(<TestChild />);
    });
  });
});
