/**
 * Diagnose EventsListGraphQL rendering issue
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { createElement } from 'react';
import { MockedProvider } from '@apollo/client/testing/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactFlowProvider } from 'reactflow';
import { ToastProvider, ErrorBoundary } from '@shared/ui';
import EventsListGraphQL from '@analytics/pages/EventsListGraphQL';
import { GET_EVENTS, GET_CATEGORIES } from '@shared/graphql/operations';
import { createMockGameContext } from '@test/test-utils';

// Mock useOutletContext
const mockOutletContext = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: () => mockOutletContext(),
    useNavigate: () => vi.fn(),
  };
});

// Mock usePerformanceMonitor
vi.mock('@shared/utils/performanceMonitor', () => ({
  usePerformanceMonitor: vi.fn(),
}));

beforeEach(() => {
  mockOutletContext.mockReturnValue(createMockGameContext());
});

const mocks = [
  {
    request: {
      query: GET_EVENTS,
      variables: {
        gameGid: 10000147,
        category: null,
        limit: 10,
        offset: 0,
      },
    },
    result: {
      data: {
        events: [
          { id: 1, eventName: 'event_1', eventNameCn: '事件1', categoryName: '分类A', paramCount: 5 },
        ],
      },
    },
  },
  {
    request: {
      query: GET_CATEGORIES,
      variables: { limit: 100, offset: 0 },
    },
    result: {
      data: {
        categories: [{ id: 1, name: '分类A', eventCount: 5 }],
      },
    },
  },
];

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
}

describe('EventsListGraphQL Rendering Diagnostics', () => {
  it('should render EventsListGraphQL with MockedProvider', async () => {
    const queryClient = createTestQueryClient();

    const { container } = render(
      createElement(
        ErrorBoundary,
        null,
        createElement(
          BrowserRouter,
          null,
          createElement(
            QueryClientProvider,
          { client: queryClient },
          createElement(
            ReactFlowProvider,
            null,
            createElement(
              ToastProvider,
              null,
              createElement(
                MockedProvider,
                { mocks, addTypename: false },
                createElement(EventsListGraphQL)
              )
            )
          )
          )
        )
      )
    );

    // Should show loading state initially
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });
});
