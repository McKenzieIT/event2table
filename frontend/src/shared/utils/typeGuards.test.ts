// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * typeGuards.test.ts
 * Unit tests for type guard utilities
 */

import { describe, it, expect } from 'vitest';
import {
  isGame,
  isEvent,
  isParameter,
  isEventArray,
  isGameArray,
  isParameterArray,
  isApiResponse,
  assertGame,
  assertEvent,
  assertEventArray,
  assertGameArray,
  assertParameterArray,
  createArrayGuard,
  createApiResponseGuard,
  guards,
  type Game,
  type Event,
  type Parameter,
  type ApiResponse
} from './typeGuards';

describe('typeGuards', () => {
  describe('isGame', () => {
    it('should return true for valid Game object', () => {
      const game: Game = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'ieu_ods',
        created_at: '2024-01-01'
      };
      expect(isGame(game)).toBe(true);
    });

    it('should return false for invalid Game object', () => {
      expect(isGame(null)).toBe(false);
      expect(isGame(undefined)).toBe(false);
      expect(isGame({})).toBe(false);
      expect(isGame({ id: 1 })).toBe(false);
      expect(isGame({ id: '1' as any, gid: 10000147, name: 'Test', ods_db: 'ieu_ods' })).toBe(false);
    });

    it('should validate all required fields', () => {
      const validGame = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'ieu_ods',
        created_at: '2024-01-01'
      };

      expect(isGame({ ...validGame, id: '1' as any })).toBe(false);
      expect(isGame({ ...validGame, gid: '10000147' as any })).toBe(false);
      expect(isGame({ ...validGame, name: 123 as any })).toBe(false);
      expect(isGame({ ...validGame, ods_db: 123 as any })).toBe(false);
    });

    it('should allow objects with extra properties', () => {
      const gameWithExtras = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'ieu_ods',
        created_at: '2024-01-01',
        description: 'Extra property',
        version: 1
      };
      expect(isGame(gameWithExtras)).toBe(true);
    });
  });

  describe('isEvent', () => {
    it('should return true for valid Event object', () => {
      const event: Event = {
        id: 1,
        event_name: 'login',
        display_name: 'Login',
        game_gid: 10000147,
        event_type: 'user',
        created_at: '2024-01-01'
      };
      expect(isEvent(event)).toBe(true);
    });

    it('should return false for invalid Event object', () => {
      expect(isEvent(null)).toBe(false);
      expect(isEvent(undefined)).toBe(false);
      expect(isEvent({})).toBe(false);
      expect(isEvent({ id: 1 })).toBe(false);
    });

    it('should validate event_type values', () => {
      const baseEvent = {
        id: 1,
        event_name: 'test',
        display_name: 'Test',
        game_gid: 10000147,
        created_at: '2024-01-01'
      };

      expect(isEvent({ ...baseEvent, event_type: 'user' })).toBe(true);
      expect(isEvent({ ...baseEvent, event_type: 'system' })).toBe(true);
      expect(isEvent({ ...baseEvent, event_type: 'auto' })).toBe(true);
      // Note: TypeScript doesn't enforce literal types at runtime
      // Type guard would need additional validation for exact values
    });
  });

  describe('isParameter', () => {
    it('should return true for valid Parameter object', () => {
      const param: Parameter = {
        id: 1,
        param_name: 'zone_id',
        param_name_cn: '区域ID',
        param_type: 'int',
        game_gid: 10000147
      };
      expect(isParameter(param)).toBe(true);
    });

    it('should return false for invalid Parameter object', () => {
      expect(isParameter(null)).toBe(false);
      expect(isParameter(undefined)).toBe(false);
      expect(isParameter({})).toBe(false);
      expect(isParameter({ id: 1, param_name: 'test' })).toBe(false);
    });

    it('should allow null game_gid', () => {
      const param = {
        id: 1,
        param_name: 'zone_id',
        param_name_cn: '区域ID',
        param_type: 'int',
        game_gid: null
      };
      expect(isParameter(param)).toBe(true);
    });
  });

  describe('Array type guards', () => {
    describe('isGameArray', () => {
      it('should return true for array of Game objects', () => {
        const games: Game[] = [
          { id: 1, gid: 10000147, name: 'Game 1', ods_db: 'ieu_ods', created_at: '2024-01-01' },
          { id: 2, gid: 10000148, name: 'Game 2', ods_db: 'ieu_ods', created_at: '2024-01-02' }
        ];
        expect(isGameArray(games)).toBe(true);
      });

      it('should return false for mixed or invalid arrays', () => {
        expect(isGameArray([])).toBe(true); // Empty array is valid
        expect(isGameArray(null)).toBe(false);
        expect(isGameArray([{}])).toBe(false);
        expect(isGameArray([{ id: 1, gid: 10000147, name: 'Game', ods_db: 'ieu_ods', created_at: '2024-01-01' }, null])).toBe(false);
      });
    });

    describe('isEventArray', () => {
      it('should return true for array of Event objects', () => {
        const events: Event[] = [
          { id: 1, event_name: 'login', display_name: 'Login', game_gid: 10000147, event_type: 'user', created_at: '2024-01-01' },
          { id: 2, event_name: 'logout', display_name: 'Logout', game_gid: 10000147, event_type: 'user', created_at: '2024-01-02' }
        ];
        expect(isEventArray(events)).toBe(true);
      });

      it('should return false for invalid arrays', () => {
        expect(isEventArray([])).toBe(true);
        expect(isEventArray(null)).toBe(false);
        expect(isEventArray([{}])).toBe(false);
      });
    });

    describe('isParameterArray', () => {
      it('should return true for array of Parameter objects', () => {
        const params: Parameter[] = [
          { id: 1, param_name: 'zone_id', param_name_cn: '区域ID', param_type: 'int', game_gid: 10000147 },
          { id: 2, param_name: 'level', param_name_cn: '等级', param_type: 'int', game_gid: 10000147 }
        ];
        expect(isParameterArray(params)).toBe(true);
      });

      it('should return false for invalid arrays', () => {
        expect(isParameterArray([])).toBe(true);
        expect(isParameterArray(null)).toBe(false);
        expect(isParameterArray([{}])).toBe(false);
      });
    });
  });

  describe('isApiResponse', () => {
    it('should return true for valid API response', () => {
      const response: ApiResponse<Game[]> = {
        data: [],
        success: true,
        message: 'Success',
        timestamp: '2024-01-01'
      };
      expect(isApiResponse(response)).toBe(true);
    });

    it('should return true for minimal valid response', () => {
      const response = {
        data: [],
        success: true
      };
      expect(isApiResponse(response)).toBe(true);
    });

    it('should return false for invalid response', () => {
      expect(isApiResponse(null)).toBe(false);
      expect(isApiResponse(undefined)).toBe(false);
      expect(isApiResponse({})).toBe(false);
      expect(isApiResponse({ data: [] })).toBe(false);
      expect(isApiResponse({ success: true })).toBe(false);
      expect(isApiResponse({ data: [], success: 'true' as any })).toBe(false);
    });
  });

  describe('Assertion functions', () => {
    describe('assertGame', () => {
      it('should not throw for valid Game', () => {
        const game: Game = {
          id: 1,
          gid: 10000147,
          name: 'Test Game',
          ods_db: 'ieu_ods',
          created_at: '2024-01-01'
        };
        expect(() => assertGame(game)).not.toThrow();
      });

      it('should throw for invalid Game', () => {
        expect(() => assertGame(null)).toThrow('Invalid Game object');
        expect(() => assertGame({})).toThrow('Invalid Game object');
      });
    });

    describe('assertEvent', () => {
      it('should not throw for valid Event', () => {
        const event: Event = {
          id: 1,
          event_name: 'login',
          display_name: 'Login',
          game_gid: 10000147,
          event_type: 'user',
          created_at: '2024-01-01'
        };
        expect(() => assertEvent(event)).not.toThrow();
      });

      it('should throw for invalid Event', () => {
        expect(() => assertEvent(null)).toThrow('Invalid Event object');
        expect(() => assertEvent({})).toThrow('Invalid Event object');
      });
    });

    describe('assertEventArray', () => {
      it('should not throw for valid Event array', () => {
        const events: Event[] = [
          { id: 1, event_name: 'login', display_name: 'Login', game_gid: 10000147, event_type: 'user', created_at: '2024-01-01' }
        ];
        expect(() => assertEventArray(events)).not.toThrow();
      });

      it('should throw for invalid Event array', () => {
        expect(() => assertEventArray(null)).toThrow('Invalid Event array');
        expect(() => assertEventArray([{}])).toThrow('Invalid Event array');
      });
    });

    describe('assertGameArray', () => {
      it('should not throw for valid Game array', () => {
        const games: Game[] = [
          { id: 1, gid: 10000147, name: 'Game', ods_db: 'ieu_ods', created_at: '2024-01-01' }
        ];
        expect(() => assertGameArray(games)).not.toThrow();
      });

      it('should throw for invalid Game array', () => {
        expect(() => assertGameArray(null)).toThrow('Invalid Game array');
        expect(() => assertGameArray([{}])).toThrow('Invalid Game array');
      });
    });

    describe('assertParameterArray', () => {
      it('should not throw for valid Parameter array', () => {
        const params: Parameter[] = [
          { id: 1, param_name: 'zone_id', param_name_cn: '区域ID', param_type: 'int', game_gid: 10000147 }
        ];
        expect(() => assertParameterArray(params)).not.toThrow();
      });

      it('should throw for invalid Parameter array', () => {
        expect(() => assertParameterArray(null)).toThrow('Invalid Parameter array');
        expect(() => assertParameterArray([{}])).toThrow('Invalid Parameter array');
      });
    });
  });

  describe('createArrayGuard', () => {
    it('should create array guard for primitive types', () => {
      const isStringArray = createArrayGuard((item): item is string => typeof item === 'string');

      expect(isStringArray(['a', 'b', 'c'])).toBe(true);
      expect(isStringArray([])).toBe(true);
      expect(isStringArray(['a', 1, 'b'])).toBe(false);
      expect(isStringArray(null)).toBe(false);
    });

    it('should create array guard for complex types', () => {
      const isGameArrayCustom = createArrayGuard(isGame);

      const games: Game[] = [
        { id: 1, gid: 10000147, name: 'Game', ods_db: 'ieu_ods', created_at: '2024-01-01' }
      ];

      expect(isGameArrayCustom(games)).toBe(true);
      expect(isGameArrayCustom([])).toBe(true);
      expect(isGameArrayCustom([null])).toBe(false);
    });
  });

  describe('createApiResponseGuard', () => {
    it('should create API response guard for specific data type', () => {
      const isEventResponse = createApiResponseGuard(isEventArray);

      const validResponse = {
        data: [
          { id: 1, event_name: 'login', display_name: 'Login', game_gid: 10000147, event_type: 'user', created_at: '2024-01-01' }
        ],
        success: true
      };

      expect(isEventResponse(validResponse)).toBe(true);

      const invalidResponse = {
        data: [{}],
        success: true
      };

      expect(isEventResponse(invalidResponse)).toBe(false);
    });

    it('should work with isGameArray', () => {
      const isGameResponse = createApiResponseGuard(isGameArray);

      const response = {
        data: [
          { id: 1, gid: 10000147, name: 'Game', ods_db: 'ieu_ods', created_at: '2024-01-01' }
        ],
        success: true
      };

      expect(isGameResponse(response)).toBe(true);
    });
  });

  describe('guards collection', () => {
    it('should export all type guards', () => {
      expect(guards).toHaveProperty('isGame');
      expect(guards).toHaveProperty('isEvent');
      expect(guards).toHaveProperty('isParameter');
      expect(guards).toHaveProperty('isGameArray');
      expect(guards).toHaveProperty('isEventArray');
      expect(guards).toHaveProperty('isParameterArray');
      expect(guards).toHaveProperty('isApiResponse');
    });

    it('should work correctly when used from guards collection', () => {
      const game: Game = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'ieu_ods',
        created_at: '2024-01-01'
      };

      expect(guards.isGame(game)).toBe(true);
      expect(guards.isGame(null)).toBe(false);
    });
  });

  describe('type narrowing', () => {
    it('should narrow type with isGame', () => {
      const data: unknown = {
        id: 1,
        gid: 10000147,
        name: 'Game',
        ods_db: 'ieu_ods',
        created_at: '2024-01-01'
      };

      if (isGame(data)) {
        // TypeScript should know data is Game here
        expect(data.gid).toBe(10000147);
        expect(data.name.toUpperCase()).toBe('GAME');
      } else {
        fail('Should have been identified as Game');
      }
    });

    it('should narrow type with isEventArray', () => {
      const data: unknown = [
        { id: 1, event_name: 'login', display_name: 'Login', game_gid: 10000147, event_type: 'user', created_at: '2024-01-01' }
      ];

      if (isEventArray(data)) {
        expect(data[0].event_name).toBe('login');
        expect(data.length).toBe(1);
      } else {
        fail('Should have been identified as Event array');
      }
    });
  });

  describe('edge cases', () => {
    it('should handle objects with extra properties', () => {
      const gameWithExtras = {
        id: 1,
        gid: 10000147,
        name: 'Game',
        ods_db: 'ieu_ods',
        created_at: '2024-01-01',
        extraProp: 'value',
        anotherProp: 123
      };
      expect(isGame(gameWithExtras)).toBe(true);
    });

    it('should handle empty objects', () => {
      expect(isGame({})).toBe(false);
      expect(isEvent({})).toBe(false);
      expect(isParameter({})).toBe(false);
    });

    it('should handle missing optional fields', () => {
      // created_at is not validated in type guard
      const gameWithoutCreatedAt = {
        id: 1,
        gid: 10000147,
        name: 'Game',
        ods_db: 'ieu_ods'
      };
      expect(isGame(gameWithoutCreatedAt)).toBe(true);
    });

    it('should handle wrong types for fields', () => {
      const game = {
        id: '1' as any,
        gid: 10000147,
        name: 'Game',
        ods_db: 'ieu_ods',
        created_at: '2024-01-01'
      };
      expect(isGame(game)).toBe(false);
    });
  });
});
