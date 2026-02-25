/**
 * DashboardGraphQL 功能测试
 *
 * 测试GraphQL版本的Dashboard页面功能
 */

import { render, screen, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import DashboardGraphQL from '../DashboardGraphQL';
import { GET_GAMES } from '@/graphql/queries';

// Mock useGameStore
vi.mock('@/stores/gameStore', () => ({
  useGameStore: () => ({
    openGameManagementModal: vi.fn(),
  }),
}));

// Mock useOutletContext
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: () => ({
      currentGame: { gid: 1, name: 'Test Game' },
    }),
  };
});

const mocks = [
  {
    request: {
      query: GET_GAMES,
      variables: { limit: 100, offset: 0 },
    },
    result: {
      data: {
        games: [
          {
            gid: 1,
            name: 'Game 1',
            odsDb: 'db1',
            eventCount: 10,
            parameterCount: 50,
          },
          {
            gid: 2,
            name: 'Game 2',
            odsDb: 'db2',
            eventCount: 20,
            parameterCount: 100,
          },
        ],
      },
    },
  },
];

describe('DashboardGraphQL', () => {
  it('should render dashboard with loading state', () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <DashboardGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    // 检查加载状态
    expect(screen.getByText('正在加载仪表板...')).toBeInTheDocument();
  });

  it('should render dashboard with games data', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <DashboardGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    // 等待数据加载
    await waitFor(() => {
      expect(screen.getByText('Event2Table')).toBeInTheDocument();
    });

    // 检查统计数据
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // 游戏总数
    });
  });

  it('should display correct statistics', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <DashboardGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      // 检查统计卡片
      expect(screen.getByText('游戏总数')).toBeInTheDocument();
      expect(screen.getByText('事件总数')).toBeInTheDocument();
      expect(screen.getByText('参数总数')).toBeInTheDocument();
    });
  });

  it('should render quick actions', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <DashboardGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('快速操作')).toBeInTheDocument();
      expect(screen.getByText('管理游戏')).toBeInTheDocument();
      expect(screen.getByText('管理事件')).toBeInTheDocument();
      expect(screen.getByText('HQL画布')).toBeInTheDocument();
      expect(screen.getByText('流程管理')).toBeInTheDocument();
    });
  });

  it('should handle error state', async () => {
    const errorMocks = [
      {
        request: {
          query: GET_GAMES,
          variables: { limit: 100, offset: 0 },
        },
        error: new Error('Network error'),
      },
    ];

    render(
      <MockedProvider mocks={errorMocks} addTypename={false}>
        <BrowserRouter>
          <DashboardGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    // 等待错误状态
    await waitFor(() => {
      expect(screen.getByText('Event2Table')).toBeInTheDocument();
    });
  });
});
