# Test Data Setup Investigation Report

**Date**: 2026-03-02
**Issue**: E2E tests finding 0 games and 0 events
**Status**: Root cause identified and documented

---

## Problem Statement

E2E tests are reporting:
```
Games API status: 200
Found 0 games
Events API status: 200
Found 0 events
```

However, the database actually contains:
- **5 games** (1 production game + 4 test games)
- **1907 events**

## Root Cause Analysis

### 1. **Test Data Setup Infrastructure EXISTS** ✅

The project has comprehensive test data seeding infrastructure:

**Frontend Helpers** (`frontend/test/e2e/helpers/setup-test-data.ts`):
- `seedTestGamesFromFixture()` - Seed from JSON fixture
- `seedTestGames()` - Batch seed games
- `createTestGame()` - Create single game
- `gameExists()` - Check if game exists
- `deleteTestGames()` - Cleanup test games
- `cleanupTestGamesFromFixture()` - Convenience cleanup

**Backend Script** (`scripts/test/setup_e2e_test_data.py`):
- Creates STAR001 game (GID: 10000147)
- Creates test events (login, register, battle, recharge)
- Creates test parameters
- Idempotent design (safe to run multiple times)

**Test Fixtures** (`frontend/test/e2e/fixtures/`):
- `test-games.json` - 3 test games (GID: 90000001-90000003)
- `test-data.js` - Additional test data helpers

### 2. **Test Data Setup is NOT Being Called** ❌

**Critical Finding**: No test files are actually calling the setup functions!

Evidence from grep search:
- ✅ Test files have `beforeEach` hooks for navigation/setup
- ❌ **ZERO test files call `seedTestGamesFromFixture()` or `seedTestGames()`**
- ❌ No `beforeAll` hook seeds test data before tests run
- ❌ No global setup file for E2E tests

### 3. **Playwright Config Shows Setup Pattern But No Global Setup**

**playwright.config.ts** (lines 18-33):
```typescript
/*
 * Test Data Setup:
 * - Test data seeding utilities: test/e2e/helpers/setup-test-data.ts
 * - Test fixtures: test/e2e/fixtures/test-games.json
 * - Use beforeAll() hooks in test files to seed test data
 * - Use afterAll() hooks in test files to clean up test data
 *
 * Example:
 *   import { seedTestGamesFromFixture, cleanupTestGamesFromFixture } from '../helpers/setup-test-data';
 *
 *   test.beforeAll(async () => {
 *     await seedTestGamesFromFixture();
 *   });
 */
```

**Problem**: This is just documentation/comments, not actual setup code!

### 4. **Current Database State**

```sql
-- Games (5 total)
GID: 10000147 | Name: STAR001 (production)
GID: 90002208 | Name: DELETE Test Game
GID: 90003949 | Name: DELETE Test Game
GID: 90005229 | Name: DELETE Test Game
GID: 90005842 | Name: DELETE Test Game

-- Events (1907 total)
-- All events belong to game_gid=10000147 (STAR001)
```

**Problem**: Tests expect to find games with GIDs 90000001-90000003 (from fixture), but these games don't exist!

---

## Why Tests Find 0 Games

### Scenario 1: Tests Query for Specific GIDs

If tests query for games with specific GIDs (e.g., 90000001-90000003 from fixture):

```typescript
// Test fixture defines games with GIDs 90000001-90000003
const testGames = [
  { gid: 90000001, name: "E2E Test Game 1" },
  { gid: 90000002, name: "E2E Test Game 2" },
  { gid: 90000003, name: "E2E Test Game 3" }
];

// But these games don't exist in database!
// Database has: 10000147, 90002208, 90003949, 90005229, 90005842
```

**Result**: API returns empty array → "Found 0 games"

### Scenario 2: Tests Query All Games But Filter by Test GID Range

If tests filter for games in 90000000+ range:

```typescript
// Tests expect games with GID >= 90000000
// Database has: 90002208, 90003949, 90005229, 90005842

// But tests might be looking for specific fixture GIDs
// or using wrong query parameters
```

**Result**: Mismatch between expected and actual GIDs

---

## Current Test Data Setup Approach

### What Exists ✅

1. **Setup Functions**: Complete and well-documented
2. **Test Fixtures**: JSON files with test game data
3. **Backend Script**: Python script for seeding data
4. **Documentation**: Usage examples and README files

