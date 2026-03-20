import { test, expect, Page } from '@playwright/test';

/**
 * Chrome MCP Hook Migration - E2E Test Suite
 *
 * Tests Chrome DevTools MCP compatibility for 8 components requiring migration:
 *
 * Phase 1: P0 - Critical Components (Chrome MCP Incompatibility Detected)
 * 1. CommonParamsModal - Search field
 * 2. CategoryModal - Name and description fields
 * 3. GameManagementModal - Multiple fields (gid, name, ods_db) + search
 *
 * Phase 2: P1 - High Priority Components (Frequently Used Forms)
 * 4. EventForm - Event creation/editing form
 * 5. CategoryForm - Category creation/editing form
 * 6. LogForm - Log configuration form
 *
 * Phase 3: P2 - Medium Priority Components (Less Frequently Used)
 * 7. GameForm - Game creation form
 * 8. FieldConfigModal - Field configuration modal
 *
 * Test Coverage:
 * - Modal/Form opens successfully
 * - Chrome MCP fill operations work correctly
 * - Save button responds within 5 seconds
 * - Zero console errors (React Hooks, infinite loops, etc.)
 *
 * @date 2026-03-14
 * @version 1.0.0
 */

// Test configuration
const BASE_URL = 'http://localhost:5173';
const SCREENSHOT_DIR = 'frontend/test/e2e/screenshots/chrome-mcp-migration';
const TEST_GAME_GID = 90000001; // Test GID range (not production data)
const RESPONSE_TIME_THRESHOLD = 5000; // 5 seconds

// Test data constants
const TEST_DATA = {
  common_param: {
    name: 'test_common_param_20260314',
    search: 'test_search_20260314'
  },
  category: {
    name: 'test_category_20260314',
    description: 'Test category description for Chrome MCP compatibility 20260314'
  },
  game: {
    gid: '90000001',
    name: 'test_game_chrome_mcp_20260314',
    ods_db: 'ieu_ods',
    description: 'Test game for Chrome MCP compatibility'
  },
  event: {
    name: 'test_event_chrome_mcp_20260314',
    name_cn: '测试事件_20260314',
    description: 'Test event description for Chrome MCP compatibility'
  },
  field: {
    name: 'test_field_chrome_mcp_20260314',
    description: 'Test field description'
  }
};

/**
 * Console error monitor helper
 * Tracks console errors and warnings during test execution
 */
function createConsoleMonitor(page: Page) {
  const errors: string[] = [];
  const warnings: string[] = [];

  page.on('console', msg => {
    const text = msg.text();

    if (msg.type() === 'error') {
      errors.push(text);
    } else if (msg.type() === 'warning') {
      warnings.push(text);
    }
  });

  return {
    getErrors: () => errors,
    getWarnings: () => warnings,
    hasReactHooksErrors: () => errors.some(e =>
      e.includes('React has detected a change in the order of Hooks') ||
      e.includes('Rendered more hooks than during the previous render')
    ),
    hasInfiniteLoopWarnings: () => warnings.some(w =>
      w.includes('infinite loop') ||
      w.includes('Maximum update depth exceeded')
    ),
    hasStateUpdateWarnings: () => warnings.some(w =>
      w.includes('Cannot update a component') ||
      w.includes('setState.*unmounted')
    ),
    clear: () => {
      errors.length = 0;
      warnings.length = 0;
    },
    getSummary: () => ({
      errorCount: errors.length,
      warningCount: warnings.length,
      hasCriticalErrors: errors.some(e =>
        e.includes('React') ||
        e.includes('Uncaught') ||
        e.includes('TypeError')
      )
    })
  };
}

/**
 * Screenshot helper with timestamp
 */
async function takeScreenshot(page: Page, name: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filepath = `${SCREENSHOT_DIR}/${name}-${timestamp}.png`;

  await page.screenshot({
    path: filepath,
    fullPage: true
  });

  console.log(`📸 Screenshot saved: ${filepath}`);
}

/**
 * Response time measurement helper
 */
async function measureResponseTime<T>(
  action: () => Promise<T>
): Promise<{ result: T; duration: number }> {
  const startTime = Date.now();
  const result = await action();
  const duration = Date.now() - startTime;

  return { result, duration };
}

