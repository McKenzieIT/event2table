/**
 * GraphQL 集成测试
 *
 * 测试GraphQL查询和变更的完整流程
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import React from 'react';
import GameManagementModalGraphQL from '../../features/games/GameManagementModalGraphQL';
import EventManagementModalGraphQL from '../../features/events/EventManagementModalGraphQL';
import AddGameModalGraphQL from '../../features/games/AddGameModalGraphQL';
import AddEventModalGraphQL from '../../features/events/AddEventModalGraphQL';
import {
  GET_GAMES,
  SEARCH_GAMES,
  GET_EVENTS,
  SEARCH_EVENTS,
} from '../../graphql/queries';
import {
  CREATE_GAME,
  UPDATE_GAME,
  DELETE_GAME,
  CREATE_EVENT,
  UPDATE_EVENT,
  DELETE_EVENT,
} from '../../graphql/mutations';

// Mock数据
const mockGames = [
  { gid: 1001, name: 'Game 1', odsDb: 'ieu_ods', eventCount: 10, parameterCount: 50 },
  { gid: 1002, name: 'Game 2', odsDb: 'ieu_ods', eventCount: 20, parameterCount: 100 },
];

const mockEvents = [
  { id: 1, eventName: 'login', eventNameCn: '登录', categoryName: '用户行为', paramCount: 5 },
  { id: 2, eventName: 'purchase', eventNameCn: '购买', categoryName: '支付相关', paramCount: 10 },
];

describe('GraphQL Integration Tests', () => {
  describe('GameManagementModalGraphQL', () => {
    const mocks = [
      {
        request: {
          query: GET_GAMES,
          variables: { limit: 100, offset: 0 },
        },
        result: {
          data: {
            games: mockGames,
          },
        },
      },
      {
        request: {
          query: SEARCH_GAMES,
          variables: { query: 'Game 1' },
        },
        result: {
          data: {
            searchGames: [mockGames[0]],
          },
        },
      },
      {
        request: {
          query: UPDATE_GAME,
          variables: { gid: 1001, name: 'Updated Game 1', odsDb: 'ieu_ods' },
        },
        result: {
          data: {
            updateGame: {
              ok: true,
              game: { gid: 1001, name: 'Updated Game 1', odsDb: 'ieu_ods' },
              errors: null,
            },
          },
        },
      },
      {
        request: {
          query: DELETE_GAME,
          variables: { gid: 1001, confirm: false },
        },
        result: {
          data: {
            deleteGame: {
              ok: true,
              message: 'Game deleted successfully',
              errors: null,
            },
          },
        },
      },
    ];

    it('should render games list', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待加载完成
      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // 检查游戏列表是否渲染
      await waitFor(() => {
        expect(screen.getByText('Game 1')).toBeInTheDocument();
        expect(screen.getByText('Game 2')).toBeInTheDocument();
      });
    });

    it('should search games', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待加载完成
      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // 输入搜索关键词
      const searchInput = screen.getByPlaceholderText('搜索游戏名称或GID...');
      fireEvent.change(searchInput, { target: { value: 'Game 1' } });

      // 等待搜索结果
      await waitFor(() => {
        expect(screen.getByText('Game 1')).toBeInTheDocument();
      });
    });

    it('should select and edit a game', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待加载完成
      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // 点击游戏项
      const gameItem = screen.getByText('Game 1').closest('.game-item');
      fireEvent.click(gameItem);

      // 检查游戏详情是否显示
      await waitFor(() => {
        expect(screen.getByText('游戏详情')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Game 1')).toBeInTheDocument();
      });
    });
  });

  describe('EventManagementModalGraphQL', () => {
    const mocks = [
      {
        request: {
          query: GET_EVENTS,
          variables: { gameGid: 1001, limit: 100, offset: 0 },
        },
        result: {
          data: {
            events: mockEvents,
          },
        },
      },
      {
        request: {
          query: SEARCH_EVENTS,
          variables: { query: 'login', gameGid: 1001 },
        },
        result: {
          data: {
            searchEvents: [mockEvents[0]],
          },
        },
      },
    ];

    it('should render events list', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <EventManagementModalGraphQL isOpen={true} onClose={() => {}} gameGid={1001} />
        </MockedProvider>
      );

      // 等待加载完成
      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // 检查事件列表是否渲染
      await waitFor(() => {
        expect(screen.getByText('login')).toBeInTheDocument();
        expect(screen.getByText('purchase')).toBeInTheDocument();
      });
    });

    it('should search events', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <EventManagementModalGraphQL isOpen={true} onClose={() => {}} gameGid={1001} />
        </MockedProvider>
      );

      // 等待加载完成
      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // 输入搜索关键词
      const searchInput = screen.getByPlaceholderText('搜索事件名称...');
      fireEvent.change(searchInput, { target: { value: 'login' } });

      // 等待搜索结果
      await waitFor(() => {
        expect(screen.getByText('login')).toBeInTheDocument();
      });
    });
  });

  describe('AddGameModalGraphQL', () => {
    const mocks = [
      {
        request: {
          query: CREATE_GAME,
          variables: { gid: 1003, name: 'New Game', odsDb: 'ieu_ods' },
        },
        result: {
          data: {
            createGame: {
              ok: true,
              game: { gid: 1003, name: 'New Game', odsDb: 'ieu_ods' },
              errors: null,
            },
          },
        },
      },
    ];

    it('should create a new game', async () => {
      const onClose = jest.fn();

      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <AddGameModalGraphQL isOpen={true} onClose={onClose} />
        </MockedProvider>
      );

      // 填写表单
      const gidInput = screen.getByPlaceholderText('请输入游戏GID（数字）');
      const nameInput = screen.getByPlaceholderText('请输入游戏名称');

      fireEvent.change(gidInput, { target: { value: '1003' } });
      fireEvent.change(nameInput, { target: { value: 'New Game' } });

      // 提交表单
      const submitButton = screen.getByText('创建游戏');
      fireEvent.click(submitButton);

      // 等待创建完成
      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });
    });

    it('should validate form inputs', async () => {
      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <AddGameModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 提交空表单
      const submitButton = screen.getByText('创建游戏');
      fireEvent.click(submitButton);

      // 检查错误消息
      await waitFor(() => {
        expect(screen.getByText('GID不能为空')).toBeInTheDocument();
        expect(screen.getByText('游戏名称不能为空')).toBeInTheDocument();
      });
    });
  });

  describe('AddEventModalGraphQL', () => {
    const mocks = [
      {
        request: {
          query: CREATE_EVENT,
          variables: {
            gameGid: 1001,
            eventName: 'new_event',
            eventNameCn: '新事件',
            categoryId: 1,
            includeInCommonParams: false,
          },
        },
        result: {
          data: {
            createEvent: {
              ok: true,
              event: { id: 3, eventName: 'new_event', eventNameCn: '新事件' },
              errors: null,
            },
          },
        },
      },
    ];

    it('should create a new event', async () => {
      const onClose = jest.fn();

      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <AddEventModalGraphQL isOpen={true} onClose={onClose} gameGid={1001} />
        </MockedProvider>
      );

      // 填写表单
      const eventNameInput = screen.getByPlaceholderText('例如: user_login');
      const eventNameCnInput = screen.getByPlaceholderText('例如: 用户登录');

      fireEvent.change(eventNameInput, { target: { value: 'new_event' } });
      fireEvent.change(eventNameCnInput, { target: { value: '新事件' } });

      // 选择分类
      const categorySelect = screen.getByLabelText('事件分类');
      fireEvent.change(categorySelect, { target: { value: '1' } });

      // 提交表单
      const submitButton = screen.getByText('创建事件');
      fireEvent.click(submitButton);

      // 等待创建完成
      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });
    });

    it('should validate event name format', async () => {
      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <AddEventModalGraphQL isOpen={true} onClose={() => {}} gameGid={1001} />
        </MockedProvider>
      );

      // 输入无效的事件名称
      const eventNameInput = screen.getByPlaceholderText('例如: user_login');
      fireEvent.change(eventNameInput, { target: { value: 'InvalidEventName' } });

      // 提交表单
      const submitButton = screen.getByText('创建事件');
      fireEvent.click(submitButton);

      // 检查错误消息
      await waitFor(() => {
        expect(screen.getByText('事件名称只能包含小写字母和下划线')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle GraphQL errors', async () => {
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
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待错误显示
      await waitFor(() => {
        expect(screen.getByText(/加载失败/)).toBeInTheDocument();
      });
    });

    it('should handle mutation errors', async () => {
      const errorMocks = [
        {
          request: {
            query: CREATE_GAME,
            variables: { gid: 1001, name: 'Existing Game', odsDb: 'ieu_ods' },
          },
          result: {
            data: {
              createGame: {
                ok: false,
                game: null,
                errors: ['Game GID already exists'],
              },
            },
          },
        },
      ];

      render(
        <MockedProvider mocks={errorMocks} addTypename={false}>
          <AddGameModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 填写表单
      const gidInput = screen.getByPlaceholderText('请输入游戏GID（数字）');
      const nameInput = screen.getByPlaceholderText('请输入游戏名称');

      fireEvent.change(gidInput, { target: { value: '1001' } });
      fireEvent.change(nameInput, { target: { value: 'Existing Game' } });

      // 提交表单
      const submitButton = screen.getByText('创建游戏');
      fireEvent.click(submitButton);

      // 等待错误消息
      await waitFor(() => {
        expect(screen.getByText('Game GID already exists')).toBeInTheDocument();
      });
    });
  });

  describe('Cache Behavior', () => {
    it('should use cached data for subsequent queries', async () => {
      const mocks = [
        {
          request: {
            query: GET_GAMES,
            variables: { limit: 100, offset: 0 },
          },
          result: {
            data: {
              games: mockGames,
            },
          },
        },
      ];

      const { unmount } = render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待第一次查询完成
      await waitFor(() => {
        expect(screen.getByText('Game 1')).toBeInTheDocument();
      });

      // 卸载并重新挂载
      unmount();

      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 应该立即显示缓存数据（不需要等待）
      expect(screen.getByText('Game 1')).toBeInTheDocument();
    });
  });
});
