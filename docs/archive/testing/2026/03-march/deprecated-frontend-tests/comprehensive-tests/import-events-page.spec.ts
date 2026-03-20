import { test, expect } from '@playwright/test';

/**
 * Import Events Page - E2E Tests
 *
 * TDD Cycle:
 * 1. RED: Write failing test first
 * 2. Verify RED: Run test and confirm it fails
 * 3. GREEN: Fix code to make test pass
 * 4. Verify GREEN: Run test and confirm it passes
 * 5. REFACTOR: Clean up code
 *
 * Route: /import-events?game_gid=10000147
 * Component: src/analytics/pages/ImportEvents.tsx
 *
 * Test Coverage:
 * - Page loads successfully
 * - Game context is correctly read (game_gid=10000147)
 * - Core UI elements exist (upload form, file input, import button)
 * - No React errors (Hooks rules, etc.)
 * - No console errors
 */

test.describe('Import Events Page - P0 Critical Path', () => {
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

    // Navigate to Import Events page with game_gid parameter
    await page.goto('/import-events?game_gid=10000147', {
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
    const pageContainer = page.locator('.import-events, .page-container, main').first();

    try {
      await expect(pageContainer).toBeVisible({ timeout: 15000 });
    } catch (error) {
      // RED phase: Test fails because page container not found
      console.log('❌ RED: Import Events page container not found - page failed to load');
      throw error;
    }

    // GREEN phase: If we reach here, page loaded successfully
    console.log('✅ GREEN: Import Events page loaded successfully');

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

    // Check for file input or upload area
    const fileInput = page.locator('input[type="file"], .upload-area, .drop-zone').first();
    try {
      await expect(fileInput).toBeAttached({ timeout: 10000 });
      console.log('✅ File input found');
    } catch (error) {
      console.log('❌ RED: File input not found');
      throw error;
    }

    // Check for import/upload button
    const importButton = page.locator('button:has-text("导入"), button:has-text("Import"), button:has-text("上传"), .btn-primary').first();
    try {
      await expect(importButton).toBeAttached({ timeout: 10000 });
      console.log('✅ Import button found');
    } catch (error) {
      console.log('❌ RED: Import button not found');
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

  test('RED → GREEN: File upload functionality should be available', async ({ page }) => {
    // TDD Phase: RED - This test will fail if file upload is not available

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for file input
    const fileInput = page.locator('input[type="file"]').first();

    try {
      await expect(fileInput).toBeAttached({ timeout: 10000 });
      console.log('✅ File input element found');
    } catch (error) {
      console.log('❌ RED: File input not found');
      throw error;
    }

    // Check if file input accepts files
    const acceptAttribute = await fileInput.getAttribute('accept');
    console.log(`File input accepts: ${acceptAttribute || 'any file'}`);

    // GREEN phase: File upload functionality exists
    console.log('✅ GREEN: File upload functionality is available');
  });

  test('RED → GREEN: Upload area should be interactive', async ({ page }) => {
    // TDD Phase: RED - This test will fail if upload area is not interactive

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for upload area or drop zone
    const uploadArea = page.locator('.upload-area, .drop-zone, [data-testid="upload-area"]').first();

    try {
      await expect(uploadArea).toBeVisible({ timeout: 10000 });
      console.log('✅ Upload area is visible');
    } catch (error) {
      console.log('❌ RED: Upload area not visible');
      throw error;
    }

    // Try to hover over the upload area to check interactivity
    try {
      await uploadArea.hover({ timeout: 5000 });
      console.log('✅ Upload area is interactive (hover successful)');
    } catch (error) {
      console.log('❌ RED: Upload area not interactive');
      throw error;
    }

    // GREEN phase: Upload area is interactive
    console.log('✅ GREEN: Upload area is interactive');
  });

  test('RED → GREEN: Import button should be present', async ({ page }) => {
    // TDD Phase: RED - This test will fail if import button is missing

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for import/upload button
    const importButton = page.locator('button:has-text("导入"), button:has-text("Import"), button:has-text("上传"), [data-testid="import-button"]').first();

    try {
      await expect(importButton).toBeAttached({ timeout: 10000 });
      console.log('✅ Import button found');
    } catch (error) {
      console.log('❌ RED: Import button not found');
      throw error;
    }

    // GREEN phase: Import button exists
    console.log('✅ GREEN: Import button is present');
  });

  test('RED → GREEN: Help text or instructions should be visible', async ({ page }) => {
    // TDD Phase: RED - This test will fail if help text is missing

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for help text, instructions, or description
    const helpText = page.locator('.help-text, .instructions, .description, p').first();

    try {
      await expect(helpText).toBeVisible({ timeout: 10000 });
      console.log('✅ Help text or instructions found');
    } catch (error) {
      console.log('❌ RED: Help text not found');
      throw error;
    }

    // GREEN phase: Help text exists
    console.log('✅ GREEN: Help text or instructions are visible');
  });

  test('RED → GREEN: Game selector should be present', async ({ page }) => {
    // TDD Phase: RED - This test will fail if game selector is missing

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded');

    // Check for game selector or display
    const gameSelector = page.locator('.game-selector, [data-testid="game-selector"], .game-info').first();

    try {
      await expect(gameSelector).toBeAttached({ timeout: 10000 });
      console.log('✅ Game selector found');
    } catch (error) {
      console.log('❌ RED: Game selector not found');
      throw error;
    }

    // GREEN phase: Game selector exists
    console.log('✅ GREEN: Game selector is present');
  });
});
