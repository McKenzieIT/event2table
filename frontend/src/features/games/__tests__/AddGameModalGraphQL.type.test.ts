/**
 * Type Migration Test for AddGameModalGraphQL
 *
 * TDD Approach:
 * 1. Verify current manual types work
 * 2. Verify generated types are compatible
 * 3. Migrate to generated types
 * 4. Ensure type safety
 */

import { GameType, CreateGameMutation, CreateGameMutationVariables } from '@types/api.generated';

// Test 1: Manual Game interface (current implementation)
interface ManualGame {
  gid: number;
  name: string;
  odsDb: string;
  eventCount?: number;
  parameterCount?: number;
  description?: string;
  dwdPrefix?: string;
}

// Test 2: Generated GameType should be compatible
const testGameTypeCompatibility = (game: GameType): ManualGame => {
  return {
    gid: game.gid,
    name: game.name,
    odsDb: game.odsDb,
    eventCount: game.eventCount ?? undefined,
    parameterCount: game.parameterCount ?? undefined,
    description: game.iconPath ?? undefined, // Map iconPath to description for now
    dwdPrefix: undefined, // Not in GameType yet
  };
};

// Test 3: CreateGameMutation variables should use generated types
const testCreateGameVariables = (): CreateGameMutationVariables => {
  return {
    gid: 10000147,
    name: 'Test Game',
    odsDb: 'ieu_ods',
  };
};

// Test 4: Mutation response should use generated types
const testMutationResponse = (response: CreateGameMutation): boolean => {
  return response.createGame?.ok ?? false;
};

describe('Type Migration - AddGameModalGraphQL', () => {
  it('should have compatible GameType', () => {
    const mockGame: GameType = {
      __typename: 'GameType',
      gid: 10000147,
      name: 'Test Game',
      odsDb: 'ieu_ods',
      id: 1,
      eventCount: 10,
      parameterCount: 20,
    };

    const manualGame = testGameTypeCompatibility(mockGame);
    expect(manualGame.gid).toBe(10000147);
    expect(manualGame.name).toBe('Test Game');
    expect(manualGame.odsDb).toBe('ieu_ods');
  });

  it('should accept CreateGameMutationVariables', () => {
    const variables = testCreateGameVariables();
    expect(variables.gid).toBe(10000147);
    expect(variables.name).toBe('Test Game');
    expect(variables.odsDb).toBe('ieu_ods');
  });

  it('should handle CreateGameMutation response', () => {
    const mockResponse: CreateGameMutation = {
      __typename: 'Mutation',
      createGame: {
        __typename: 'CreateGame',
        ok: true,
        errors: [],
        game: {
          __typename: 'GameType',
          gid: 10000147,
          name: 'Test Game',
          odsDb: 'ieu_ods',
          id: 1,
        },
      },
    };

    const result = testMutationResponse(mockResponse);
    expect(result).toBe(true);
  });
});
