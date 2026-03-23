/**
 * Form Component - Rendering Tests
 * 
 * Tests for Form component rendering behavior.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import Form, { FormErrorMessage, FormHelperText } from './Form';

// Test schema
const testSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type TestFormData = z.infer<typeof testSchema>;

// Test wrapper component
const TestFormWrapper = ({
  children,
  schema = testSchema,
  mode = 'onTouched',
  defaultValues = { email: '', password: '' },
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

describe('Form Component - Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render form element', () => {
    render(<TestFormWrapper><div>Test</div></TestFormWrapper>);

    expect(screen.getByRole('form')).toBeInTheDocument();
  });

  it('should render children', () => {
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

  it('should render with default values', () => {
    render(
      <TestFormWrapper defaultValues={{ email: 'test@example.com', password: 'password123' }}>
        <div>Test</div>
      </TestFormWrapper>
    );

    expect(screen.getByRole('form')).toBeInTheDocument();
  });
});

describe('FormErrorMessage - Rendering', () => {
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

  it('should not render when error is empty string', () => {
    render(<FormErrorMessage error="" />);

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

describe('FormHelperText - Rendering', () => {
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

  it('should have correct id attribute', () => {
    render(<FormHelperText text="Helper text" />);

    expect(screen.getByText('Helper text')).toHaveAttribute('id', 'form-helper-text');
  });
});
