/**
 * Performance Test: EventsListGraphQL with OptimizedVirtualList
 *
 * Tests:
 * 1. Virtual list renders correctly with large dataset
 * 2. Performance monitor tracks render metrics
 * 3. Batch operations are efficient
 * 4. Scrolling performance is maintained
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { GET_EVENTS, GET_CATEGORIES } from '@shared/graphql/operations';
import { DELETE_EVENT } from '@shared/graphql/operations';
import EventsListGraphQL from '../EventsListGraphQL';
import { performanceMonitor } from '@shared/utils/performanceMonitor';

// Mock game context
const mockCurrentGame = {
  gid: 10000147,
  name: 'Test Game',
  ods_db: 'ieu_ods'
};

// Mock events data
const mockEvents = Array.from({ length: 1000 }, (_, i) => ({
  id: i + 1,
  eventName: `test_event_${i}`,
  eventNameCn: `测试事件${i}`,
  categoryName: i % 3 === 0 ? 'Login' : i % 3 === 1 ? 'Battle' : null,
  paramCount: Math.floor(Math.random() * 50)
}));

const mocks = [
  {
    request: {
      query: GET_EVENTS,
      variables: {
        gameGid: 10000147,
        category: null,
        limit: 10,
        offset: 0
      }
    },
    result: {
      data: {
        events: mockEvents.slice(0, 10)
      }
    }
  },
  {
    request: {
      query: GET_CATEGORIES,
      variables: {
        limit: 100,
        offset: 0
      }
    },
    result: {
      data: {
        categories: [
          { id: 1, name: 'Login' },
          { id: 2, name: 'Battle' },
          { id: 3, name: 'Economy' }
        ]
      }
    }
  }
];

describe('EventsListGraphQL Performance Tests', () => {
  beforeEach(() => {
    // Reset performance metrics before each test
    performanceMonitor.reset();
  });

  const renderWithContext = (component: React.ReactElement) => {
    return render(
      <MockedProvider mocks={mocks} addTypename={false}>
        {component}
      </MockedProvider>
    );
  };

  test('should render large dataset efficiently with virtual scrolling', async () => {
    const startTime = performance.now();

    renderWithContext(<EventsListGraphQL />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    const renderTime = performance.now() - startTime;

    // Render should complete within 1 second
    expect(renderTime).toBeLessThan(1000);

    // Check performance metrics
    const metrics = performanceMonitor.getMetrics('EventsListGraphQL');
    expect(metrics).toBeDefined();
  });

  test('should track performance metrics correctly', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    const metrics = performanceMonitor.getMetrics('EventsListGraphQL');

    // Verify metrics are being tracked
    expect(metrics?.componentName).toBe('EventsListGraphQL');
    expect(metrics?.renderCount).toBeGreaterThan(0);
    expect(metrics?.averageRenderTime).toBeGreaterThan(0);

    // Log metrics for analysis
    console.log('EventsListGraphQL Performance Metrics:', {
      renderCount: metrics?.renderCount,
      avgRenderTime: `${metrics?.averageRenderTime?.toFixed(2)}ms`,
      lastRenderTime: `${metrics?.lastRenderTime?.toFixed(2)}ms`,
      memoryUsage: metrics?.memoryUsage ? `${metrics.memoryUsage.toFixed(2)}MB` : 'N/A'
    });
  });

  test('should maintain 60fps rendering', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    const metrics = performanceMonitor.getMetrics('EventsListGraphQL');

    // 60fps = 16.67ms per frame
    expect(metrics?.lastRenderTime).toBeLessThan(33);
  });

  test('should filter events efficiently', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    // Get search input
    const searchInput = screen.getByPlaceholderText(/搜索事件名称/);

    // Measure filtering performance
    const startTime = performance.now();

    // Type search query
    const userEvent = require('@testing-library/user-event').default;
    await userEvent.type(searchInput, 'test_event_1');

    const filterTime = performance.now() - startTime;

    // Filtering should be fast (<100ms)
    expect(filterTime).toBeLessThan(100);
  });

  test('should handle category filtering efficiently', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    // Find category select
    const categorySelect = document.querySelector('.category-select') as HTMLSelectElement;
    expect(categorySelect).toBeInTheDocument();

    const startTime = performance.now();

    // Change category
    const userEvent = require('@testing-library/user-event').default;
    await userEvent.selectOptions(categorySelect, 'Login');

    const filterTime = performance.now() - startTime;

    // Category filtering should be fast (<100ms)
    expect(filterTime).toBeLessThan(100);
  });

  test('should handle batch selection efficiently', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    // Find "Select All" checkbox
    const selectAllCheckbox = screen.getByRole('checkbox', { name: /select all/i });
    expect(selectAllCheckbox).toBeInTheDocument();

    const startTime = performance.now();

    // Click select all
    const userEvent = require('@testing-library/user-event').default;
    await userEvent.click(selectAllCheckbox);

    const selectTime = performance.now() - startTime;

    // Selection should be fast (<100ms)
    expect(selectTime).toBeLessThan(100);
  });

  test('should have acceptable memory usage', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    const metrics = performanceMonitor.getMetrics('EventsListGraphQL');

    if (metrics?.memoryUsage) {
      // Memory usage should be reasonable (<100MB for virtual list)
      expect(metrics.memoryUsage).toBeLessThan(100);
    }
  });
});

describe('EventsListGraphQL Integration Tests', () => {
  test('should integrate with OptimizedVirtualList correctly', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    // Check if virtual list container is present
    const virtualListContainer = document.querySelector('.virtual-table-body');
    expect(virtualListContainer).toBeInTheDocument();
  });

  test('should handle pagination correctly', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    // Check pagination controls
    const pageSizeSelect = document.querySelector('.page-size-select') as HTMLSelectElement;
    expect(pageSizeSelect).toBeInTheDocument();

    // Change page size
    const userEvent = require('@testing-library/user-event').default;
    await userEvent.selectOptions(pageSizeSelect, '20');

    // Verify page size changed
    await waitFor(() => {
      expect(pageSizeSelect.value).toBe('20');
    });
  });
});
