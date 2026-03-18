/**
 * Performance Test: GamesListGraphQL with OptimizedVirtualList
 *
 * Tests:
 * 1. Virtual list renders correctly with large dataset
 * 2. Performance monitor tracks render metrics
 * 3. Scrolling performance is maintained
 * 4. Memory usage is acceptable
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { GET_GAMES } from '@/graphql/queries';
import GamesListGraphQL from '../GamesListGraphQL';
import { performanceMonitor } from '@shared/utils/performanceMonitor';

// Mock GraphQL response
const mockGames = Array.from({ length: 1000 }, (_, i) => ({
  gid: 10000000 + i,
  name: `Test Game ${i}`,
  odsDb: 'ieu_ods',
  eventCount: Math.floor(Math.random() * 100),
  parameterCount: Math.floor(Math.random() * 200),
  description: `Test game description ${i}`
}));

const mocks = [
  {
    request: {
      query: GET_GAMES,
      variables: {
        limit: 100,
        offset: 0
      }
    },
    result: {
      data: {
        games: mockGames
      }
    }
  }
];

describe('GamesListGraphQL Performance Tests', () => {
  beforeEach(() => {
    // Reset performance metrics before each test
    performanceMonitor.reset();
  });

  test('should render large dataset efficiently with virtual scrolling', async () => {
    const startTime = performance.now();

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GamesListGraphQL />
      </MockedProvider>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/总游戏数/)).toBeInTheDocument();
    });

    const renderTime = performance.now() - startTime;

    // Render should complete within 1 second for 1000 items
    expect(renderTime).toBeLessThan(1000);

    // Check performance metrics
    const metrics = performanceMonitor.getMetrics('GamesListGraphQL');
    expect(metrics).toBeDefined();
    expect(metrics?.renderCount).toBeGreaterThan(0);
  });

  test('should track performance metrics correctly', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GamesListGraphQL />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/总游戏数/)).toBeInTheDocument();
    });

    const metrics = performanceMonitor.getMetrics('GamesListGraphQL');

    // Verify metrics are being tracked
    expect(metrics?.componentName).toBe('GamesListGraphQL');
    expect(metrics?.renderCount).toBeGreaterThan(0);
    expect(metrics?.averageRenderTime).toBeGreaterThan(0);

    // Log metrics for analysis
    console.log('GamesListGraphQL Performance Metrics:', {
      renderCount: metrics?.renderCount,
      avgRenderTime: `${metrics?.averageRenderTime?.toFixed(2)}ms`,
      lastRenderTime: `${metrics?.lastRenderTime?.toFixed(2)}ms`,
      memoryUsage: metrics?.memoryUsage ? `${metrics.memoryUsage.toFixed(2)}MB` : 'N/A'
    });
  });

  test('should maintain 60fps rendering', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GamesListGraphQL />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/总游戏数/)).toBeInTheDocument();
    });

    const metrics = performanceMonitor.getMetrics('GamesListGraphQL');

    // 60fps = 16.67ms per frame
    // Allow some margin for testing environment
    expect(metrics?.lastRenderTime).toBeLessThan(33); // ~30fps minimum
  });

  test('should filter games efficiently', async () => {
    const { container } = render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GamesListGraphQL />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/总游戏数/)).toBeInTheDocument();
    });

    // Get search input
    const searchInput = screen.getByPlaceholderText(/搜索游戏名称或GID/);

    // Measure filtering performance
    const startTime = performance.now();

    // Type search query
    const userEvent = require('@testing-library/user-event').default;
    await userEvent.type(searchInput, 'Test Game 1');

    const filterTime = performance.now() - startTime;

    // Filtering should be fast (<100ms)
    expect(filterTime).toBeLessThan(100);
  });

  test('should have acceptable memory usage', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GamesListGraphQL />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/总游戏数/)).toBeInTheDocument();
    });

    const metrics = performanceMonitor.getMetrics('GamesListGraphQL');

    if (metrics?.memoryUsage) {
      // Memory usage should be reasonable (<100MB for virtual list)
      expect(metrics.memoryUsage).toBeLessThan(100);
    }
  });

  test('should handle empty state efficiently', async () => {
    const emptyMocks = [
      {
        request: {
          query: GET_GAMES,
          variables: {
            limit: 100,
            offset: 0
          }
        },
        result: {
          data: {
            games: []
          }
        }
      }
    ];

    const startTime = performance.now();

    render(
      <MockedProvider mocks={emptyMocks} addTypename={false}>
        <GamesListGraphQL />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/暂无游戏数据/)).toBeInTheDocument();
    });

    const renderTime = performance.now() - startTime;

    // Empty state should render quickly (<500ms)
    expect(renderTime).toBeLessThan(500);
  });
});

describe('GamesListGraphQL Integration Tests', () => {
  test('should integrate with OptimizedVirtualList correctly', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GamesListGraphQL />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/总游戏数/)).toBeInTheDocument();
    });

    // Check if virtual list container is present
    const virtualListContainer = document.querySelector('.virtual-table-body');
    expect(virtualListContainer).toBeInTheDocument();
  });

  test('should handle search and filter correctly', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GamesListGraphQL />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/总游戏数/)).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/搜索游戏名称或GID/);
    const userEvent = require('@testing-library/user-event').default;

    // Test search functionality
    await userEvent.type(searchInput, 'Test Game 1');

    // Verify filtered results
    await waitFor(() => {
      const filteredCount = screen.getByText(/显示 \d+ \/ \d+ 个游戏/);
      expect(filteredCount).toBeInTheDocument();
    });
  });
});
