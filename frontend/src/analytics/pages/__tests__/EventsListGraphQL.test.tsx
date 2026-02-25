/**
 * EventsListGraphQL 功能测试
 *
 * 测试GraphQL版本的EventsList页面功能
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import EventsListGraphQL from '../EventsListGraphQL';
import { GET_EVENTS, GET_CATEGORIES } from '@/graphql/queries';
import { DELETE_EVENT } from '@/graphql/mutations';

// Mock useOutletContext
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: () => ({
      currentGame: { gid: 1, name: 'Test Game' },
    }),
    useNavigate: () => vi.fn(),
  };
});

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

const mocks = [
  {
    request: {
      query: GET_EVENTS,
      variables: {
        gameGid: 1,
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
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('should render events list with data', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
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
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('总事件数')).toBeInTheDocument();
      expect(screen.getByText('已分类')).toBeInTheDocument();
      expect(screen.getByText('未分类')).toBeInTheDocument();
    });
  });

  it('should render action buttons', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('导入Excel')).toBeInTheDocument();
      expect(screen.getByTestId('add-event-button')).toBeInTheDocument();
    });
  });

  it('should handle search input', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
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
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('全部分类')).toBeInTheDocument();
    });
  });

  it('should render events table', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
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
    render(
      <MockedProvider mocks={deleteMocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
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
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useOutletContext: () => ({
          currentGame: null,
        }),
        useNavigate: () => vi.fn(),
      };
    });

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <EventsListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    expect(screen.getByText('查看事件列表需要先选择游戏')).toBeInTheDocument();
  });
});
