/**
 * Critical User Journey Tests - P0 Priority
 *
 * These tests cover the most critical user workflows that must work correctly.
 * P0 = Blocking issues that prevent core functionality
 *
 * Run: npx playwright test critical-journey.spec.ts
 */

import { test, expect } from '@playwright/test';

test.describe('Critical User Journeys - P0', () => {

  test.describe('Game Management', () => {

    test('should create, edit, and delete a game', async ({ page }) => {
      // Set up console and network monitoring
      page.on('console', msg => {
        if (msg.type() === 'error') {
          console.log('Browser console error:', msg.text());
        }
      });
      page.on('pageerror', error => {
        console.log('Browser page error:', error.message);
      });

      // Navigate to games list (use hash URL for HashRouter)
      await page.goto('/#/games');

      // Wait for React app to mount and page to be ready
      await page.waitForTimeout(2000);
      await page.waitForLoadState('networkidle');

      // Wait for the add button to be visible
      await expect(page.locator('[data-testid="add-game-button"]')).toBeVisible({ timeout: 10000 });

      // Click "Add Game" button
      await page.click('[data-testid="add-game-button"]');
      await page.waitForURL('/#/games/create');

      // Fill game creation form with random GID to avoid conflicts
      const testGid = 90000000 + Math.floor(Math.random() * 9999);
      console.log('Creating game with GID:', testGid);
      await page.fill('input[name="gid"]', testGid.toString());
      await page.fill('input[name="name"]', 'E2E Test Game');
      // Select ODS database type (click domestic option card)
      await page.click('[data-testid="ods-type-domestic"]');

      // Wait a bit for state to update
      await page.waitForTimeout(500);

      // Submit form
      await page.click('button[type="submit"]');

      // Verify success - should redirect to games list
      // Wait a bit for the API call to complete
      await page.waitForTimeout(3000);

      // Check if there's an error message before expecting redirect
      const errorMessage = page.locator('.alert-danger, .error, [data-testid="error-message"]');
      const hasError = await errorMessage.count() > 0;

      if (hasError) {
        const errorText = await errorMessage.textContent();
        console.log('Form submission error:', errorText);
      }

      // Check current URL
      const currentUrl = page.url();
      console.log('Current URL after submit:', currentUrl);

      await page.waitForURL('/#/games', { timeout: 10000 });

      // Success message is optional (GameForm doesn't display toast, just navigates)
      // The main verification is that the game appears in the list

      // Wait for games list to load and refresh
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);

      // Verify game appears in list - use the actual game name with .first() to handle multiple matches
      await expect(page.locator(`text=E2E Test Game`).first()).toBeVisible({ timeout: 5000 });

      // Verify game card with specific GID exists
      await expect(page.locator(`[data-testid="game-card-${testGid}"]`)).toBeVisible({ timeout: 5000 });

      // Edit the game
      await page.click(`[data-testid="edit-game-button-${testGid}"]`);
      await page.waitForURL(`/#/games/${testGid}/edit`, { timeout: 10000 });

      // Modify game name
      await page.fill('input[name="name"]', 'E2E Test Game (Updated)');
      await page.click('button[type="submit"]');

      // Wait for API call and navigation
      await page.waitForTimeout(2000);

      // Verify update - use .first() to handle potential multiple matches
      await page.waitForURL('/#/games', { timeout: 10000 });
      await expect(page.locator('text=E2E Test Game (Updated)').first()).toBeVisible({ timeout: 5000 });

      // Delete the game (DELETE API test) - set up dialog handler BEFORE clicking
      page.on('dialog', dialog => dialog.accept());
      await page.click(`[data-testid="delete-game-button-${testGid}"]`);

      // Wait for deletion to complete
      await page.waitForTimeout(2000);

      // Verify deletion success - check that the game card with our GID is not visible
      await expect(page.locator(`[data-testid="game-card-${testGid}"]`)).not.toBeVisible({ timeout: 5000 });
    });

    test('should batch delete multiple games', async ({ page }) => {
      // Create test games first
      await page.goto('/#/games/create');

      // Wait for React app to mount and form to be ready
      await page.waitForTimeout(2000);
      await page.waitForLoadState('networkidle');

      // Wait for the form input to be visible
      await expect(page.locator('input[name="gid"]')).toBeVisible({ timeout: 10000 });

      // Create first test game
      const batchGid1 = 90000000 + Math.floor(Math.random() * 9999);
      await page.fill('input[name="gid"]', batchGid1.toString());
      await page.fill('input[name="name"]', 'Batch Test Game 1');
      await page.click('[data-testid="ods-type-domestic"]');
      await page.click('button[type="submit"]');

      // Wait for navigation and game to appear
      await page.waitForTimeout(2000);
      await page.waitForURL('/#/games', { timeout: 10000 });
      await expect(page.locator('text=Batch Test Game 1').first()).toBeVisible({ timeout: 5000 });

      // Create second test game
      await page.click('[data-testid="add-game-button"]');
      await page.waitForURL('/#/games/create');

      const batchGid2 = 90000000 + Math.floor(Math.random() * 9999);
      await page.fill('input[name="gid"]', batchGid2.toString());
      await page.fill('input[name="name"]', 'Batch Test Game 2');
      await page.click('[data-testid="ods-type-domestic"]');
      await page.click('button[type="submit"]');

      // Wait for navigation and game to appear
      await page.waitForTimeout(2000);
      await page.waitForURL('/#/games', { timeout: 10000 });
      await expect(page.locator('text=Batch Test Game 2').first()).toBeVisible({ timeout: 5000 });

      // Select multiple games for deletion
      // Use .first() to handle multiple games with same name from previous test runs
      const game1Card = page.locator('.game-card').filter({ hasText: 'Batch Test Game 1' }).first();
      const game2Card = page.locator('.game-card').filter({ hasText: 'Batch Test Game 2' }).first();

      await game1Card.locator('.game-checkbox').click();
      await game2Card.locator('.game-checkbox').click();

      // Set up dialog handler BEFORE clicking delete button
      // Note: window.confirm requires page evaluation, not Playwright dialog handler
      await page.evaluate(() => {
        window.confirm = () => true; // Auto-confirm all dialogs
      });

      // Click batch delete button
      await page.click('[data-testid="delete-selected-button"]');

      // Wait for deletion to complete and for list to refresh
      await page.waitForTimeout(3000);

      // Force reload to ensure fresh data from server
      await page.reload({ waitUntil: 'networkidle' });
      await page.waitForTimeout(2000);

      // Verify DELETE API was called and games were deleted
      // Use GID-based selectors to verify specific games were deleted
      await expect(page.locator(`[data-testid="game-card-${batchGid1}"]`)).not.toBeVisible({ timeout: 5000 });
      await expect(page.locator(`[data-testid="game-card-${batchGid2}"]`)).not.toBeVisible({ timeout: 5000 });
    });

  });

  test.describe('Event Management', () => {

    test('should create, edit, and delete an event', async ({ page }) => {
      // Set up console monitoring for debugging
      page.on('console', msg => {
        if (msg.type() === 'error') {
          console.log('Browser console error:', msg.text());
        }
      });

      // Navigate to events list with game context to avoid game selection prompt
      await page.goto('/#/events?game_gid=10000147');

      // Wait for React app to mount and page to be ready
      await page.waitForTimeout(2000);
      await page.waitForLoadState('networkidle');

      // Wait for the add button to be visible
      await expect(page.locator('[data-testid="add-event-button"]')).toBeVisible({ timeout: 10000 });

      // Click "Add Event" button
      await page.click('[data-testid="add-event-button"]');
      await page.waitForURL('/#/events/create', { timeout: 10000 });

      // Fill event creation form
      await page.fill('input[name="event_name"]', 'e2e_test_event');
      await page.fill('input[name="event_name_cn"]', 'E2E Test Event');

      // Select category (first option)
      await page.selectOption('select[name="category_id"]', { index: 0 });

      // Submit form
      await page.click('button[type="submit"]');

      // Wait for API call and navigation
      await page.waitForTimeout(3000);

      // Check current URL before expecting navigation
      const currentUrl = page.url();
      console.log('Current URL after event submit:', currentUrl);

      // Verify success - navigation happened
      await page.waitForURL('/#/events', { timeout: 10000 });
      await expect(page.locator('text=E2E Test Event').first()).toBeVisible({ timeout: 5000 });

      // Edit the event
      await page.click('[data-testid="edit-event-e2e_test_event"]');
      await page.waitForURL(/\/#\/events\/.*\/edit/, { timeout: 10000 });

      // Modify event name
      await page.fill('input[name="event_name_cn"]', 'E2E Test Event (Updated)');
      await page.click('button[type="submit"]');

      // Wait for API call and navigation
      await page.waitForTimeout(3000);

      // Verify update
      await page.waitForURL('/#/events', { timeout: 10000 });
      await expect(page.locator('text=E2E Test Event (Updated)').first()).toBeVisible({ timeout: 5000 });

      // Set up dialog handler BEFORE clicking delete button
      page.on('dialog', dialog => dialog.accept());

      // Delete the event
      await page.click('[data-testid="delete-event-e2e_test_event"]');

      // Wait for deletion to complete
      await page.waitForTimeout(2000);

      // Verify deletion
      await expect(page.locator('text=E2E Test Event (Updated)').first()).not.toBeVisible();
    });

  });

  test.describe('Parameter Management', () => {

    test.skip('should add and edit event parameters', async ({ page }) => {
      // NOTE: This test is skipped because the ParametersList page is view-only.
      // Parameter creation is done through a different workflow (CommonParamsList).
      test.info().annotations.push({
        type: 'issue',
        description: 'ParametersList is view-only, parameter workflow needs to be updated'
      });

      // Navigate to parameters page
      await page.goto('/#/parameters?game_gid=10000147');
      await page.waitForLoadState('networkidle');

      // Click "Add Parameter" button
      await page.click('[data-testid="add-parameter-button"]');

      // Fill parameter form
      await page.fill('input[name="param_name"]', 'e2e_test_param');
      await page.fill('input[name="param_type"]', 'string');
      await page.fill('input[name="description"]', 'E2E Test Parameter');

      // Submit form
      await page.click('button[type="submit"]');

      // Verify parameter was added
      await expect(page.locator('text=e2e_test_param')).toBeVisible();

      // Edit parameter
      await page.click('[data-testid="edit-param-e2e_test_param"]');
      await page.fill('input[name="description"]', 'Updated description');
      await page.click('button[type="submit"]');

      // Verify update
      await expect(page.locator('text=Updated description')).toBeVisible();
    });

  });

  test.describe('API Contract Validation', () => {

    test('DELETE /api/games/:id should return 200 on success', async ({ request }) => {
      // Create a test game first (使用随机GID避免UNIQUE约束冲突)
      const testGid = 90000000 + Math.floor(Math.random() * 9999);
      const createResponse = await request.post('/api/games', {
        data: {
          gid: testGid,
          name: 'DELETE Test Game',
          ods_db: 'test_db'
        }
      });

      // 打印调试信息
      if (!createResponse.ok()) {
        const errorData = await createResponse.text();
        console.log('Create game failed:', createResponse.status(), errorData);
      }

      expect(createResponse.ok()).toBeTruthy();
      const createData = await createResponse.json();
      // API使用业务GID而非数据库ID
      const gameGid = createData.data?.gid || testGid;

      // Test DELETE API - 使用业务GID
      const deleteResponse = await request.delete(`/api/games/${gameGid}`);

      // Verify response
      expect(deleteResponse.status()).toBe(200);
      const deleteData = await deleteResponse.json();
      expect(deleteData.success).toBeTruthy();
      expect(deleteData.message).toContain('deleted successfully');
    });

    test('DELETE /api/games/:id should return 404 for non-existent game', async ({ request }) => {
      const response = await request.delete('/api/games/999999999');

      expect(response.status()).toBe(404);
      const data = await response.json();
      expect(data.error).toContain('not found');
    });

    test('DELETE /api/games/:id with events should return 409', async ({ request }) => {
      // Get a game that likely has events (game_gid = 10000147)
      const gamesResponse = await request.get('/api/games');
      const gamesData = await gamesResponse.json();
      const gameWithEvents = gamesData.data.find((g: any) => g.event_count > 0);

      if (gameWithEvents) {
        // API使用业务GID而非数据库ID
        const response = await request.delete(`/api/games/${gameWithEvents.gid}`);

        expect(response.status()).toBe(409);
        const data = await response.json();
        expect(data.error).toContain('associated events');
      }
    });

  });

});
