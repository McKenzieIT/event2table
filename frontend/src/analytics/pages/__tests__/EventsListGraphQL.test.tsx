// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * EventsListGraphQL 功能测试
 *
 * 测试GraphQL版本的EventsList页面功能
 */

import { vi, describe, it, expect, beforeEach } from 'vitest';
import React from 'react';

// 创建可变的mock函数，允许在测试中动态修改返回值
const mockOutletContext = vi.fn();

// Mock usePerformanceMonitor - 避免在测试环境中执行性能监控
vi.mock('@/shared/utils/performanceMonitor', () => ({
  usePerformanceMonitor: vi.fn(),
}));

// Mock OptimizedVirtualList - 简化虚拟列表渲染
vi.mock('@/shared/components/VirtualList/OptimizedVirtualList', () => ({
  default: ({ items, renderItem }: any) => {
    return React.createElement('div', { 'data-testid': 'virtual-list' },
      items?.map((item: any, index: number) =>
        React.createElement('div', { key: item.id || index }, renderItem(item, index))
      )
    );
  },
}));

// Mock useOutletContext using the new unified mock approach
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: () => mockOutletContext(),
    useNavigate: () => vi.fn(),
  };
});

// 现在可以安全地导入其他模块
import { renderWithMockedApollo, screen, waitFor, fireEvent, createMockGameContext } from '@test/test-utils';
import { MockedProvider } from '@apollo/client/testing/react';
import EventsListGraphQL from '../EventsListGraphQL';
import { GET_EVENTS, GET_CATEGORIES, DELETE_EVENT } from '@shared/graphql/operations';

// 默认返回有游戏上下文
beforeEach(() => {
  mockOutletContext.mockReturnValue(createMockGameContext());
});

const mocks = [
  {
    request: {
      query: GET_EVENTS,
      variables: {
        gameGid: 10000147,  // 匹配 DEFAULT_MOCK_GAME.gid
        category: null,
        limit: 10,
        offset: 0,
      },
    },
    result: {
      data: {
        events: [
          {
            id: 1,
            eventName: 'event_1',
            eventNameCn: '事件1',
            categoryName: '分类A',
            paramCount: 5,
          },
          {
            id: 2,
            eventName: 'event_2',
            eventNameCn: '事件2',
            categoryName: '分类B',
            paramCount: 10,
          },
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
        categories: [
          { id: 1, name: '分类A', eventCount: 5 },
          { id: 2, name: '分类B', eventCount: 10 },
        ],
      },
    },
  },
];

const deleteMocks = [
  ...mocks,
  {
    request: {
      query: DELETE_EVENT,
      variables: { id: 1 },
    },
    result: {
      data: {
        deleteEvent: {
          ok: true,
          message: 'Event deleted successfully',
          errors: null,
        },
      },
    },
  },
];

describe('EventsListGraphQL', () => {
  it('should render events list with loading state', () => {
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('should render events list with data', async () => {
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    await waitFor(() => {
      expect(screen.getByText('日志事件管理 (GraphQL版本)')).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('event_1')).toBeInTheDocument();
      expect(screen.getByText('事件1')).toBeInTheDocument();
      expect(screen.getByText('event_2')).toBeInTheDocument();
      expect(screen.getByText('事件2')).toBeInTheDocument();
    });
  });

  it('should display statistics cards', async () => {
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    await waitFor(() => {
      expect(screen.getByText('总事件数')).toBeInTheDocument();
      expect(screen.getByText('已分类')).toBeInTheDocument();
      expect(screen.getByText('未分类')).toBeInTheDocument();
    });
  });

  it('should render action buttons', async () => {
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    await waitFor(() => {
      expect(screen.getByText('导入Excel')).toBeInTheDocument();
      expect(screen.getByTestId('add-event-button')).toBeInTheDocument();
    });
  });

  it('should handle search input', async () => {
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    await waitFor(() => {
      expect(screen.getByPlaceholderText('搜索事件名称...')).toBeInTheDocument();
    });
    const searchInput = screen.getByPlaceholderText('搜索事件名称...');
    fireEvent.change(searchInput, { target: { value: 'event_1' } });
    expect(searchInput.value).toBe('event_1');
  });

  it('should handle category filter', async () => {
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    await waitFor(() => {
      expect(screen.getByText('全部分类')).toBeInTheDocument();
    });
  });

  it('should render events table', async () => {
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    await waitFor(() => {
      expect(screen.getByText('事件名称')).toBeInTheDocument();
      expect(screen.getByText('中文名称')).toBeInTheDocument();
      expect(screen.getByText('分类')).toBeInTheDocument();
      expect(screen.getByText('参数数量')).toBeInTheDocument();
      expect(screen.getByText('操作')).toBeInTheDocument();
    });
  });

  it('should handle event deletion', async () => {
    renderWithMockedApollo(
      <MockedProvider mocks={deleteMocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    await waitFor(() => {
      expect(screen.getByText('event_1')).toBeInTheDocument();
    });
    // 找到删除按钮
    const deleteButtons = screen.getAllByText('删除');
    expect(deleteButtons.length).toBeGreaterThan(0);
  });

  it('should handle no game context', () => {
    // 动态修改mock返回值为null
    mockOutletContext.mockReturnValue(createMockGameContext({ currentGame: null }));
    
    renderWithMockedApollo(
      <MockedProvider mocks={mocks} addTypename={false}>
        <EventsListGraphQL />
      </MockedProvider>
    );
    expect(screen.getByText('查看事件列表需要先选择游戏')).toBeInTheDocument();
  });
});
