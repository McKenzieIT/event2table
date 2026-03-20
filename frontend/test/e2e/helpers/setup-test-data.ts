/**
 * Test Data Seeding Utilities for E2E Tests
 *
 * Provides functions to seed and clean test data in the backend database.
 * All test data uses GIDs in the 90000000+ range to avoid conflicts with production data.
 *
 * CRITICAL: NEVER use GID 10000147 (STAR001) in tests - this is protected production data.
 *
 * @see CLAUDE.md - STAR001 Game Protection Rule
 */

const BASE_URL = process.env.BACKEND_URL || 'http://127.0.0.1:5001';

/**
 * Test Game data structure matching backend GameEntity
 */
export interface TestGame {
  gid: number;
  name: string;
  ods_db: string;
  description?: string;
  dwd_prefix?: string;
}

/**
 * API Response wrapper
 */
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

/**
 * Create a single test game via backend API
 *
 * @param game - Game data to create
 * @returns Promise resolving to created game data or null if failed
 */
export async function createTestGame(game: TestGame): Promise<TestGame | null> {
  try {
    const response = await fetch(`${BASE_URL}/api/games`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(game),
    });

    const result: ApiResponse<TestGame> = await response.json();

    if (response.ok && result.success && result.data) {
      console.log(`✅ Created test game: ${game.name} (GID: ${game.gid})`);
      return result.data;
    } else {
      console.error(`❌ Failed to create test game GID ${game.gid}:`, result.error || result.message);
      return null;
    }
  } catch (error) {
    console.error(`❌ Error creating test game GID ${game.gid}:`, error);
    return null;
  }
}

/**
 * Check if a game exists by GID
 *
 * @param gid - Game GID to check
 * @returns Promise resolving to true if game exists
 */
export async function gameExists(gid: number): Promise<boolean> {
  try {
    const response = await fetch(`${BASE_URL}/api/games/${gid}`);

    if (response.ok) {
      const result: ApiResponse<TestGame> = await response.json();
      return result.success && result.data !== undefined;
    }

    return false;
  } catch (error) {
    console.error(`❌ Error checking if game GID ${gid} exists:`, error);
    return false;
  }
}

/**
 * Seed multiple test games
 * - Checks if games already exist (by GID)
 * - Creates only missing games
 * - Returns list of successfully seeded games
 *
 * @param games - Array of game data to seed
 * @returns Promise resolving to array of seeded game data
 */
export async function seedTestGames(games: TestGame[]): Promise<TestGame[]> {
  console.log('🌱 Starting test data seeding...');

  const seededGames: TestGame[] = [];

  for (const game of games) {
    // Validate GID range (must be 90000000+ to avoid conflicts)
    if (game.gid < 90000000) {
      console.error(`❌ Invalid test GID ${game.gid}: must be 90000000+ to avoid conflicts with production data`);
      continue;
    }

    // Check if game already exists
    const exists = await gameExists(game.gid);

    if (exists) {
      console.log(`ℹ️  Game GID ${game.gid} already exists, skipping creation`);
      seededGames.push(game);
    } else {
      // Create the game
      const created = await createTestGame(game);
      if (created) {
        seededGames.push(created);
      }
    }
  }

  console.log(`✅ Test data seeding complete: ${seededGames.length}/${games.length} games ready`);
  return seededGames;
}

/**
 * Load test games from JSON fixture file
 *
 * @param fixturePath - Relative path to fixture file (e.g., '../fixtures/test-games.json')
 * @returns Promise resolving to array of test game data
 */
export async function loadTestGamesFixture(fixturePath: string): Promise<TestGame[]> {
  try {
    // Use fs.readFile for Node.js compatibility in global setup
    const { readFile } = await import('fs/promises');
    const { resolve, dirname } = await import('path');
    const { fileURLToPath } = await import('url');

    // Get current file directory
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = dirname(__filename);

    // Resolve fixture path
    const fullPath = resolve(__dirname, fixturePath);

    // Read file
    const contents = await readFile(fullPath, 'utf-8');
    const games: TestGame[] = JSON.parse(contents);
    return games;
  } catch (error) {
    console.error('❌ Error loading test games fixture:', error);
    return [];
  }
}

/**
 * Delete a test game by GID
 *
 * WARNING: This will cascade delete all associated data (events, parameters, etc.)
 *
 * @param gid - Game GID to delete
 * @param confirm - Set to true to force deletion even with associated data
 * @returns Promise resolving to true if deletion was successful
 */
export async function deleteTestGame(gid: number, confirm: boolean = true): Promise<boolean> {
  try {
    const response = await fetch(`${BASE_URL}/api/games/${gid}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ confirm }),
    });

    if (response.ok) {
      const result: ApiResponse<any> = await response.json();
      console.log(`🗑️  Deleted test game GID ${gid}`);
      return true;
    } else {
      console.error(`❌ Failed to delete test game GID ${gid}:`, response.statusText);
      return false;
    }
  } catch (error) {
    console.error(`❌ Error deleting test game GID ${gid}:`, error);
    return false;
  }
}

/**
 * Batch delete multiple test games
 *
 * WARNING: This will cascade delete all associated data
 *
 * @param gids - Array of game GIDs to delete
 * @returns Promise resolving to number of games deleted
 */
export async function deleteTestGames(gids: number[]): Promise<number> {
  console.log(`🗑️  Cleaning up test games: ${gids.length} games to delete...`);

  let deletedCount = 0;

  for (const gid of gids) {
    const deleted = await deleteTestGame(gid, true);
    if (deleted) {
      deletedCount++;
    }
  }

  console.log(`✅ Cleanup complete: ${deletedCount}/${gids.length} games deleted`);
  return deletedCount;
}

/**
 * Seed test games from fixture file
 * Convenience function that loads fixture and seeds games in one call
 *
 * @param fixturePath - Relative path to fixture file
 * @returns Promise resolving to array of seeded game data
 */
export async function seedTestGamesFromFixture(fixturePath: string = '../fixtures/test-games.json'): Promise<TestGame[]> {
  const games = await loadTestGamesFixture(fixturePath);
  return seedTestGames(games);
}

/**
 * Clean up test games from fixture file
 * Convenience function that loads fixture and deletes games in one call
 *
 * @param fixturePath - Relative path to fixture file
 * @returns Promise resolving to number of games deleted
 */
export async function cleanupTestGamesFromFixture(fixturePath: string = '../fixtures/test-games.json'): Promise<number> {
  const games = await loadTestGamesFixture(fixturePath);
  const gids = games.map(g => g.gid);
  return deleteTestGames(gids);
}
