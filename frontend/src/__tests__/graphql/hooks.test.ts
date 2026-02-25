/**
 * GraphQL Hooks 单元测试
 */

import { renderHook, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
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
} from '../../graphql/hooks';
import {
  GET_GAMES,
  GET_GAME,
  SEARCH_GAMES,
  GET_EVENTS,
  GET_EVENT,
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

const mockGame = { gid: 1001, name: 'Game 1', odsDb: 'ieu_ods', eventCount: 10, parameterCount: 50 };

const mockEvents = [
  { id: 1, eventName: 'login', eventNameCn: '登录', categoryName: '用户行为', paramCount: 5 },
  { id: 2, eventName: 'purchase', eventNameCn: '购买', categoryName: '支付相关', paramCount: 10 },
];

const mockEvent = {
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
const wrapper = ({ children }) => (
  <MockedProvider mocks={[]} addTypename={false}>
    {children}
  </MockedProvider>
);

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
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
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
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.game).toEqual(mockGame);
    });

    it('should skip query when gid is null', () => {
      const { result } = renderHook(() => useGame(null), { wrapper });

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useSearchGames', () => {
    it('should search games', async () => {
      const mocks = [
        {
          request: {
            query: SEARCH_GAMES,
            variables: { query: 'Game' },
          },
          result: {
            data: {
              searchGames: mockGames,
            },
          },
        },
      ];

      const { result } = renderHook(() => useSearchGames('Game'), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.searchGames).toEqual(mockGames);
    });

    it('should skip query when query is empty', () => {
      const { result } = renderHook(() => useSearchGames(''), { wrapper });

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useEvents', () => {
    it('should fetch events for a game', async () => {
      const mocks = [
        {
          request: {
            query: GET_EVENTS,
            variables: { gameGid: 1001, limit: 50, offset: 0 },
          },
          result: {
            data: {
              events: mockEvents,
            },
          },
        },
      ];

      const { result } = renderHook(() => useEvents(1001, 50, 0), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.events).toEqual(mockEvents);
    });

    it('should skip query when gameGid is null', () => {
      const { result } = renderHook(() => useEvents(null), { wrapper });

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
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.event).toEqual(mockEvent);
    });
  });

  describe('useSearchEvents', () => {
    it('should search events', async () => {
      const mocks = [
        {
          request: {
            query: SEARCH_EVENTS,
            variables: { query: 'login', gameGid: 1001 },
          },
          result: {
            data: {
              searchEvents: mockEvents,
            },
          },
        },
      ];

      const { result } = renderHook(() => useSearchEvents('login', 1001), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.searchEvents).toEqual(mockEvents);
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
                game: { gid: 1003, name: 'Game 3', odsDb: 'ieu_ods' },
                errors: null,
              },
            },
          },
        },
        {
          request: {
            query: GET_GAMES,
            variables: { limit: 20, offset: 0 },
          },
          result: {
            data: {
              games: [...mockGames, { gid: 1003, name: 'Game 3', odsDb: 'ieu_ods' }],
            },
          },
        },
      ];

      const { result } = renderHook(() => useCreateGame(), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [createGame] = result.current;
      const response = await createGame({
        variables: { gid: 1003, name: 'Game 3', odsDb: 'ieu_ods' },
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
                game: { gid: 1001, name: 'Updated Game 1', odsDb: 'ieu_ods' },
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useUpdateGame(), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [updateGame] = result.current;
      const response = await updateGame({
        variables: { gid: 1001, name: 'Updated Game 1', odsDb: 'ieu_ods' },
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
                ok: true,
                message: 'Game deleted successfully',
                errors: null,
              },
            },
          },
        },
        {
          request: {
            query: GET_GAMES,
            variables: { limit: 20, offset: 0 },
          },
          result: {
            data: {
              games: [mockGames[1]],
            },
          },
        },
      ];

      const { result } = renderHook(() => useDeleteGame(), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [deleteGame] = result.current;
      const response = await deleteGame({
        variables: { gid: 1001, confirm: false },
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
              includeInCommonParams: false,
            },
          },
          result: {
            data: {
              createEvent: {
                ok: true,
                event: { id: 3, eventName: 'logout', eventNameCn: '登出' },
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useCreateEvent(), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [createEvent] = result.current;
      const response = await createEvent({
        variables: {
          gameGid: 1001,
          eventName: 'logout',
          eventNameCn: '登出',
          categoryId: 1,
          includeInCommonParams: false,
        },
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
              includeInCommonParams: true,
            },
          },
          result: {
            data: {
              updateEvent: {
                ok: true,
                event: { id: 1, eventNameCn: '用户登录' },
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useUpdateEvent(), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [updateEvent] = result.current;
      const response = await updateEvent({
        variables: {
          id: 1,
          eventNameCn: '用户登录',
          categoryId: 1,
          includeInCommonParams: true,
        },
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
                ok: true,
                message: 'Event deleted successfully',
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useDeleteEvent(), {
        wrapper: ({ children }) => (
          <MockedProvider mocks={mocks} addTypename={false}>
            {children}
          </MockedProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [deleteEvent] = result.current;
      const response = await deleteEvent({
        variables: { id: 1 },
      });

      expect(response.data?.deleteEvent?.ok).toBe(true);
    });
  });
});
