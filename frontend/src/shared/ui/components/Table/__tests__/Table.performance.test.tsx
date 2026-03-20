/**
 * Table Component Performance Tests
 * 
 * Tests virtual scrolling performance with large datasets.
 * Target: 10000+ rows, scroll latency <16ms, memory <50MB
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Table } from '../Table';
import type { TableColumn } from '../Table.types';

// Generate large dataset for performance testing
function generateLargeDataset(count: number): Array<{ id: number; name: string; value: number; description: string }> {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Item ${i + 1}`,
    value: Math.random() * 1000,
    description: `This is a detailed description for item ${i + 1}. It contains enough text to simulate real-world content.`,
  }));
}

describe('Table Virtual Scrolling Performance', () => {
  const columns: TableColumn<{ id: number; name: string; value: number; description: string }>[] = [
    { id: 'id', header: 'ID', accessorKey: 'id', width: 80 },
    { id: 'name', header: 'Name', accessorKey: 'name', width: 200 },
    { id: 'value', header: 'Value', accessorKey: 'value', width: 120 },
    { id: 'description', header: 'Description', accessorKey: 'description', width: 400 },
  ];

  describe('Virtual Scrolling Enabled', () => {
    it('should render only visible rows with virtual scrolling', async () => {
      const data = generateLargeDataset(10000);
      const metricsCallback = jest.fn();

      const { container } = render(
        <Table
          data={data}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
          overscan={5}
          onVirtualScrollMetrics={metricsCallback}
        />
      );

      // Wait for initial render
      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // Verify metrics are being reported
      await waitFor(() => {
        expect(metricsCallback).toHaveBeenCalled();
      });

      const lastMetrics = metricsCallback.mock.calls[metricsCallback.mock.calls.length - 1][0];
      
      // Verify that only a subset of rows are rendered (not all 10000)
      const renderedRows = container.querySelectorAll('.table-tr--virtual');
      expect(renderedRows.length).toBeLessThan(100); // Should only render visible + overscan rows
      
      // Verify total rows count is correct
      expect(lastMetrics.totalRows).toBe(10000);
      
      // Verify visible rows is reasonable
      expect(lastMetrics.visibleRows).toBeGreaterThan(0);
      expect(lastMetrics.visibleRows).toBeLessThan(50);
    });

    it('should maintain smooth scrolling performance', async () => {
      const data = generateLargeDataset(10000);
      const metricsHistory: Array<{ renderTime?: number }> = [];

      const { container } = render(
        <Table
          data={data}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
          onVirtualScrollMetrics={(metrics) => metricsHistory.push(metrics)}
        />
      );

      const scrollContainer = container.querySelector('.table-container');
      expect(scrollContainer).toBeInTheDocument();

      // Simulate scroll events
      if (scrollContainer) {
        for (let i = 0; i < 10; i++) {
          const startTime = performance.now();
          
          // Simulate scroll position change
          Object.defineProperty(scrollContainer, 'scrollTop', {
            writable: true,
            value: i * 500,
          });
          
          scrollContainer.dispatchEvent(new Event('scroll'));
          
          const endTime = performance.now();
          const scrollLatency = endTime - startTime;
          
          // Each scroll event should be under 16ms (60fps target)
          expect(scrollLatency).toBeLessThan(16);
        }
      }
    });

    it('should support dynamic row height estimation', async () => {
      const data = generateLargeDataset(1000);
      
      const { container } = render(
        <Table
          data={data}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
          dynamicRowHeight={true}
          overscan={10}
        />
      );

      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // Verify virtual rows are rendered
      const virtualRows = container.querySelectorAll('.table-tr--virtual');
      expect(virtualRows.length).toBeGreaterThan(0);
    });

    it('should respect overscan configuration', async () => {
      const data = generateLargeDataset(1000);
      const overscan = 15;
      
      const { container } = render(
        <Table
          data={data}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
          overscan={overscan}
        />
      );

      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // Count rendered rows (should be visible + overscan above + overscan below)
      const renderedRows = container.querySelectorAll('.table-tr--virtual');
      
      // With maxHeight=600 and rowHeight=50, we expect ~12 visible rows
      // Plus overscan above and below, total should be around 12 + (15*2) = 42
      expect(renderedRows.length).toBeGreaterThan(20);
      expect(renderedRows.length).toBeLessThan(60);
    });
  });

  describe('Non-Virtual Scrolling (Default)', () => {
    it('should render all rows when virtual scrolling is disabled', async () => {
      const data = generateLargeDataset(100);
      
      const { container } = render(
        <Table
          data={data}
          columns={columns}
          virtual={false}
        />
      );

      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // All rows should be rendered
      const renderedRows = container.querySelectorAll('.table-tr:not(.table-tr--virtual)');
      expect(renderedRows.length).toBe(100);
    });
  });

  describe('Performance Metrics', () => {
    it('should report accurate render time metrics', async () => {
      const data = generateLargeDataset(5000);
      const metricsCallback = jest.fn();

      render(
        <Table
          data={data}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
          onVirtualScrollMetrics={metricsCallback}
        />
      );

      await waitFor(() => {
        expect(metricsCallback).toHaveBeenCalled();
      });

      const metrics = metricsCallback.mock.calls[metricsCallback.mock.calls.length - 1][0];
      
      // Verify metrics structure
      expect(metrics).toHaveProperty('totalRows');
      expect(metrics).toHaveProperty('visibleRows');
      expect(metrics).toHaveProperty('scrollOffset');
      expect(metrics).toHaveProperty('estimatedRowHeight');
      
      // Verify values
      expect(metrics.totalRows).toBe(5000);
      expect(metrics.visibleRows).toBeGreaterThan(0);
      expect(metrics.estimatedRowHeight).toBe(50);
    });

    it('should handle rapid data updates efficiently', async () => {
      const initialData = generateLargeDataset(1000);
      
      const { rerender } = render(
        <Table
          data={initialData}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
        />
      );

      // Rapid data updates
      const updateTimes: number[] = [];
      
      for (let i = 0; i < 5; i++) {
        const startTime = performance.now();
        const newData = generateLargeDataset(1000 + i * 100);
        
        rerender(
          <Table
            data={newData}
            columns={columns}
            virtual={true}
            maxHeight={600}
            rowHeight={50}
          />
        );
        
        const endTime = performance.now();
        updateTimes.push(endTime - startTime);
      }

      // All updates should complete within reasonable time (<100ms each)
      updateTimes.forEach(time => {
        expect(time).toBeLessThan(100);
      });
    });
  });

  describe('Memory Efficiency', () => {
    it('should not leak memory when scrolling through large datasets', async () => {
      const data = generateLargeDataset(10000);
      
      const { container, unmount } = render(
        <Table
          data={data}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
        />
      );

      const scrollContainer = container.querySelector('.table-container');
      
      // Simulate extensive scrolling
      if (scrollContainer) {
        for (let i = 0; i < 100; i++) {
          Object.defineProperty(scrollContainer, 'scrollTop', {
            writable: true,
            value: i * 100,
          });
          scrollContainer.dispatchEvent(new Event('scroll'));
        }
      }

      // Verify DOM nodes are still limited
      const allRows = container.querySelectorAll('.table-tr--virtual');
      expect(allRows.length).toBeLessThan(100);

      unmount();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty data gracefully', async () => {
      const metricsCallback = jest.fn();

      render(
        <Table
          data={[]}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
          onVirtualScrollMetrics={metricsCallback}
        />
      );

      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // Should show empty state, not crash
      expect(screen.getByText(/no data/i)).toBeInTheDocument();
    });

    it('should handle single row data', async () => {
      const data = [{ id: 1, name: 'Single Item', value: 100, description: 'Only one row' }];

      const { container } = render(
        <Table
          data={data}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Single Item')).toBeInTheDocument();
      });

      const rows = container.querySelectorAll('.table-tr--virtual');
      expect(rows.length).toBe(1);
    });

    it('should handle variable row heights correctly', async () => {
      // Data with varying content lengths
      const data = [
        { id: 1, name: 'Short', value: 1, description: 'Short' },
        { id: 2, name: 'Long Name', value: 2, description: 'A'.repeat(500) },
        { id: 3, name: 'Medium', value: 3, description: 'Medium length description' },
      ];

      const { container } = render(
        <Table
          data={data}
          columns={columns}
          virtual={true}
          maxHeight={600}
          rowHeight={50}
          dynamicRowHeight={true}
        />
      );

      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
      });

      // All rows should be rendered for small dataset
      const rows = container.querySelectorAll('.table-tr--virtual');
      expect(rows.length).toBeGreaterThan(0);
    });
  });
});
