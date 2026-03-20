import { test, expect, Page } from '@playwright/test';

/**
 * Events CRUD Smoke Tests
 * Phase 3: Automated E2E Testing
 *
 * Tests basic Create, Read, Update, Delete operations for events.
 * Uses test game GID 90000001 to avoid production data.
 */

interface TestConfig {
  readonly BASE_URL: string;
  readonly TEST_GAME_GID: number;
}

const CONFIG: TestConfig = {
  BASE_URL: 'http://localhost:5173',
  TEST_GAME_GID: 90000001
};

test.describe('Events CRUD Smoke Tests', () => {
  const testGameGid: number = CONFIG.TEST_GAME_GID;

  test.beforeEach(async ({ page }: { page: Page }) => {
    // Navigate to events list with test game
    await page.goto(`/#/events?game_gid=${testGameGid}`);

    // Wait for page to load
    await expect(page.locator('[data-testid="events-list"], .events-list')).toBeVisible({ timeout: 10000 });
  });

  test('Events list loads and displays events', async ({ page }: { page: Page }) => {
    // Verify events list is visible
    await expect(page.locator('.event-item, .event-card, [data-testid*="event"]')).toHaveCount({ min: 1 });

    // Verify pagination is present (if there are many events)
    const pagination = page.locator('.pagination, [data-testid="pagination"]');
    if (await pagination.isVisible()) {
      await expect(pagination).toBeVisible();
    }
  });

  test('User can navigate to create event form', async ({ page }: { page: Page }) => {
    // Click create event button
    await page.click('text=/新增|create|add/i');

    // Verify navigation to form
    await expect(page).toHaveURL(/\/events\/create/);

    // Verify form elements are present
    await expect(page.locator('input[name="event_name"], [data-testid="event-name-input"]')).toBeVisible();
    await expect(page.locator('input[name="event_name_cn"], [data-testid="event-name-cn-input"]')).toBeVisible();
    await expect(page.locator('select[name="game_gid"], [data-testid="game-gid-select"]')).toBeVisible();
  });

  test('User can create a new event', async ({ page }: { page: Page }) => {
    // Click create button
    await page.click('text=/新增|create/i');

    // Generate unique event name
    const timestamp = Date.now();
    const eventName = `e2e.test.event.${timestamp}`;
    const eventNameCn = `E2E测试事件_${timestamp}`;

    // Fill form
    await page.fill('input[name="event_name"]', eventName);
    await page.fill('input[name="event_name_cn"]', eventNameCn);
    await page.selectOption('select[name="game_gid"]', String(testGameGid));

    // Category is optional, leave as default or select first available
    const categorySelect = page.locator('select[name="category_id"]');
    if (await categorySelect.isVisible()) {
      const options = await categorySelect.locator('option').count();
      if (options > 1) {
        await categorySelect.selectOption({ index: 1 });
      }
    }

    // Submit form
    await page.click('button[type="submit"], text=/保存|提交|创建/i');

    // Wait for response and verify success
    await expect(page.locator('.toast-success, [data-testid="toast-success"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.toast-success, [data-testid="toast-success"]')).toContainText(/成功|created/i);

    // Verify navigation back to list
    await expect(page).toHaveURL(/\/events/);

    // Verify new event appears in list
    await expect(page.locator(`text=${eventName}`)).toBeVisible();
  });

  test('Event form validation works correctly', async ({ page }: { page: Page }) => {
    // Click create button
    await page.click('text=/新增|create/i');

    // Try to submit form without filling required fields
    await page.click('button[type="submit"], text=/保存|提交/i');

    // Verify validation errors
    const errorElement = page.locator('.error, .invalid-feedback, [data-testid*="error"]');
    await expect(errorElement).toBeVisible();

    // Verify submit was blocked
    await expect(page).toHaveURL(/\/events\/create/);
  });

  test('User can search and filter events', async ({ page }: { page: Page }) => {
    // Get initial event count
    const initialEvents = await page.locator('.event-item, .event-card').count();

    // Search for specific event
    await page.fill('input[placeholder*="搜索"], [data-testid="search-input"]', 'login');

    // Wait for filter to apply
    await page.waitForTimeout(500);

    // Get filtered event count
    const filteredEvents = await page.locator('.event-item, .event-card').count();

    // Verify filter worked (fewer or equal events)
    expect(filteredEvents).toBeLessThanOrEqual(initialEvents);

    // Clear search
    await page.fill('input[placeholder*="搜索"], [data-testid="search-input"]', '');

    // Verify all events are shown again
    await page.waitForTimeout(500);
    const eventsAfterClear = await page.locator('.event-item, .event-card').count();
    expect(eventsAfterClear).toBeGreaterThanOrEqual(initialEvents);
  });

  test('User can view event details', async ({ page }: { page: Page }) => {
    // Click on first event in list
    const firstEvent = page.locator('.event-item, .event-card').first();
    await firstEvent.click();

    // Verify navigation to detail page
    await expect(page).toHaveURL(/\/events\/\d+/);

    // Verify event details are displayed
    await expect(page.locator('[data-testid="event-detail"], .event-detail')).toBeVisible();
  });

  test('User can edit an existing event', async ({ page }: { page: Page }) => {
    // Click on first event
    const firstEvent = page.locator('.event-item, .event-card').first();
    await firstEvent.click();

    // Click edit button
    await page.click('text=/编辑|edit/i');

    // Verify navigation to edit form
    await expect(page).toHaveURL(/\/events\/\d+\/edit/);

    // Modify event name
    const timestamp = Date.now();
    const newName = `Updated_Event_${timestamp}`;
    await page.fill('input[name="event_name_cn"]', newName);

    // Submit form
    await page.click('button[type="submit"], text=/保存|更新/i');

    // Verify success message
    await expect(page.locator('.toast-success, [data-testid="toast-success"]')).toBeVisible();
    await expect(page.locator('.toast-success, [data-testid="toast-success"]')).toContainText(/更新|updated/i);
  });

  test('Events page has no console errors', async ({ page }: { page: Page }) => {
    // Collect console errors
    const errors: Array<{ text: string; location: { url?: string; lineNumber?: number } }> = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push({
          text: msg.text(),
          location: msg.location()
        });
      }
    });

    // Reload page to catch any errors
    await page.reload();

    // Wait for page to stabilize
    await page.waitForTimeout(2000);

    // Filter out non-critical errors
    const criticalErrors = errors.filter(err =>
      !err.text.includes('DevTools') &&
      !err.text.includes('chrome-extension') &&
      !err.text.includes('Extension')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('User can filter events by game', async ({ page }: { page: Page }) => {
    // If game filter is available
    const gameFilter = page.locator('select[name="game_gid"], [data-testid="game-filter"]');

    if (await gameFilter.isVisible()) {
      // Select different game
      await gameFilter.selectOption({ index: 0 });

      // Wait for filter to apply
      await page.waitForTimeout(1000);

      // Verify events are filtered
      await expect(page.locator('.event-item, .event-card')).toBeVisible();
    }
  });
});