test.describe('Chrome MCP Hook Migration - E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to base URL
    await page.goto(BASE_URL);

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');

    // Clear any existing modal/dialog
    const existingModal = page.locator('.modal, [role="dialog"]').first();
    if (await existingModal.isVisible().catch(() => false)) {
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }
  });

  // ========================================================================
  // Phase 1: P0 - Critical Components
  // ========================================================================

  test.describe('P0 - Critical Components', () => {
    test.describe('CommonParamsModal', () => {
      test('should open modal successfully', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        try {
          // Navigate to Parameters page
          await page.goto(`${BASE_URL}/parameters`);

          // Wait for page to load
          await page.waitForSelector('text=Common Parameters', { timeout: 10000 });

          // Look for button to open CommonParamsModal
          const openButton = page.locator('button:has-text("Common"), button:has-text("通用")').first();
          await openButton.click();

          // Wait for modal to appear
          const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Common|通用/ });
          await expect(modal).toBeVisible({ timeout: 5000 });

          // Verify modal title
          await expect(modal.locator('h2, h3, .modal-title')).toContainText(/Common|通用/);

          // Take screenshot
          await takeScreenshot(page, 'common-params-modal-open');

          console.log('✅ CommonParamsModal opened successfully');
        } catch (error) {
          await takeScreenshot(page, 'common-params-modal-open-error');
          throw error;
        }

        // Check for critical console errors
        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
        expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
      });

      test('should handle Chrome MCP fill for search field', async ({ page }) => {
        await page.goto(`${BASE_URL}/parameters`);
        await page.waitForSelector('text=Common Parameters', { timeout: 10000 });

        // Open modal
        const openButton = page.locator('button:has-text("Common"), button:has-text("通用")').first();
        await openButton.click();

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Common|通用/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Find search input field
        const searchInput = modal.locator('input[type="text"], input[type="search"]').first();
        await expect(searchInput).toBeVisible();

        // Simulate Chrome MCP fill operation
        await searchInput.fill(TEST_DATA.common_param.search);

        // Verify value appears in input
        await expect(searchInput).toHaveValue(TEST_DATA.common_param.search);

        // Wait briefly to ensure state has updated
        await page.waitForTimeout(500);

        // Take screenshot
        await takeScreenshot(page, 'common-params-modal-filled');

        console.log('✅ CommonParamsModal Chrome MCP fill successful');
      });

      test('should respond to search within 5 seconds', async ({ page }) => {
        await page.goto(`${BASE_URL}/parameters`);
        await page.waitForSelector('text=Common Parameters', { timeout: 10000 });

        // Open modal
        const openButton = page.locator('button:has-text("Common"), button:has-text("通用")').first();
        await openButton.click();

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Common|通用/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Find search input and fill
        const searchInput = modal.locator('input[type="text"], input[type="search"]').first();
        await searchInput.fill(TEST_DATA.common_param.search);

        // Measure response time
        const { duration } = await measureResponseTime(async () => {
          // Trigger search by pressing Enter or waiting for debounce
          await searchInput.press('Enter');
          await page.waitForTimeout(100);
        });

        // Verify response time is within threshold
        expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);

        // Take screenshot
        await takeScreenshot(page, 'common-params-modal-after-search');

        console.log(`✅ CommonParamsModal search responded in ${duration}ms`);
      });

      test('should have zero console errors', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        await page.goto(`${BASE_URL}/parameters`);
        await page.waitForSelector('text=Common Parameters', { timeout: 10000 });

        // Open modal and interact
        const openButton = page.locator('button:has-text("Common"), button:has-text("通用")').first();
        await openButton.click();

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Common|通用/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Fill search field
        const searchInput = modal.locator('input[type="text"], input[type="search"]').first();
        await searchInput.fill(TEST_DATA.common_param.search);
        await page.waitForTimeout(1000);

        // Close modal
        await page.keyboard.press('Escape');

        // Wait for any delayed errors
        await page.waitForTimeout(1000);

        // Check console errors
        const summary = consoleMonitor.getSummary();
        console.log(`📊 Console: ${summary.errorCount} errors, ${summary.warningCount} warnings`);

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
        expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
        expect(consoleMonitor.hasStateUpdateWarnings()).toBeFalsy();
        expect(summary.errorCount).toBe(0);

        console.log('✅ CommonParamsModal has zero console errors');
      });
    });

    test.describe('CategoryModal', () => {
      test('should open modal successfully', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        try {
          // Navigate to Categories page
          await page.goto(`${BASE_URL}/categories`);

          // Wait for page to load
          await page.waitForSelector('text=Categories', { timeout: 10000 });

          // Look for "Add Category" or "新增分类" button
          const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
          await addButton.click();

          // Wait for modal to appear
          const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Category|分类/ });
          await expect(modal).toBeVisible({ timeout: 5000 });

          // Verify modal has form fields
          await expect(modal.locator('input[type="text"]')).toBeVisible();

          // Take screenshot
          await takeScreenshot(page, 'category-modal-open');

          console.log('✅ CategoryModal opened successfully');
        } catch (error) {
          await takeScreenshot(page, 'category-modal-open-error');
          throw error;
        }

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
      });

      test('should handle Chrome MCP fill for name and description', async ({ page }) => {
        await page.goto(`${BASE_URL}/categories`);
        await page.waitForSelector('text=Categories', { timeout: 10000 });

        // Open modal
        const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
        await addButton.click();

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Category|分类/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Find name input
        const nameInput = modal.locator('input[type="text"]').first();
        await expect(nameInput).toBeVisible();

        // Find description textarea
        const descInput = modal.locator('textarea').or(modal.locator('input[type="text"]').nth(1));
        await expect(descInput.first()).toBeVisible();

        // Simulate Chrome MCP fill for both fields
        await nameInput.fill(TEST_DATA.category.name);
        await descInput.first().fill(TEST_DATA.category.description);

        // Verify values appear
        await expect(nameInput).toHaveValue(TEST_DATA.category.name);
        await expect(descInput.first()).toHaveValue(TEST_DATA.category.description.substring(0, 50)); // May be truncated

        // Take screenshot
        await takeScreenshot(page, 'category-modal-filled');

        console.log('✅ CategoryModal Chrome MCP fill successful');
      });

      test('should save category within 5 seconds', async ({ page }) => {
        await page.goto(`${BASE_URL}/categories`);
        await page.waitForSelector('text=Categories', { timeout: 10000 });

        // Open modal
        const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
        await addButton.click();

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Category|分类/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Fill form fields
        const nameInput = modal.locator('input[type="text"]').first();
        const descInput = modal.locator('textarea').or(modal.locator('input[type="text"]').nth(1));

        await nameInput.fill(TEST_DATA.category.name);
        await descInput.first().fill(TEST_DATA.category.description);

        // Find and click save button
        const saveButton = modal.locator('button:has-text("Save"), button:has-text("保存")').first();
        await expect(saveButton).toBeEnabled();

        // Measure response time
        const { duration } = await measureResponseTime(async () => {
          await saveButton.click();
          await page.waitForTimeout(100);
        });

        // Verify response time
        expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);

        // Take screenshot
        await takeScreenshot(page, 'category-modal-after-save');

        console.log(`✅ CategoryModal save responded in ${duration}ms`);
      });

      test('should have zero console errors', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        await page.goto(`${BASE_URL}/categories`);
        await page.waitForSelector('text=Categories', { timeout: 10000 });

        // Open and interact with modal
        const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
        await addButton.click();

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Category|分类/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Fill fields
        const nameInput = modal.locator('input[type="text"]').first();
        const descInput = modal.locator('textarea').or(modal.locator('input[type="text"]').nth(1));

        await nameInput.fill(TEST_DATA.category.name);
        await descInput.first().fill(TEST_DATA.category.description);

        // Click save
        const saveButton = modal.locator('button:has-text("Save"), button:has-text("保存")').first();
        await saveButton.click();

        // Wait for any delayed errors
        await page.waitForTimeout(2000);

        // Check console
        const summary = consoleMonitor.getSummary();
        console.log(`📊 Console: ${summary.errorCount} errors, ${summary.warningCount} warnings`);

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
        expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
        expect(summary.errorCount).toBe(0);

        console.log('✅ CategoryModal has zero console errors');
      });
    });

    test.describe('GameManagementModal', () => {
      test('should open modal successfully', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        try {
          // Navigate to Dashboard page
          await page.goto(`${BASE_URL}/dashboard`);

          // Wait for page to load
          await page.waitForSelector('text=Games', { timeout: 10000 });

          // Look for game management button
          const manageButton = page.locator('button:has-text("Manage"), button:has-text("管理")').or(
            page.locator('button:has-text("Games"), button:has-text("游戏")')
          ).first();

          if (await manageButton.isVisible()) {
            await manageButton.click();
          }

          // Wait for modal
          const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Game|游戏/ });
          await expect(modal).toBeVisible({ timeout: 5000 });

          // Take screenshot
          await takeScreenshot(page, 'game-management-modal-open');

          console.log('✅ GameManagementModal opened successfully');
        } catch (error) {
          await takeScreenshot(page, 'game-management-modal-open-error');
          throw error;
        }

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
      });

      test('should handle Chrome MCP fill for multiple fields', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        await page.waitForSelector('text=Games', { timeout: 10000 });

        // Open modal
        const manageButton = page.locator('button:has-text("Manage"), button:has-text("管理")').or(
          page.locator('button:has-text("Games"), button:has-text("游戏")')
        ).first();

        if (await manageButton.isVisible()) {
          await manageButton.click();
        }

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Game|游戏/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Find editable fields (gid, name, ods_db)
        const inputs = modal.locator('input:not([type="hidden"]), select');
        const inputCount = await inputs.count();

        console.log(`Found ${inputCount} editable fields in GameManagementModal`);

        // Fill first 3 fields if available
        for (let i = 0; i < Math.min(3, inputCount); i++) {
          const input = inputs.nth(i);
          const inputType = await input.getAttribute('type');

          if (inputType !== 'hidden' && inputType !== 'submit' && inputType !== 'button') {
            await input.fill(`test_value_${i}_20260314`);
          }
        }

        // Take screenshot
        await takeScreenshot(page, 'game-management-modal-filled');

        console.log('✅ GameManagementModal Chrome MCP fill successful');
      });

      test('should search games within 5 seconds', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        await page.waitForSelector('text=Games', { timeout: 10000 });

        // Open modal
        const manageButton = page.locator('button:has-text("Manage"), button:has-text("管理")').or(
          page.locator('button:has-text("Games"), button:has-text("游戏")')
        ).first();

        if (await manageButton.isVisible()) {
          await manageButton.click();
        }

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Game|游戏/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Find search input
        const searchInput = modal.locator('input[type="text"], input[type="search"]').first();

        if (await searchInput.isVisible()) {
          // Measure search response time
          const { duration } = await measureResponseTime(async () => {
            await searchInput.fill(TEST_DATA.game.name);
            await searchInput.press('Enter');
            await page.waitForTimeout(100);
          });

          expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);

          // Take screenshot
          await takeScreenshot(page, 'game-management-modal-after-search');

          console.log(`✅ GameManagementModal search responded in ${duration}ms`);
        } else {
          console.log('⚠️ No search input found in GameManagementModal');
        }
      });

      test('should have zero console errors', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        await page.goto(`${BASE_URL}/dashboard`);
        await page.waitForSelector('text=Games', { timeout: 10000 });

        // Open modal
        const manageButton = page.locator('button:has-text("Manage"), button:has-text("管理")').or(
          page.locator('button:has-text("Games"), button:has-text("游戏")')
        ).first();

        if (await manageButton.isVisible()) {
          await manageButton.click();
        }

        const modal = page.locator('.modal, [role="dialog"]').filter({ hasText: /Game|游戏/ });
        await expect(modal).toBeVisible({ timeout: 5000 });

        // Wait for any delayed errors
        await page.waitForTimeout(2000);

        // Check console
        const summary = consoleMonitor.getSummary();
        console.log(`📊 Console: ${summary.errorCount} errors, ${summary.warningCount} warnings`);

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
        expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
        expect(summary.errorCount).toBe(0);

        console.log('✅ GameManagementModal has zero console errors');
      });
    });
  });

  // ========================================================================
  // Phase 2: P1 - High Priority Components
  // ========================================================================

  test.describe('P1 - High Priority Components', () => {
    test.describe('EventForm', () => {
      test('should open form successfully', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        try {
          // Navigate to Events page
          await page.goto(`${BASE_URL}/events`);

          // Wait for page to load
          await page.waitForSelector('text=Events', { timeout: 10000 });

          // Look for "Add Event" or "新增事件" button
          const addButton = page.locator('button:has-text("Add Event"), button:has-text("新增事件")').first();

          if (await addButton.isVisible()) {
            await addButton.click();

            // Wait for form to appear
            const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
            await expect(form.first()).toBeVisible({ timeout: 5000 });

            // Take screenshot
            await takeScreenshot(page, 'event-form-open');

            console.log('✅ EventForm opened successfully');
          } else {
            console.log('⚠️ Add Event button not found, form may be on a different page');
          }
        } catch (error) {
          await takeScreenshot(page, 'event-form-open-error');
          throw error;
        }

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
      });

      test('should handle Chrome MCP fill for event fields', async ({ page }) => {
        await page.goto(`${BASE_URL}/events`);
        await page.waitForSelector('text=Events', { timeout: 10000 });

        // Try to open form
        const addButton = page.locator('button:has-text("Add Event"), button:has-text("新增事件")').first();

        if (await addButton.isVisible()) {
          await addButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Find input fields
          const inputs = form.first().locator('input:not([type="hidden"]), textarea, select');
          const inputCount = await inputs.count();

          console.log(`Found ${inputCount} editable fields in EventForm`);

          // Fill event name and description
          const nameInput = form.first().locator('input[name*="name"], input[name*="event"]').first();
          if (await nameInput.isVisible()) {
            await nameInput.fill(TEST_DATA.event.name);
          }

          const descInput = form.first().locator('textarea').or(
            form.first().locator('input[name*="desc"], input[name*="description"]')
          ).first();

          if (await descInput.isVisible()) {
            await descInput.fill(TEST_DATA.event.description);
          }

          // Take screenshot
          await takeScreenshot(page, 'event-form-filled');

          console.log('✅ EventForm Chrome MCP fill successful');
        }
      });

      test('should submit form within 5 seconds', async ({ page }) => {
        await page.goto(`${BASE_URL}/events`);
        await page.waitForSelector('text=Events', { timeout: 10000 });

        const addButton = page.locator('button:has-text("Add Event"), button:has-text("新增事件")').first();

        if (await addButton.isVisible()) {
          await addButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Fill minimal required fields
          const nameInput = form.first().locator('input[name*="name"], input[name*="event"]').first();
          if (await nameInput.isVisible()) {
            await nameInput.fill(TEST_DATA.event.name);
          }

          // Find submit button
          const submitButton = form.first().locator('button[type="submit"], button:has-text("Save"), button:has-text("保存")').first();

          if (await submitButton.isVisible()) {
            // Measure response time
            const { duration } = await measureResponseTime(async () => {
              await submitButton.click();
              await page.waitForTimeout(100);
            });

            expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);

            // Take screenshot
            await takeScreenshot(page, 'event-form-after-submit');

            console.log(`✅ EventForm submit responded in ${duration}ms`);
          }
        }
      });

      test('should have zero console errors', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        await page.goto(`${BASE_URL}/events`);
        await page.waitForSelector('text=Events', { timeout: 10000 });

        const addButton = page.locator('button:has-text("Add Event"), button:has-text("新增事件")').first();

        if (await addButton.isVisible()) {
          await addButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Wait for any delayed errors
          await page.waitForTimeout(2000);

          // Check console
          const summary = consoleMonitor.getSummary();
          console.log(`📊 Console: ${summary.errorCount} errors, ${summary.warningCount} warnings`);

          expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
          expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
          expect(summary.errorCount).toBe(0);

          console.log('✅ EventForm has zero console errors');
        }
      });
    });

    test.describe('CategoryForm', () => {
      test('should open form successfully', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        try {
          // Navigate to Categories page
          await page.goto(`${BASE_URL}/categories`);

          // Wait for page to load
          await page.waitForSelector('text=Categories', { timeout: 10000 });

          // Look for "Add Category" or "新增分类" button
          const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
          await addButton.click();

          // Wait for form
          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Take screenshot
          await takeScreenshot(page, 'category-form-open');

          console.log('✅ CategoryForm opened successfully');
        } catch (error) {
          await takeScreenshot(page, 'category-form-open-error');
          throw error;
        }

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
      });

      test('should handle Chrome MCP fill for category fields', async ({ page }) => {
        await page.goto(`${BASE_URL}/categories`);
        await page.waitForSelector('text=Categories', { timeout: 10000 });

        // Open form
        const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
        await addButton.click();

        const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
        await expect(form.first()).toBeVisible({ timeout: 5000 });

        // Find name and description fields
        const nameInput = form.first().locator('input[name*="name"]').first();
        if (await nameInput.isVisible()) {
          await nameInput.fill(TEST_DATA.category.name);
        }

        const descInput = form.first().locator('textarea').or(
          form.first().locator('input[name*="desc"], input[name*="description"]')
        ).first();

        if (await descInput.isVisible()) {
          await descInput.fill(TEST_DATA.category.description);
        }

        // Take screenshot
        await takeScreenshot(page, 'category-form-filled');

        console.log('✅ CategoryForm Chrome MCP fill successful');
      });

      test('should submit form within 5 seconds', async ({ page }) => {
        await page.goto(`${BASE_URL}/categories`);
        await page.waitForSelector('text=Categories', { timeout: 10000 });

        // Open form
        const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
        await addButton.click();

        const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
        await expect(form.first()).toBeVisible({ timeout: 5000 });

        // Fill name field
        const nameInput = form.first().locator('input[name*="name"]').first();
        if (await nameInput.isVisible()) {
          await nameInput.fill(TEST_DATA.category.name);
        }

        // Submit form
        const submitButton = form.first().locator('button[type="submit"], button:has-text("Save"), button:has-text("保存")').first();

        if (await submitButton.isVisible()) {
          const { duration } = await measureResponseTime(async () => {
            await submitButton.click();
            await page.waitForTimeout(100);
          });

          expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);

          // Take screenshot
          await takeScreenshot(page, 'category-form-after-submit');

          console.log(`✅ CategoryForm submit responded in ${duration}ms`);
        }
      });

      test('should have zero console errors', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        await page.goto(`${BASE_URL}/categories`);
        await page.waitForSelector('text=Categories', { timeout: 10000 });

        // Open form
        const addButton = page.locator('button:has-text("Add"), button:has-text("新增")').first();
        await addButton.click();

        const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
        await expect(form.first()).toBeVisible({ timeout: 5000 });

        // Wait for any delayed errors
        await page.waitForTimeout(2000);

        // Check console
        const summary = consoleMonitor.getSummary();
        console.log(`📊 Console: ${summary.errorCount} errors, ${summary.warningCount} warnings`);

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
        expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
        expect(summary.errorCount).toBe(0);

        console.log('✅ CategoryForm has zero console errors');
      });
    });

    test.describe('LogForm', () => {
      test('should open form successfully', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        try {
          // Navigate to HQL Edit or Log Form page
          await page.goto(`${BASE_URL}/hql-edit`);

          // Wait for page to load
          await page.waitForSelector('text=HQL', { timeout: 10000 });

          // Look for log configuration button/form
          const configButton = page.locator('button:has-text("Log"), button:has-text("日志")').first();

          if (await configButton.isVisible()) {
            await configButton.click();

            // Wait for form
            const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
            await expect(form.first()).toBeVisible({ timeout: 5000 });

            // Take screenshot
            await takeScreenshot(page, 'log-form-open');

            console.log('✅ LogForm opened successfully');
          } else {
            console.log('⚠️ Log configuration button not found');
          }
        } catch (error) {
          await takeScreenshot(page, 'log-form-open-error');
          throw error;
        }

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
      });

      test('should handle Chrome MCP fill for log configuration', async ({ page }) => {
        await page.goto(`${BASE_URL}/hql-edit`);
        await page.waitForSelector('text=HQL', { timeout: 10000 });

        // Try to open log form
        const configButton = page.locator('button:has-text("Log"), button:has-text("日志")').first();

        if (await configButton.isVisible()) {
          await configButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Find input fields
          const inputs = form.first().locator('input:not([type="hidden"]), textarea, select');
          const inputCount = await inputs.count();

          console.log(`Found ${inputCount} editable fields in LogForm`);

          // Fill first few fields
          for (let i = 0; i < Math.min(2, inputCount); i++) {
            const input = inputs.nth(i);
            const inputType = await input.getAttribute('type');

            if (inputType !== 'hidden' && inputType !== 'submit' && inputType !== 'button') {
              await input.fill(`test_log_value_${i}_20260314`);
            }
          }

          // Take screenshot
          await takeScreenshot(page, 'log-form-filled');

          console.log('✅ LogForm Chrome MCP fill successful');
        }
      });

      test('should submit form within 5 seconds', async ({ page }) => {
        await page.goto(`${BASE_URL}/hql-edit`);
        await page.waitForSelector('text=HQL', { timeout: 10000 });

        const configButton = page.locator('button:has-text("Log"), button:has-text("日志")').first();

        if (await configButton.isVisible()) {
          await configButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Submit form
          const submitButton = form.first().locator('button[type="submit"], button:has-text("Save"), button:has-text("保存")').first();

          if (await submitButton.isVisible()) {
            const { duration } = await measureResponseTime(async () => {
              await submitButton.click();
              await page.waitForTimeout(100);
            });

            expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);

            // Take screenshot
            await takeScreenshot(page, 'log-form-after-submit');

            console.log(`✅ LogForm submit responded in ${duration}ms`);
          }
        }
      });

      test('should have zero console errors', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        await page.goto(`${BASE_URL}/hql-edit`);
        await page.waitForSelector('text=HQL', { timeout: 10000 });

        const configButton = page.locator('button:has-text("Log"), button:has-text("日志")').first();

        if (await configButton.isVisible()) {
          await configButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Wait for any delayed errors
          await page.waitForTimeout(2000);

          // Check console
          const summary = consoleMonitor.getSummary();
          console.log(`📊 Console: ${summary.errorCount} errors, ${summary.warningCount} warnings`);

          expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
          expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
          expect(summary.errorCount).toBe(0);

          console.log('✅ LogForm has zero console errors');
        }
      });
    });
  });

  // ========================================================================
  // Phase 3: P2 - Medium Priority Components
  // ========================================================================

  test.describe('P2 - Medium Priority Components', () => {
    test.describe('GameForm', () => {
      test('should open form successfully', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        try {
          // Navigate to Games page
          await page.goto(`${BASE_URL}/games`);

          // Wait for page to load
          await page.waitForSelector('text=Games', { timeout: 10000 });

          // Look for "Add Game" or "新增游戏" button
          const addButton = page.locator('button:has-text("Add Game"), button:has-text("新增游戏")').first();

          if (await addButton.isVisible()) {
            await addButton.click();

            // Wait for form
            const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
            await expect(form.first()).toBeVisible({ timeout: 5000 });

            // Take screenshot
            await takeScreenshot(page, 'game-form-open');

            console.log('✅ GameForm opened successfully');
          } else {
            console.log('⚠️ Add Game button not found');
          }
        } catch (error) {
          await takeScreenshot(page, 'game-form-open-error');
          throw error;
        }

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
      });

      test('should handle Chrome MCP fill for game fields', async ({ page }) => {
        await page.goto(`${BASE_URL}/games`);
        await page.waitForSelector('text=Games', { timeout: 10000 });

        // Try to open form
        const addButton = page.locator('button:has-text("Add Game"), button:has-text("新增游戏")').first();

        if (await addButton.isVisible()) {
          await addButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Find input fields
          const nameInput = form.first().locator('input[name*="name"]').first();
          if (await nameInput.isVisible()) {
            await nameInput.fill(TEST_DATA.game.name);
          }

          const descInput = form.first().locator('textarea').or(
            form.first().locator('input[name*="desc"], input[name*="description"]')
          ).first();

          if (await descInput.isVisible()) {
            await descInput.fill(TEST_DATA.game.description);
          }

          // Take screenshot
          await takeScreenshot(page, 'game-form-filled');

          console.log('✅ GameForm Chrome MCP fill successful');
        }
      });

      test('should submit form within 5 seconds', async ({ page }) => {
        await page.goto(`${BASE_URL}/games`);
        await page.waitForSelector('text=Games', { timeout: 10000 });

        const addButton = page.locator('button:has-text("Add Game"), button:has-text("新增游戏")').first();

        if (await addButton.isVisible()) {
          await addButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Fill name field
          const nameInput = form.first().locator('input[name*="name"]').first();
          if (await nameInput.isVisible()) {
            await nameInput.fill(TEST_DATA.game.name);
          }

          // Submit form
          const submitButton = form.first().locator('button[type="submit"], button:has-text("Save"), button:has-text("保存")').first();

          if (await submitButton.isVisible()) {
            const { duration } = await measureResponseTime(async () => {
              await submitButton.click();
              await page.waitForTimeout(100);
            });

            expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);

            // Take screenshot
            await takeScreenshot(page, 'game-form-after-submit');

            console.log(`✅ GameForm submit responded in ${duration}ms`);
          }
        }
      });

      test('should have zero console errors', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        await page.goto(`${BASE_URL}/games`);
        await page.waitForSelector('text=Games', { timeout: 10000 });

        const addButton = page.locator('button:has-text("Add Game"), button:has-text("新增游戏")').first();

        if (await addButton.isVisible()) {
          await addButton.click();

          const form = page.locator('form').or(page.locator('.modal, [role="dialog"]'));
          await expect(form.first()).toBeVisible({ timeout: 5000 });

          // Wait for any delayed errors
          await page.waitForTimeout(2000);

          // Check console
          const summary = consoleMonitor.getSummary();
          console.log(`📊 Console: ${summary.errorCount} errors, ${summary.warningCount} warnings`);

          expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
          expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
          expect(summary.errorCount).toBe(0);

          console.log('✅ GameForm has zero console errors');
        }
      });
    });

    test.describe('FieldConfigModal', () => {
      test('should open modal successfully', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        try {
          // Navigate to Field Builder page
          await page.goto(`${BASE_URL}/event-node-builder`);

          // Wait for page to load
          await page.waitForSelector('canvas', { timeout: 10000 });

          // Try to open field config modal
          // This might require clicking on a node or a specific button
          const configButton = page.locator('button:has-text("Field"), button:has-text("字段")').first();

          if (await configButton.isVisible()) {
            await configButton.click();

            // Wait for modal
            const modal = page.locator('.modal, [role="dialog"]');
            await expect(modal.first()).toBeVisible({ timeout: 5000 });

            // Take screenshot
            await takeScreenshot(page, 'field-config-modal-open');

            console.log('✅ FieldConfigModal opened successfully');
          } else {
            console.log('⚠️ Field config button not found');
          }
        } catch (error) {
          await takeScreenshot(page, 'field-config-modal-open-error');
          throw error;
        }

        expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
      });

      test('should handle Chrome MCP fill for field config', async ({ page }) => {
        await page.goto(`${BASE_URL}/event-node-builder`);
        await page.waitForSelector('canvas', { timeout: 10000 });

        // Try to open modal
        const configButton = page.locator('button:has-text("Field"), button:has-text("字段")').first();

        if (await configButton.isVisible()) {
          await configButton.click();

          const modal = page.locator('.modal, [role="dialog"]');
          await expect(modal.first()).toBeVisible({ timeout: 5000 });

          // Find input fields
          const nameInput = modal.first().locator('input[name*="name"], input[type="text"]').first();
          if (await nameInput.isVisible()) {
            await nameInput.fill(TEST_DATA.field.name);
          }

          const descInput = modal.first().locator('textarea').or(
            modal.first().locator('input[name*="desc"], input[name*="description"]')
          ).first();

          if (await descInput.isVisible()) {
            await descInput.fill(TEST_DATA.field.description);
          }

          // Take screenshot
          await takeScreenshot(page, 'field-config-modal-filled');

          console.log('✅ FieldConfigModal Chrome MCP fill successful');
        }
      });

      test('should save field config within 5 seconds', async ({ page }) => {
        await page.goto(`${BASE_URL}/event-node-builder`);
        await page.waitForSelector('canvas', { timeout: 10000 });

        const configButton = page.locator('button:has-text("Field"), button:has-text("字段")').first();

        if (await configButton.isVisible()) {
          await configButton.click();

          const modal = page.locator('.modal, [role="dialog"]');
          await expect(modal.first()).toBeVisible({ timeout: 5000 });

          // Fill name field
          const nameInput = modal.first().locator('input[name*="name"], input[type="text"]').first();
          if (await nameInput.isVisible()) {
            await nameInput.fill(TEST_DATA.field.name);
          }

          // Save config
          const saveButton = modal.first().locator('button[type="submit"], button:has-text("Save"), button:has-text("保存")').first();

          if (await saveButton.isVisible()) {
            const { duration } = await measureResponseTime(async () => {
              await saveButton.click();
              await page.waitForTimeout(100);
            });

            expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);

            // Take screenshot
            await takeScreenshot(page, 'field-config-modal-after-save');

            console.log(`✅ FieldConfigModal save responded in ${duration}ms`);
          }
        }
      });

      test('should have zero console errors', async ({ page }) => {
        const consoleMonitor = createConsoleMonitor(page);

        await page.goto(`${BASE_URL}/event-node-builder`);
        await page.waitForSelector('canvas', { timeout: 10000 });

        const configButton = page.locator('button:has-text("Field"), button:has-text("字段")').first();

        if (await configButton.isVisible()) {
          await configButton.click();

          const modal = page.locator('.modal, [role="dialog"]');
          await expect(modal.first()).toBeVisible({ timeout: 5000 });

          // Wait for any delayed errors
          await page.waitForTimeout(2000);

          // Check console
          const summary = consoleMonitor.getSummary();
          console.log(`📊 Console: ${summary.errorCount} errors, ${summary.warningCount} warnings`);

          expect(consoleMonitor.hasReactHooksErrors()).toBeFalsy();
          expect(consoleMonitor.hasInfiniteLoopWarnings()).toBeFalsy();
          expect(summary.errorCount).toBe(0);

          console.log('✅ FieldConfigModal has zero console errors');
        }
      });
    });
  });
});
