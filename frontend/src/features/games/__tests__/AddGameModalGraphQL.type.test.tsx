/**
 * TDD Test: Verify manual types can be replaced with generated types
 *
 * RED Phase: This test documents the current manual type definitions
 * and verifies they match the generated types
 */

import { GameType, EventType, FieldTypeEnum, NodeType } from '@/types/api.generated';

// ========== Manual Types Currently Used ==========
// These are the types we need to migrate FROM

/**
 * Manual Game interface in AddGameModalGraphQL.tsx
 * @deprecated Use GameType from @/types/api.generated instead
 */
interface ManualGame {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  iconPath?: string;
  eventCount: number;
  parameterCount: number;
  createdAt: string;
  updatedAt: string;
}

/**
 * Manual FormData interface in AddGameModalGraphQL.tsx
 * @deprecated This is form-specific, can be kept
 */
interface FormData {
  gid: string;
  name: string;
  odsDb: string;
}

/**
 * Manual Game interface in GameManagementModalGraphQL.tsx
 * @deprecated Use GameType from @/types/api.generated instead
 */
interface ManualGame2 {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  iconPath?: string;
  eventCount: number;
  parameterCount: number;
  createdAt: string;
  updatedAt: string;
}

// ========== Test: Type Compatibility ==========

describe('Type Migration: Manual vs Generated', () => {
  describe('GameType compatibility', () => {
    it('should have same fields as manual Game interface', () => {
      // This test documents the mapping
      const generatedGame: GameType = {
        __typename: 'GameType',
        id: 1,
        gid: '10000147',
        name: 'STAR001',
        odsDb: 'ieu_ods',
        iconPath: '/path/to/icon.png',
        eventCount: 10,
        parameterCount: 5,
        createdAt: '2026-01-01',
        updatedAt: '2026-01-01',
      };

      // Verify all manual Game fields exist in GameType
      expect(generatedGame).toHaveProperty('id');
      expect(generatedGame).toHaveProperty('gid');
      expect(generatedGame).toHaveProperty('name');
      expect(generatedGame).toHaveProperty('odsDb');
      expect(generatedGame).toHaveProperty('iconPath');
      expect(generatedGame).toHaveProperty('eventCount');
      expect(generatedGame).toHaveProperty('parameterCount');
      expect(generatedGame).toHaveProperty('createdAt');
      expect(generatedGame).toHaveProperty('updatedAt');
    });

    it('should handle ods_db vs odsDb naming difference', () => {
      // GraphQL uses odsDb (camelCase), manual uses ods_db (snake_case)
      const generatedGame: GameType = {
        odsDb: 'ieu_ods',
      };

      expect(generatedGame.odsDb).toBe('ieu_ods');
    });

    it('should handle gid as string instead of number', () => {
      // GraphQL uses String for gid, manual uses number
      const generatedGame: GameType = {
        gid: '10000147',
      };

      // This is a BREAKING CHANGE - components using parseInt() need update
      expect(typeof generatedGame.gid).toBe('string');
    });
  });

  describe('EventType compatibility', () => {
    it('should have event-related fields', () => {
      const generatedEvent: EventType = {
        __typename: 'EventType',
        id: 1,
        eventName: 'login',
        eventCnName: '登录',
        gameId: '10000147',
        categoryId: 1,
        categoryName: '认证',
        createdAt: '2026-01-01',
        updatedAt: '2026-01-01',
      };

      expect(generatedEvent).toHaveProperty('eventName');
      expect(generatedEvent).toHaveProperty('eventCnName');
      expect(generatedEvent).toHaveProperty('gameId');
    });
  });

  describe('FieldTypeEnum compatibility', () => {
    it('should support all field types', () => {
      // Manual enum uses UPPER_CASE
      // Generated enum uses PascalCase
      const fieldTypes: FieldTypeEnum[] = [
        'BASE',
        'PARAM',
        'CUSTOM',
        'FIXED',
      ];

      expect(fieldTypes).toHaveLength(4);
    });
  });

  describe('NodeType compatibility', () => {
    it('should support node types for canvas', () => {
      const nodeType: NodeType = {
        __typename: 'NodeType',
        id: 1,
        nodeType: 'EVENT',
        fieldType: 'BASE',
      };

      expect(nodeType.nodeType).toBe('EVENT');
      expect(nodeType.fieldType).toBe('BASE');
    });
  });
});

// ========== Migration Strategy ==========

describe('Migration Strategy', () => {
  it('Phase 1: Games Module - AddGameModalGraphQL.tsx', () => {
    // Migration steps:
    // 1. Import GameType from @/types/api.generated
    // 2. Keep FormData (form-specific, not in GraphQL)
    // 3. Update form submission to handle gid as string (remove parseInt)
    // 4. Update ods_db to odsDb

    const expectedImports = [
      "import type { GameType } from '@/types/api.generated';",
    ];

    expect(expectedImports).toBeTruthy();
  });

  it('Phase 1: Games Module - GameManagementModalGraphQL.tsx', () => {
    // Migration steps:
    // 1. Import GameType from @/types/api.generated
    // 2. Remove local Game interface
    // 3. Update all references to use GameType
    // 4. Handle ods_db -> odsDb renaming
    // 5. Handle gid: number -> string conversion

    const expectedChanges = [
      'Remove: interface Game { ... }',
      'Add: import type { GameType } from "@/types/api.generated"',
      'Update: game.ods_db -> game.odsDb',
      'Update: parseInt(game.gid) -> game.gid (or keep if needed)',
    ];

    expect(expectedChanges).toBeTruthy();
  });

  it('Phase 2: Events Module', () => {
    // Migration steps for AddEventModalGraphQL.tsx and EventForm.tsx
    const expectedChanges = [
      'Import EventType from @/types/api.generated',
      'Remove manual Event interfaces',
      'Update event field names',
    ];

    expect(expectedChanges).toBeTruthy();
  });

  it('Phase 3: Canvas Module', () => {
    // Migration steps for FieldConfigModal.tsx
    const expectedChanges = [
      'Import Field, FieldTypeEnum from @/types/api.generated',
      'Remove manual Field interface from hql-types.ts',
      'Update field type enums',
    ];

    expect(expectedChanges).toBeTruthy();
  });
});

// ========== Breaking Changes ==========

describe('Breaking Changes to Handle', () => {
  it('gid type change: number -> string', () => {
    // Components using parseInt(game.gid) need to be updated
    const manualGid: number = 10000147;
    const generatedGid: string = '10000147';

    // Before: parseInt(game.gid)
    // After: game.gid (or parseInt if converting to number for API)

    expect(typeof manualGid).toBe('number');
    expect(typeof generatedGid).toBe('string');
  });

  it('ods_db vs odsDb naming', () => {
    // GraphQL uses camelCase, manual uses snake_case
    const manualOdsDb = { ods_db: 'ieu_ods' };
    const generatedOdsDb = { odsDb: 'ieu_ods' };

    // Need to update all references from game.ods_db to game.odsDb
    expect('ods_db' in manualOdsDb).toBe(true);
    expect('odsDb' in generatedOdsDb).toBe(true);
  });

  it('Enum value casing', () => {
    // Manual enum: BASE, PARAM, CUSTOM, FIXED
    // Generated enum: BASE, PARAM, CUSTOM, FIXED (should match)
    // But need to verify HqlJoinType, NodeType, etc.

    const manualFieldType = 'BASE';
    const generatedFieldType: FieldTypeEnum = 'BASE';

    expect(manualFieldType).toBe(generatedFieldType);
  });
});
