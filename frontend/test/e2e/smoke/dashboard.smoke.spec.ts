import { test, expect, Page } from '@playwright/test';

/**
 * Dashboard Smoke Tests
 * Phase 3: Automated E2E Testing
 *
 * Tests basic dashboard functionality to ensure
 * the application loads and displays correctly.
 */

interface TestConfig {
  readonly BASE_URL: string;
}

const CONFIG: TestConfig = {
  BASE_URL: 'http://localhost:5173'
};

test.describe('Dashboard Smoke Tests', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    // Navigate to dashboard before each test
    await page.goto('/');
  });

  test('Dashboard loads and displays statistics', async ({ page }: { page: Page }) => {
    // Wait for page to load
    await expect(page.locator('.dashboard-container')).toBeVisible({ timeout: 5000 });

    // Verify statistics cards are displayed
    await expect(page.locator('.stat-card')).toHaveCount({ min: 3 });

    // Verify dashboard title
    await expect(page.locator('h1, h2').filter({ hasText: /dashboard|控制台/i })).toBeVisible();
  });

  test('Dashboard games management button works', async ({ page }: { page: Page }) => {
    // Click games management button
    await page.click('text=游戏管理');

    // Verify games modal opens
    await expect(page.locator('.modal, .dialog, [role="dialog"]')).toBeVisible({ timeout: 3000 });

    // Verify games are displayed in modal
    await expect(page.locator('.game-item, .game-card, [data-testid*="game"]')).toBeVisible();

    // Close modal
    await page.click('button:has-text("关闭"), .close-button, [aria-label="close"]');

    // Verify modal is closed
    await expect(page.locator('.modal, .dialog')).not.toBeVisible();
  });

  test('Dashboard navigation links work', async ({ page }: { page: Page }) => {
    // Test navigation to Events page
    await page.click('a[href*="/events"], text=日志事件');

    // Verify navigation
    await expect(page).toHaveURL(/\/events/);

    // Navigate back to dashboard
    await page.goto('/');

    // Test navigation to Games page
    await page.click('a[href*="/games"], text=游戏管理');

    // Verify navigation
    await expect(page).toHaveURL(/\/games/);
  });

  test('Dashboard has no console errors', async ({ page }: { page: Page }) => {
    // Collect console errors during page load
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

    // Verify no critical errors
    // Filter out non-critical errors (e.g., from third-party scripts)
    const criticalErrors = errors.filter(err =>
      !err.text.includes('DevTools') &&
      !err.text.includes('chrome-extension') &&
      !err.text.includes('Extension')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('Dashboard loads within performance budget', async ({ page }: { page: Page }) => {
    // Measure page load time
    const startTime = Date.now();

    await page.goto('/');
    await expect(page.locator('.dashboard-container')).toBeVisible();

    const loadTime = Date.now() - startTime;

    // Verify page loads within 5 seconds
    expect(loadTime).toBeLessThan(5000);

    // Log performance metric
    console.log(`Dashboard load time: ${loadTime}ms`);
  });

  test('Dashboard displays correct game count', async ({ page }: { page: Page }) => {
    // Get displayed game count from dashboard
    const gameCountElement = page.locator('[data-testid="game-count"], .stat-value').filter({ hasText: /\d+/ });

    await expect(gameCountElement).toBeVisible();

    // Extract number from text
    const gameCountText = await gameCountElement.textContent();
    const gameCount = parseInt(gameCountText?.match(/\d+/)?.[0] || '0', 10);

    // Verify there are games displayed
    expect(gameCount).toBeGreaterThan(0);

    console.log(`Dashboard displays ${gameCount} games`);
  });
});
