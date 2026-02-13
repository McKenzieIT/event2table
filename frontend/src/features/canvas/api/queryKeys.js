// Define base keys first to avoid circular references
const eventConfigsBase = ['event-configs'];
const flowsBase = ['flows'];
const gamesBase = ['games'];
const canvasBase = ['canvas'];

export const queryKeys = {
  eventConfigs: {
    all: eventConfigsBase,
    lists: () => [...eventConfigsBase, 'list'],
    list: (gameGid) =>
      [...eventConfigsBase, 'list', gameGid],
    details: () => [...eventConfigsBase, 'detail'],
    detail: (configId) =>
      [...eventConfigsBase, 'detail', configId],
  },

  flows: {
    all: flowsBase,
    lists: () => [...flowsBase, 'list'],
    list: (gameGid) =>
      [...flowsBase, 'list', gameGid].filter(Boolean),
    details: () => [...flowsBase, 'detail'],
    detail: (flowId) =>
      [...flowsBase, 'detail', flowId],
  },

  games: {
    all: gamesBase,
    details: () => [...gamesBase, 'detail'],
    detail: (gameGid) =>
      [...gamesBase, 'detail', gameGid],
  },

  canvas: {
    all: canvasBase,
    health: () => [...canvasBase, 'health'],
  },
};