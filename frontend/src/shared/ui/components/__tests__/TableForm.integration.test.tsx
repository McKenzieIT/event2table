/**
 * Table + Form Integration Tests
 * 
 * Tests for Table and Form component integration scenarios.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Table } from '../Table/Table';
import { Form } from '../Form/Form';
import { FormInput, FormSelect, FormCheckbox } from '../Form/index';

describe('Table + Form Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should update table when form is submitted', async () => {
    const user = userEvent.setup();
    
    const schema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
      status: z.string().min(1, 'Status is required'),
    });

    const TableFormIntegration = () => {
      const [data, setData] = useState([
        { id: 1, name: 'John Doe', email: 'john@example.com', status: 'Active' },
      ]);

      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { name: '', email: '', status: '' },
      });

      const handleSubmit = form.handleSubmit((formData) => {
        const newRecord = {
          id: data.length + 1,
          ...formData,
        };
        setData([...data, newRecord]);
        form.reset();
      });

      const columns = [
        { id: 'name', header: 'Name', accessorKey: 'name' },
        { id: 'email', header: 'Email', accessorKey: 'email' },
        { id: 'status', header: 'Status', accessorKey: 'status' },
      ];

      return (
        <div>
          <Form form={form} onSubmit={handleSubmit}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <FormSelect
              name="status"
              label="Status"
              options={[
                { value: 'Active', label: 'Active' },
                { value: 'Inactive', label: 'Inactive' },
              ]}
            />
            <button type="submit">Add Record</button>
          </Form>
          <Table data={data} columns={columns} />
        </div>
      );
    };

    render(<TableFormIntegration />);

    // Fill form
    await user.type(screen.getByRole('textbox', { name: /name/i }), 'Jane Doe');
    await user.type(screen.getByRole('textbox', { name: /email/i }), 'jane@example.com');
    await user.selectOptions(screen.getByRole('combobox'), 'Active');

    // Submit form
    await user.click(screen.getByRole('button', { name: 'Add Record' }));

    // Verify table updated
    await waitFor(() => {
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
      expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    });
  });

  it('should handle table data editing with form', async () => {
    const user = userEvent.setup();
    
    const schema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
    });

    const TableEditIntegration = () => {
      const [data, setData] = useState([
        { id: 1, name: 'John Doe', email: 'john@example.com' },
      ]);
      const [editingId, setEditingId] = useState<number | null>(null);

      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
      });

      const handleEdit = (record: typeof data[0]) => {
        setEditingId(record.id);
        form.reset(record);
      };

      const handleSubmit = form.handleSubmit((formData) => {
        setData(data.map(item => 
          item.id === editingId ? { ...item, ...formData } : item
        ));
        setEditingId(null);
        form.reset();
      });

      const columns = [
        { 
          id: 'name', 
          header: 'Name', 
          accessorKey: 'name',
          cell: ({ row }: any) => (
            <span>{row.original.name}</span>
          )
        },
        { 
          id: 'actions', 
          header: 'Actions', 
          cell: ({ row }: any) => (
            <button onClick={() => handleEdit(row.original)}>Edit</button>
          )
        },
      ];

      return (
        <div>
          {editingId && (
            <Form form={form} onSubmit={handleSubmit}>
              <FormInput name="name" label="Name" />
              <FormInput name="email" label="Email" type="email" />
              <button type="submit">Update</button>
              <button type="button" onClick={() => setEditingId(null)}>Cancel</button>
            </Form>
          )}
          <Table data={data} columns={columns} />
        </div>
      );
    };

    render(<TableEditIntegration />);

    // Click edit button
    await user.click(screen.getByRole('button', { name: 'Edit' }));

    // Verify form is populated
    const nameInput = screen.getByRole('textbox', { name: /name/i });
    expect(nameInput).toHaveValue('John Doe');

    // Update form
    await user.clear(nameInput);
    await user.type(nameInput, 'John Smith');
    await user.click(screen.getByRole('button', { name: 'Update' }));

    // Verify table updated
    await waitFor(() => {
      expect(screen.getByText('John Smith')).toBeInTheDocument();
    });
  });

  it('should handle form validation errors before updating table', async () => {
    const user = userEvent.setup();
    
    const schema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
    });

    const TableValidationIntegration = () => {
      const [data, setData] = useState([
        { id: 1, name: 'John Doe', email: 'john@example.com' },
      ]);

      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { name: '', email: '' },
      });

      const handleSubmit = form.handleSubmit((formData) => {
        const newRecord = {
          id: data.length + 1,
          ...formData,
        };
        setData([...data, newRecord]);
        form.reset();
      });

      const columns = [
        { id: 'name', header: 'Name', accessorKey: 'name' },
        { id: 'email', header: 'Email', accessorKey: 'email' },
      ];

      return (
        <div>
          <Form form={form} onSubmit={handleSubmit}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <button type="submit">Add Record</button>
          </Form>
          <Table data={data} columns={columns} />
        </div>
      );
    };

    render(<TableValidationIntegration />);

    // Submit without filling form
    await user.click(screen.getByRole('button', { name: 'Add Record' }));

    // Verify errors shown
    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
    });

    // Verify table not updated
    expect(screen.queryByText('John Doe')).toBeInTheDocument();
    expect(screen.getAllByText('John Doe')).toHaveLength(1);
  });

  it('should handle empty table state with form', () => {
    const schema = z.object({
      name: z.string().min(1, 'Name is required'),
    });

    const EmptyTableIntegration = () => {
      const [data, setData] = useState<any[]>([]);

      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
        defaultValues: { name: '' },
      });

      const handleSubmit = form.handleSubmit((formData) => {
        setData([...data, { id: 1, ...formData }]);
        form.reset();
      });

      const columns = [
        { id: 'name', header: 'Name', accessorKey: 'name' },
      ];

      return (
        <div>
          <Form form={form} onSubmit={handleSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Add Record</button>
          </Form>
          <Table data={data} columns={columns} />
        </div>
      );
    };

    render(<EmptyTableIntegration />);

    // Verify table renders with empty data
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
  });
});