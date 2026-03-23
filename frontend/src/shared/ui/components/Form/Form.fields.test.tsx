/**
 * Form Component - Field Tests
 * 
 * Tests for individual form field components.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
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

describe('FormInput Field', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

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

  it('should be disabled when disabled is true', () => {
    render(
      <TestFormWrapper>
        <FormInput name="email" disabled />
      </TestFormWrapper>
    );

    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('should handle type attribute', () => {
    render(
      <TestFormWrapper>
        <FormInput name="password" type="password" />
      </TestFormWrapper>
    );

    expect(screen.getByLabelText(/password/i)).toHaveAttribute('type', 'password');
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

  it('should handle autoComplete attribute', () => {
    render(
      <TestFormWrapper>
        <FormInput name="email" autoComplete="email" />
      </TestFormWrapper>
    );

    expect(screen.getByRole('textbox')).toHaveAttribute('autoComplete', 'email');
  });
});

describe('FormSelect Field', () => {
  const options = [
    { value: 'football', label: 'Football' },
    { value: 'basketball', label: 'Basketball' },
    { value: 'tennis', label: 'Tennis' },
  ];

  it('should render select field', () => {
    render(
      <TestFormWrapper>
        <FormSelect name="sport" label="Sport" options={options} />
      </TestFormWrapper>
    );

    expect(screen.getByLabelText('Sport')).toBeInTheDocument();
  });

  it('should render all options', () => {
    render(
      <TestFormWrapper>
        <FormSelect name="sport" options={options} />
      </TestFormWrapper>
    );

    options.forEach((option) => {
      expect(screen.getByText(option.label)).toBeInTheDocument();
    });
  });

  it('should render placeholder option when provided', () => {
    render(
      <TestFormWrapper>
        <FormSelect name="sport" options={options} placeholder="Select a sport" />
      </TestFormWrapper>
    );

    expect(screen.getByText('Select a sport')).toBeInTheDocument();
  });

  it('should select option when clicked', async () => {
    const user = userEvent.setup();

    render(
      <TestFormWrapper>
        <FormSelect name="sport" options={options} />
      </TestFormWrapper>
    );

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'football');

    expect(select).toHaveValue('football');
  });

  it('should disable individual options', () => {
    const disabledOptions = [
      { value: 'football', label: 'Football' },
      { value: 'basketball', label: 'Basketball', disabled: true },
    ];

    render(
      <TestFormWrapper>
        <FormSelect name="sport" options={disabledOptions} />
      </TestFormWrapper>
    );

    const basketballOption = screen.getByText('Basketball');
    expect(basketballOption).toBeDisabled();
  });

  it('should be disabled when disabled is true', () => {
    render(
      <TestFormWrapper>
        <FormSelect name="sport" options={options} disabled />
      </TestFormWrapper>
    );

    expect(screen.getByRole('combobox')).toBeDisabled();
  });

  it('should apply custom className', () => {
    render(
      <TestFormWrapper>
        <FormSelect name="sport" options={options} className="custom-select" />
      </TestFormWrapper>
    );

    const wrapper = screen.getByRole('combobox').closest('.form-field-wrapper');
    expect(wrapper).toHaveClass('custom-select');
  });
});

describe('FormCheckbox Field', () => {
  it('should render checkbox', () => {
    render(
      <TestFormWrapper>
        <FormCheckbox name="agree" label="I agree" />
      </TestFormWrapper>
    );

    expect(screen.getByLabelText('I agree')).toBeInTheDocument();
  });

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

  it('should be disabled when disabled is true', () => {
    render(
      <TestFormWrapper>
        <FormCheckbox name="agree" label="I agree" disabled />
      </TestFormWrapper>
    );

    expect(screen.getByRole('checkbox')).toBeDisabled();
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

  it('should have correct ARIA attributes', () => {
    render(
      <TestFormWrapper>
        <FormCheckbox name="agree" label="I agree" required />
      </TestFormWrapper>
    );

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toHaveAttribute('aria-required', 'true');
    expect(checkbox).toHaveAttribute('aria-checked', 'false');
  });
});

describe('FormRadio Field', () => {
  const options = [
    { value: 'football', label: 'Football' },
    { value: 'basketball', label: 'Basketball' },
    { value: 'tennis', label: 'Tennis' },
  ];

  it('should render radio group', () => {
    render(
      <TestFormWrapper>
        <FormRadio name="sport" label="Sport" options={options} />
      </TestFormWrapper>
    );

    expect(screen.getByText('Sport')).toBeInTheDocument();
    expect(screen.getByRole('radiogroup')).toBeInTheDocument();
  });

  it('should render all radio options', () => {
    render(
      <TestFormWrapper>
        <FormRadio name="sport" options={options} />
      </TestFormWrapper>
    );

    options.forEach((option) => {
      expect(screen.getByLabelText(option.label)).toBeInTheDocument();
    });
  });

  it('should select option when clicked', async () => {
    const user = userEvent.setup();

    render(
      <TestFormWrapper>
        <FormRadio name="sport" options={options} />
      </TestFormWrapper>
    );

    const footballRadio = screen.getByLabelText('Football');
    await user.click(footballRadio);

    expect(footballRadio).toBeChecked();
  });

  it('should switch between options', async () => {
    const user = userEvent.setup();

    render(
      <TestFormWrapper>
        <FormRadio name="sport" options={options} />
      </TestFormWrapper>
    );

    const footballRadio = screen.getByLabelText('Football');
    const basketballRadio = screen.getByLabelText('Basketball');

    await user.click(footballRadio);
    expect(footballRadio).toBeChecked();

    await user.click(basketballRadio);
    expect(basketballRadio).toBeChecked();
    expect(footballRadio).not.toBeChecked();
  });

  it('should render in column direction by default', () => {
    render(
      <TestFormWrapper>
        <FormRadio name="sport" options={options} />
      </TestFormWrapper>
    );

    const group = screen.getByRole('radiogroup');
    expect(group).not.toHaveClass('form-radio-group--row');
  });

  it('should render in row direction when specified', () => {
    render(
      <TestFormWrapper>
        <FormRadio name="sport" options={options} direction="row" />
      </TestFormWrapper>
    );

    const group = screen.getByRole('radiogroup');
    expect(group).toHaveClass('form-radio-group--row');
  });

  it('should disable individual options', () => {
    const disabledOptions = [
      { value: 'football', label: 'Football' },
      { value: 'basketball', label: 'Basketball', disabled: true },
    ];

    render(
      <TestFormWrapper>
        <FormRadio name="sport" options={disabledOptions} />
      </TestFormWrapper>
    );

    expect(screen.getByLabelText('Basketball')).toBeDisabled();
  });

  it('should be disabled when disabled is true', () => {
    render(
      <TestFormWrapper>
        <FormRadio name="sport" options={options} disabled />
      </TestFormWrapper>
    );

    options.forEach((option) => {
      expect(screen.getByLabelText(option.label)).toBeDisabled();
    });
  });

  it('should apply custom className', () => {
    render(
      <TestFormWrapper>
        <FormRadio name="sport" options={options} className="custom-radio" />
      </TestFormWrapper>
    );

    const wrapper = screen.getByRole('radiogroup').closest('.form-radio-wrapper');
    expect(wrapper).toHaveClass('custom-radio');
  });
});
