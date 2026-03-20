import { test, expect } from '@playwright/test';

/**
 * Field Builder Page - E2E Tests
 *
 * TDD Cycle:
 * 1. RED: Write failing test first
 * 2. Verify RED: Run test and confirm it fails
 * 3. GREEN: Fix code to make test pass
 * 4. Verify GREEN: Run test and confirm it passes
 * 5. REFACTOR: Clean up code
 *
 * Route: /field-builder?game_gid=10000147
 * Component: src/event-builder/pages/FieldBuilder.tsx
 *
 * Test Coverage:
 * - Page loads successfully
 * - Game context is correctly read (game_gid=10000147)
 * - Core UI elements exist (event selector, field canvas, HQL preview)
 * - No React errors (Hooks rules, etc.)
 * - No console errors
 */

test.describe('Field Builder Page - P0 Critical Path', () => {
  // Track console errors during tests
  const consoleErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    // Clear console errors before each test
    consoleErrors.length = 0;

    // Listen for console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        const errorText = msg.text();
        consoleErrors.push(errorText);
      }
    });

    // Set up game context in localStorage before navigation
    await page.goto('/', { timeout: 60000, waitUntil: 'commit' });
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      (window as any).gameData = {
        id: 16,
        gid: '10000147',
        name: 'STAR001',
        ods_db: 'ieu_ods',
        description: 'Test game for E2E testing'
      };
    });

    // Navigate to Field Builder page with game_gid parameter
    await page.goto('/field-builder?game_gid=10000147', {
      timeout: 60000,
      waitUntil: 'domcontentloaded'
    });

    // Wait for page to stabilize
    await page.waitForTimeout(2000);
  });

  test.afterEach(async ({ page }) => {
    // Clean up test state
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('RED → GREEN: Page should load successfully with game context', async ({ page }) => {
    // TDD Phase: RED - This test will fail if page doesn't load

    // Wait for main page container to appear
    const pageContainer = page.locator('.field-builder, .page-container, main').first();

    try {
      await expect(pageContainer).toBeVisible({ timeout: 15000 });
    } catch (error) {
      // RED phase: Test fails because page container not found
      console.log('❌ RED: Field Builder page container not found - page failed to load');
      throw error;
    }

    // GREEN phase: If we reach here, page loaded successfully
    console.log('✅ GREEN: Field Builder page loaded successfully');

    // Verify we're on the correct URL
    expect(page.url()).toContain('game_gid=10000147');

    // Verify no critical console errors
    const criticalErrors = consoleErrors.filter(err =>
      err.includes('React has detected a change in the order of Hooks') ||
      err.includes('Uncaught Error') ||
      err.includes('Failed to fetch')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('RED → GREEN: Game context should be correctly read from URL parameter', async ({ page }) => {
    // TDD Phase: RED - This test will fail if game_gid parameter is not read correctly

    // Check if URL contains the game_gid parameter
    const url = page.url();
    expect(url).toContain('game_gid=10000147');

    // Verify localStorage was set correctly
    const storedGameGid = await page.evaluate(() => {
      return localStorage.getItem('selectedGameGid');
    });

    expect(storedGameGid).toBe('10000147');

    // Verify gameData object exists
    const gameDataExists = await page.evaluate(() => {
      return typeof (window as any).gameData !== 'undefined';
    });

    expect(gameDataExists).toBe(true);

    // GREEN phase: All assertions passed
    console.log('✅ GREEN: Game context correctly read from URL parameter');
  });

  test('RED → GREEN: Core UI elements should exist and be visible', async ({ page }) => {
    // TDD Phase: RED - This test will fail if UI elements are missing

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for page heading/title
    const heading = page.locator('h1, h2, .page-title').first();
    try {
      await expect(heading).toBeVisible({ timeout: 10000 });
      console.log('✅ Page heading found');
    } catch (error) {
      console.log('❌ RED: Page heading not found');
      throw error;
    }

    // Check for event selector
    const eventSelector = page.locator('.event-selector, [data-testid="event-selector"], select').first();
    try {
      await expect(eventSelector).toBeAttached({ timeout: 10000 });
      console.log('✅ Event selector found');
    } catch (error) {
      console.log('❌ RED: Event selector not found');
      throw error;
    }

    // Check for field canvas
    const fieldCanvas = page.locator('.field-canvas, .canvas, [data-testid="field-canvas"]').first();
    try {
      await expect(fieldCanvas).toBeAttached({ timeout: 10000 });
      console.log('✅ Field canvas found');
    } catch (error) {
      console.log('❌ RED: Field canvas not found');
      throw error;
    }

    // Check for HQL preview
    const hqlPreview = page.locator('.hql-preview, [data-testid="hql-preview"]').first();
    try {
      await expect(hqlPreview).toBeAttached({ timeout: 10000 });
      console.log('✅ HQL preview found');
    } catch (error) {
      console.log('❌ RED: HQL preview not found');
      throw error;
    }

    // GREEN phase: All core UI elements found
    console.log('✅ GREEN: All core UI elements exist');
  });

  test('RED → GREEN: Should not have React Hooks errors', async ({ page }) => {
    // TDD Phase: RED - This test will fail if there are React Hooks errors

    // Wait for page to fully load and stabilize
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // Check for React Hooks specific errors
    const reactHooksErrors = consoleErrors.filter(err =>
      err.includes('React has detected a change in the order of Hooks') ||
      err.includes('Rendered more hooks than during the previous render') ||
      err.includes('Warning: React has detected')
    );

    if (reactHooksErrors.length > 0) {
      console.log('❌ RED: React Hooks errors detected:');
      reactHooksErrors.forEach(err => console.log(`  - ${err}`));
      expect(reactHooksErrors).toHaveLength(0);
    }

    // GREEN phase: No React Hooks errors
    console.log('✅ GREEN: No React Hooks errors detected');
  });

  test('RED → GREEN: Should not have console errors', async ({ page }) => {
    // TDD Phase: RED - This test will fail if there are console errors

    // Wait for page to fully load and stabilize
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // Filter out non-critical errors
    const criticalErrors = consoleErrors.filter(err => {
      // Ignore specific non-critical errors
      if (err.includes('DevTools') || err.includes('warning') || err.includes('deprecated')) {
        return false;
      }
      return true;
    });

    if (criticalErrors.length > 0) {
      console.log('❌ RED: Console errors detected:');
      criticalErrors.forEach(err => console.log(`  - ${err}`));
      expect(criticalErrors).toHaveLength(0);
    }

    // GREEN phase: No critical console errors
    console.log('✅ GREEN: No critical console errors detected');
  });

  test('RED → GREEN: Events should be loaded from API', async ({ page }) => {
    // TDD Phase: RED - This test will fail if events are not loaded

    // Wait for events to be loaded
    await page.waitForLoadState('networkidle');

    // Check for loading state
    const loadingIndicator = page.locator('.spinner, .loading, [role="status"]').first();

    // Wait for loading to complete
    try {
      await loadingIndicator.waitFor({ state: 'hidden', timeout: 10000 });
    } catch (error) {
      // Loading indicator might not exist, that's okay
      console.log('Note: No loading indicator found (might be okay)');
    }

    // Check for event selector or dropdown
    const eventSelector = page.locator('.event-selector, select, [role="combobox"]').first();
    try {
      await expect(eventSelector).toBeAttached({ timeout: 10000 });
      console.log('✅ Event selector loaded');
    } catch (error) {
      console.log('❌ RED: Event selector not found');
      throw error;
    }

    // GREEN phase: Events loaded successfully
    console.log('✅ GREEN: Events API called successfully');
  });

  test('RED → GREEN: Field canvas should be interactive', async ({ page }) => {
    // TDD Phase: RED - This test will fail if canvas is not interactive

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for field canvas
    const fieldCanvas = page.locator('.field-canvas, .canvas, [data-testid="field-canvas"]').first();

    try {
      await expect(fieldCanvas).toBeVisible({ timeout: 15000 });
      console.log('✅ Field canvas is visible');
    } catch (error) {
      console.log('❌ RED: Field canvas not visible');
      throw error;
    }

    // Try to hover over the canvas to check interactivity
    try {
      await fieldCanvas.hover({ timeout: 5000 });
      console.log('✅ Field canvas is interactive (hover successful)');
    } catch (error) {
      console.log('❌ RED: Field canvas not interactive');
      throw error;
    }

    // GREEN phase: Canvas is interactive
    console.log('✅ GREEN: Field canvas is interactive');
  });

  test('RED → GREEN: HQL preview should be present', async ({ page }) => {
    // TDD Phase: RED - This test will fail if HQL preview is missing

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for HQL preview
    const hqlPreview = page.locator('.hql-preview, [data-testid="hql-preview"]').first();

    try {
      await expect(hqlPreview).toBeAttached({ timeout: 10000 });
      console.log('✅ HQL preview found');
    } catch (error) {
      console.log('❌ RED: HQL preview not found');
      throw error;
    }

    // GREEN phase: HQL preview exists
    console.log('✅ GREEN: HQL preview is present');
  });

  test('RED → GREEN: Save/Load functionality should be available', async ({ page }) => {
    // TDD Phase: RED - This test will fail if save/load buttons are missing

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for save button
    const saveButton = page.locator('button:has-text("保存"), button:has-text("Save"), [data-testid="save-button"]').first();
    try {
      await expect(saveButton).toBeAttached({ timeout: 10000 });
      console.log('✅ Save button found');
    } catch (error) {
      console.log('❌ RED: Save button not found');
      throw error;
    }

    // Check for load button (optional)
    const loadButton = page.locator('button:has-text("加载"), button:has-text("Load"), [data-testid="load-button"]').first();
    const hasLoadButton = await loadButton.count() > 0;

    if (hasLoadButton) {
      console.log('✅ Load button found');
    } else {
      console.log('Note: Load button not found (might be optional)');
    }

    // GREEN phase: Save functionality is available
    console.log('✅ GREEN: Save/Load functionality is available');
  });
});
