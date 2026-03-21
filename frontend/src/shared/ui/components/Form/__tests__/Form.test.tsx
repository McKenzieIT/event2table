/**
 * Form Component Tests
 * 
 * Tests for the Form component that integrates React Hook Form with validation.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Form, { FormErrorMessage, FormHelperText, useFormContextValue } from '../Form';

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
        {form.formState.errors.email && (
          <FormErrorMessage error={form.formState.errors.email.message} />
        )}
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          {...form.register('password')}
          placeholder="Enter password"
        />
        {form.formState.errors.password && (
          <FormErrorMessage error={form.formState.errors.password.message} />
        )}
      </div>
      <button type="submit" disabled={form.formState.isSubmitting}>
        Submit
      </button>
    </Form>
  );
};

describe('Form Component', () => {
  const mockSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render form element', () => {
      render(<TestForm onSubmit={mockSubmit} />);

      expect(screen.getByRole('form')).toBeInTheDocument();
    });

    it('should render children', () => {
      render(<TestForm onSubmit={mockSubmit} />);

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
    });

    it('should have noValidate attribute', () => {
      render(<TestForm onSubmit={mockSubmit} />);

      const form = screen.getByRole('form');
      expect(form).toHaveAttribute('noValidate');
    });

    it('should apply custom className', () => {
      const form = useForm();
      render(
        <Form form={form} onSubmit={() => {}} className="custom-class">
          <div>Test</div>
        </Form>
      );

      const formElement = screen.getByRole('form');
      expect(formElement).toHaveClass('custom-class');
    });

    it('should apply custom id', () => {
      const form = useForm();
      render(
        <Form form={form} onSubmit={() => {}} id="test-form">
          <div>Test</div>
        </Form>
      );

      const formElement = screen.getByRole('form');
      expect(formElement).toHaveAttribute('id', 'test-form');
    });
  });

  describe('Form Submission', () => {
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
  });

  describe('Reset After Submit', () => {
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

      // Form should retain values
      expect(screen.getByPlaceholderText('email')).toHaveValue('test@example.com');
      expect(screen.getByPlaceholderText('password')).toHaveValue('password123');
    });
  });

  describe('Form State', () => {
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
      const form = useForm<TestFormData>({
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
      const form = useForm<TestFormData>({
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
});

describe('FormErrorMessage', () => {
  it('should render error message', () => {
    render(<FormErrorMessage error="Test error message" />);

    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('should not render when error is null', () => {
    render(<FormErrorMessage error={null} />);

    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('should not render when error is undefined', () => {
    render(<FormErrorMessage error={undefined} />);

    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('should have alert role', () => {
    render(<FormErrorMessage error="Test error" />);

    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('should have aria-live attribute', () => {
    render(<FormErrorMessage error="Test error" />);

    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'polite');
  });

  it('should apply custom className', () => {
    render(<FormErrorMessage error="Test error" className="custom-error" />);

    const error = screen.getByRole('alert');
    expect(error).toHaveClass('custom-error');
  });
});

describe('FormHelperText', () => {
  it('should render helper text', () => {
    render(<FormHelperText text="Helper text" />);

    expect(screen.getByText('Helper text')).toBeInTheDocument();
  });

  it('should not render when text is null', () => {
    render(<FormHelperText text={null} />);

    expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
  });

  it('should not render when text is undefined', () => {
    render(<FormHelperText text={undefined} />);

    expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
  });

  it('should not render when text is empty string', () => {
    render(<FormHelperText text="" />);

    expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
  });

  it('should apply custom className', () => {
    render(<FormHelperText text="Helper text" className="custom-helper" />);

    const helper = screen.getByText('Helper text');
    expect(helper).toHaveClass('custom-helper');
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
