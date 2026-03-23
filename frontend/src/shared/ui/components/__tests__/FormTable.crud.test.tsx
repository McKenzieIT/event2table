/**
 * Form + Table CRUD Integration Tests
 * 
 * Tests for Form adding and editing table data.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import Form from '../Form/Form';
import FormInput from '../Form/FormInput';
import FormSelect from '../Form/FormSelect';
import { Table } from '../Table/Table';
import type { TableColumn } from '../Table/Table.types';

const initialUsers = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'admin' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'user' },
];

const roleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'user', label: 'User' },
];

const userColumns: TableColumn<typeof initialUsers[0]>[] = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'email', header: 'Email' },
  { accessorKey: 'role', header: 'Role' },
];

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
  role: z.string().min(1, 'Role is required'),
});

describe('Form + Table CRUD', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should add new row to table from form submission', async () => {
    const user = userEvent.setup();

    const AddUserTable = () => {
      const [users, setUsers] = useState(initialUsers);
      const form = useForm({
        resolver: zodResolver(schema),
        defaultValues: { name: '', email: '', role: '' },
      });

      const onSubmit = (data: any) => {
        setUsers([...users, { id: users.length + 1, ...data }]);
        form.reset();
      };

      return (
        <div>
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <FormSelect name="role" label="Role" options={roleOptions} />
            <button type="submit">Add User</button>
          </Form>
          <Table data={users} columns={userColumns} pagination={false} />
        </div>
      );
    };

    render(<AddUserTable />);

    await user.type(screen.getByLabelText('Name'), 'Alice');
    await user.type(screen.getByLabelText('Email'), 'alice@example.com');
    await user.selectOptions(screen.getByLabelText('Role'), 'user');
    await user.click(screen.getByRole('button', { name: 'Add User' }));

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });
  });

  it('should update table row on form submission', async () => {
    const user = userEvent.setup();

    const EditableTable = () => {
      const [users, setUsers] = useState(initialUsers);
      const [editingId, setEditingId] = useState<number | null>(null);
      const form = useForm({
        resolver: zodResolver(schema),
        defaultValues: { name: '', email: '', role: '' },
      });

      const startEdit = (userId: number) => {
        const user = users.find((u) => u.id === userId);
        if (user) {
          form.reset(user);
          setEditingId(userId);
        }
      };

      const onSubmit = (data: any) => {
        if (editingId) {
          setUsers(users.map((u) => u.id === editingId ? { ...u, ...data } : u));
          setEditingId(null);
          form.reset();
        }
      };

      const columnsWithActions: TableColumn<typeof initialUsers[0]>[] = [
        ...userColumns,
        {
          id: 'actions',
          header: 'Actions',
          cell: ({ row }) => <button onClick={() => startEdit(row.original.id)}>Edit</button>,
        },
      ];

      return (
        <div>
          {editingId && (
            <Form form={form} onSubmit={onSubmit}>
              <FormInput name="name" label="Name" />
              <FormInput name="email" label="Email" type="email" />
              <FormSelect name="role" label="Role" options={roleOptions} />
              <button type="submit">Save</button>
            </Form>
          )}
          <Table data={users} columns={columnsWithActions} pagination={false} />
        </div>
      );
    };

    render(<EditableTable />);

    await user.click(screen.getAllByText('Edit')[0]);
    const nameInput = screen.getByLabelText('Name');
    await user.clear(nameInput);
    await user.type(nameInput, 'John Updated');
    await user.click(screen.getByRole('button', { name: 'Save' }));

    await waitFor(() => {
      expect(screen.getByText('John Updated')).toBeInTheDocument();
    });
  });
});
