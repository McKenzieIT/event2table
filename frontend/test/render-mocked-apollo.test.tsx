// Test renderWithMockedApollo function
import { describe, it, expect, vi } from 'vitest';
import React from 'react';

// Mock usePerformanceMonitor
vi.mock('@/shared/utils/performanceMonitor', () => ({
  usePerformanceMonitor: vi.fn(),
}));

// Mock OptimizedVirtualList
vi.mock('@/shared/components/VirtualList/OptimizedVirtualList', () => ({
  default: ({ items, renderItem }: any) => {
    return React.createElement('div', { 'data-testid': 'virtual-list' },
      items?.map((item: any, index: number) =>
        React.createElement('div', { key: item.id || index }, renderItem(item, index))
      )
    );
  },
}));

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: () => ({ currentGame: { gid: 10000147, name: 'Test Game' } }),
    useNavigate: () => vi.fn(),
  };
});

import { renderWithMockedApollo, screen } from '@test/test-utils';
import { MockedProvider } from '@apollo/client/testing/react';
import EventsListGraphQL from '@analytics/pages/EventsListGraphQL';
import { GET_EVENTS, GET_CATEGORIES } from '@shared/graphql/operations';

const mocks = [
  {
    request: {
      query: GET_EVENTS,
      variables: { gameGid: 10000147, category: null, limit: 10, offset: 0 },
    },
    result: {
      data: {
        events: [{ id: 1, eventName: 'event_1', eventNameCn: '事件1', categoryName: '分类A', paramCount: 5 }],
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

describe('renderWithMockedApollo Test', () => {
  it('should render with renderWithMockedApollo', () => {
    console.log('Testing renderWithMockedApollo...');
    
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });
});
