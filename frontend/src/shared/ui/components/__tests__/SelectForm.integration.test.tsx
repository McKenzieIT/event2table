/**
 * Select + Form Integration Tests
 * 
 * Tests for Select and Form component integration scenarios.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Select } from '../Select/Select';
import { Form } from '../Form';
import { FormInput, FormCheckbox } from '../Form';

describe('Select + Form Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle select options in form submission', async () => {
    const user = userEvent.setup();
    const onSubmitData = vi.fn();
    
    const schema = z.object({
      name: z.string().min(1, 'Name is required'),
      category: z.string().min(1, 'Category is required'),
      tags: z.array(z.string()).min(1, 'Select at least one tag'),
    });

    const SelectFormIntegration = () => {
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { name: '', category: '', tags: [] },
      });

      const handleSubmit = form.handleSubmit((data) => {
        onSubmitData(data);
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <FormInput name="name" label="Name" />
          <Select
            name="category"
            label="Category"
            options={[
              { value: 'tech', label: 'Technology' },
              { value: 'design', label: 'Design' },
              { value: 'business', label: 'Business' },
            ]}
          />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<SelectFormIntegration />);

    // Fill form
    await user.type(screen.getByRole('textbox', { name: /name/i }), 'Test Item');
    await user.selectOptions(screen.getByRole('combobox'), 'tech');

    // Submit form
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    // Verify submission
    await waitFor(() => {
      expect(onSubmitData).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Test Item',
          category: 'tech',
        })
      );
    });
  });

  it('should handle multiple select in form', async () => {
    const user = userEvent.setup();
    const onSubmitData = vi.fn();
    
    const schema = z.object({
      interests: z.array(z.string()).min(1, 'Select at least one interest'),
    });

    const MultiSelectFormIntegration = () => {
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { interests: [] },
      });

      const handleSubmit = form.handleSubmit((data) => {
        onSubmitData(data);
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <Select
            name="interests"
            label="Interests"
            multiple
            options={[
              { value: 'coding', label: 'Coding' },
              { value: 'design', label: 'Design' },
              { value: 'music', label: 'Music' },
            ]}
          />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<MultiSelectFormIntegration />);

    // Select multiple options
    const select = screen.getByRole('listbox');
    await user.click(select);
    await user.click(screen.getByText('Coding'));
    await user.click(screen.getByText('Design'));

    // Submit form
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    // Verify submission
    await waitFor(() => {
      expect(onSubmitData).toHaveBeenCalledWith(
        expect.objectContaining({
          interests: expect.arrayContaining(['coding', 'design']),
        })
      );
    });
  });

  it('should handle select validation in form', async () => {
    const user = userEvent.setup();
    
    const schema = z.object({
      category: z.string().min(1, 'Category is required'),
    });

    const SelectValidationIntegration = () => {
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onSubmit',
        defaultValues: { category: '' },
      });

      const handleSubmit = form.handleSubmit(() => {
        // Should not reach here
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <Select
            name="category"
            label="Category"
            options={[
              { value: 'tech', label: 'Technology' },
              { value: 'design', label: 'Design' },
            ]}
          />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<SelectValidationIntegration />);

    // Submit without selecting
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    // Verify error
    await waitFor(() => {
      expect(screen.getByText('Category is required')).toBeInTheDocument();
    });
  });

  it('should handle select with dynamic options', async () => {
    const user = userEvent.setup();
    const onSubmitData = vi.fn();
    
    const schema = z.object({
      country: z.string().min(1, 'Country is required'),
    });

    const DynamicSelectIntegration = () => {
      const [options, setOptions] = useState([
        { value: 'us', label: 'United States' },
        { value: 'uk', label: 'United Kingdom' },
      ]);

      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { country: '' },
      });

      const handleSubmit = form.handleSubmit((data) => {
        onSubmitData(data);
      });

      const addOption = () => {
        setOptions([...options, { value: 'ca', label: 'Canada' }]);
      };

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <Select
            name="country"
            label="Country"
            options={options}
          />
          <button type="button" onClick={addOption}>Add Canada</button>
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<DynamicSelectIntegration />);

    // Add new option
    await user.click(screen.getByRole('button', { name: 'Add Canada' }));

    // Select newly added option
    await user.selectOptions(screen.getByRole('combobox'), 'ca');

    // Submit form
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    // Verify submission
    await waitFor(() => {
      expect(onSubmitData).toHaveBeenCalledWith(
        expect.objectContaining({
          country: 'ca',
        })
      );
    });
  });

  it('should handle select with disabled state', () => {
    const schema = z.object({
      category: z.string(),
    });

    const DisabledSelectIntegration = () => {
      const form = useForm({
        resolver: zodResolver(schema),
        defaultValues: { category: 'tech' },
      });

      return (
        <Form form={form} onSubmit={() => {}}>
          <Select
            name="category"
            label="Category"
            disabled
            options={[
              { value: 'tech', label: 'Technology' },
              { value: 'design', label: 'Design' },
            ]}
          />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<DisabledSelectIntegration />);

    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });

  it('should handle select with controlled value', async () => {
    const user = userEvent.setup();
    const onSubmitData = vi.fn();
    
    const schema = z.object({
      category: z.string(),
    });

    const ControlledSelectIntegration = () => {
      const [selectedCategory, setSelectedCategory] = useState('tech');

      const form = useForm({
        resolver: zodResolver(schema),
        defaultValues: { category: selectedCategory },
      });

      const handleSubmit = form.handleSubmit((data) => {
        onSubmitData(data);
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <Select
            name="category"
            label="Category"
            options={[
              { value: 'tech', label: 'Technology' },
              { value: 'design', label: 'Design' },
            ]}
          />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<ControlledSelectIntegration />);

    // Submit with default value
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    // Verify submission
    await waitFor(() => {
      expect(onSubmitData).toHaveBeenCalledWith(
        expect.objectContaining({
          category: 'tech',
        })
      );
    });
  });
});