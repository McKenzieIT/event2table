# Test Data Seeding Infrastructure

Comprehensive test data seeding utilities for E2E tests in the Event2Table frontend.

## Overview

This infrastructure provides a robust way to seed and clean test data for E2E tests, ensuring:

- **No production data contamination** - All test data uses GIDs in the 90000000+ range
- **STAR001 protection** - Never uses GID 10000147 (protected production game)
- **Idempotent operations** - Safe to run multiple times (checks if data exists)
- **Easy cleanup** - Automatic cleanup of test data after tests run

## Files

| File | Purpose |
|------|---------|
| `setup-test-data.ts` | Main test data seeding utilities |
| `fixtures/test-games.json` | Sample test game data (3 games) |
| `USAGE-EXAMPLES.ts` | Example tests showing all usage patterns |
| `README.md` | This documentation file |

## Quick Start

### 1. Seed Test Data from Fixture (Recommended)

```typescript
import { test, expect } from '@playwright/test';
import { seedTestGamesFromFixture, cleanupTestGamesFromFixture } from '../helpers/setup-test-data';

test.describe('My E2E Tests', () => {
  test.beforeAll(async () => {
    // Seed test games from fixture file
    await seedTestGamesFromFixture();
  });

  test.afterAll(async () => {
    // Clean up all test games
    await cleanupTestGamesFromFixture();
  });

  test('my test', async ({ page }) => {
    await page.goto('/#/games');
    await expect(page.locator('text=E2E Test Game 1')).toBeVisible();
  });
});
```

### 2. Create Custom Test Game

```typescript
import { createTestGame, deleteTestGames, type TestGame } from '../helpers/setup-test-data';

test.describe('Custom Test Data', () => {
  let gameGid: number;

  test.afterAll(async () => {
    await deleteTestGames([gameGid]);
  });

  test('create custom game', async ({ page }) => {
    const game: TestGame = {
      gid: 90000099,
      name: 'My Custom Test Game',
      ods_db: 'test_db',
      description: 'Custom test game',
    };

    const created = await createTestGame(game);
    gameGid = created!.gid;

    await page.goto(`/#/events?game_gid=${gameGid}`);
    await expect(page.locator('text=My Custom Test Game')).toBeVisible();
  });
});
```

## API Reference

### `seedTestGamesFromFixture(fixturePath?)`

Seed test games from a JSON fixture file.

- **Checks if games exist** (by GID) before creating
- **Returns**: Array of seeded game data
- **Example**: `await seedTestGamesFromFixture('../fixtures/test-games.json')`

### `cleanupTestGamesFromFixture(fixturePath?)`

Delete all test games from a JSON fixture file.

- **Cascade deletes** all associated data (events, parameters, etc.)
- **Returns**: Number of games deleted
- **Example**: `await cleanupTestGamesFromFixture('../fixtures/test-games.json')`

### `createTestGame(game)`

Create a single test game.

- **game**: TestGame object with gid, name, ods_db, etc.
- **Returns**: Created game data or null if failed
- **Example**:
  ```typescript
  const game = await createTestGame({
    gid: 90000001,
    name: 'Test Game',
    ods_db: 'test_db',
  });
  ```

### `gameExists(gid)`

Check if a game exists by GID.

- **gid**: Game GID to check
- **Returns**: Promise<boolean>
- **Example**: `const exists = await gameExists(90000001);`

### `seedTestGames(games)`

Seed multiple test games programmatically.

- **games**: Array of TestGame objects
- **Returns**: Array of seeded game data
- **Example**:
  ```typescript
  const games = await seedTestGames([
    { gid: 90000001, name: 'Game 1', ods_db: 'db1' },
    { gid: 90000002, name: 'Game 2', ods_db: 'db2' },
  ]);
  ```

### `deleteTestGame(gid, confirm?)`

Delete a single test game by GID.

- **gid**: Game GID to delete
- **confirm**: Set true to force delete even with associated data
- **Returns**: Promise<boolean>
- **Example**: `await deleteTestGame(90000001, true);`

### `deleteTestGames(gids)`

Batch delete multiple test games.

- **gids**: Array of game GIDs to delete
- **Returns**: Number of games deleted
- **Example**: `await deleteTestGames([90000001, 90000002]);`

### `loadTestGamesFixture(fixturePath)`

Load test games from a JSON fixture file.

- **fixturePath**: Relative path to fixture file
- **Returns**: Array of TestGame objects
- **Example**:
  ```typescript
  const games = await loadTestGamesFixture('../fixtures/test-games.json');
  ```

## Test Game Data Structure

```typescript
interface TestGame {
  gid: number;           // Game GID (MUST be 90000000+)
  name: string;          // Game name
  ods_db: string;        // ODS database name
  description?: string;  // Optional description
  dwd_prefix?: string;   // DWD table prefix (default: "dwd")
}
```

## Test Fixture File

The default fixture file (`fixtures/test-games.json`) contains 3 test games:

```json
[
  {
    "gid": 90000001,
    "name": "E2E Test Game 1",
    "ods_db": "test_ods_db_1",
    "description": "First E2E test game for automated testing",
    "dwd_prefix": "dwd"
  },
  {
    "gid": 90000002,
    "name": "E2E Test Game 2",
    "ods_db": "test_ods_db_2",
    "description": "Second E2E test game for automated testing",
    "dwd_prefix": "dwd"
  },
  {
    "gid": 90000003,
    "name": "E2E Test Game 3",
    "ods_db": "test_ods_db_3",
    "description": "Third E2E test game for automated testing",
    "dwd_prefix": "dwd"
  }
]
```

## Critical Rules

### 1. STAR001 Protection Rule ⚠️ **EXTREMELY IMPORTANT**

**NEVER use GID 10000147 (STAR001) in tests**

- GID 10000147 is protected production data
- Using it in tests risks data loss
- **Always use GIDs in the 90000000+ range**

### 2. GID Range Validation

- **Valid test GIDs**: 90000000-99999999
- **Invalid test GIDs**: < 90000000 (risk of production conflict)
- **Protected GIDs**: 10000147 (STAR001) - NEVER use

### 3. Cleanup is Mandatory

- **Always** clean up test data in `afterAll` hooks
- **Never** leave test data in the database after tests run
- **Use** cascade delete to remove all associated data

### 4. Idempotent Operations

- Seeding functions check if data exists before creating
- Safe to run multiple times without side effects
- Tests can be re-run without manual cleanup

## Backend API Integration

The seeding utilities use the backend Games API:

- **POST /api/games** - Create game
- **GET /api/games/<gid>** - Check if game exists
- **DELETE /api/games/<gid>** - Delete game (with cascade)

All API calls include proper error handling and logging.

## Error Handling

All seeding functions include comprehensive error handling:

```typescript
// Functions return null on failure
const game = await createTestGame({ ... });
if (game === null) {
  console.error('Failed to create game');
  return;
}

