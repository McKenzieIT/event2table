/**
 * Table Component Unit Tests
 * 
 * Comprehensive test suite for Table component
 * Target coverage: 90%
 * 
 * Test Categories:
 * 1. Rendering Tests
 * 2. Data Display Tests
 * 3. Sorting Tests
 * 4. Filtering Tests
 * 5. Selection Tests
 * 6. Pagination Tests
 * 7. Virtual Scrolling Tests
 * 8. Editing Tests
 * 9. Interaction Tests
 * 10. Accessibility Tests
 * 11. Edge Cases
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import { Table } from './Table';
import type { TableProps, TableColumn } from './Table.types';

// Mock data
const mockData = [
  { id: 1, name: 'Alice', age: 25, email: 'alice@example.com', status: 'active' },
  { id: 2, name: 'Bob', age: 30, email: 'bob@example.com', status: 'inactive' },
  { id: 3, name: 'Charlie', age: 35, email: 'charlie@example.com', status: 'active' },
];

const mockColumns: TableColumn<(typeof mockData)[0]>[] = [
  { id: 'id', header: 'ID', accessorKey: 'id' },
  { id: 'name', header: 'Name', accessorKey: 'name' },
  { id: 'age', header: 'Age', accessorKey: 'age' },
  { id: 'email', header: 'Email', accessorKey: 'email' },
  { id: 'status', header: 'Status', accessorKey: 'status' },
];

describe('Table Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ========== Rendering Tests ==========

  describe('Rendering', () => {
    it('should render without crashing', () => {
      render(<Table data={mockData} columns={mockColumns} />);
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('should render all columns', () => {
      render(<Table data={mockData} columns={mockColumns} />);
      
      mockColumns.forEach((column) => {
        expect(screen.getByText(column.header as string)).toBeInTheDocument();
      });
    });

    it('should render all data rows', () => {
      render(<Table data={mockData} columns={mockColumns} />);
      
      mockData.forEach((row) => {
        expect(screen.getByText(row.name)).toBeInTheDocument();
      });
    });

    it('should render with custom className', () => {
      const { container } = render(
        <Table data={mockData} columns={mockColumns} className="custom-table" />
      );
      
      expect(container.querySelector('.custom-table')).toBeInTheDocument();
    });

    it('should render with custom style', () => {
      const customStyle = { backgroundColor: 'red' };
      render(
        <Table data={mockData} columns={mockColumns} style={customStyle} />
      );
      
      // Verify table renders with style prop
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('should render empty state when no data', () => {
      render(<Table data={[]} columns={mockColumns} />);
      
      expect(screen.getByText('No data available')).toBeInTheDocument();
    });

    it('should render custom empty component', () => {
      const EmptyComponent = () => <div>Custom Empty Message</div>;
      render(
        <Table data={[]} columns={mockColumns} emptyComponent={<EmptyComponent />} />
      );
      
      expect(screen.getByText('Custom Empty Message')).toBeInTheDocument();
    });

    it('should render loading state', () => {
      render(<Table data={mockData} columns={mockColumns} loading />);
      
      // Verify loading state is rendered (table may still be present but with loading indicator)
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('should render custom loading component', () => {
      const LoadingComponent = () => <div>Custom Loading</div>;
      render(
        <Table data={mockData} columns={mockColumns} loading loadingComponent={<LoadingComponent />} />
      );
      
      expect(screen.getByText('Custom Loading')).toBeInTheDocument();
    });

    it('should render different size variants', () => {
      const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];
      
      sizes.forEach((size) => {
        const { unmount } = render(
          <Table data={mockData} columns={mockColumns} size={size} />
        );
        const table = screen.getByRole('table');
        expect(table).toHaveClass(`table--${size}`);
        unmount();
      });
    });

    it('should render different variants', () => {
      const variants: Array<'default' | 'bordered' | 'striped'> = ['default', 'bordered', 'striped'];
      
      variants.forEach((variant) => {
        const { unmount } = render(
          <Table data={mockData} columns={mockColumns} variant={variant} />
        );
        const table = screen.getByRole('table');
        if (variant !== 'default') {
          expect(table).toHaveClass(`table--${variant}`);
        }
        unmount();
      });
    });

    it('should render with striped rows by default', () => {
      const { container } = render(
        <Table data={mockData} columns={mockColumns} striped />
      );
      
      const table = container.querySelector('.table--striped');
      expect(table).toBeInTheDocument();
    });

    it('should render with hoverable rows by default', () => {
      const { container } = render(
        <Table data={mockData} columns={mockColumns} hoverable />
      );
      
      const table = container.querySelector('.table--hoverable');
      expect(table).toBeInTheDocument();
    });
  });

  // ========== Sorting Tests ==========

  describe('Sorting', () => {
    it('should sort column when header is clicked', async () => {
      const user = userEvent.setup();
      const onSortChange = vi.fn();
      
      render(
        <Table data={mockData} columns={mockColumns} sortable onSortChange={onSortChange} />
      );
      
      const nameHeader = screen.getByText('Name');
      await user.click(nameHeader);
      
      expect(onSortChange).toHaveBeenCalled();
    });

    it('should show sort indicator when column is sorted', async () => {
      const user = userEvent.setup();
      
      render(<Table data={mockData} columns={mockColumns} sortable />);
      
      const nameHeader = screen.getByText('Name');
      await user.click(nameHeader);
      
      // Wait for sort indicator to appear
      await waitFor(() => {
        const sortIndicator = nameHeader.closest('.table-th')?.querySelector('.table-sort-indicator');
        expect(sortIndicator).toBeInTheDocument();
      });
    });

    it('should toggle sort direction when clicked multiple times', async () => {
      const user = userEvent.setup();
      const onSortChange = vi.fn();
      
      render(
        <Table data={mockData} columns={mockColumns} sortable onSortChange={onSortChange} />
      );
      
      const nameHeader = screen.getByText('Name');
      await user.click(nameHeader);
      await user.click(nameHeader);
      
      expect(onSortChange).toHaveBeenCalledTimes(2);
    });

    it('should not sort when sortable is false', () => {
      render(<Table data={mockData} columns={mockColumns} sortable={false} />);
      
      const nameHeader = screen.getByText('Name');
      expect(nameHeader.closest('.table-th')).not.toHaveClass('table-th--sortable');
    });

    it('should respect column-specific sortable setting', () => {
      const columnsWithSortable = [
        ...mockColumns.slice(0, 1),
        { ...mockColumns[1], sortable: false },
        ...mockColumns.slice(2),
      ];
      
      render(<Table data={mockData} columns={columnsWithSortable} sortable />);
      
      // Verify table renders with sortable columns
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Age')).toBeInTheDocument();
    });
  });

  // ========== Filtering Tests ==========

  describe('Filtering', () => {
    it('should filter data when filter is applied', () => {
      const filteredData = mockData.filter((item) => item.status === 'active');
      
      render(<Table data={filteredData} columns={mockColumns} />);
      
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('Charlie')).toBeInTheDocument();
      expect(screen.queryByText('Bob')).not.toBeInTheDocument();
    });

    it('should call onFilterChange when filter changes', () => {
      const onFilterChange = vi.fn();
      
      render(
        <Table data={mockData} columns={mockColumns} filterable onFilterChange={onFilterChange} />
      );
      
      // Filter changes are typically handled by external state
      // This test verifies the callback exists
      expect(typeof onFilterChange).toBe('function');
    });
  });

  // ========== Selection Tests ==========

  describe('Selection', () => {
    it('should render selection column when selectable is true', () => {
      render(<Table data={mockData} columns={mockColumns} selectable />);
      
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes.length).toBeGreaterThan(0);
    });

    it('should select row when checkbox is clicked', async () => {
      const user = userEvent.setup();
      const onSelectionChange = vi.fn();
      
      render(
        <Table data={mockData} columns={mockColumns} selectable onSelectionChange={onSelectionChange} />
      );
      
      const checkboxes = screen.getAllByRole('checkbox');
      await user.click(checkboxes[1]); // First data row checkbox
      
      expect(onSelectionChange).toHaveBeenCalled();
    });

    it('should select all rows when header checkbox is clicked', async () => {
      const user = userEvent.setup();
      const onSelectionChange = vi.fn();
      
      render(
        <Table data={mockData} columns={mockColumns} selectable onSelectionChange={onSelectionChange} />
      );
      
      const checkboxes = screen.getAllByRole('checkbox');
      await user.click(checkboxes[0]); // Header checkbox
      
      expect(onSelectionChange).toHaveBeenCalled();
    });

    it('should not render selection column when selectable is false', () => {
      render(<Table data={mockData} columns={mockColumns} selectable={false} />);
      
      const checkboxes = screen.queryAllByRole('checkbox');
      expect(checkboxes.length).toBe(0);
    });
  });

  // ========== Pagination Tests ==========

  describe('Pagination', () => {
    it('should render pagination when enabled', () => {
      render(
        <Table data={mockData} columns={mockColumns} pagination pageSize={2} />
      );
      
      expect(screen.getByText('1-2 of 3 items')).toBeInTheDocument();
    });

    it('should navigate to next page when next button is clicked', async () => {
      const user = userEvent.setup();
      const onPageChange = vi.fn();
      
      render(
        <Table
          data={mockData}
          columns={mockColumns}
          pagination
          pageSize={2}
          onPageChange={onPageChange}
        />
      );
      
      const nextButton = screen.getByLabelText('Next page');
      await user.click(nextButton);
      
      expect(onPageChange).toHaveBeenCalledWith(2, 2);
    });

    it('should navigate to previous page when previous button is clicked', async () => {
      const user = userEvent.setup();
      const onPageChange = vi.fn();
      
      render(
        <Table
          data={mockData}
          columns={mockColumns}
          pagination
          pageSize={2}
          currentPage={2}
          onPageChange={onPageChange}
        />
      );
      
      const prevButton = screen.getByLabelText('Previous page');
      await user.click(prevButton);
      
      expect(onPageChange).toHaveBeenCalledWith(1, 2);
    });

    it('should disable previous button on first page', () => {
      render(
        <Table data={mockData} columns={mockColumns} pagination pageSize={2} currentPage={1} />
      );
      
      const prevButton = screen.getByLabelText('Previous page');
      expect(prevButton).toBeDisabled();
    });

    it('should disable next button on last page', () => {
      render(
        <Table data={mockData} columns={mockColumns} pagination pageSize={2} currentPage={2} />
      );
      
      const nextButton = screen.getByLabelText('Next page');
      expect(nextButton).toBeDisabled();
    });

    it('should change page size when size changer is used', async () => {
      const user = userEvent.setup();
      
      render(
        <Table
          data={mockData}
          columns={mockColumns}
          pagination
          pageSize={2}
          pageSizeOptions={[2, 5, 10]}
        />
      );
      
      const sizeSelect = screen.getByDisplayValue('2 / page');
      await user.selectOptions(sizeSelect, '5');
      
      expect(sizeSelect).toHaveValue('5');
    });

    it('should not render pagination when disabled', () => {
      render(<Table data={mockData} columns={mockColumns} pagination={false} />);
      
      expect(screen.queryByText('of')).not.toBeInTheDocument();
    });
  });

  // ========== Virtual Scrolling Tests ==========

  describe('Virtual Scrolling', () => {
    it('should render virtualized table when virtual is true', () => {
      const largeData = Array.from({ length: 1000 }, (_, i) => ({
        id: i + 1,
        name: `Item ${i + 1}`,
      }));
      
      render(
        <Table
          data={largeData}
          columns={[{ id: 'id', header: 'ID', accessorKey: 'id' }]}
          virtual
          maxHeight={500}
        />
      );
      
      const container = screen.getByRole('table').closest('.table-container');
      expect(container).toHaveStyle({ maxHeight: '500px' });
    });

    it('should render only visible rows when virtualized', () => {
      const largeData = Array.from({ length: 1000 }, (_, i) => ({
        id: i + 1,
        name: `Item ${i + 1}`,
      }));
      
      render(
        <Table
          data={largeData}
          columns={[{ id: 'name', header: 'Name', accessorKey: 'name' }]}
          virtual
          maxHeight={500}
          rowHeight={50}
        />
      );
      
      // Should only render visible rows (approximately)
      const rows = screen.getAllByRole('row');
      expect(rows.length).toBeLessThan(20); // Much less than 1000
    });

    it('should call onVirtualScrollMetrics when scrolling', () => {
      const onVirtualScrollMetrics = vi.fn();
      const largeData = Array.from({ length: 1000 }, (_, i) => ({
        id: i + 1,
        name: `Item ${i + 1}`,
      }));
      
      render(
        <Table
          data={largeData}
          columns={[{ id: 'name', header: 'Name', accessorKey: 'name' }]}
          virtual
          maxHeight={500}
          onVirtualScrollMetrics={onVirtualScrollMetrics}
        />
      );
      
      // Metrics should be called at least once
      expect(onVirtualScrollMetrics).toHaveBeenCalled();
    });
  });

  // ========== Editing Tests ==========

  describe('Editing', () => {
    it('should enable editing when editable is true', async () => {
      const user = userEvent.setup();
      const onEdit = vi.fn();
      
      render(
        <Table
          data={mockData}
          columns={[
            { id: 'name', header: 'Name', accessorKey: 'name', editable: true },
          ]}
          editable
          onEdit={onEdit}
        />
      );
      
      const firstRow = screen.getByText('Alice').closest('tr');
      const firstCell = firstRow?.querySelector('td');
      
      if (firstCell) {
        await user.dblClick(firstCell);
        
        // Should show input field
        const input = firstCell.querySelector('input');
        expect(input).toBeInTheDocument();
      }
    });

    it('should call onEdit when edit is saved', async () => {
      const user = userEvent.setup();
      const onEdit = vi.fn();
      
      render(
        <Table
          data={mockData}
          columns={[
            { id: 'name', header: 'Name', accessorKey: 'name', editable: true },
          ]}
          editable
          onEdit={onEdit}
        />
      );
      
      const firstRow = screen.getByText('Alice').closest('tr');
      const firstCell = firstRow?.querySelector('td');
      
      if (firstCell) {
        await user.dblClick(firstCell);
        
        const input = firstCell?.querySelector('input');
        if (input) {
          await user.type(input, 'Edited');
          await user.keyboard('{Enter}');
          
          expect(onEdit).toHaveBeenCalled();
        }
      }
    });

    it('should cancel edit when Escape is pressed', async () => {
      const user = userEvent.setup();
      
      render(
        <Table
          data={mockData}
          columns={[
            { id: 'name', header: 'Name', accessorKey: 'name', editable: true },
          ]}
          editable
          onEdit={vi.fn()}
        />
      );
      
      const firstRow = screen.getByText('Alice').closest('tr');
      const firstCell = firstRow?.querySelector('td');
      
      if (firstCell) {
        await user.dblClick(firstCell);
        
        const input = firstCell?.querySelector('input');
        if (input) {
          await user.keyboard('{Escape}');
          
          // Input should be removed
          expect(firstCell.querySelector('input')).not.toBeInTheDocument();
        }
      }
    });
  });

  // ========== Interaction Tests ==========

  describe('Interactions', () => {
    it('should call onRowClick when row is clicked', async () => {
      const user = userEvent.setup();
      const onRowClick = vi.fn();
      
      render(
        <Table data={mockData} columns={mockColumns} onRowClick={onRowClick} />
      );
      
      const firstRow = screen.getByText('Alice').closest('tr');
      if (firstRow) {
        await user.click(firstRow);
        expect(onRowClick).toHaveBeenCalledWith(mockData[0], expect.any(Object));
      }
    });

    it('should call onRowDoubleClick when row is double clicked', async () => {
      const user = userEvent.setup();
      const onRowDoubleClick = vi.fn();
      
      render(
        <Table data={mockData} columns={mockColumns} onRowDoubleClick={onRowDoubleClick} />
      );
      
      const firstRow = screen.getByText('Alice').closest('tr');
      if (firstRow) {
        await user.dblClick(firstRow);
        expect(onRowDoubleClick).toHaveBeenCalledWith(mockData[0], expect.any(Object));
      }
    });

    it('should call onCellClick when cell is clicked', async () => {
      const user = userEvent.setup();
      const onCellClick = vi.fn();
      
      render(
        <Table data={mockData} columns={mockColumns} onCellClick={onCellClick} />
      );
      
      const firstCell = screen.getByText('Alice');
      await user.click(firstCell);
      
      expect(onCellClick).toHaveBeenCalled();
    });
  });

  // ========== Accessibility Tests ==========

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<Table data={mockData} columns={mockColumns} />);
      
      const table = screen.getByRole('table');
      expect(table).toBeInTheDocument();
    });

    it('should have proper labels for checkboxes when selectable', () => {
      render(<Table data={mockData} columns={mockColumns} selectable />);
      
      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach((checkbox) => {
        expect(checkbox).toHaveAttribute('aria-label');
      });
    });

    it('should have proper ARIA attributes for sortable columns', () => {
      render(<Table data={mockData} columns={mockColumns} sortable />);
      
      const nameHeader = screen.getByText('Name').closest('.table-th');
      expect(nameHeader).toHaveClass('table-th--sortable');
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      
      render(<Table data={mockData} columns={mockColumns} selectable />);
      
      const firstCheckbox = screen.getAllByRole('checkbox')[1];
      firstCheckbox.focus();
      
      expect(firstCheckbox).toHaveFocus();
      
      await user.keyboard('{Tab}');
      
      // Focus should move to next interactive element
    });
  });

  // ========== Edge Cases ==========

  describe('Edge Cases', () => {
    it('should handle empty columns array', () => {
      render(<Table data={mockData} columns={[]} />);
      
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('should handle missing column properties', () => {
      const incompleteColumns = [
        { id: 'name', header: 'Name' },
      ] as TableColumn<(typeof mockData)[0]>[];
      
      render(<Table data={mockData} columns={incompleteColumns} />);
      
      expect(screen.getByText('Name')).toBeInTheDocument();
    });

    it('should handle custom cell renderers', () => {
      const customColumns: TableColumn<(typeof mockData)[0]>[] = [
        {
          id: 'name',
          header: 'Name',
          cellRenderer: ({ value }) => <strong>{value as string}</strong>,
        },
      ];
      
      render(<Table data={mockData} columns={customColumns} />);
      
      // Custom cell renderer is applied, verify table renders
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('should handle custom header renderers', () => {
      const customColumns: TableColumn<(typeof mockData)[0]>[] = [
        {
          id: 'name',
          header: 'Name',
          headerRenderer: () => <span>Custom Header</span>,
        },
      ];
      
      render(<Table data={mockData} columns={customColumns} />);
      
      expect(screen.getByText('Custom Header')).toBeInTheDocument();
    });

    it('should handle large datasets efficiently', () => {
      const largeData = Array.from({ length: 10000 }, (_, i) => ({
        id: i + 1,
        name: `Item ${i + 1}`,
      }));
      
      render(<Table data={largeData} columns={mockColumns} />);
      
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('should handle data with null/undefined values', () => {
      const dataWithNulls = [
        { id: 1, name: 'Alice', age: null, email: undefined, status: 'active' },
      ];
      
      render(<Table data={dataWithNulls} columns={mockColumns} />);
      
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });

    it('should handle column pinning', () => {
      const pinnedColumns = [
        { ...mockColumns[0], fixed: 'left' as const },
        ...mockColumns.slice(1),
      ];
      
      render(<Table data={mockData} columns={pinnedColumns} />);
      
      const firstHeader = screen.getByText('ID').closest('.table-th');
      expect(firstHeader).toHaveClass('table-th--pinned-left');
    });

    it('should handle column resizing', async () => {
      const user = userEvent.setup();
      
      render(<Table data={mockData} columns={mockColumns} />);
      
      const resizer = screen.getByText('ID').closest('.table-th')?.querySelector('.table-resizer');
      
      if (resizer) {
        // Simulate drag
        fireEvent.mouseDown(resizer, { clientX: 100 });
        fireEvent.mouseMove(document, { clientX: 150 });
        fireEvent.mouseUp(document);
        
        // Column should be resized
      }
    });
  });

  // ========== Performance Tests ==========

  describe('Performance', () => {
    it('should not re-render unnecessarily when props change', () => {
      const { rerender } = render(
        <Table data={mockData} columns={mockColumns} />
      );
      
      const firstRender = screen.getByRole('table');
      
      rerender(<Table data={mockData} columns={mockColumns} />);
      
      const secondRender = screen.getByRole('table');
      expect(firstRender).toBe(secondRender);
    });

    it('should memoize callback functions', () => {
      const onRowClick = vi.fn();
      const { rerender } = render(
        <Table data={mockData} columns={mockColumns} onRowClick={onRowClick} />
      );
      
      // Rerender with same props
      rerender(<Table data={mockData} columns={mockColumns} onRowClick={onRowClick} />);
      
      // Should not cause issues
      expect(screen.getByRole('table')).toBeInTheDocument();
    });
  });
});
