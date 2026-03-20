/**
 * Form Component Unit Tests
 * 
 * Comprehensive test suite for Form system components
 * Target coverage: 85%
 * 
 * Test Categories:
 * 1. Form Container Tests
 * 2. FormInput Tests
 * 3. FormSelect Tests
 * 4. FormCheckbox Tests
 * 5. FormRadio Tests
 * 6. FormErrorMessage Tests
 * 7. FormHelperText Tests
 * 8. Integration Tests
 * 9. Edge Cases
 * 10. Performance Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Form, {
  FormErrorMessage,
  FormHelperText,
  useFormContextValue,
} from './Form';
import FormInput from './FormInput';
import FormSelect from './FormSelect';
import FormCheckbox from './FormCheckbox';
import FormRadio from './FormRadio';

// Test wrapper component
const TestFormWrapper = ({ children, schema, defaultValues = {} }: any) => {
  const form = useForm({
    resolver: schema ? zodResolver(schema) : undefined,
    defaultValues,
    mode: 'onBlur',
  });

  return <Form form={form} onSubmit={vi.fn()}>{children}</Form>;
};

describe('Form System', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ========== Form Container Tests ==========

  describe('Form Container', () => {
    it('should render form element', () => {
      const form = useForm();
      const onSubmit = vi.fn();

      render(
        <Form form={form} onSubmit={onSubmit}>
          <div>Form Content</div>
        </Form>
      );

      expect(screen.getByRole('form')).toBeInTheDocument();
    });

    it('should call onSubmit when form is submitted', async () => {
      const user = userEvent.setup();
      const form = useForm({ defaultValues: { name: 'test' } });
      const onSubmit = vi.fn();

      render(
        <Form form={form} onSubmit={onSubmit}>
          <button type="submit">Submit</button>
        </Form>
      );

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      expect(onSubmit).toHaveBeenCalled();
    });

    it('should prevent default form submission', async () => {
      const user = userEvent.setup();
      const form = useForm();
      const onSubmit = vi.fn();

      render(
        <Form form={form} onSubmit={onSubmit}>
          <button type="submit">Submit</button>
        </Form>
      );

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          preventDefault: expect.any(Function),
        })
      );
    });

    it('should apply custom className', () => {
      const form = useForm();
      const onSubmit = vi.fn();

      render(
        <Form form={form} onSubmit={onSubmit} className="custom-form">
          <div>Content</div>
        </Form>
      );

      expect(screen.getByRole('form')).toHaveClass('custom-form');
    });

    it('should apply custom id', () => {
      const form = useForm();
      const onSubmit = vi.fn();

      render(
        <Form form={form} onSubmit={onSubmit} id="test-form">
          <div>Content</div>
        </Form>
      );

      expect(screen.getByRole('form')).toHaveAttribute('id', 'test-form');
    });

    it('should reset form after submission when resetAfterSubmit is true', async () => {
      const user = userEvent.setup();
      const form = useForm({ defaultValues: { name: 'test' } });
      const onSubmit = vi.fn();

      render(
        <Form form={form} onSubmit={onSubmit} resetAfterSubmit={true}>
          <input {...form.register('name')} />
          <button type="submit">Submit</button>
        </Form>
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveValue('test');

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(input).toHaveValue('');
      });
    });

    it('should have noValidate attribute', () => {
      const form = useForm();
      const onSubmit = vi.fn();

      render(
        <Form form={form} onSubmit={onSubmit}>
          <div>Content</div>
        </Form>
      );

      expect(screen.getByRole('form')).toHaveAttribute('novalidate');
    });
  });

  // ========== FormInput Tests ==========

  describe('FormInput', () => {
    const schema = z.object({
      email: z.string().email('Invalid email'),
      password: z.string().min(8, 'Password must be at least 8 characters'),
    });

    it('should render input field', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );

      expect(screen.getByLabelText('Email')).toBeInTheDocument();
    });

    it('should render with label', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" label="Email Address" />
        </TestFormWrapper>
      );

      expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
    });

    it('should render without label', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" />
        </TestFormWrapper>
      );

      expect(screen.queryByRole('textbox')).toBeInTheDocument();
    });

    it('should render with placeholder', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" placeholder="Enter your email" />
        </TestFormWrapper>
      );

      const input = screen.getByPlaceholderText('Enter your email');
      expect(input).toBeInTheDocument();
    });

    it('should render all input types', () => {
      const types: Array<'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'> = [
        'text',
        'email',
        'password',
        'number',
        'tel',
        'url',
        'search',
      ];

      types.forEach((type) => {
        const { unmount } = render(
          <TestFormWrapper>
            <FormInput name="field" type={type} />
          </TestFormWrapper>
        );

        const input = screen.getByRole('textbox') || screen.getByRole('spinbutton');
        expect(input).toHaveAttribute('type', type);
        unmount();
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

    it('should be disabled when disabled is true', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" disabled />
        </TestFormWrapper>
      );

      expect(screen.getByRole('textbox')).toBeDisabled();
    });

    it('should show error message on validation error', async () => {
      const user = userEvent.setup();

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" label="Email" />
        </TestFormWrapper>
      );

      const input = screen.getByLabelText('Email');
      await user.type(input, 'invalid-email');
      await user.tab();

      await waitFor(() => {
        expect(screen.getByText('Invalid email')).toBeInTheDocument();
      });
    });

    it('should show helper text when provided', () => {
      render(
        <TestFormWrapper>
          <FormInput name="email" helperText="Enter a valid email address" />
        </TestFormWrapper>
      );

      expect(screen.getByText('Enter a valid email address')).toBeInTheDocument();
    });

    it('should not show helper text when error is present', async () => {
      const user = userEvent.setup();

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" helperText="Enter a valid email address" />
        </TestFormWrapper>
      );

      const input = screen.getByRole('textbox');
      await user.type(input, 'invalid');
      await user.tab();

      await waitFor(() => {
        expect(screen.queryByText('Enter a valid email address')).not.toBeInTheDocument();
      });
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

    it('should have correct ARIA attributes when error is present', async () => {
      const user = userEvent.setup();

      render(
        <TestFormWrapper schema={schema}>
          <FormInput name="email" label="Email" required />
        </TestFormWrapper>
      );

      const input = screen.getByLabelText('Email');
      await user.type(input, 'invalid');
      await user.tab();

      await waitFor(() => {
        expect(input).toHaveAttribute('aria-invalid', 'true');
        expect(input).toHaveAttribute('aria-required', 'true');
      });
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

  // ========== FormSelect Tests ==========

  describe('FormSelect', () => {
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

    it('should show required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormSelect name="sport" label="Sport" options={options} required />
        </TestFormWrapper>
      );

      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should show error message on validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Please select a sport'),
      });

      render(
        <TestFormWrapper schema={schema}>
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

  // ========== FormCheckbox Tests ==========

  describe('FormCheckbox', () => {
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

    it('should show required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormCheckbox name="agree" label="I agree" required />
        </TestFormWrapper>
      );

      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should show error message on validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        agree: z.boolean().refine((val) => val === true, 'You must agree'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormCheckbox name="agree" label="I agree" />
        </TestFormWrapper>
      );

      const checkbox = screen.getByRole('checkbox');
      await user.click(checkbox);
      await user.click(checkbox); // Uncheck

      await waitFor(() => {
        expect(screen.getByText('You must agree')).toBeInTheDocument();
      });
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

  // ========== FormRadio Tests ==========

  describe('FormRadio', () => {
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

      expect(screen.getByLabelText('Sport')).toBeInTheDocument();
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

    it('should show error message on validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Please select a sport'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRadio name="sport" label="Sport" options={options} />
        </TestFormWrapper>
      );

      const label = screen.getByLabelText('Sport');
      await user.click(label);
      await user.tab();

      await waitFor(() => {
        expect(screen.getByText('Please select a sport')).toBeInTheDocument();
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

  // ========== FormErrorMessage Tests ==========

  describe('FormErrorMessage', () => {
    it('should not render when error is not provided', () => {
      render(<FormErrorMessage error={undefined} />);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });

    it('should not render when error is empty string', () => {
      render(<FormErrorMessage error="" />);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });

    it('should render error message when provided', () => {
      render(<FormErrorMessage error="This field is required" />);

      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('should have correct ARIA attributes', () => {
      render(<FormErrorMessage error="Error message" />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live', 'polite');
    });

    it('should apply custom className', () => {
      render(
        <FormErrorMessage error="Error" className="custom-error" />
      );

      expect(screen.getByRole('alert')).toHaveClass('custom-error');
    });
  });

  // ========== FormHelperText Tests ==========

  describe('FormHelperText', () => {
    it('should not render when text is not provided', () => {
      render(<FormHelperText text={undefined} />);

      expect(screen.queryByText(/./)).not.toBeInTheDocument();
    });

    it('should not render when text is empty string', () => {
      render(<FormHelperText text="" />);

      expect(screen.queryByText(/./)).not.toBeInTheDocument();
    });

    it('should render helper text when provided', () => {
      render(<FormHelperText text="This is helpful information" />);

      expect(screen.getByText('This is helpful information')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(
        <FormHelperText text="Helper text" className="custom-helper" />
      );

      expect(screen.getByText('Helper text')).toHaveClass('custom-helper');
    });

    it('should have correct id attribute', () => {
      render(<FormHelperText text="Helper text" />);

      expect(screen.getByText('Helper text')).toHaveAttribute('id', 'form-helper-text');
    });
  });

  // ========== Integration Tests ==========

  describe('Form Integration', () => {
    const complexSchema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
      sport: z.string().min(1, 'Sport is required'),
      agree: z.boolean().refine((val) => val === true, 'You must agree'),
    });

    it('should handle multiple fields together', async () => {
      const user = userEvent.setup();
      const onSubmit = vi.fn();

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(complexSchema),
          mode: 'onBlur',
        });

        return (
          <Form form={form} onSubmit={onSubmit}>
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
            <FormCheckbox name="agree" label="I agree" required />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      // Fill form
      await user.type(screen.getByLabelText('Name'), 'John Doe');
      await user.type(screen.getByLabelText('Email'), 'john@example.com');
      await user.selectOptions(screen.getByLabelText('Sport'), 'football');
      await user.click(screen.getByLabelText('I agree'));

      // Submit
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith(
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

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(complexSchema),
          mode: 'onBlur',
        });

        return (
          <Form form={form} onSubmit={vi.fn()}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <FormSelect
              name="sport"
              label="Sport"
              options={[
                { value: 'football', label: 'Football' },
              ]}
            />
            <FormCheckbox name="agree" label="I agree" required />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      // Submit empty form
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.getByText('Invalid email')).toBeInTheDocument();
        expect(screen.getByText('Sport is required')).toBeInTheDocument();
        expect(screen.getByText('You must agree')).toBeInTheDocument();
      });
    });

    it('should clear errors when valid input is provided', async () => {
      const user = userEvent.setup();

      const TestForm = () => {
        const form = useForm({
          resolver: zodResolver(complexSchema),
          mode: 'onBlur',
        });

        return (
          <Form form={form} onSubmit={vi.fn()}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <button type="submit">Submit</button>
          </Form>
        );
      };

      render(<TestForm />);

      // Submit empty form to show errors
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
      });

      // Provide valid input
      await user.type(screen.getByLabelText('Name'), 'John');

      await waitFor(() => {
        expect(screen.queryByText('Name is required')).not.toBeInTheDocument();
      });
    });
  });

  // ========== Edge Cases ==========

  describe('Edge Cases', () => {
    it('should handle form without schema', () => {
      const form = useForm();
      const onSubmit = vi.fn();

      render(
        <Form form={form} onSubmit={onSubmit}>
          <FormInput name="field" />
          <button type="submit">Submit</button>
        </Form>
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

  // ========== Performance Tests ==========

  describe('Performance', () => {
    it('should not re-render unnecessarily', () => {
      const form = useForm();
      const onSubmit = vi.fn();

      const { rerender } = render(
        <Form form={form} onSubmit={onSubmit}>
          <FormInput name="field" />
        </Form>
      );

      const firstRender = screen.getByRole('textbox');
      
      rerender(
        <Form form={form} onSubmit={onSubmit}>
          <FormInput name="field" />
        </Form>
      );

      const secondRender = screen.getByRole('textbox');
      
      expect(firstRender).toBe(secondRender);
    });
  });
});
