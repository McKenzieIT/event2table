/**
 * Form + Table Filtering Integration Tests
 * 
 * Tests for Form filtering table data scenarios.
 */

import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import Form from '../Form/Form';
import FormInput from '../Form/FormInput';
import { Table } from '../Table/Table';
import type { TableColumn } from '../Table/Table.types';

const initialUsers = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'admin' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'user' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'user' },
];

const userColumns: TableColumn<typeof initialUsers[0]>[] = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'email', header: 'Email' },
  { accessorKey: 'role', header: 'Role' },
];

describe('Form + Table Filtering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should filter table data based on form input', async () => {
    const user = userEvent.setup();

    const FilterableTable = () => {
      const form = useForm({ defaultValues: { search: '' } });
      const searchValue = form.watch('search');

      const filteredUsers = initialUsers.filter(
        (u) => u.name.toLowerCase().includes(searchValue.toLowerCase()) ||
                 u.email.toLowerCase().includes(searchValue.toLowerCase())
      );

      return (
        <div>
          <Form form={form} onSubmit={() => {}}>
            <FormInput
              name="search"
              label="Search"
              placeholder="Search by name or email"
            />
          </Form>
          <Table data={filteredUsers} columns={userColumns} pagination={false} />
        </div>
      );
    };

    render(<FilterableTable />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();

    const searchInput = screen.getByPlaceholderText('Search by name or email');
    await user.type(searchInput, 'John');

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });
});
