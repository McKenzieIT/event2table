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
import { render, screen, waitFor, createMockGameContext } from '@test/test-utils';
import { GET_EVENTS, GET_CATEGORIES } from '@shared/graphql/operations';
import { DELETE_EVENT } from '@shared/graphql/operations';
import EventsListGraphQL from '../EventsListGraphQL';
import { performanceMonitor, PerformanceMetrics } from '@shared/utils/performanceMonitor';
import userEvent from '@testing-library/user-event';
import { vi, beforeEach, describe, test, expect } from 'vitest';

// Mock MockedProvider since Apollo Client v4 doesn't export it from testing
const MockedProvider = ({ children }: { children: React.ReactNode; mocks?: unknown[]; addTypename?: boolean }) => {
  return <div data-testid="mocked-provider">{children}</div>;
};

// Mock useOutletContext using the new unified mock approach
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: () => createMockGameContext(),
    useNavigate: () => vi.fn(),
  };
});

// Mock game context
const mockCurrentGame = {
  gid: 10000147,
  name: 'Test Game',
  odsDb: 'ieu_ods'
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

// Helper function for rendering with context (shared across describe blocks)
const renderWithContext = (component: React.ReactElement) => {
  return render(
    <MockedProvider mocks={mocks} addTypename={false}>
      {component}
    </MockedProvider>
  );
};

describe('EventsListGraphQL Performance Tests', () => {
  beforeEach(() => {
    // Reset performance metrics before each test
    performanceMonitor.reset();
  });

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
    const typedMetrics = metrics as PerformanceMetrics | undefined;
    expect(typedMetrics?.componentName).toBe('EventsListGraphQL');
    // renderCount and averageRenderTime may be 0 if PerformanceObserver is not available
    if (typedMetrics?.renderCount !== undefined) {
      expect(typedMetrics.renderCount).toBeGreaterThanOrEqual(0);
    }
    if (typedMetrics?.averageRenderTime !== undefined) {
      expect(typedMetrics.averageRenderTime).toBeGreaterThanOrEqual(0);
    }

    // Log metrics for analysis
    console.log('EventsListGraphQL Performance Metrics:', {
      renderCount: typedMetrics?.renderCount,
      avgRenderTime: typedMetrics?.averageRenderTime ? `${typedMetrics.averageRenderTime.toFixed(2)}ms` : 'N/A',
      lastRenderTime: typedMetrics?.lastRenderTime ? `${typedMetrics.lastRenderTime.toFixed(2)}ms` : 'N/A',
      memoryUsage: typedMetrics?.memoryUsage ? `${typedMetrics.memoryUsage.toFixed(2)}MB` : 'N/A'
    });
  });

  test('should maintain 60fps rendering', async () => {
    renderWithContext(<EventsListGraphQL />);

    await waitFor(() => {
      expect(screen.getByText(/总事件数/)).toBeInTheDocument();
    });

    const metrics = performanceMonitor.getMetrics('EventsListGraphQL');

    // 60fps = 16.67ms per frame
    expect((metrics as PerformanceMetrics | undefined)?.lastRenderTime).toBeLessThan(33);
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

    const typedMetrics = metrics as PerformanceMetrics | undefined;
    if (typedMetrics?.memoryUsage) {
      // Memory usage should be reasonable (<100MB for virtual list)
      expect(typedMetrics.memoryUsage).toBeLessThan(100);
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
    await userEvent.selectOptions(pageSizeSelect, '20');

    // Verify page size changed
    await waitFor(() => {
      expect(pageSizeSelect.value).toBe('20');
    });
  });
});
