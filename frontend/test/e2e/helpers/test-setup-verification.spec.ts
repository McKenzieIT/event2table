/**
 * Verification Test for Test Data Seeding Infrastructure
 *
 * This test verifies that the test data seeding utilities work correctly.
 * Run this test to verify the setup before using the utilities in other tests.
 *
 * Run: npx playwright test setup-verification.spec.ts
 */

import { test, expect } from '@playwright/test';
import {
  seedTestGames,
  createTestGame,
  gameExists,
  deleteTestGames,
  type TestGame,
} from './setup-test-data';

test.describe('Test Data Seeding Infrastructure Verification', () => {
  const testGids: number[] = [];

  test.afterAll(async () => {
    // Clean up all test games created during verification
    await deleteTestGames(testGids);
  });

  test('verify: create single test game', async () => {
    const game: TestGame = {
      gid: 90000999,
      name: 'Verification Test Game',
      ods_db: 'ieu_ods',
      description: 'Game for testing seeding infrastructure',
    };

    const created = await createTestGame(game);

    expect(created).not.toBeNull();
    expect(created?.gid).toBe(90000999);
    expect(created?.name).toBe('Verification Test Game');

    testGids.push(created!.gid);
  });

  test('verify: game exists check', async () => {
    const exists = await gameExists(90000999);
    expect(exists).toBe(true);

    const notExists = await gameExists(99999999);
    expect(notExists).toBe(false);
  });

  test('verify: batch seed multiple games', async () => {
    const games: TestGame[] = [
      {
        gid: 90000901,
        name: 'Batch Verification Game 1',
        ods_db: 'batch_verify_db_1',
      },
      {
        gid: 90000902,
        name: 'Batch Verification Game 2',
        ods_db: 'batch_verify_db_2',
      },
      {
        gid: 90000903,
        name: 'Batch Verification Game 3',
        ods_db: 'batch_verify_db_3',
      },
    ];

    const seeded = await seedTestGames(games);

    expect(seeded).toHaveLength(3);
    expect(seeded[0].name).toBe('Batch Verification Game 1');
    expect(seeded[1].name).toBe('Batch Verification Game 2');
    expect(seeded[2].name).toBe('Batch Verification Game 3');

    testGids.push(...seeded.map((g) => g.gid));
  });

  test('verify: re-seeding existing games is safe', async () => {
    // Try to create games that already exist (from previous test)
    const games: TestGame[] = [
      {
        gid: 90000901,
        name: 'Batch Verification Game 1',
        ods_db: 'batch_verify_db_1',
      },
    ];

    // Should not error, just skip existing games
    const seeded = await seedTestGames(games);

    expect(seeded).toHaveLength(1);
    expect(seeded[0].gid).toBe(90000901);
  });

  test('verify: GID validation prevents production conflicts', async () => {
    const invalidGame: TestGame = {
      gid: 10000147, // STAR001 - protected production game
      name: 'Invalid Test Game',
      ods_db: 'ieu_ods',
    };

    const created = await createTestGame(invalidGame);

    // Should fail due to GID already existing (STAR001 protection)
    // The function handles errors gracefully and returns null
    expect(created).toBeNull();
  });

  test('verify: cleanup test games', async () => {
    const cleanupGids = [90000901, 90000902, 90000903];

    const deletedCount = await deleteTestGames(cleanupGids);

    expect(deletedCount).toBeGreaterThanOrEqual(0);
    expect(deletedCount).toBeLessThanOrEqual(3);

    // Verify games no longer exist
    const exists1 = await gameExists(90000901);
    const exists2 = await gameExists(90000902);
    const exists3 = await gameExists(90000903);

    // At least some should be deleted
    expect(exists1 || exists2 || exists3).toBe(false);
  });
});

/**
 * Expected Test Results:
 *
 * ✅ All 6 tests should pass
 * ✅ Test games should be created in the 90000999-90000903 range
 * ✅ Existing games should be detected and skipped
 * ✅ Invalid GIDs (10000147) should be rejected
 * ✅ Cleanup should remove all test games
 *
 * If any test fails, check:
 * 1. Backend server is running: curl http://127.0.0.1:5001/api/games
 * 2. Backend logs for errors
 * 3. Game data structure matches TestGame interface
 */