### What's Missing ❌

1. **No Global Setup**: No `global.ts` or `global.setup.ts` for E2E tests
2. **No beforeAll Hooks**: Tests don't call setup functions
3. **No Automatic Seeding**: Test data must be manually seeded
4. **No Cleanup**: Tests don't clean up after themselves

---

## Recommended Approach

### Option A: Global Setup File (Recommended)

**Create**: `frontend/test/e2e/global.setup.ts`

```typescript
import { FullConfig } from '@playwright/test';
import { seedTestGamesFromFixture } from './helpers/setup-test-data';

async function globalSetup(config: FullConfig) {
  console.log('🌱 Seeding test data before E2E tests...');

  // Seed test games from fixture
  const games = await seedTestGamesFromFixture();

  console.log(`✅ Seeded ${games.length} test games`);
}

export default globalSetup;
```

**Update**: `playwright.config.ts`

```typescript
export default defineConfig({
  // ... existing config ...
  globalSetup: require.resolve('./test/e2e/global.setup.ts'),
});
```

**Pros**:
- ✅ Runs once before all tests
- ✅ All tests have access to test data
- ✅ Centralized setup logic
- ✅ No need to modify individual test files

**Cons**:
- ❌ Test data persists after tests run (need cleanup)

### Option B: beforeAll Hooks in Test Files

**Add to each test file**:

```typescript
import { test, expect } from '@playwright/test';
import { seedTestGamesFromFixture, cleanupTestGamesFromFixture } from '../helpers/setup-test-data';

test.describe('Some Test Suite', () => {
  test.beforeAll(async () => {
    await seedTestGamesFromFixture();
  });

  test.afterAll(async () => {
    await cleanupTestGamesFromFixture();
  });

  // ... tests ...
});
```

**Pros**:
- ✅ Explicit setup per test suite
- ✅ Can customize data per test
- ✅ Cleanup logic included

**Cons**:
- ❌ Must add to every test file
- ❌ Code duplication
- ❌ Easy to forget

### Option C: Fixtures (Recommended for Specific Tests)

**Create**: `frontend/test/e2e/fixtures/test-data.fixture.ts`

```typescript
import { test as base } from '@playwright/test';
import { seedTestGamesFromFixture, cleanupTestGamesFromFixture } from '../helpers/setup-test-data';

type TestDataFixture = {
  seedTestData: () => Promise<void>;
  cleanupTestData: () => Promise<void>;
};

export const test = base.extend<TestDataFixture>({
  seedTestData: async ({}, use) => {
    await seedTestGamesFromFixture();
    await use();
  },
  cleanupTestData: async ({}, use) => {
    await use();
    await cleanupTestGamesFromFixture();
  },
});
```

**Use in tests**:

```typescript
import { test } from '../fixtures/test-data.fixture';

test('my test', async ({ page, seedTestData }) => {
  // Test data is already seeded
  // ... test logic ...
});
```

**Pros**:
- ✅ Reusable fixture
- ✅ Explicit dependency
- ✅ Clean API

**Cons**:
- ❌ More complex setup
- ❌ Still need to import fixture

---

## Immediate Action Required

### Quick Fix (5 minutes)

**Run the backend setup script manually**:

```bash
# Activate virtual environment
source backend/venv/bin/activate

# Seed test data (creates STAR001 game + events)
python3 scripts/test/setup_e2e_test_data.py

# Verify data was seeded
sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM games WHERE gid = 10000147;"
sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM log_events WHERE game_gid = 10000147;"
```

**Then update tests to use game_gid=10000147**:

```typescript
// Instead of querying for games with GID 90000001-90000003
// Query for game 10000147 (STAR001)

const response = await fetch(`${BASE_URL}/api/games/10000147`);
const data = await response.json();
expect(data.success).toBe(true);
```

### Long-term Fix (1 hour)

**Implement Option A**: Global setup file with automatic seeding

1. Create `frontend/test/e2e/global.setup.ts`
2. Update `playwright.config.ts` to reference global setup
3. Update test fixtures to use correct GIDs (90000001-90000003)
4. Add cleanup logic to `global.teardown.ts`

---

## Test Data Best Practices

### 1. **Use Separate Test Database** ⭐ P0

**Current State**: Tests use production database (`data/dwd_generator.db`)

