// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * GraphQL Hooks 单元测试
 */

import React from 'react';
import { renderHook, waitFor, act } from '@test/test-utils';
import { MockedProvider } from '@apollo/client/testing/react';
import { describe, it, expect } from 'vitest';
import {
  useGames,
  useGame,
  useSearchGames,
  useEvents,
  useEvent,
  useSearchEvents,
  useCreateGame,
  useUpdateGame,
  useDeleteGame,
  useCreateEvent,
  useUpdateEvent,
  useDeleteEvent,
} from '../../shared/graphql/hooks';
import {
  GET_GAMES,
  GET_GAME,
  SEARCH_GAMES,
  GET_EVENTS,
  GET_EVENT,
  SEARCH_EVENTS,
} from '../../shared/graphql/queries';
import {
  CREATE_GAME,
  UPDATE_GAME,
  DELETE_GAME,
  CREATE_EVENT,
  UPDATE_EVENT,
  DELETE_EVENT,
} from '../../shared/graphql/operations';

// Mock数据
const mockGames = [
  { __typename: 'Game', gid: 1001, name: 'Game 1', odsDb: 'ieu_ods', eventCount: 10, parameterCount: 50 },
  { __typename: 'Game', gid: 1002, name: 'Game 2', odsDb: 'ieu_ods', eventCount: 20, parameterCount: 100 },
];

const mockGame = { __typename: 'Game', gid: 1001, name: 'Game 1', odsDb: 'ieu_ods', eventCount: 10, parameterCount: 50 };

const mockEvent = {
  __typename: 'Event',
  id: 1,
  gameGid: 1001,
  eventName: 'login',
  eventNameCn: '登录',
  categoryId: 1,
  categoryName: '用户行为',
  sourceTable: 'log_events',
  targetTable: 'dwd_events',
  paramCount: 5,
};

// 测试wrapper
const createWrapper = (mocks: any[] = []) => {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <MockedProvider mocks={mocks} addTypename={false}>
        {children}
      </MockedProvider>
    );
  };
};

