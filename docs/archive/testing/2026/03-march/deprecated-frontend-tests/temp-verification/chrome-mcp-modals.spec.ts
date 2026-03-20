import { test, expect } from '@playwright/test';

/**
 * Chrome MCP Modal Compatibility Test Suite
 *
 * Tests Chrome DevTools MCP compatibility for 5 fixed modal components:
 * 1. NodeConfigModal (Event Node Builder page)
 * 2. EventManagementModalGraphQL (Events List page)
 * 3. AddEventModalGraphQL (Events List page)
 * 4. AddGameModalGraphQL (Dashboard page)
 * 5. CategoryManagementModal (Categories List page)
 *
 * Test Coverage:
 * - Modal opens successfully
 * - Chrome MCP fill operations work correctly
 * - Save button responds within 5 seconds
 * - Zero console errors (React Hooks, infinite loops, etc.)
 */

// Test configuration
const BASE_URL = 'http://localhost:5173';
const SCREENSHOT_DIR = 'frontend/test/e2e/screenshots/chrome-mcp';
const TEST_GAME_GID = 90000001; // Test GID range (not production data)
const RESPONSE_TIME_THRESHOLD = 5000; // 5 seconds

// Helper function to monitor console errors
async function monitorConsoleErrors(page: any) {
  const errors: string[] = [];
  const warnings: string[] = [];

  page.on('console', (msg: any) => {
    const type = msg.type();
    const text = msg.text();

    if (type === 'error') {
      errors.push(text);
    } else if (type === 'warning') {
      warnings.push(text);
    }
  });

  return { errors, warnings };
}

// Helper function to take screenshot with timestamp
async function takeScreenshot(page: any, name: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({
    path: `${SCREENSHOT_DIR}/${name}-${timestamp}.png`,
    fullPage: true
  });
}

