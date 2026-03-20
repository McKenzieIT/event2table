/**
 * Example E2E Test Using Test Data Seeding Utilities
 *
 * This file demonstrates how to use the test data seeding infrastructure
 * for E2E tests. Copy this pattern into your actual test files.
 */

import { test, expect } from '@playwright/test';
import {
  seedTestGamesFromFixture,
  cleanupTestGamesFromFixture,
  seedTestGames,
  deleteTestGames,
  createTestGame,
  gameExists,
  type TestGame,
} from '../helpers/setup-test-data';

test.describe('Example E2E Tests with Test Data Seeding', () => {
  // Method 1: Seed from fixture file (recommended for most tests)
  test.beforeAll(async () => {
    // Seed test games from fixture file
    // This checks if games exist and creates only missing ones
    await seedTestGamesFromFixture();
  });

  test.afterAll(async () => {
    // Clean up all test games from fixture file
    await cleanupTestGamesFromFixture();
  });

  test('example test using seeded games', async ({ page }) => {
    // Navigate to games list page
    await page.goto('/#/games');
    await page.waitForLoadState('domcontentloaded');

    // Verify test games are visible
    await expect(page.locator('text=E2E Test Game 1')).toBeVisible();
    await expect(page.locator('text=E2E Test Game 2')).toBeVisible();
    await expect(page.locator('text=E2E Test Game 3')).toBeVisible();
  });

  test('example test with specific game GID', async ({ page }) => {
    const testGid = 90000001;

    // Navigate to events page with specific game
    await page.goto(`/#/events?game_gid=${testGid}`);
    await page.waitForLoadState('domcontentloaded');

    // Verify game context is set
    await expect(page.locator('text=E2E Test Game 1')).toBeVisible();
  });
});

test.describe('Manual Test Data Seeding (Advanced)', () => {
  let customGameGid: number;

  test.afterAll(async () => {
    // Clean up custom test game
    if (customGameGid) {
      await deleteTestGames([customGameGid]);
    }
  });

  test('example: create custom test game', async ({ page }) => {
    // Method 2: Create custom test game programmatically
    const customGame: TestGame = {
      gid: 90000099, // Must be 90000000+ range
      name: 'Custom Test Game',
      ods_db: 'custom_test_db',
      description: 'Custom game for specific test scenario',
      dwd_prefix: 'dwd',
    };

    const created = await createTestGame(customGame);
    expect(created).not.toBeNull();

    if (created) {
      customGameGid = created.gid;

      // Use the created game in test
      await page.goto(`/#/events?game_gid=${customGameGid}`);
      await page.waitForLoadState('domcontentloaded');

      await expect(page.locator('text=Custom Test Game')).toBeVisible();
    }
  });

  test('example: check if game exists before creating', async ({ page }) => {
    const testGid = 90000001;

    // Method 3: Check if game exists before operations
    const exists = await gameExists(testGid);
    expect(exists).toBe(true);

    // Only create if doesn't exist
    if (!exists) {
      const newGame: TestGame = {
        gid: testGid,
        name: 'Conditional Test Game',
        ods_db: 'test_db',
      };

      await createTestGame(newGame);
    }
  });
});

test.describe('Batch Test Data Seeding', () => {
  const testGids: number[] = [];

  test.beforeAll(async () => {
    // Method 4: Seed multiple games at once
    const games: TestGame[] = [
      {
        gid: 90000101,
        name: 'Batch Test Game 1',
        ods_db: 'batch_test_db_1',
        description: 'Batch test game 1',
      },
      {
        gid: 90000102,
        name: 'Batch Test Game 2',
        ods_db: 'batch_test_db_2',
        description: 'Batch test game 2',
      },
      {
        gid: 90000103,
        name: 'Batch Test Game 3',
        ods_db: 'batch_test_db_3',
        description: 'Batch test game 3',
      },
    ];

    const seeded = await seedTestGames(games);
    testGids.push(...seeded.map(g => g.gid));
  });

  test.afterAll(async () => {
    // Clean up all batch test games
    await deleteTestGames(testGids);
  });

  test('example test with batch seeded games', async ({ page }) => {
    await page.goto('/#/games');
    await page.waitForLoadState('domcontentloaded');

    // Verify all batch games are visible
    await expect(page.locator('text=Batch Test Game 1')).toBeVisible();
    await expect(page.locator('text=Batch Test Game 2')).toBeVisible();
    await expect(page.locator('text=Batch Test Game 3')).toBeVisible();
  });
});

/**
 * CRITICAL RULES FOR TEST DATA:
 *
 * 1. NEVER use GID 10000147 (STAR001) - this is protected production data
 * 2. ALWAYS use GIDs in the 90000000+ range for tests
 * 3. ALWAYS clean up test data in afterAll hooks
 * 4. ALWAYS check if data exists before creating (to avoid conflicts)
 * 5. NEVER use GIDs below 90000000 (conflict risk with production)
 *
 * @see CLAUDE.md - STAR001 Game Protection Rule
 * @see test/e2e/helpers/setup-test-data.ts - Implementation details
 */
