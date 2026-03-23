/**
 * Table + TableFilter + TablePagination Integration Tests
 * 
 * Tests for Table, TableFilter and TablePagination component integration scenarios.
 */

import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React, { useState } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { Table } from '../Table/Table';

describe('Table + TableFilter + TablePagination Integration', () => {
  const mockData = Array.from({ length: 25 }, (_, i) => ({
    id: i + 1,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    status: i % 2 === 0 ? 'Active' : 'Inactive',
  }));

  const columns = [
    { id: 'name', header: 'Name', accessorKey: 'name' },
    { id: 'email', header: 'Email', accessorKey: 'email' },
    { id: 'status', header: 'Status', accessorKey: 'status' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should filter table data and update pagination', async () => {
    const user = userEvent.setup();

    const FilteredPaginatedTable = () => {
      const [filter, setFilter] = useState('');
      const [page, setPage] = useState(1);
      const pageSize = 10;

      const filteredData = mockData.filter(item =>
        item.name.toLowerCase().includes(filter.toLowerCase())
      );

      const paginatedData = filteredData.slice(
        (page - 1) * pageSize,
        page * pageSize
      );

      return (
        <div>
          <input
            placeholder="Filter by name"
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setPage(1);
            }}
            data-testid="filter-input"
          />
          <Table
            data={paginatedData}
            columns={columns}
            pagination={{
              currentPage: page,
              totalPages: Math.ceil(filteredData.length / pageSize),
              pageSize,
              totalItems: filteredData.length,
              onPageChange: setPage,
            }}
          />
        </div>
      );
    };

    render(<FilteredPaginatedTable />);

    // Initially shows 10 items (page 1)
    expect(screen.getByText('User 1')).toBeInTheDocument();
    expect(screen.getByText('User 10')).toBeInTheDocument();
    expect(screen.queryByText('User 11')).not.toBeInTheDocument();

    // Filter to only show users with "User 1" in name
    const filterInput = screen.getByTestId('filter-input');
    await user.type(filterInput, 'User 1');

    await waitFor(() => {
      // Should show only User 1, User 10-19 (items with "1" in name)
      expect(screen.getByText('User 1')).toBeInTheDocument();
      expect(screen.getByText('User 10')).toBeInTheDocument();
    });
  });

  it('should reset pagination when filter changes', async () => {
    const user = userEvent.setup();

    const FilteredPaginatedTable = () => {
      const [filter, setFilter] = useState('');
      const [page, setPage] = useState(2);
      const pageSize = 10;

      const filteredData = mockData.filter(item =>
        item.name.toLowerCase().includes(filter.toLowerCase())
      );

      const paginatedData = filteredData.slice(
        (page - 1) * pageSize,
        page * pageSize
      );

      return (
        <div>
          <input
            placeholder="Filter by name"
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setPage(1);
            }}
            data-testid="filter-input"
          />
          <Table
            data={paginatedData}
            columns={columns}
            pagination={{
              currentPage: page,
              totalPages: Math.ceil(filteredData.length / pageSize),
              pageSize,
              totalItems: filteredData.length,
              onPageChange: setPage,
            }}
          />
        </div>
      );
    };

    render(<FilteredPaginatedTable />);

    // Initially on page 2
    expect(screen.getByText('User 11')).toBeInTheDocument();
    expect(screen.queryByText('User 1')).not.toBeInTheDocument();

    // Apply filter
    const filterInput = screen.getByTestId('filter-input');
    await user.type(filterInput, 'User');

    await waitFor(() => {
      // Should reset to page 1
      expect(screen.getByText('User 1')).toBeInTheDocument();
      expect(screen.queryByText('User 11')).not.toBeInTheDocument();
    });
  });

  it('should handle pagination with empty filter result', async () => {
    const user = userEvent.setup();

    const FilteredPaginatedTable = () => {
      const [filter, setFilter] = useState('');
      const [page, setPage] = useState(1);
      const pageSize = 10;

      const filteredData = mockData.filter(item =>
        item.name.toLowerCase().includes(filter.toLowerCase())
      );

      const paginatedData = filteredData.slice(
        (page - 1) * pageSize,
        page * pageSize
      );

      return (
        <div>
          <input
            placeholder="Filter by name"
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setPage(1);
            }}
            data-testid="filter-input"
          />
          <Table
            data={paginatedData}
            columns={columns}
            pagination={{
              currentPage: page,
              totalPages: Math.ceil(filteredData.length / pageSize),
              pageSize,
              totalItems: filteredData.length,
              onPageChange: setPage,
            }}
          />
        </div>
      );
    };

    render(<FilteredPaginatedTable />);

    // Initially shows data
    expect(screen.getByText('User 1')).toBeInTheDocument();

    // Filter to show no results
    const filterInput = screen.getByTestId('filter-input');
    await user.type(filterInput, 'NonExistent');

    await waitFor(() => {
      expect(screen.queryByText('User 1')).not.toBeInTheDocument();
    });
  });

  it('should update total items count when filtering', async () => {
    const user = userEvent.setup();

    const FilteredPaginatedTable = () => {
      const [filter, setFilter] = useState('');
      const [page, setPage] = useState(1);
      const pageSize = 10;

      const filteredData = mockData.filter(item =>
        item.name.toLowerCase().includes(filter.toLowerCase())
      );

      const paginatedData = filteredData.slice(
        (page - 1) * pageSize,
        page * pageSize
      );

      return (
        <div>
          <input
            placeholder="Filter by name"
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setPage(1);
            }}
            data-testid="filter-input"
          />
          <Table
            data={paginatedData}
            columns={columns}
            pagination={{
              currentPage: page,
              totalPages: Math.ceil(filteredData.length / pageSize),
              pageSize,
              totalItems: filteredData.length,
              onPageChange: setPage,
            }}
          />
          <div data-testid="total-count">Total: {filteredData.length}</div>
        </div>
      );
    };

    render(<FilteredPaginatedTable />);

    // Initially shows 25 total items
    expect(screen.getByTestId('total-count')).toHaveTextContent('Total: 25');

    // Filter to show fewer items
    const filterInput = screen.getByTestId('filter-input');
    await user.type(filterInput, 'User 1');

    await waitFor(() => {
      // Should show reduced count
      const totalCount = screen.getByTestId('total-count');
      expect(totalCount.textContent).not.toBe('Total: 25');
    });
  });

  it('should handle page navigation with filtered data', async () => {
    const user = userEvent.setup();

    const FilteredPaginatedTable = () => {
      const [filter, setFilter] = useState('');
      const [page, setPage] = useState(1);
      const pageSize = 10;

      const filteredData = mockData.filter(item =>
        item.name.toLowerCase().includes(filter.toLowerCase())
      );

      const paginatedData = filteredData.slice(
        (page - 1) * pageSize,
        page * pageSize
      );

      return (
        <div>
          <input
            placeholder="Filter by name"
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setPage(1);
            }}
            data-testid="filter-input"
          />
          <Table
            data={paginatedData}
            columns={columns}
            pagination={{
              currentPage: page,
              totalPages: Math.ceil(filteredData.length / pageSize),
              pageSize,
              totalItems: filteredData.length,
              onPageChange: setPage,
            }}
          />
        </div>
      );
    };

    render(<FilteredPaginatedTable />);

    // Navigate to page 2
    const nextPageButton = screen.getByRole('button', { name: /next|>/i });
    await user.click(nextPageButton);

    await waitFor(() => {
      expect(screen.getByText('User 11')).toBeInTheDocument();
      expect(screen.queryByText('User 1')).not.toBeInTheDocument();
    });

    // Apply filter while on page 2
    const filterInput = screen.getByTestId('filter-input');
    await user.type(filterInput, 'User');

    await waitFor(() => {
      // Should reset to page 1 and show filtered results
      expect(screen.getByText('User 1')).toBeInTheDocument();
    });
  });
});
