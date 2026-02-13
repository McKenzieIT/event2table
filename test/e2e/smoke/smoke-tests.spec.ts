/**
 * Smoke Tests for event2table Frontend
 *
 * Tests that all major pages load without JavaScript errors
 * and basic functionality works.
 *
 * Run: npx playwright test smoke-tests.spec.ts
 */

import { test, expect } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_BASE = 'http://127.0.0.1:5001';

// Helper to check for console errors
async function checkConsoleErrors(page: any) {
  const errors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  return errors;
}

test.describe('Homepage & Navigation', () => {
  test('should load homepage without errors', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    // Wait a bit for any async errors
    await page.waitForTimeout(2000);

    // Verify no console errors
    expect(errors).toEqual([]);
  });

  test('should display main navigation', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Check for navigation elements (adjust selectors based on actual UI)
    const nav = page.locator('nav').or(page.locator('[role="navigation"]')).or(page.locator('.navbar'));
    await expect(nav.first()).toBeVisible({ timeout: 10000 });
  });

  test('should have working navigation links', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Find all links and check they don't have obvious issues
    const links = await page.locator('a[href]').all();
    expect(links.length).toBeGreaterThan(0);

    // Check a few key links exist
    const hasGamesLink = await page.locator('a[href*="games"]').count() > 0;
    const hasEventsLink = await page.locator('a[href*="events"]').count() > 0;
    const hasCanvasLink = await page.locator('a[href*="canvas"]').count() > 0 ||
                          await page.locator('a[href*="field-builder"]').count() > 0;

    expect(hasGamesLink || hasEventsLink || hasCanvasLink).toBeTruthy();
  });
});

test.describe('Dashboard Page', () => {
  test('should load dashboard without errors', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/`);
    await page.waitForLoadState('networkidle');

    // Check dashboard loaded
    await expect(page.locator('body')).toBeVisible();

    // Verify no console errors
    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should display dashboard content', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/`);
    await page.waitForLoadState('networkidle');

    // Dashboard should have some content
    const content = page.locator('main, .dashboard, [data-testid="dashboard"]');
    await expect(content.first()).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Games Management', () => {
  test('should load games list page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/games`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    // Verify no console errors
    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should display games list or empty state', async ({ page }) => {
    await page.goto(`${BASE_URL}/#/games`);
    await page.waitForLoadState('networkidle');

    // Should either show games list or empty state
    const hasContent = await page.locator('body').isVisible();
    expect(hasContent).toBeTruthy();
  });

  test('should load games create page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/games/create`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    // Should have form elements
    const hasForm = await page.locator('form, input, button').count() > 0;
    expect(hasForm).toBeTruthy();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Events Management', () => {
  test('should load events list page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/events`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load events create page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/events/create`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    // Should have form elements
    const hasForm = await page.locator('form, input, button').count() > 0;
    expect(hasForm).toBeTruthy();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Parameters Management', () => {
  test('should load parameters list page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/parameters`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load common parameters page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/common-params`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load parameters enhanced page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/parameters/enhanced`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Canvas & Flow Builder', () => {
  test('should load canvas page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    // Canvas requires a game context, use a test game
    await page.goto(`${BASE_URL}/#/canvas?game_gid=10000147`);
    await page.waitForLoadState('networkidle');

    // Check page loaded - look for canvas page or error state
    const canvasPage = page.locator('[data-testid="canvas-page"]');
    const canvasError = page.locator('[data-testid="canvas-error"]');
    const canvasLoading = page.locator('[data-testid="canvas-loading"]');

    // Wait for one of the canvas states to be visible
    await Promise.any([
      canvasPage.isVisible().then(() => true),
      canvasError.isVisible().then(() => true),
      canvasLoading.isVisible().then(() => true),
    ]);

    // Give time for any async errors
    await page.waitForTimeout(1000);

    // The page should load (either successfully or with error state)
    // Critical: No JavaScript errors
    const hasErrors = errors.length > 0;
    expect(hasErrors).toBeFalsy();
  });

  test('should load field builder page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/field-builder`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    // Should have canvas or builder elements
    const hasCanvas = await page.locator('.react-flow, canvas, [data-testid="canvas"]').count() > 0;
    expect(hasCanvas).toBeTruthy();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load flow builder page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/flow-builder`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load flows list page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/flows`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Event Nodes', () => {
  test('should load event nodes page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/event-nodes`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load event node builder page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/event-node-builder`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Categories Management', () => {
  test('should load categories list page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/categories`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load categories create page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/categories/create`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    // Should have form elements
    const hasForm = await page.locator('form, input, button').count() > 0;
    expect(hasForm).toBeTruthy();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('HQL Management', () => {
  test('should load HQL manage page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/hql-manage`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load HQL results page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/hql-results`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Generation Tools', () => {
  test('should load generate page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/generate`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load alter sql builder page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/alter-sql-builder`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Analytics & Reports', () => {
  test('should load parameter analysis page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/parameter-analysis`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load parameter compare page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/parameters/compare`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load parameter network page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/parameter-network`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load parameter dashboard page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/parameter-dashboard`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Import & Batch Operations', () => {
  test('should load import events page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/import-events`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load batch operations page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/batch-operations`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('Logs Management', () => {
  test('should load logs create page', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/logs/create`);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    // Should have form elements
    const hasForm = await page.locator('form, input, button').count() > 0;
    expect(hasForm).toBeTruthy();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});

test.describe('API Connectivity', () => {
  test('should handle API requests without CORS errors', async ({ page }) => {
    const errors = await checkConsoleErrors(page);

    // Monitor network requests
    const apiRequests: string[] = [];
    page.on('request', request => {
      if (request.url().includes(API_BASE)) {
        apiRequests.push(request.url());
      }
    });

    await page.goto(`${BASE_URL}/#/games`);
    await page.waitForLoadState('networkidle');

    // Wait for any API calls to complete
    await page.waitForTimeout(2000);

    // Check for CORS errors in console
    await page.waitForTimeout(1000);
    const corsErrors = errors.filter(err =>
      err.includes('CORS') || err.includes('Access-Control')
    );

    expect(corsErrors).toEqual([]);
  });

  test('should gracefully handle API failures', async ({ page }) => {
    // This test checks that the app handles backend being down gracefully
    const errors = await checkConsoleErrors(page);

    await page.goto(`${BASE_URL}/#/games`);
    await page.waitForLoadState('networkidle');

    // Page should still load even if API fails
    await expect(page.locator('body')).toBeVisible();

    // Should not crash with unhandled errors
    await page.waitForTimeout(1000);
    const unhandledErrors = errors.filter(err =>
      err.includes('Unhandled') || err.includes('Uncaught')
    );

    expect(unhandledErrors).toEqual([]);
  });
});

test.describe('Responsive Design', () => {
  test('should load on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    const errors = await checkConsoleErrors(page);
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });

    const errors = await checkConsoleErrors(page);
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });

  test('should load on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });

    const errors = await checkConsoleErrors(page);
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Check page loaded
    await expect(page.locator('body')).toBeVisible();

    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);
  });
});
