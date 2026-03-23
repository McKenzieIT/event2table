/**
 * FormRadio Component - Enhanced Test Suite
 * 
 * Comprehensive tests for FormRadio component including:
 * - Rendering behavior
 * - User interactions
 * - Validation and error handling
 * - Edge cases and accessibility
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Form from './Form';
import FormRadio from './FormRadio';

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

const options = [
  { value: 'football', label: 'Football' },
  { value: 'basketball', label: 'Basketball' },
  { value: 'tennis', label: 'Tennis' },
];

describe('FormRadio Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
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

    it('should render helper text when provided', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" options={options} helperText="Choose your favorite sport" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Choose your favorite sport')).toBeInTheDocument();
    });

    it('should render required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" label="Sport" options={options} required />
        </TestFormWrapper>
      );
      expect(screen.getByText('*')).toBeInTheDocument();
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

  describe('interactions', () => {
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

    it('should handle default value', () => {
      render(
        <TestFormWrapper defaultValues={{ sport: 'basketball' }}>
          <FormRadio name="sport" options={options} />
        </TestFormWrapper>
      );
      expect(screen.getByLabelText('Basketball')).toBeChecked();
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
  });

  describe('edge cases', () => {
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

    it('should handle empty options array', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" options={[]} />
        </TestFormWrapper>
      );
      expect(screen.getByRole('radiogroup')).toBeInTheDocument();
    });

    it('should handle null value', () => {
      render(
        <TestFormWrapper defaultValues={{ sport: null }}>
          <FormRadio name="sport" options={options} />
        </TestFormWrapper>
      );
      options.forEach((option) => {
        expect(screen.getByLabelText(option.label)).not.toBeChecked();
      });
    });

    it('should handle undefined value', () => {
      render(
        <TestFormWrapper defaultValues={{}}>
          <FormRadio name="sport" options={options} />
        </TestFormWrapper>
      );
      options.forEach((option) => {
        expect(screen.getByLabelText(option.label)).not.toBeChecked();
      });
    });

    it('should not render label when not provided', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" options={options} />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/sport/i)).not.toBeInTheDocument();
    });

    it('should not render helper text when not provided', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" label="Sport" options={options} />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/helper/i)).not.toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('should display validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Please select a sport'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRadio name="sport" label="Sport" options={options} />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Please select a sport')).toBeInTheDocument();
      });
    });

    it('should display error with custom className', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRadio name="sport" options={options} className="custom-radio" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const wrapper = screen.getByRole('radiogroup').closest('.form-radio-wrapper');
        expect(wrapper).toHaveClass('form-radio-wrapper--error');
      });
    });

    it('should clear error when option is selected', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema} mode="onSubmit">
          <FormRadio name="sport" options={options} />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      // Initially trigger validation by clicking submit
      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Required')).toBeInTheDocument();
      });

      // Select an option to clear the error
      const footballRadio = screen.getByLabelText('Football');
      await user.click(footballRadio);

      // Submit again to validate and clear the error
      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText('Required')).not.toBeInTheDocument();
      });
    });

    it('should hide helper text when error is present', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRadio name="sport" options={options} helperText="Choose your sport" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      expect(screen.getByText('Choose your sport')).toBeInTheDocument();

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText('Choose your sport')).not.toBeInTheDocument();
        expect(screen.getByText('Required')).toBeInTheDocument();
      });
    });
  });

  describe('accessibility', () => {
    it('should have correct ARIA attributes for required field', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" label="Sport" options={options} required />
        </TestFormWrapper>
      );

      const group = screen.getByRole('radiogroup');
      expect(group).toHaveAttribute('aria-required', 'true');
    });

    it('should have correct ARIA attributes for disabled field', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" label="Sport" options={options} disabled />
        </TestFormWrapper>
      );

      options.forEach((option) => {
        const radio = screen.getByLabelText(option.label);
        expect(radio).toHaveAttribute('disabled');
      });
    });

    it('should have correct ARIA attributes for invalid field', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        sport: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRadio name="sport" options={options} />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        options.forEach((option) => {
          const radio = screen.getByLabelText(option.label);
          expect(radio).toHaveAttribute('aria-invalid', 'true');
        });
      });
    });

    it('should have radiogroup role', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" options={options} />
        </TestFormWrapper>
      );
      expect(screen.getByRole('radiogroup')).toBeInTheDocument();
    });

    it('should associate labels with radio buttons', () => {
      render(
        <TestFormWrapper>
          <FormRadio name="sport" options={options} />
        </TestFormWrapper>
      );
      options.forEach((option) => {
        const radio = screen.getByLabelText(option.label);
        expect(radio).toBeInTheDocument();
        expect(radio).toHaveAttribute('type', 'radio');
      });
    });
  });
});