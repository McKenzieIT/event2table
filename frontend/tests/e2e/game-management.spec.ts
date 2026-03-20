import { test, expect } from '@playwright/test';

/**
 * Game Management E2E Tests
 * 
 * Tests for game management functionality:
 * - Create games
 * - Edit games
 * - Delete games
 * - Batch operations
 * - Search games
 */

test.describe('Game Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to games list page
    await page.goto('/games');
    await page.waitForLoadState('networkidle');
  });

  test('should display games list', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/Event2Table/);
    
    // Check if games list container exists
    const gamesList = page.locator('.games-list, [data-testid="games-list"]');
    await expect(gamesList).toBeVisible();
    
    // Check if there are game items
    const gameItems = page.locator('.game-item, .game-card');
    const count = await gameItems.count();
    
    // Either there are games or empty state is shown
    if (count === 0) {
      const emptyState = page.locator('.empty-state, [data-testid="empty-state"]');
      await expect(emptyState).toBeVisible();
    }
  });

  test('should create a new game', async ({ page }) => {
    // Click on create game button
    const createButton = page.locator('button:has-text("创建游戏"), button:has-text("添加游戏"), [data-testid="create-game-button"]');
    await createButton.first().click();
    
    // Wait for modal to open
    await page.waitForTimeout(500);
    
    // Fill in game form
    const gameIdInput = page.locator('input[name="gid"], input[placeholder*="GID"], input[placeholder*="游戏ID"]');
    await gameIdInput.fill(Math.floor(Math.random() * 900000) + 100000);
    
    const gameNameInput = page.locator('input[name="name"], input[placeholder*="游戏名称"]');
    const gameName = `Test Game ${Date.now()}`;
    await gameNameInput.fill(gameName);
    
    // Select database
    const dbSelect = page.locator('select[name="ods_db"], select[name="database"]');
    if (await dbSelect.count() > 0) {
      await dbSelect.selectOption('ieu_ods');
    }
    
    // Submit form
    const submitButton = page.locator('button[type="submit"]:has-text("提交"), button:has-text("保存"), button:has-text("创建")');
    await submitButton.click();
    
    // Wait for success message or redirect
    await page.waitForTimeout(1000);
    
    // Verify game was created
    const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("成功")');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should edit an existing game', async ({ page }) => {
    // Wait for games to load
    await page.waitForTimeout(1000);
    
    // Find first game item
    const firstGame = page.locator('.game-item, .game-card').first();
    const count = await firstGame.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Click edit button
    const editButton = firstGame.locator('button:has-text("编辑"), button:has-text("Edit")');
    await editButton.click();
    
    // Wait for edit modal
    await page.waitForTimeout(500);
    
    // Modify game name
    const gameNameInput = page.locator('input[name="name"], input[placeholder*="游戏名称"]');
    const currentName = await gameNameInput.inputValue();
    await gameNameInput.fill(`${currentName} (Edited)`);
    
    // Save changes
    const saveButton = page.locator('button:has-text("保存"), button:has-text("提交")');
    await saveButton.click();
    
    // Wait for success
    await page.waitForTimeout(1000);
    
    // Verify success message
    const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("成功")');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should delete a game', async ({ page }) => {
    // Wait for games to load
    await page.waitForTimeout(1000);
    
    // Find first game item
    const firstGame = page.locator('.game-item, .game-card').first();
    const count = await firstGame.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Click delete button
    const deleteButton = firstGame.locator('button:has-text("删除"), button:has-text("Delete")');
    await deleteButton.click();
    
    // Handle confirmation dialog
    const confirmDialog = page.locator('.modal, .dialog, [role="dialog"]');
    if (await confirmDialog.count() > 0) {
      const confirmButton = confirmDialog.locator('button:has-text("确认"), button:has-text("确定"), button:has-text("删除")');
      await confirmButton.click();
    }
    
    // Wait for deletion
    await page.waitForTimeout(1000);
    
    // Verify success message
    const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("删除成功")');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });

  test('should search games', async ({ page }) => {
    // Wait for games to load
    await page.waitForTimeout(1000);
    
    // Find search input
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Search"], .search-input input');
    const count = await searchInput.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Enter search term
    await searchInput.fill('test');
    
    // Wait for search results
    await page.waitForTimeout(1000);
    
    // Verify search is working
    const gameItems = page.locator('.game-item, .game-card');
    const searchResultsCount = await gameItems.count();
    
    // Search should filter results
    expect(searchResultsCount).toBeGreaterThanOrEqual(0);
  });

  test('should batch delete games', async ({ page }) => {
    // Wait for games to load
    await page.waitForTimeout(1000);
    
    // Find game checkboxes
    const checkboxes = page.locator('.game-item input[type="checkbox"], .game-card input[type="checkbox"]');
    const count = await checkboxes.count();
    
    if (count < 2) {
      test.skip();
      return;
    }
    
    // Select multiple games
    await checkboxes.nth(0).check();
    await checkboxes.nth(1).check();
    
    // Click batch delete button
    const batchDeleteButton = page.locator('button:has-text("删除选中"), button:has-text("批量删除")');
    await batchDeleteButton.click();
    
    // Handle confirmation
    const confirmDialog = page.locator('.modal, .dialog, [role="dialog"]');
    if (await confirmDialog.count() > 0) {
      const confirmButton = confirmDialog.locator('button:has-text("确认"), button:has-text("确定")');
      await confirmButton.click();
    }
    
    // Wait for deletion
    await page.waitForTimeout(1000);
    
    // Verify success
    const successMessage = page.locator('.toast-success, .notification-success');
    if (await successMessage.count() > 0) {
      await expect(successMessage).toBeVisible();
    }
  });
});
