/**
 * TDD Test: ParametersListGraphQL Virtual Scrolling Integration
 *
 * Test-Driven Development approach:
 * 1. Write failing test for performance issue (RED)
 * 2. Implement virtual scrolling optimization (GREEN)
 * 3. Verify performance improvements (REFACTOR)
 *
 * Performance Requirements:
 * - Render 1000+ parameters in <100ms
 * - Smooth scrolling at 60fps
 * - Memory usage <50MB
 */

import { render, screen, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import ParametersListGraphQL from '../ParametersListGraphQL';
import { GET_PARAMETERS_MANAGEMENT } from '@/graphql/queries';

// Mock useGameStore
vi.mock('@/stores/gameStore', () => ({
  useGameStore: () => ({
    currentGame: { gid: 1, name: 'Test Game' },
  }),
}));

// Mock useToast
vi.mock('@shared/ui', async () => {
  const actual = await vi.importActual('@shared/ui');
  return {
    ...actual,
    useToast: () => ({
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
    }),
  };
});

/**
 * Create mock data for 1000+ parameters
 */
const createLargeParametersMock = (count: number = 1000) => {
  const parameters = Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    paramName: `param_${i + 1}`,
    paramNameCn: `参数${i + 1}`,
    paramType: ['string', 'int', 'bigint', 'float', 'boolean', 'datetime'][i % 6],
    eventName: `event_${Math.floor(i / 10) + 1}`,
    isCommon: i % 20 === 0,
    eventsCount: Math.floor(Math.random() * 10) + 1,
  }));

  return {
    request: {
      query: GET_PARAMETERS_MANAGEMENT,
      variables: {
        gameGid: 1,
        mode: 'all',
        eventId: null,
      },
    },
    result: {
      data: {
        parametersManagement: parameters,
      },
    },
  };
};

describe('ParametersListGraphQL - Virtual Scrolling Performance', () => {
  /**
   * Test Case 1: Large list renders within performance budget
   *
   * TDD Phase: RED → GREEN
   * Expected: Render 1000 parameters in <100ms
   */
  it('should render 1000 parameters in less than 100ms', async () => {
    const mocks = [createLargeParametersMock(1000)];

    const startTime = performance.now();

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/总参数数/)).toBeInTheDocument();
    });

    // Verify performance requirement
    expect(renderTime).toBeLessThan(100);

    // Verify parameters are displayed
    expect(screen.getByText('param_1')).toBeInTheDocument();
    expect(screen.getByText('param_1000')).toBeInTheDocument();
  });

  /**
   * Test Case 2: Very large list (5000 parameters)
   *
   * TDD Phase: RED → GREEN
   * Expected: Render 5000 parameters in <200ms
   */
  it('should render 5000 parameters in less than 200ms', async () => {
    const mocks = [createLargeParametersMock(5000)];

    const startTime = performance.now();

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/总参数数/)).toBeInTheDocument();
    });

    // Verify performance requirement
    expect(renderTime).toBeLessThan(200);

    // Verify statistics
    expect(screen.getByText('5000')).toBeInTheDocument(); // Total params
  });

  /**
   * Test Case 3: Search functionality works with virtual scrolling
   *
   * TDD Phase: RED → GREEN
   * Expected: Search should filter 1000+ items efficiently
   */
  it('should handle search efficiently with large list', async () => {
    const mocks = [createLargeParametersMock(1000)];

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByPlaceholderText('搜索参数名...')).toBeInTheDocument();
    });

    const startTime = performance.now();

    // Type search query
    const searchInput = screen.getByPlaceholderText('搜索参数名...');
    searchInput.value = 'param_1';
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));

    const endTime = performance.now();
    const searchTime = endTime - startTime;

    // Search should be fast (debounced)
    expect(searchTime).toBeLessThan(50);
  });

  /**
   * Test Case 4: Memory efficiency
   *
   * TDD Phase: RED → GREEN
   * Expected: Virtual scrolling reduces DOM nodes
   */
  it('should use virtual scrolling to reduce DOM nodes', async () => {
    const mocks = [createLargeParametersMock(1000)];

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/总参数数/)).toBeInTheDocument();
    });

    // With virtual scrolling, only ~20-30 rows should be in DOM
    // instead of 1000
    const tableRows = document.querySelectorAll('tbody tr');

    // Virtual scrolling should render fewer rows than total
    expect(tableRows.length).toBeLessThan(100);
  });

  /**
   * Test Case 5: Type filter works with virtual scrolling
   *
   * TDD Phase: RED → GREEN
   * Expected: Type filter should work efficiently
   */
  it('should handle type filter efficiently', async () => {
    const mocks = [createLargeParametersMock(1000)];

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('全部类型')).toBeInTheDocument();
    });

    // Type filter should be present
    const typeFilter = screen.getByText('全部类型').closest('select');
    expect(typeFilter).toBeInTheDocument();
  });

  /**
   * Test Case 6: Statistics calculation performance
   *
   * TDD Phase: RED → GREEN
   * Expected: Statistics should calculate quickly
   */
  it('should calculate statistics quickly for large list', async () => {
    const mocks = [createLargeParametersMock(5000)];

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    const startTime = performance.now();

    await waitFor(() => {
      expect(screen.getByText('5000')).toBeInTheDocument(); // Total params
    });

    const endTime = performance.now();
    const statsTime = endTime - startTime;

    // Stats calculation should be fast
    expect(statsTime).toBeLessThan(100);
  });
});
