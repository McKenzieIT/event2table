import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@test/test-utils';
import { Table } from '../Table';
import type { TableColumn } from '../Table.types';

interface TestData {
  id: number;
  name: string;
  age: number;
  email: string;
  department: string;
  salary: number;
}

describe('Table Column Grouping', () => {
  const groupedColumns: TableColumn<TestData>[] = [
    {
      id: 'info',
      header: 'Personal Information',
      columns: [
        {
          id: 'name',
          accessorKey: 'name',
          header: 'Name',
        },
        {
          id: 'age',
          accessorKey: 'age',
          header: 'Age',
        },
      ],
    },
    {
      id: 'contact',
      header: 'Contact',
      columns: [
        {
          id: 'email',
          accessorKey: 'email',
          header: 'Email',
        },
      ],
    },
    {
      id: 'work',
      header: 'Work',
      columns: [
        {
          id: 'department',
          accessorKey: 'department',
          header: 'Department',
        },
        {
          id: 'salary',
          accessorKey: 'salary',
          header: 'Salary',
        },
      ],
    },
  ];

  const testData: TestData[] = [
    { id: 1, name: 'John Doe', age: 30, email: 'john@example.com', department: 'Engineering', salary: 80000 },
    { id: 2, name: 'Jane Smith', age: 25, email: 'jane@example.com', department: 'Marketing', salary: 60000 },
  ];

  it('should render grouped column headers', () => {
    render(
      <Table
        data={testData}
        columns={groupedColumns}
      />
    );

    // Check for group headers
    expect(screen.getByText('Personal Information')).toBeInTheDocument();
    expect(screen.getByText('Contact')).toBeInTheDocument();
    expect(screen.getByText('Work')).toBeInTheDocument();
  });

  it('should render nested column headers', () => {
    render(
      <Table
        data={testData}
        columns={groupedColumns}
      />
    );

    // Check for nested column headers
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Age')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('Department')).toBeInTheDocument();
    expect(screen.getByText('Salary')).toBeInTheDocument();
  });

  it('should render data cells correctly with grouped columns', () => {
    render(
      <Table
        data={testData}
        columns={groupedColumns}
      />
    );

    // Check for data cells
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(screen.getByText('Engineering')).toBeInTheDocument();
    expect(screen.getByText('80000')).toBeInTheDocument();

    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('25')).toBeInTheDocument();
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    expect(screen.getByText('Marketing')).toBeInTheDocument();
    expect(screen.getByText('60000')).toBeInTheDocument();
  });

  it('should apply correct CSS classes to group headers', () => {
    const { container } = render(
      <Table
        data={testData}
        columns={groupedColumns}
      />
    );

    // Find group header cells
    const groupHeaders = container.querySelectorAll('.table-th--group');
    expect(groupHeaders.length).toBeGreaterThan(0);
  });

  it('should handle mixed grouped and ungrouped columns', () => {
    const mixedColumns: TableColumn<TestData>[] = [
      {
        id: 'info',
        header: 'Personal Information',
        columns: [
          {
            id: 'name',
            accessorKey: 'name',
            header: 'Name',
          },
          {
            id: 'age',
            accessorKey: 'age',
            header: 'Age',
          },
        ],
      },
      {
        id: 'email',
        accessorKey: 'email',
        header: 'Email',
      },
    ];

    render(
      <Table
        data={testData}
        columns={mixedColumns}
      />
    );

    // Check for grouped header
    expect(screen.getByText('Personal Information')).toBeInTheDocument();
    
    // Check for ungrouped header - use getAllByText since Email appears in header and data
    const emailHeaders = screen.getAllByText('Email');
    expect(emailHeaders.length).toBeGreaterThan(0);
    
    // Check for nested headers
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Age')).toBeInTheDocument();
  });

  it('should support sorting within grouped columns', () => {
    const columnsWithSorting: TableColumn<TestData>[] = [
      {
        id: 'info',
        header: 'Personal Information',
        columns: [
          {
            id: 'name',
            accessorKey: 'name',
            header: 'Name',
            enableSorting: true,
          },
          {
            id: 'age',
            accessorKey: 'age',
            header: 'Age',
            enableSorting: true,
          },
        ],
      },
    ];

    render(
      <Table
        data={testData}
        columns={columnsWithSorting}
        enableSorting
      />
    );

    // Check that sortable columns have the sortable class
    const nameHeader = screen.getByText('Name').closest('th');
    const ageHeader = screen.getByText('Age').closest('th');
    
    expect(nameHeader).toHaveClass('table-th--sortable');
    expect(ageHeader).toHaveClass('table-th--sortable');
  });

  it('should handle empty groups gracefully', () => {
    const columnsWithEmptyGroup: TableColumn<TestData>[] = [
      {
        id: 'empty-group',
        header: 'Empty Group',
        columns: [],
      },
      {
        id: 'name',
        accessorKey: 'name',
        header: 'Name',
      },
    ];

    // Should not throw error
    expect(() => {
      render(
        <Table
          data={testData}
          columns={columnsWithEmptyGroup}
        />
      );
    }).not.toThrow();
  });

  it('should support nested grouping (multi-level)', () => {
    const nestedColumns: TableColumn<TestData>[] = [
      {
        id: 'personal',
        header: 'Personal',
        columns: [
          {
            id: 'basic-info',
            header: 'Basic Info',
            columns: [
              {
                id: 'name',
                accessorKey: 'name',
                header: 'Name',
              },
              {
                id: 'age',
                accessorKey: 'age',
                header: 'Age',
              },
            ],
          },
        ],
      },
    ];

    render(
      <Table
        data={testData}
        columns={nestedColumns}
      />
    );

    // Check for multi-level headers
    expect(screen.getByText('Personal')).toBeInTheDocument();
    expect(screen.getByText('Basic Info')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Age')).toBeInTheDocument();
  });
});
