/**
 * Select + Form Integration Tests
 * 
 * Tests for Select and Form component integration scenarios.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import { Form, FormInput, FormCheckbox } from '../Form';
import Select from '../Select/Select';

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
    });

    const SelectFormIntegration = () => {
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { name: '', category: '' },
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

  it('should handle select search and option selection', async () => {
    const user = userEvent.setup();
    const onSubmitData = vi.fn();
    
    const schema = z.object({
      country: z.string().min(1, 'Country is required'),
    });

    const SelectSearchIntegration = () => {
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { country: '' },
      });

      const handleSubmit = form.handleSubmit((data) => {
        onSubmitData(data);
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <Select
            name="country"
            label="Country"
            searchable
            options={[
              { value: 'us', label: 'United States' },
              { value: 'uk', label: 'United Kingdom' },
              { value: 'ca', label: 'Canada' },
              { value: 'au', label: 'Australia' },
              { value: 'de', label: 'Germany' },
            ]}
          />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<SelectSearchIntegration />);

    // Click select to open dropdown
    const select = screen.getByRole('combobox');
    await user.click(select);

    // Type in search box to filter options
    const searchInput = screen.getByRole('textbox');
    await user.type(searchInput, 'Uni');

    // Verify filtered options
    await waitFor(() => {
      expect(screen.getByText('United States')).toBeInTheDocument();
      expect(screen.getByText('United Kingdom')).toBeInTheDocument();
      expect(screen.queryByText('Canada')).not.toBeInTheDocument();
    });

    // Select an option
    await user.click(screen.getByText('United States'));

    // Submit form
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    // Verify submission
    await waitFor(() => {
      expect(onSubmitData).toHaveBeenCalledWith(
        expect.objectContaining({
          country: 'us',
        })
      );
    });
  });

  it('should handle select with dependent options', async () => {
    const user = userEvent.setup();
    const onSubmitData = vi.fn();
    
    const schema = z.object({
      category: z.string().min(1, 'Category is required'),
      subcategory: z.string().min(1, 'Subcategory is required'),
    });

    const categoryOptions = [
      { value: 'tech', label: 'Technology' },
      { value: 'design', label: 'Design' },
    ];

    const subcategoryOptions: Record<string, Array<{ value: string; label: string }>> = {
      tech: [
        { value: 'frontend', label: 'Frontend' },
        { value: 'backend', label: 'Backend' },
      ],
      design: [
        { value: 'ui', label: 'UI Design' },
        { value: 'ux', label: 'UX Design' },
      ],
    };

    const DependentSelectIntegration = () => {
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { category: '', subcategory: '' },
      });

      const category = form.watch('category');
      const currentSubcategoryOptions = subcategoryOptions[category] || [];

      const handleSubmit = form.handleSubmit((data) => {
        onSubmitData(data);
      });

      return (
        <Form form={form} onSubmit={handleSubmit}>
          <Select
            name="category"
            label="Category"
            options={categoryOptions}
          />
          <Select
            name="subcategory"
            label="Subcategory"
            options={currentSubcategoryOptions}
            disabled={!category}
          />
          <button type="submit">Submit</button>
        </Form>
      );
    };

    render(<DependentSelectIntegration />);

    // Subcategory select should be disabled initially
    const subcategorySelect = screen.getAllByRole('combobox')[1];
    expect(subcategorySelect).toBeDisabled();

    // Select category
    const categorySelect = screen.getAllByRole('combobox')[0];
    await user.click(categorySelect);
    await user.click(screen.getByText('Technology'));

    // Subcategory select should now be enabled
    await waitFor(() => {
      expect(subcategorySelect).not.toBeDisabled();
    });

    // Select subcategory
    await user.click(subcategorySelect);
    await user.click(screen.getByText('Frontend'));

    // Submit form
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    // Verify submission
    await waitFor(() => {
      expect(onSubmitData).toHaveBeenCalledWith(
        expect.objectContaining({
          category: 'tech',
          subcategory: 'frontend',
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