**Recommendation**: Use test database (`data/test_database.db`)

**Implementation**:
```bash
# Set environment variable
export FLASK_ENV=testing

# Backend will automatically use test database
# See: backend/core/config/config.py
```

### 2. **Isolate Test Data by GID Range** ⭐ P0

**Current State**: Tests use random GIDs or production GIDs

**Recommendation**: Reserve GID ranges for tests

- `90000000-90009999`: E2E tests
- `90010000-90019999`: Integration tests
- `90020000-90029999`: Unit tests

### 3. **Cleanup After Tests** ⭐ P1

**Current State**: Test data persists in database

**Recommendation**: Always cleanup after tests

```typescript
test.afterAll(async () => {
  await cleanupTestGamesFromFixture();
});
```

### 4. **Idempotent Setup** ⭐ P1

**Current State**: Setup functions check for existing data ✅

**Recommendation**: Keep this behavior!

```typescript
// setup-test-data.ts already implements this
export async function seedTestGames(games: TestGame[]): Promise<TestGame[]> {
  for (const game of games) {
    const exists = await gameExists(game.gid);
    if (exists) {
      console.log(`ℹ️  Game GID ${game.gid} already exists, skipping`);
      seededGames.push(game);
    } else {
      const created = await createTestGame(game);
      if (created) {
        seededGames.push(created);
      }
    }
  }
}
```

---

## Missing Components Summary

### 1. Global E2E Setup File ❌

**Expected**: `frontend/test/e2e/global.setup.ts`
**Actual**: Does not exist

### 2. Global E2E Teardown File ❌

**Expected**: `frontend/test/e2e/global.teardown.ts`
**Actual**: Does not exist

### 3. Test Data Seeding Calls ❌

**Expected**: Tests call `seedTestGamesFromFixture()` in `beforeAll`
**Actual**: No tests call setup functions

### 4. Test Data Cleanup Calls ❌

**Expected**: Tests call `cleanupTestGamesFromFixture()` in `afterAll`
**Actual**: No tests call cleanup functions

### 5. Test Database Configuration ⚠️

**Expected**: Tests use `data/test_database.db`
**Actual**: Tests use `data/dwd_generator.db` (production)

---

## Action Items

### P0 - Critical (Do Today)

1. ✅ **Run manual setup script**: `python3 scripts/test/setup_e2e_test_data.py`
2. ✅ **Verify test data exists**: Check database has games and events
3. ❌ **Create global setup file**: `frontend/test/e2e/global.setup.ts`
4. ❌ **Update playwright config**: Add `globalSetup` reference

### P1 - High (Do This Week)

1. ❌ **Switch to test database**: Set `FLASK_ENV=testing` for tests
2. ❌ **Add cleanup logic**: Create `global.teardown.ts`
3. ❌ **Update test fixtures**: Ensure GIDs match setup data
4. ❌ **Document setup process**: Update E2E testing guide

### P2 - Medium (Do Next Sprint)

1. ❌ **Create test data fixtures**: Add events, parameters to fixtures
2. ❌ **Implement fixtures pattern**: Use Playwright fixtures for setup
3. ❌ **Add data reset utility**: Function to reset test database
4. ❌ **CI/CD integration**: Ensure test data setup runs in CI

---

## Conclusion

**Root Cause**: Test data setup infrastructure exists but is not being called by tests.

**Immediate Fix**: Run `python3 scripts/test/setup_e2e_test_data.py` to seed test data manually.

**Long-term Fix**: Implement global setup file (`global.setup.ts`) to automatically seed test data before E2E tests run.

**Best Practice**: Use separate test database and cleanup after tests to prevent data pollution.

---

## References

- **Setup Helpers**: `/Users/mckenzie/Documents/event2table/frontend/test/e2e/helpers/setup-test-data.ts`
- **Test Fixtures**: `/Users/mckenzie/Documents/event2table/frontend/test/e2e/fixtures/test-games.json`
- **Backend Script**: `/Users/mckenzie/Documents/event2table/scripts/test/setup_e2e_test_data.py`
- **Playwright Config**: `/Users/mckenzie/Documents/event2table/frontend/playwright.config.ts`
- **E2E Testing Guide**: `/Users/mckenzie/Documents/event2table/docs/testing/e2e-testing-guide.md`
