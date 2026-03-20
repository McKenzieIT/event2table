import { test, expect, Page } from '@playwright/test';

/**
 * Games CRUD Smoke Tests
 * Phase 3: Automated E2E Testing
 *
 * Tests basic Create, Read, Update, Delete operations for games.
 * Uses test GID range (90000000+) to avoid production data.
 */

interface TestConfig {
  readonly BASE_URL: string;
  readonly TEST_GAME_GID: number;
}

const CONFIG: TestConfig = {
  BASE_URL: 'http://localhost:5173',
  TEST_GAME_GID: 90000001
};

test.describe('Games CRUD Smoke Tests', () => {
  // Helper function to generate unique test GID
  const generateTestGid = (): number => {
    return Math.floor(Math.random() * 100000) + 90000000; // 90000000-90099999
  };

  test.beforeEach(async ({ page }: { page: Page }) => {
    // Navigate to games list
    await page.goto('/#/games');
  });

  test('User can view games list', async ({ page }: { page: Page }) => {
    // Verify games grid/list is visible
    await expect(page.locator('.games-grid, .games-list, [data-testid="games-list"]')).toBeVisible();

    // Verify at least one game is displayed
    await expect(page.locator('.game-card, .game-item, [data-testid*="game"]')).toHaveCount({ min: 1 });
  });

  test('User can navigate to create game form', async ({ page }: { page: Page }) => {
    // Click create button
    await page.click('text=/新增|create|add/i');

    // Verify navigation to form
    await expect(page).toHaveURL(/\/games\/create/);

    // Verify form elements are present
    await expect(page.locator('input[name="gid"], [data-testid="gid-input"]')).toBeVisible();
    await expect(page.locator('input[name="name"], [data-testid="name-input"]')).toBeVisible();
    await expect(page.locator('select[name="ods_db"], [data-testid="ods-db-select"]')).toBeVisible();
  });

  test('User can create a new game with valid data', async ({ page }: { page: Page }) => {
    // Click create button
    await page.click('text=/新增|create/i');

    // Generate unique test GID
    const testGid = generateTestGid();
    const gameName = `E2E测试游戏_${testGid}`;

    // Fill form
    await page.fill('input[name="gid"]', String(testGid));
    await page.fill('input[name="name"]', gameName);
    await page.selectOption('select[name="ods_db"]', 'ieu_ods');

    // Submit form
    await page.click('button[type="submit"], text=/保存|提交|创建/i');

    // Wait for response and verify success
    await expect(page.locator('.toast-success, [data-testid="toast-success"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.toast-success, [data-testid="toast-success"]')).toContainText(/成功|created/i);

    // Verify navigation back to list
    await expect(page).toHaveURL(/\/games/);

    // Verify new game appears in list
    await expect(page.locator(`text=${gameName}`)).toBeVisible();
  });

  test('User receives helpful error for duplicate GID', async ({ page }: { page: Page }) => {
    // Click create button
    await page.click('text=/新增|create/i');

    // Try to create game with existing GID (STAR001)
    await page.fill('input[name="gid"]', '10000147'); // STAR001 exists
    await page.fill('input[name="name"]', '测试重复GID');
    await page.selectOption('select[name="ods_db"]', 'ieu_ods');

    // Submit form
    await page.click('button[type="submit"], text=/保存|提交/i');

    // Verify error message is displayed
    await expect(page.locator('.toast-error, [data-testid="toast-error"]')).toBeVisible();

    // Verify error message is helpful
    const errorText = await page.locator('.toast-error, [data-testid="toast-error"]').textContent();
    expect(errorText).toMatch(/已存在|already exists|duplicate/i);

    // Verify error message suggests test GID range
    expect(errorText).toMatch(/90000000+/);
  });

  test('User receives helpful error for invalid GID format', async ({ page }: { page: Page }) => {
    // Click create button
    await page.click('text=/新增|create/i');

    // Try to create game with non-numeric GID
    await page.fill('input[name="gid"]', 'invalid');
    await page.fill('input[name="name"]', '测试无效GID');
    await page.selectOption('select[name="ods_db"]', 'ieu_ods');

    // Submit form
    await page.click('button[type="submit"], text=/保存|提交/i');

    // Verify error message
    const errorElement = page.locator('.toast-error, [data-testid="toast-error"]');
    await expect(errorElement).toBeVisible();

    const errorText = await errorElement.textContent();
    expect(errorText).toMatch(/正整数|positive integer|numeric/i);
  });

  test('User can search and filter games', async ({ page }: { page: Page }) => {
    // Get initial game count
    const allGames = await page.locator('.game-card, .game-item').count();

    // Search for specific game
    await page.fill('input[placeholder*="搜索"], [data-testid="search-input"]', 'STAR');

    // Wait for filter to apply
    await page.waitForTimeout(500);

    // Get filtered game count
    const filteredGames = await page.locator('.game-card, .game-item').count();

    // Verify filter worked
    expect(filteredGames).toBeLessThanOrEqual(allGames);

    // Clear search
    await page.fill('input[placeholder*="搜索"], [data-testid="search-input"]', '');

    // Verify all games are shown again
    await page.waitForTimeout(500);
    const gamesAfterClear = await page.locator('.game-card, .game-item').count();
    expect(gamesAfterClear).toBe(allGames);
  });

  test('Game form validation works correctly', async ({ page }: { page: Page }) => {
    // Click create button
    await page.click('text=/新增|create/i');

    // Try to submit form without filling required fields
    await page.click('button[type="submit"], text=/保存|提交/i');

    // Verify validation errors
    await expect(page.locator('.error, .invalid-feedback, [data-testid*="error"]')).toBeVisible();

    // Verify submit was blocked
    await expect(page).toHaveURL(/\/games\/create/);
  });
});
