/**
 * FormDatePicker Component Unit Tests
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@test/test-utils';
import { useForm } from 'react-hook-form';
import FormDatePicker from '../FormDatePicker';
import Form from '../Form';

// Test wrapper component
const TestFormWrapper = ({ children, defaultValues = {} }: { children: React.ReactNode; defaultValues?: Record<string, any> }) => {
  const form = useForm({ defaultValues });
  return (
    <Form form={form} onSubmit={vi.fn()}>{children}</Form>
  );
};

describe('FormDatePicker', () => {
  it('should render with label', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('Test Date')).toBeInTheDocument();
  });

  it('should render required indicator when required', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" required />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('should render helper text', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" helperText="Select a date" />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('Select a date')).toBeInTheDocument();
  });

  it('should render date input by default', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="date"]');
    expect(input).toBeInTheDocument();
  });

  it('should render datetime-local input when showTime is true', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" showTime />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="datetime-local"]');
    expect(input).toBeInTheDocument();
  });

  it('should handle date selection', async () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="date"]') as HTMLInputElement;
    fireEvent.change(input, { target: { value: '2024-01-15' } });
    
    expect(input).toHaveValue('2024-01-15');
  });

  it('should be disabled when disabled prop is true', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" disabled />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="date"]');
    expect(input).toBeDisabled();
  });

  it('should apply min date constraint', () => {
    const minDate = new Date('2024-01-01');
    
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" minDate={minDate} />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="date"]');
    expect(input).toHaveAttribute('min', '2024-01-01');
  });

  it('should apply max date constraint', () => {
    const maxDate = new Date('2024-12-31');
    
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" maxDate={maxDate} />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="date"]');
    expect(input).toHaveAttribute('max', '2024-12-31');
  });

  it('should render with default value', () => {
    const defaultDate = new Date('2024-06-15');
    
    render(
      <TestFormWrapper defaultValues={{ testDate: defaultDate }}>
        <FormDatePicker name="testDate" label="Test Date" />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="date"]') as HTMLInputElement;
    expect(input).toHaveValue('2024-06-15');
  });

  it('should have correct ARIA attributes', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" required />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="date"]');
    expect(input).toHaveAttribute('aria-required', 'true');
    expect(input).toHaveAttribute('aria-invalid', 'false');
  });

  it('should show error state', () => {
    // Use a wrapper component to properly use hooks
    const ErrorTestWrapper = () => {
      const form = useForm({
        defaultValues: { testDate: null },
        mode: 'onSubmit'
      });
      
      // Use useEffect to set error only once after mount
      React.useEffect(() => {
        form.setError('testDate', { type: 'required', message: 'Date is required' });
      }, [form]);
      
      return (
        <Form form={form} onSubmit={vi.fn()}>
          <FormDatePicker name="testDate" label="Test Date" />
        </Form>
      );
    };
    
    render(<ErrorTestWrapper />);
    
    expect(screen.getByRole('alert')).toHaveTextContent('Date is required');
  });

  it('should render calendar icon', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" />
      </TestFormWrapper>
    );
    
    const icon = document.querySelector('.form-datepicker-icon');
    expect(icon).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    render(
      <TestFormWrapper>
        <FormDatePicker name="testDate" label="Test Date" className="custom-class" />
      </TestFormWrapper>
    );
    
    const wrapper = document.querySelector('.custom-class');
    expect(wrapper).toBeInTheDocument();
  });
});
