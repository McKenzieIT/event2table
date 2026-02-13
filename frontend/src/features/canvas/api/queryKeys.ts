/**
 * React Query Keys for Canvas Module
 *
 * Centralized query key definitions for React Query cache management
 */

import type { QueryKey } from '@tanstack/react-query';

// Define base keys first to avoid circular references
const eventConfigsBase = ['event-configs'] as const;
const flowsBase = ['flows'] as const;
const gamesBase = ['games'] as const;
const canvasBase = ['canvas'] as const;

interface QueryKeys {
  eventConfigs: {
    all: QueryKey;
    lists: () => QueryKey;
    list: (gameGid: number) => QueryKey;
    details: () => QueryKey;
    detail: (configId: number) => QueryKey;
  };
  flows: {
    all: QueryKey;
    lists: () => QueryKey;
    list: (gameGid: number) => QueryKey;
    details: () => QueryKey;
    detail: (flowId: number) => QueryKey;
  };
  games: {
    all: QueryKey;
    details: () => QueryKey;
    detail: (gameGid: number) => QueryKey;
  };
  canvas: {
    all: QueryKey;
    health: () => QueryKey;
  };
}

export const queryKeys: QueryKeys = {
  eventConfigs: {
    all: eventConfigsBase,
    lists: () => [...eventConfigsBase, 'list'],
    list: (gameGid: number) => [...eventConfigsBase, 'list', gameGid],
    details: () => [...eventConfigsBase, 'detail'],
    detail: (configId: number) => [...eventConfigsBase, 'detail', configId],
  },

  flows: {
    all: flowsBase,
    lists: () => [...flowsBase, 'list'],
    list: (gameGid: number) =>
      [...flowsBase, 'list', gameGid].filter(Boolean),
    details: () => [...flowsBase, 'detail'],
    detail: (flowId: number) => [...flowsBase, 'detail', flowId],
  },

  games: {
    all: gamesBase,
    details: () => [...gamesBase, 'detail'],
    detail: (gameGid: number) => [...gamesBase, 'detail', gameGid],
  },

  canvas: {
    all: canvasBase,
    health: () => [...canvasBase, 'health'],
  },
};