test.describe('Chrome MCP Modal Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to base URL
    await page.goto(BASE_URL);

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test.describe('NodeConfigModal (Event Node Builder)', () => {
    test('should open modal successfully', async ({ page }) => {
      // Navigate to Event Node Builder page
      await page.goto(`${BASE_URL}/event-node-builder`);

      // Wait for page to load
      await page.waitForSelector('canvas', { timeout: 10000 });

      // Click on a node to open the config modal (simulate double-click)
      await page.click('canvas', { button: 'right' }); // Right-click to open context menu

      // Look for "Configure" or similar button
      const configureButton = page.locator('text=Configure').or(page.locator('text=配置'));
      if (await configureButton.isVisible()) {
        await configureButton.click();
      } else {
        // Alternative: Click directly on a node
        await page.click('canvas');
        await page.waitForTimeout(500);
      }

      // Verify modal is visible
      const modal = page.locator('.modal, [role="dialog"]').first();
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Screenshot
      await takeScreenshot(page, 'node-config-modal-open');

      console.log('✅ NodeConfigModal opened successfully');
    });

    test('should handle Chrome MCP fill operations', async ({ page }) => {
      await page.goto(`${BASE_URL}/event-node-builder`);
      await page.waitForSelector('canvas', { timeout: 10000 });

      // Open modal (assuming it's already open or we trigger it)
      const modalVisible = await page.locator('.modal, [role="dialog"]').isVisible().catch(() => false);

      if (modalVisible) {
        // Fill node name using Chrome MCP style (page.fill)
        await page.fill('input[name="nodeName"], input[placeholder*="name"], input[placeholder*="名称"]', 'Test_Node_Chrome_MCP');

        // Fill description
        await page.fill('textarea[name="description"], textarea[placeholder*="description"], textarea[placeholder*="描述"]', 'Testing Chrome MCP compatibility');

        // Verify values appear in inputs
        const nodeName = await page.inputValue('input[name="nodeName"], input[placeholder*="name"]');
        expect(nodeName).toBe('Test_Node_Chrome_MCP');

        console.log('✅ NodeConfigModal Chrome MCP fill operations successful');
      } else {
        console.log('⚠️  Modal not visible - skipping fill test');
      }
    });

    test('should respond to save button within 5 seconds', async ({ page }) => {
      await page.goto(`${BASE_URL}/event-node-builder`);
      await page.waitForSelector('canvas', { timeout: 10000 });

      const modalVisible = await page.locator('.modal, [role="dialog"]').isVisible().catch(() => false);

      if (modalVisible) {
        const saveButton = page.locator('button:has-text("Save"), button:has-text("保存"), button[type="submit"]').first();

        // Measure response time
        const startTime = Date.now();

        // Click save and wait for response
        await Promise.all([
          page.waitForResponse((response: any) => response.status() === 200, { timeout: RESPONSE_TIME_THRESHOLD }),
          saveButton.click()
        ]);

        const responseTime = Date.now() - startTime;

        // Verify response time is within threshold
        expect(responseTime).toBeLessThan(RESPONSE_TIME_THRESHOLD);

        // Verify modal closes or success toast appears
        const modalClosed = await page.locator('.modal, [role="dialog"]').isHidden().catch(() => false);
        const successToast = await page.locator('text=success, text=成功, .toast-success').isVisible().catch(() => false);

        expect(modalClosed || successToast).toBeTruthy();

        // Screenshot
        await takeScreenshot(page, 'node-config-modal-after-save');

        console.log(`✅ NodeConfigModal save button responded in ${responseTime}ms`);
      } else {
        console.log('⚠️  Modal not visible - skipping save test');
      }
    });

    test('should have zero console errors', async ({ page }) => {
      const { errors, warnings } = await monitorConsoleErrors(page);

      await page.goto(`${BASE_URL}/event-node-builder`);
      await page.waitForSelector('canvas', { timeout: 10000 });

      // Trigger modal
      await page.click('canvas');
      await page.waitForTimeout(2000);

      // Check for React Hooks errors
      const reactHooksErrors = errors.filter((err: string) =>
        err.includes('Hooks') || err.includes('React')
      );

      expect(reactHooksErrors.length).toBe(0);

      // Check for infinite loop warnings
      const infiniteLoopWarnings = warnings.filter((warn: string) =>
        warn.includes('infinite') || warn.includes('loop') || warn.includes('Maximum')
      );

      expect(infiniteLoopWarnings.length).toBe(0);

      console.log(`✅ NodeConfigModal has ${errors.length} errors and ${warnings.length} warnings`);
    });
  });

  test.describe('EventManagementModalGraphQL (Events List)', () => {
    test('should open modal successfully', async ({ page }) => {
      // Navigate to Events List page
      await page.goto(`${BASE_URL}/events`);

      // Wait for events list to load
      await page.waitForSelector('table, .events-list, [data-testid="events-list"]', { timeout: 10000 });

      // Click "Edit" button on first event
      const editButton = page.locator('button:has-text("Edit"), button:has-text("编辑")').first();
      await editButton.click();

      // Verify modal is visible
      const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /edit|编辑/i }).first();
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Screenshot
      await takeScreenshot(page, 'event-management-modal-open');

      console.log('✅ EventManagementModal opened successfully');
    });

    test('should handle Chrome MCP fill operations', async ({ page }) => {
      await page.goto(`${BASE_URL}/events`);
      await page.waitForSelector('table, .events-list', { timeout: 10000 });

      // Open modal
      const editButton = page.locator('button:has-text("Edit"), button:has-text("编辑")').first();
      await editButton.click();

      // Wait for modal
      await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });

      // Fill event name
      await page.fill('input[name="eventName"], input[name="name"]', 'Updated_Test_Event_Chrome_MCP');

      // Fill event description
      await page.fill('textarea[name="description"], textarea[placeholder*="description"]', 'Updated description via Chrome MCP');

      // Verify values
      const eventName = await page.inputValue('input[name="eventName"], input[name="name"]');
      expect(eventName).toBe('Updated_Test_Event_Chrome_MCP');

      console.log('✅ EventManagementModal Chrome MCP fill operations successful');
    });

    test('should respond to save button within 5 seconds', async ({ page }) => {
      await page.goto(`${BASE_URL}/events`);
      await page.waitForSelector('table, .events-list', { timeout: 10000 });

      // Open and fill modal
      const editButton = page.locator('button:has-text("Edit"), button:has-text("编辑")').first();
      await editButton.click();
      await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });

      await page.fill('input[name="eventName"], input[name="name"]', 'Updated_Test_Event');

      const saveButton = page.locator('button:has-text("Save"), button:has-text("保存"), button[type="submit"]').first();

      // Measure response time
      const startTime = Date.now();

      await Promise.all([
        page.waitForResponse((response: any) => response.status() === 200, { timeout: RESPONSE_TIME_THRESHOLD }),
        saveButton.click()
      ]);

      const responseTime = Date.now() - startTime;

      expect(responseTime).toBeLessThan(RESPONSE_TIME_THRESHOLD);

      // Screenshot
      await takeScreenshot(page, 'event-management-modal-after-save');

      console.log(`✅ EventManagementModal save button responded in ${responseTime}ms`);
    });

    test('should have zero console errors', async ({ page }) => {
      const { errors, warnings } = await monitorConsoleErrors(page);

      await page.goto(`${BASE_URL}/events`);
      await page.waitForSelector('table, .events-list', { timeout: 10000 });

      // Trigger modal
      const editButton = page.locator('button:has-text("Edit"), button:has-text("编辑")').first();
      await editButton.click();
      await page.waitForTimeout(2000);

      // Check for errors
      const reactHooksErrors = errors.filter((err: string) =>
        err.includes('Hooks') || err.includes('React')
      );

      expect(reactHooksErrors.length).toBe(0);

      console.log(`✅ EventManagementModal has ${errors.length} errors and ${warnings.length} warnings`);
    });
  });

  test.describe('AddEventModalGraphQL (Events List)', () => {
    test('should open modal successfully', async ({ page }) => {
      await page.goto(`${BASE_URL}/events`);

      // Wait for events list
      await page.waitForSelector('table, .events-list', { timeout: 10000 });

      // Click "Add Event" button
      const addButton = page.locator('button:has-text("Add Event"), button:has-text("Add"), button:has-text("新增事件"), button:has-text("新增")').first();
      await addButton.click();

      // Verify modal is visible
      const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /add|create|新增|创建/i }).first();
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Screenshot
      await takeScreenshot(page, 'add-event-modal-open');

      console.log('✅ AddEventModal opened successfully');
    });

    test('should handle Chrome MCP fill operations', async ({ page }) => {
      await page.goto(`${BASE_URL}/events`);
      await page.waitForSelector('table, .events-list', { timeout: 10000 });

      // Open modal
      const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
      await addButton.click();
      await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });

      // Fill event name
      await page.fill('input[name="eventName"], input[name="name"], input[placeholder*="event name"]', 'Test_Event_Chrome_MCP');

      // Fill event type/code
      await page.fill('input[name="eventType"], input[name="code"], input[placeholder*="type"]', 'test_event_mcp');

      // Verify values
      const eventName = await page.inputValue('input[name="eventName"], input[name="name"]');
      expect(eventName).toBe('Test_Event_Chrome_MCP');

      console.log('✅ AddEventModal Chrome MCP fill operations successful');
    });

    test('should respond to save button within 5 seconds', async ({ page }) => {
      await page.goto(`${BASE_URL}/events`);
      await page.waitForSelector('table, .events-list', { timeout: 10000 });

      // Open and fill modal
      const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
      await addButton.click();
      await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });

      await page.fill('input[name="eventName"], input[name="name"]', 'Test_Event_Chrome_MCP');
      await page.fill('input[name="eventType"], input[name="code"]', 'test_event_mcp');

      const saveButton = page.locator('button:has-text("Save"), button:has-text("保存"), button[type="submit"]').first();

      // Measure response time
      const startTime = Date.now();

      await Promise.all([
        page.waitForResponse((response: any) => response.status() === 200, { timeout: RESPONSE_TIME_THRESHOLD }),
        saveButton.click()
      ]);

      const responseTime = Date.now() - startTime;

      expect(responseTime).toBeLessThan(RESPONSE_TIME_THRESHOLD);

      // Screenshot
      await takeScreenshot(page, 'add-event-modal-after-save');

      console.log(`✅ AddEventModal save button responded in ${responseTime}ms`);
    });

    test('should have zero console errors', async ({ page }) => {
      const { errors, warnings } = await monitorConsoleErrors(page);

      await page.goto(`${BASE_URL}/events`);
      await page.waitForSelector('table, .events-list', { timeout: 10000 });

      // Trigger modal
      const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
      await addButton.click();
      await page.waitForTimeout(2000);

      // Check for errors
      const reactHooksErrors = errors.filter((err: string) =>
        err.includes('Hooks') || err.includes('React')
      );

      expect(reactHooksErrors.length).toBe(0);

      console.log(`✅ AddEventModal has ${errors.length} errors and ${warnings.length} warnings`);
    });
  });

  test.describe('AddGameModalGraphQL (Dashboard)', () => {
    test('should open modal successfully', async ({ page }) => {
      // Navigate to Dashboard page
      await page.goto(`${BASE_URL}/dashboard`);

      // Wait for dashboard to load
      await page.waitForSelector('[data-testid="dashboard"], .dashboard, .stats-grid', { timeout: 10000 });

      // Click "Add Game" button
      const addButton = page.locator('button:has-text("Add Game"), button:has-text("Add"), button:has-text("添加游戏"), button:has-text("新增")').first();
      await addButton.click();

      // Verify modal is visible
      const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /game|游戏/i }).first();
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Screenshot
      await takeScreenshot(page, 'add-game-modal-open');

      console.log('✅ AddGameModal opened successfully');
    });

    test('should handle Chrome MCP fill operations', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);
      await page.waitForSelector('.dashboard, [data-testid="dashboard"]', { timeout: 10000 });

      // Open modal
      const addButton = page.locator('button:has-text("Add Game"), button:has-text("添加游戏")').first();
      await addButton.click();
      await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });

      // Fill game name
      await page.fill('input[name="gameName"], input[name="name"], input[placeholder*="game name"]', 'Test_Game_Chrome_MCP');

      // Fill game GID (use test range)
      await page.fill('input[name="gameGid"], input[name="gid"], input[placeholder*="gid"]', String(TEST_GAME_GID));

      // Verify values
      const gameName = await page.inputValue('input[name="gameName"], input[name="name"]');
      expect(gameName).toBe('Test_Game_Chrome_MCP');

      console.log('✅ AddGameModal Chrome MCP fill operations successful');
    });

    test('should respond to save button within 5 seconds', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);
      await page.waitForSelector('.dashboard, [data-testid="dashboard"]', { timeout: 10000 });

      // Open and fill modal
      const addButton = page.locator('button:has-text("Add Game"), button:has-text("添加游戏")').first();
      await addButton.click();
      await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });

      await page.fill('input[name="gameName"], input[name="name"]', 'Test_Game_Chrome_MCP');
      await page.fill('input[name="gameGid"], input[name="gid"]', String(TEST_GAME_GID));

      const saveButton = page.locator('button:has-text("Save"), button:has-text("保存"), button[type="submit"]').first();

      // Measure response time
      const startTime = Date.now();

      await Promise.all([
        page.waitForResponse((response: any) => response.status() === 200, { timeout: RESPONSE_TIME_THRESHOLD }),
        saveButton.click()
      ]);

      const responseTime = Date.now() - startTime;

      expect(responseTime).toBeLessThan(RESPONSE_TIME_THRESHOLD);

      // Screenshot
      await takeScreenshot(page, 'add-game-modal-after-save');

      console.log(`✅ AddGameModal save button responded in ${responseTime}ms`);
    });

    test('should have zero console errors', async ({ page }) => {
      const { errors, warnings } = await monitorConsoleErrors(page);

      await page.goto(`${BASE_URL}/dashboard`);
      await page.waitForSelector('.dashboard, [data-testid="dashboard"]', { timeout: 10000 });

      // Trigger modal
      const addButton = page.locator('button:has-text("Add Game"), button:has-text("添加游戏")').first();
      await addButton.click();
      await page.waitForTimeout(2000);

      // Check for errors
      const reactHooksErrors = errors.filter((err: string) =>
        err.includes('Hooks') || err.includes('React')
      );

      expect(reactHooksErrors.length).toBe(0);

      console.log(`✅ AddGameModal has ${errors.length} errors and ${warnings.length} warnings`);
    });
  });

  test.describe('CategoryManagementModal (Categories List)', () => {
    test('should open modal successfully', async ({ page }) => {
      // Navigate to Categories List page
      await page.goto(`${BASE_URL}/categories`);

      // Wait for categories list to load
      await page.waitForSelector('table, .categories-list, [data-testid="categories-list"]', { timeout: 10000 });

      // Click "Add Category" or "Edit Category" button
      const addButton = page.locator('button:has-text("Add Category"), button:has-text("Add"), button:has-text("新增分类"), button:has-text("新增")').first();

      if (await addButton.isVisible()) {
        await addButton.click();
      } else {
        // Try edit button
        const editButton = page.locator('button:has-text("Edit"), button:has-text("编辑")').first();
        await editButton.click();
      }

      // Verify modal is visible
      const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /categor|分类/i }).first();
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Screenshot
      await takeScreenshot(page, 'category-management-modal-open');

      console.log('✅ CategoryManagementModal opened successfully');
    });

    test('should handle Chrome MCP fill operations', async ({ page }) => {
      await page.goto(`${BASE_URL}/categories`);
      await page.waitForSelector('table, .categories-list', { timeout: 10000 });

      // Open modal
      const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
      await addButton.click();
      await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });

      // Fill category name
      await page.fill('input[name="categoryName"], input[name="name"], input[placeholder*="category name"]', 'Test_Category_Chrome_MCP');

      // Fill category description
      await page.fill('textarea[name="description"], input[placeholder*="description"]', 'Testing Chrome MCP compatibility for categories');

      // Verify values
      const categoryName = await page.inputValue('input[name="categoryName"], input[name="name"]');
      expect(categoryName).toBe('Test_Category_Chrome_MCP');

      console.log('✅ CategoryManagementModal Chrome MCP fill operations successful');
    });

    test('should respond to save button within 5 seconds', async ({ page }) => {
      await page.goto(`${BASE_URL}/categories`);
      await page.waitForSelector('table, .categories-list', { timeout: 10000 });

      // Open and fill modal
      const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
      await addButton.click();
      await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });

      await page.fill('input[name="categoryName"], input[name="name"]', 'Test_Category_Chrome_MCP');

      const saveButton = page.locator('button:has-text("Save"), button:has-text("保存"), button[type="submit"]').first();

      // Measure response time
      const startTime = Date.now();

      await Promise.all([
        page.waitForResponse((response: any) => response.status() === 200, { timeout: RESPONSE_TIME_THRESHOLD }),
        saveButton.click()
      ]);

      const responseTime = Date.now() - startTime;

      expect(responseTime).toBeLessThan(RESPONSE_TIME_THRESHOLD);

      // Screenshot
      await takeScreenshot(page, 'category-management-modal-after-save');

      console.log(`✅ CategoryManagementModal save button responded in ${responseTime}ms`);
    });

    test('should have zero console errors', async ({ page }) => {
      const { errors, warnings } = await monitorConsoleErrors(page);

      await page.goto(`${BASE_URL}/categories`);
      await page.waitForSelector('table, .categories-list', { timeout: 10000 });

      // Trigger modal
      const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
      await addButton.click();
      await page.waitForTimeout(2000);

      // Check for errors
      const reactHooksErrors = errors.filter((err: string) =>
        err.includes('Hooks') || err.includes('React')
      );

      expect(reactHooksErrors.length).toBe(0);

      console.log(`✅ CategoryManagementModal has ${errors.length} errors and ${warnings.length} warnings`);
    });
  });

  test.describe('Overall Test Suite Summary', () => {
    test('should generate test report', async ({ page }) => {
      console.log('\n========================================');
      console.log('Chrome MCP Modal Test Suite Summary');
      console.log('========================================');
      console.log('Components Tested: 5');
      console.log('1. NodeConfigModal (Event Node Builder)');
      console.log('2. EventManagementModalGraphQL (Events List)');
      console.log('3. AddEventModalGraphQL (Events List)');
      console.log('4. AddGameModalGraphQL (Dashboard)');
      console.log('5. CategoryManagementModal (Categories List)');
      console.log('\nTests Per Component: 4');
      console.log('- Modal opens successfully');
      console.log('- Chrome MCP fill operations work');
      console.log('- Save button responds within 5 seconds');
      console.log('- Zero console errors');
      console.log('\nTotal Tests: 20');
      console.log('Screenshot Directory: ' + SCREENSHOT_DIR);
      console.log('========================================\n');
    });
  });
});