// Console logging for debugging
// ✅ Created test game: E2E Test Game 1 (GID: 90000001)
// ℹ️  Game GID 90000001 already exists, skipping creation
// ❌ Failed to create test game GID 90000001: [error details]
```

## Environment Configuration

The backend URL is configurable via environment variable:

```bash
# Default: http://127.0.0.1:5001
# Override with:
export BACKEND_URL=http://localhost:5001
npm run test:e2e
```

## Examples

See `USAGE-EXAMPLES.ts` for comprehensive examples of:

- Seeding from fixture files
- Creating custom test games
- Batch operations
- Checking if data exists
- Cleaning up test data

## Troubleshooting

### Issue: "Failed to create test game"

**Possible causes**:
- Backend server not running
- Invalid game data (validation failed)
- Database connection error

**Solution**:
1. Check backend server is running: `curl http://127.0.0.1:5001/api/games`
2. Check backend logs for errors
3. Verify game data structure matches TestGame interface

### Issue: "Game GID already exists"

**Expected behavior**:
- Seeding functions check if games exist before creating
- This is normal and not an error

**If you need fresh data**:
1. Delete existing games first: `await deleteTestGames([90000001])`
2. Then create new games: `await createTestGame({ ... })`

### Issue: "Cleanup failed"

**Possible causes**:
- Games have associated data (events, parameters)
- Need to set `confirm: true` for cascade delete

**Solution**:
```typescript
// Always use confirm: true in tests
await deleteTestGame(90000001, true);
```

## Best Practices

1. **Use fixture files** for standard test data
2. **Clean up in afterAll** to ensure clean state
3. **Check if data exists** before creating
4. **Use descriptive game names** for debugging
5. **Log seeding operations** for test debugging
6. **Use GIDs in 90000000+ range** only
7. **Never use production GIDs** (especially 10000147)

## Related Documentation

- [CLAUDE.md - STAR001 Game Protection Rule](../../../../../CLAUDE.md#star001-游戏保护规则-⚠️-极其重要---强制执行)
- [Playwright Configuration](../../../playwright.config.ts)
- [Game Context Helper](./game-context.ts)
- [Wait Helpers](./wait-helpers.ts)

## Migration Notes

This infrastructure was created as part of **Track 2** of the E2E test fix plan:

- Replaces manual test data setup with programmatic seeding
- Ensures consistency across all E2E tests
- Prevents production data contamination
- Simplifies test maintenance

**Status**: ✅ Complete (2026-03-01)