describe('GraphQL Hooks', () => {
  describe('useGames', () => {
    it('should fetch games list', async () => {
      const mocks = [
        {
          request: {
            query: GET_GAMES,
            variables: { limit: 20, offset: 0 },
          },
          result: {
            data: {
              games: mockGames,
            },
          },
        },
      ];

      const { result } = renderHook(() => useGames(20, 0), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.games).toEqual(mockGames);
    });
  });

  describe('useGame', () => {
    it('should fetch a single game', async () => {
      const mocks = [
        {
          request: {
            query: GET_GAME,
            variables: { gid: 1001 },
          },
          result: {
            data: {
              game: mockGame,
            },
          },
        },
      ];

      const { result } = renderHook(() => useGame(1001), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.game).toEqual(mockGame);
    });

    it('should skip query when gid is null', () => {
      const { result } = renderHook(() => useGame(null as any), {
        wrapper: createWrapper([]),
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useSearchGames', () => {
    it('should search games', async () => {
      const searchMockGames = [
        { __typename: 'Game', gid: 1001, name: 'Game 1', odsDb: 'ieu_ods' },
        { __typename: 'Game', gid: 1002, name: 'Game 2', odsDb: 'ieu_ods' },
      ];

      const mocks = [
        {
          request: {
            query: SEARCH_GAMES,
            variables: { query: 'Game' },
          },
          result: {
            data: {
              searchGames: searchMockGames,
            },
          },
        },
      ];

      const { result } = renderHook(() => useSearchGames('Game'), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.searchGames).toEqual(searchMockGames);
    });

    it('should skip query when query is empty', () => {
      const { result } = renderHook(() => useSearchGames(''), {
        wrapper: createWrapper([]),
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useEvents', () => {
    it('should fetch events for a game', async () => {
      const eventsMock = [
        { 
          __typename: 'Event', 
          id: 1, 
          eventName: 'login', 
          eventNameCn: '登录', 
          categoryId: 1, 
          categoryName: '用户行为', 
          sourceTable: 'log_events', 
          targetTable: 'dwd_events', 
          paramCount: 5 
        },
        { 
          __typename: 'Event', 
          id: 2, 
          eventName: 'purchase', 
          eventNameCn: '购买', 
          categoryId: 2, 
          categoryName: '支付相关', 
          sourceTable: 'log_events', 
          targetTable: 'dwd_events', 
          paramCount: 10 
        },
      ];

      const mocks = [
        {
          request: {
            query: GET_EVENTS,
            variables: { gameGid: 1001, limit: 50, offset: 0 },
          },
          result: {
            data: {
              events: eventsMock,
            },
          },
        },
      ];

      const { result } = renderHook(() => useEvents(1001, 50, 0), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.events).toEqual(eventsMock);
    });

    it('should skip query when gameGid is null', () => {
      const { result } = renderHook(() => useEvents(null as any), {
        wrapper: createWrapper([]),
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useEvent', () => {
    it('should fetch a single event', async () => {
      const mocks = [
        {
          request: {
            query: GET_EVENT,
            variables: { id: 1 },
          },
          result: {
            data: {
              event: mockEvent,
            },
          },
        },
      ];

      const { result } = renderHook(() => useEvent(1), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.event).toEqual(mockEvent);
    });
  });

  describe('useSearchEvents', () => {
    it('should search events', async () => {
      const searchMockEvents = [
        { __typename: 'Event', id: 1, eventName: 'login', eventNameCn: '登录', gameGid: 1001 },
        { __typename: 'Event', id: 2, eventName: 'purchase', eventNameCn: '购买', gameGid: 1001 },
      ];

      const mocks = [
        {
          request: {
            query: SEARCH_EVENTS,
            variables: { query: 'login', gameGid: 1001 },
          },
          result: {
            data: {
              searchEvents: searchMockEvents,
            },
          },
        },
      ];

      const { result } = renderHook(() => useSearchEvents('login', 1001), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.searchEvents).toEqual(searchMockEvents);
    });
  });

  describe('useCreateGame', () => {
    it('should create a game', async () => {
      const mocks = [
        {
          request: {
            query: CREATE_GAME,
            variables: { gid: 1003, name: 'Game 3', odsDb: 'ieu_ods' },
          },
          result: {
            data: {
              createGame: {
                ok: true,
                game: { __typename: 'Game', gid: 1003, name: 'Game 3', odsDb: 'ieu_ods' },
                errors: null,
              },
            },
          },
        },
        // Refetch query mock for refetchQueries
        {
          request: {
            query: GET_GAMES,
            variables: { limit: 20, offset: 0 },
          },
          result: {
            data: {
              games: mockGames,
            },
          },
        },
      ];

      const { result } = renderHook(() => useCreateGame(), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      let response;
      await act(async () => {
        const [createGame] = result.current;
        response = await createGame({
          variables: { gid: 1003, name: 'Game 3', odsDb: 'ieu_ods' },
        });
      });

      expect(response.data?.createGame?.ok).toBe(true);
    });
  });

  describe('useUpdateGame', () => {
    it('should update a game', async () => {
      const mocks = [
        {
          request: {
            query: UPDATE_GAME,
            variables: { gid: 1001, name: 'Updated Game 1', odsDb: 'ieu_ods' },
          },
          result: {
            data: {
              updateGame: {
                ok: true,
                game: { __typename: 'Game', gid: 1001, name: 'Updated Game 1', odsDb: 'ieu_ods' },
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useUpdateGame(), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      let response;
      await act(async () => {
        const [updateGame] = result.current;
        response = await updateGame({
          variables: { gid: 1001, name: 'Updated Game 1', odsDb: 'ieu_ods' },
        });
      });

      expect(response.data?.updateGame?.ok).toBe(true);
    });
  });

  describe('useDeleteGame', () => {
    it('should delete a game', async () => {
      const mocks = [
        {
          request: {
            query: DELETE_GAME,
            variables: { gid: 1001, confirm: false },
          },
          result: {
            data: {
              deleteGame: {
                __typename: 'DeleteGamePayload',
                ok: true,
                message: 'Game deleted successfully',
                errors: null,
              },
            },
          },
        },
        // Refetch query mock for refetchQueries
        {
          request: {
            query: GET_GAMES,
            variables: { limit: 20, offset: 0 },
          },
          result: {
            data: {
              games: mockGames,
            },
          },
        },
      ];

      const { result } = renderHook(() => useDeleteGame(), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      let response;
      await act(async () => {
        const [deleteGame] = result.current;
        response = await deleteGame({
          variables: { gid: 1001, confirm: false },
        });
      });

      expect(response.data?.deleteGame?.ok).toBe(true);
    });
  });

  describe('useCreateEvent', () => {
    it('should create an event', async () => {
      const mocks = [
        {
          request: {
            query: CREATE_EVENT,
            variables: {
              gameGid: 1001,
              eventName: 'logout',
              eventNameCn: '登出',
              categoryId: 1,
            },
          },
          result: {
            data: {
              createEvent: {
                ok: true,
                event: { __typename: 'Event', id: 3, eventName: 'logout', eventNameCn: '登出' },
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useCreateEvent(), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      let response;
      await act(async () => {
        const [createEvent] = result.current;
        response = await createEvent({
          variables: {
            gameGid: 1001,
            eventName: 'logout',
            eventNameCn: '登出',
            categoryId: 1,
          },
        });
      });

      expect(response.data?.createEvent?.ok).toBe(true);
    });
  });

  describe('useUpdateEvent', () => {
    it('should update an event', async () => {
      const mocks = [
        {
          request: {
            query: UPDATE_EVENT,
            variables: {
              id: 1,
              eventNameCn: '用户登录',
              categoryId: 1,
            },
          },
          result: {
            data: {
              updateEvent: {
                ok: true,
                event: { __typename: 'Event', id: 1, eventNameCn: '用户登录' },
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useUpdateEvent(), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      let response;
      await act(async () => {
        const [updateEvent] = result.current;
        response = await updateEvent({
          variables: {
            id: 1,
            eventNameCn: '用户登录',
            categoryId: 1,
          },
        });
      });

      expect(response.data?.updateEvent?.ok).toBe(true);
    });
  });

  describe('useDeleteEvent', () => {
    it('should delete an event', async () => {
      const mocks = [
        {
          request: {
            query: DELETE_EVENT,
            variables: { id: 1 },
          },
          result: {
            data: {
              deleteEvent: {
                __typename: 'DeleteEventPayload',
                ok: true,
                message: 'Event deleted successfully',
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useDeleteEvent(), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      let response;
      await act(async () => {
        const [deleteEvent] = result.current;
        response = await deleteEvent({
          variables: { id: 1 },
        });
      });

      expect(response.data?.deleteEvent?.ok).toBe(true);
    });
  });
});
