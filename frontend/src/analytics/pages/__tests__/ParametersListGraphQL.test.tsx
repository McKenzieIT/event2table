/**
 * ParametersListGraphQL 功能测试
 *
 * 测试GraphQL版本的ParametersList页面功能
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
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

const mocks = [
  {
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
        parametersManagement: [
          {
            id: 1,
            eventId: 1,
            paramName: 'param_1',
            paramNameCn: '参数1',
            paramType: 'string',
            paramDescription: '描述1',
            jsonPath: '$.param1',
            isActive: true,
            version: 1,
            usageCount: 5,
            eventsCount: 3,
            isCommon: true,
            eventCode: 'event_1',
            eventName: '事件1',
            gameGid: 1,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-02T00:00:00Z',
          },
          {
            id: 2,
            eventId: 1,
            paramName: 'param_2',
            paramNameCn: '参数2',
            paramType: 'int',
            paramDescription: '描述2',
            jsonPath: '$.param2',
            isActive: true,
            version: 1,
            usageCount: 10,
            eventsCount: 5,
            isCommon: false,
            eventCode: 'event_2',
            eventName: '事件2',
            gameGid: 1,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-02T00:00:00Z',
          },
        ],
      },
    },
  },
];

describe('ParametersListGraphQL', () => {
  it('should render parameters list with loading state', () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    expect(screen.getByText('正在加载参数...')).toBeInTheDocument();
  });

  it('should render parameters list with data', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('参数管理 (GraphQL版本)')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('param_1')).toBeInTheDocument();
      expect(screen.getByText('参数1')).toBeInTheDocument();
      expect(screen.getByText('param_2')).toBeInTheDocument();
      expect(screen.getByText('参数2')).toBeInTheDocument();
    });
  });

  it('should display statistics cards', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('总参数数')).toBeInTheDocument();
      expect(screen.getByText('唯一参数名')).toBeInTheDocument();
      expect(screen.getByText('公参数量')).toBeInTheDocument();
      expect(screen.getByText('平均参数/事件')).toBeInTheDocument();
    });
  });

  it('should render action buttons', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('使用分析')).toBeInTheDocument();
      expect(screen.getByText('变更历史')).toBeInTheDocument();
      expect(screen.getByText('关系网络')).toBeInTheDocument();
      expect(screen.getByText('进入公参管理')).toBeInTheDocument();
      expect(screen.getByText('导出Excel')).toBeInTheDocument();
    });
  });

  it('should handle search input', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText('搜索参数名...')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('搜索参数名...');
    fireEvent.change(searchInput, { target: { value: 'param_1' } });

    expect(searchInput.value).toBe('param_1');
  });

  it('should handle type filter', async () => {
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
  });

  it('should render parameters table', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('参数名')).toBeInTheDocument();
      expect(screen.getByText('中文名')).toBeInTheDocument();
      expect(screen.getByText('类型')).toBeInTheDocument();
      expect(screen.getByText('事件')).toBeInTheDocument();
      expect(screen.getByText('是否公参')).toBeInTheDocument();
      expect(screen.getByText('操作')).toBeInTheDocument();
    });
  });

  it('should display parameter types as badges', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('string')).toBeInTheDocument();
      expect(screen.getByText('int')).toBeInTheDocument();
    });
  });

  it('should display common parameter badges', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    await waitFor(() => {
      const yesBadges = screen.getAllByText('是');
      const noBadges = screen.getAllByText('否');
      expect(yesBadges.length).toBeGreaterThan(0);
      expect(noBadges.length).toBeGreaterThan(0);
    });
  });

  it('should handle no game context', () => {
    vi.mock('@/stores/gameStore', () => ({
      useGameStore: () => ({
        currentGame: null,
      }),
    }));

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <ParametersListGraphQL />
        </BrowserRouter>
      </MockedProvider>
    );

    expect(screen.getByText('查看参数管理需要先选择游戏')).toBeInTheDocument();
  });
});
