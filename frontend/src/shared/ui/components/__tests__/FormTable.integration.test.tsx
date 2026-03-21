/**
 * Form + Table Integration Tests
 * 
 * Comprehensive integration tests for Form and Table components
 * Testing real-world user workflows and component interactions
 * 
 * Test Scenarios:
 * 1. Form filtering table data
 * 2. Form adding data to table
 * 3. Form editing table row
 * 4. Form deleting table row
 * 5. Table row selection with form
 * 6. Form validation before table operations
 * 7. Complex workflows with multiple tables and forms
 * 8. Edge cases and error handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Form from '../Form/Form';
import FormInput from '../Form/FormInput';
import FormSelect from '../Form/FormSelect';
import Table from '../Table';

// Mock data
const initialUsers = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'admin' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'user' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'user' },
];

const roleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'user', label: 'User' },
  { value: 'guest', label: 'Guest' },
];

describe('Form + Table Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ========== Form Filtering Table Data ==========

  describe('Form Filtering Table Data', () => {
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
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Email</Table.Head>
                  <Table.Head>Role</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {filteredUsers.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                    <Table.Cell>{user.email}</Table.Cell>
                    <Table.Cell>{user.role}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<FilterableTable />);

      // Initially shows all users
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('Bob Johnson')).toBeInTheDocument();

      // Filter by name
      const searchInput = screen.getByPlaceholderText('Search by name or email');
      await user.type(searchInput, 'John');

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
        expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
      });
    });

    it('should filter by role using form select', async () => {
      const user = userEvent.setup();

      const RoleFilterableTable = () => {
        const [roleFilter, setRoleFilter] = useState('');
        const form = useForm({ defaultValues: { role: '' } });

        const filteredUsers = roleFilter
          ? initialUsers.filter((u) => u.role === roleFilter)
          : initialUsers;

        return (
          <div>
            <Form form={form} onSubmit={() => {}}>
              <FormSelect
                name="role"
                label="Filter by Role"
                options={[
                  { value: '', label: 'All Roles' },
                  ...roleOptions,
                ]}
                onChange={(e) => setRoleFilter(e.target.value)}
              />
            </Form>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Email</Table.Head>
                  <Table.Head>Role</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {filteredUsers.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                    <Table.Cell>{user.email}</Table.Cell>
                    <Table.Cell>{user.role}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<RoleFilterableTable />);

      // Initially shows all users
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();

      // Filter by admin role
      const roleSelect = screen.getByLabelText('Filter by Role');
      await user.selectOptions(roleSelect, 'admin');

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
        expect(screen.queryByText('Bob Johnson')).not.toBeInTheDocument();
      });
    });
  });

  // ========== Form Adding Data to Table ==========

  describe('Form Adding Data to Table', () => {
    const schema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
      role: z.string().min(1, 'Role is required'),
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
          const newUser = {
            id: users.length + 1,
            ...data,
          };
          setUsers([...users, newUser]);
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
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Email</Table.Head>
                  <Table.Head>Role</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {users.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                    <Table.Cell>{user.email}</Table.Cell>
                    <Table.Cell>{user.role}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<AddUserTable />);

      // Initially shows 3 users
      expect(screen.getAllByRole('row').length - 1).toBe(3); // -1 for header row

      // Fill form
      await user.type(screen.getByLabelText('Name'), 'Alice Williams');
      await user.type(screen.getByLabelText('Email'), 'alice@example.com');
      await user.selectOptions(screen.getByLabelText('Role'), 'user');

      // Submit form
      await user.click(screen.getByRole('button', { name: 'Add User' }));

      // Should now show 4 users
      await waitFor(() => {
        expect(screen.getByText('Alice Williams')).toBeInTheDocument();
        expect(screen.getByText('alice@example.com')).toBeInTheDocument();
      });

      // Form should be reset
      expect(screen.getByLabelText('Name')).toHaveValue('');
    });

    it('should not add row if form validation fails', async () => {
      const user = userEvent.setup();

      const AddUserTable = () => {
        const [users, setUsers] = useState(initialUsers);
        const form = useForm({
          resolver: zodResolver(schema),
          defaultValues: { name: '', email: '', role: '' },
        });

        const onSubmit = (data: any) => {
          const newUser = {
            id: users.length + 1,
            ...data,
          };
          setUsers([...users, newUser]);
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
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Email</Table.Head>
                  <Table.Head>Role</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {users.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                    <Table.Cell>{user.email}</Table.Cell>
                    <Table.Cell>{user.role}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<AddUserTable />);

      // Initially shows 3 users
      expect(screen.getAllByRole('row').length - 1).toBe(3);

      // Submit empty form
      await user.click(screen.getByRole('button', { name: 'Add User' }));

      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.getByText('Invalid email')).toBeInTheDocument();
        expect(screen.getByText('Role is required')).toBeInTheDocument();
      });

      // Should still show 3 users
      expect(screen.getAllByRole('row').length - 1).toBe(3);
    });
  });

  // ========== Form Editing Table Row ==========

  describe('Form Editing Table Row', () => {
    const schema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
      role: z.string().min(1, 'Role is required'),
    });

    it('should populate form with row data when editing', async () => {
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
            setUsers(users.map((u) =>
              u.id === editingId ? { ...u, ...data } : u
            ));
            setEditingId(null);
            form.reset();
          }
        };

        return (
          <div>
            {editingId && (
              <Form form={form} onSubmit={onSubmit}>
                <FormInput name="name" label="Name" />
                <FormInput name="email" label="Email" type="email" />
                <FormSelect name="role" label="Role" options={roleOptions} />
                <button type="submit">Save</button>
                <button type="button" onClick={() => setEditingId(null)}>Cancel</button>
              </Form>
            )}
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Email</Table.Head>
                  <Table.Head>Role</Table.Head>
                  <Table.Head>Actions</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {users.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                    <Table.Cell>{user.email}</Table.Cell>
                    <Table.Cell>{user.role}</Table.Cell>
                    <Table.Cell>
                      <button onClick={() => startEdit(user.id)}>Edit</button>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<EditableTable />);

      // Click edit on first row
      await user.click(screen.getAllByText('Edit')[0]);

      // Form should be populated with user data
      expect(screen.getByLabelText('Name')).toHaveValue('John Doe');
      expect(screen.getByLabelText('Email')).toHaveValue('john@example.com');
      expect(screen.getByLabelText('Role')).toHaveValue('admin');
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
            setUsers(users.map((u) =>
              u.id === editingId ? { ...u, ...data } : u
            ));
            setEditingId(null);
            form.reset();
          }
        };

        return (
          <div>
            {editingId && (
              <Form form={form} onSubmit={onSubmit}>
                <FormInput name="name" label="Name" />
                <FormInput name="email" label="Email" type="email" />
                <FormSelect name="role" label="Role" options={roleOptions} />
                <button type="submit">Save</button>
                <button type="button" onClick={() => setEditingId(null)}>Cancel</button>
              </Form>
            )}
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Email</Table.Head>
                  <Table.Head>Role</Table.Head>
                  <Table.Head>Actions</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {users.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                    <Table.Cell>{user.email}</Table.Cell>
                    <Table.Cell>{user.role}</Table.Cell>
                    <Table.Cell>
                      <button onClick={() => startEdit(user.id)}>Edit</button>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<EditableTable />);

      // Click edit on first row
      await user.click(screen.getAllByText('Edit')[0]);

      // Update name
      const nameInput = screen.getByLabelText('Name');
      await user.clear(nameInput);
      await user.type(nameInput, 'John Updated');

      // Submit form
      await user.click(screen.getByRole('button', { name: 'Save' }));

      // Table should be updated
      await waitFor(() => {
        expect(screen.getByText('John Updated')).toBeInTheDocument();
        expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
      });
    });
  });

  // ========== Table Row Selection with Form ==========

  describe('Table Row Selection with Form', () => {
    it('should show selected row data in form', async () => {
      const user = userEvent.setup();

      const SelectableTable = () => {
        const [selectedId, setSelectedId] = useState<number | null>(null);
        const form = useForm({
          defaultValues: { name: '', email: '', role: '' },
        });

        const handleRowClick = (userId: number) => {
          const user = initialUsers.find((u) => u.id === userId);
          if (user) {
            setSelectedId(userId);
            form.reset(user);
          }
        };

        return (
          <div>
            <Form form={form} onSubmit={() => {}}>
              <FormInput name="name" label="Name" disabled />
              <FormInput name="email" label="Email" type="email" disabled />
              <FormInput name="role" label="Role" disabled />
            </Form>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Email</Table.Head>
                  <Table.Head>Role</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {initialUsers.map((user) => (
                  <Table.Row
                    key={user.id}
                    onClick={() => handleRowClick(user.id)}
                  >
                    <Table.Cell>{user.name}</Table.Cell>
                    <Table.Cell>{user.email}</Table.Cell>
                    <Table.Cell>{user.role}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<SelectableTable />);

      // Click on first row
      await user.click(screen.getByText('John Doe'));

      // Form should show selected user data
      expect(screen.getByLabelText('Name')).toHaveValue('John Doe');
      expect(screen.getByLabelText('Email')).toHaveValue('john@example.com');
      expect(screen.getByLabelText('Role')).toHaveValue('admin');
    });

    it('should highlight selected row', async () => {
      const user = userEvent.setup();

      const SelectableTable = () => {
        const [selectedId, setSelectedId] = useState<number | null>(null);
        const form = useForm({
          defaultValues: { name: '', email: '', role: '' },
        });

        const handleRowClick = (userId: number) => {
          const user = initialUsers.find((u) => u.id === userId);
          if (user) {
            setSelectedId(userId);
            form.reset(user);
          }
        };

        return (
          <div>
            <Form form={form} onSubmit={() => {}}>
              <FormInput name="name" label="Name" disabled />
            </Form>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {initialUsers.map((user) => (
                  <Table.Row
                    key={user.id}
                    onClick={() => handleRowClick(user.id)}
                    style={{
                      backgroundColor: selectedId === user.id ? '#e0f2fe' : undefined,
                    }}
                  >
                    <Table.Cell>{user.name}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<SelectableTable />);

      // Click on first row
      const firstRow = screen.getByText('John Doe').closest('tr');
      await user.click(firstRow!);

      // Row should be highlighted
      await waitFor(() => {
        expect(firstRow).toHaveStyle({ backgroundColor: '#e0f2fe' });
      });
    });
  });

  // ========== Complex Workflows ==========

  describe('Complex Workflows', () => {
    it('should handle filter, add, and edit in sequence', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        name: z.string().min(1),
        email: z.string().email(),
        role: z.string().min(1),
      });

      const ComplexTable = () => {
        const [users, setUsers] = useState(initialUsers);
        const [editingId, setEditingId] = useState<number | null>(null);
        const filterForm = useForm({ defaultValues: { search: '' } });
        const editForm = useForm({
          resolver: zodResolver(schema),
          defaultValues: { name: '', email: '', role: '' },
        });

        const searchValue = filterForm.watch('search');

        const filteredUsers = users.filter(
          (u) => u.name.toLowerCase().includes(searchValue.toLowerCase())
        );

        const startEdit = (userId: number) => {
          const user = users.find((u) => u.id === userId);
          if (user) {
            editForm.reset(user);
            setEditingId(userId);
          }
        };

        const onSubmit = (data: any) => {
          if (editingId) {
            setUsers(users.map((u) =>
              u.id === editingId ? { ...u, ...data } : u
            ));
            setEditingId(null);
            editForm.reset();
          }
        };

        return (
          <div>
            <Form form={filterForm} onSubmit={() => {}}>
              <FormInput
                name="search"
                label="Search"
              />
            </Form>
            {editingId && (
              <Form form={editForm} onSubmit={onSubmit}>
                <FormInput name="name" label="Name" />
                <FormInput name="email" label="Email" type="email" />
                <FormSelect name="role" label="Role" options={roleOptions} />
                <button type="submit">Save</button>
                <button type="button" onClick={() => setEditingId(null)}>Cancel</button>
              </Form>
            )}
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Email</Table.Head>
                  <Table.Head>Role</Table.Head>
                  <Table.Head>Actions</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {filteredUsers.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                    <Table.Cell>{user.email}</Table.Cell>
                    <Table.Cell>{user.role}</Table.Cell>
                    <Table.Cell>
                      <button onClick={() => startEdit(user.id)}>Edit</button>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<ComplexTable />);

      // Filter by "John"
      const searchInput = screen.getByLabelText('Search');
      await user.type(searchInput, 'John');

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
      });

      // Edit John Doe
      await user.click(screen.getAllByText('Edit')[0]);

      // Update name
      const nameInput = screen.getByLabelText('Name');
      await user.clear(nameInput);
      await user.type(nameInput, 'John Updated');

      // Submit
      await user.click(screen.getByRole('button', { name: 'Save' }));

      // Clear filter
      await user.clear(searchInput);

      // Should show updated name
      await waitFor(() => {
        expect(screen.getByText('John Updated')).toBeInTheDocument();
        expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
      });
    });
  });

  // ========== Edge Cases ==========

  describe('Edge Cases', () => {
    it('should handle empty table with form', () => {
      const EmptyTableWithForm = () => {
        const [users, setUsers] = useState<any[]>([]);
        const form = useForm({ defaultValues: { name: '' } });

        const onSubmit = (data: any) => {
          setUsers([...users, { id: 1, ...data }]);
          form.reset();
        };

        return (
          <div>
            <Form form={form} onSubmit={onSubmit}>
              <FormInput name="name" label="Name" />
              <button type="submit">Add</button>
            </Form>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {users.length === 0 && (
                  <Table.Row>
                    <Table.Cell colSpan={1}>No data</Table.Cell>
                  </Table.Row>
                )}
                {users.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<EmptyTableWithForm />);

      expect(screen.getByText('No data')).toBeInTheDocument();
    });

    it('should handle form submission with empty table', async () => {
      const user = userEvent.setup();

      const EmptyTableWithForm = () => {
        const [users, setUsers] = useState<any[]>([]);
        const form = useForm({ defaultValues: { name: '' } });

        const onSubmit = (data: any) => {
          setUsers([...users, { id: Date.now(), ...data }]);
          form.reset();
        };

        return (
          <div>
            <Form form={form} onSubmit={onSubmit}>
              <FormInput name="name" label="Name" />
              <button type="submit">Add</button>
            </Form>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>Name</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {users.length === 0 && (
                  <Table.Row>
                    <Table.Cell colSpan={1}>No data</Table.Cell>
                  </Table.Row>
                )}
                {users.map((user) => (
                  <Table.Row key={user.id}>
                    <Table.Cell>{user.name}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      };

      render(<EmptyTableWithForm />);

      expect(screen.getByText('No data')).toBeInTheDocument();

      // Add data
      await user.type(screen.getByLabelText('Name'), 'Test User');
      await user.click(screen.getByRole('button', { name: 'Add' }));

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument();
        expect(screen.queryByText('No data')).not.toBeInTheDocument();
      });
    });
  });
});
