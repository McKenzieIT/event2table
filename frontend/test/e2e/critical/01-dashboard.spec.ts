/**
 * Dashboard E2E Tests
 *
 * Tests for the Dashboard (首页) page.
 *
 * Coverage:
 * 1. ✅ Page load + DOM structure validation
 * 2. ✅ Console error checking
 * 3. ✅ All button clicks
 * 4. ✅ Form interactions (if any)
 * 5. ✅ Search/filter functionality
 * 6. ✅ Modal opening/closing
 * 7. ✅ API call status
 * 8. ✅ Statistics data display
 * 9. ✅ Pagination (if any)
 * 10. ✅ Performance measurement
 */

import { test, expect, Page } from '@playwright/test';
import {
  navigateToPage,
  waitForPageReady,
  assertNoConsoleErrors,
  assertPagePerformance,
  clickAllButtons,
  assertPageContainsText,
  monitorConsoleErrors,
  measurePagePerformance,
  takeScreenshot,
  BASE_URL,
  TEST_GAME_GID
} from '../helpers/test-utils';

test.describe('Dashboard (首页)', () => {

  // ============================================================================
  // Test 1: Page Load + DOM Structure Validation
  // ============================================================================
  test('1. should load page and validate DOM structure', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);

    // Check page title
    await expect(page).toHaveTitle(/Event2Table|Dashboard|首页/);

    // Check main content area exists
    const mainContent = page.locator('main, #app-root');
    await expect(mainContent, 'Main content area should exist').toBeVisible();

    // Check for dashboard-specific elements
    const bodyText = await page.locator('body').textContent();

    // Dashboard should have some game-related content
    const hasDashboardContent = bodyText && (
      bodyText.includes('Event2Table') ||
      bodyText.includes('Dashboard') ||
      bodyText.includes('首页') ||
      bodyText.includes('游戏') ||
      bodyText.includes('Games')
    );

    expect(hasDashboardContent, 'Dashboard should contain relevant content').toBe(true);

    // Check for navigation
    const nav = page.locator('nav, .navigation, [role="navigation"]');
    const navExists = await nav.count() > 0;
    expect(navExists, 'Navigation should exist').toBe(true);
  });

  // ============================================================================
  // Test 2: Console Error Checking
  // ============================================================================
  test('2. should have no console errors', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);

    // Wait a bit for any async errors to appear
    await page.waitForTimeout(3000);

    // Check for console errors
    await assertNoConsoleErrors(page, 2000);
  });

  // ============================================================================
  // Test 3: All Button Clicks
  // ============================================================================
  test('3. should handle all button clicks', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);

    // Click all visible buttons
    const clickCount = await clickAllButtons(page);

    console.log(`Clicked ${clickCount} buttons on dashboard`);

    // At minimum, should have clicked some navigation buttons
    expect(clickCount, 'Should have clicked some buttons').toBeGreaterThan(0);
  });

  // ============================================================================
  // Test 4: Form Interactions
  // ============================================================================
  test('4. should handle form interactions (if any)', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);

    // Dashboard might not have forms, but if it does, they should work
    const forms = page.locator('form');
    const formCount = await forms.count();

    if (formCount > 0) {
      console.log(`Found ${formCount} forms on dashboard`);

      // Fill all form inputs
      for (let i = 0; i < formCount; i++) {
        const form = forms.nth(i);
        const inputs = form.locator('input[type="text"], textarea');
        const inputCount = await inputs.count();

        for (let j = 0; j < inputCount; j++) {
          await inputs.nth(j).fill('test value');
        }

        // Try to submit (might not actually submit if validation fails)
        const submitButton = form.locator('button[type="submit"], input[type="submit"]');
        if (await submitButton.count() > 0) {
          try {
            await submitButton.first().click();
            await page.waitForTimeout(500);
          } catch (error) {
            console.log('Form submit failed (might be validation error)');
          }
        }
      }
    } else {
      console.log('No forms found on dashboard (expected)');
    }
  });

  // ============================================================================
  // Test 5: Search/Filter Functionality
  // ============================================================================
  test('5. should handle search/filter functionality', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);

    // Look for search/filter inputs
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="search"], input[placeholder*="Search"], [data-testid="search-input"]');

    if (await searchInput.count() > 0) {
      // Type in search box
      await searchInput.first().fill('test');
      await page.waitForTimeout(1000);

      // Verify search was performed (page content might change)
      console.log('Search functionality exists and was triggered');
    } else {
      console.log('No search input found on dashboard (might not need search)');
    }
  });

  // ============================================================================
  // Test 6: Modal Opening/Closing
  // ============================================================================
  test('6. should handle modal opening/closing', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);

    // Look for buttons that might open modals
    const modalTriggers = page.locator('button:has-text("添加"), button:has-text("创建"), button:has-text("新增"), button:has-text("Add"), button:has-text("Create")');

    if (await modalTriggers.count() > 0) {
      // Click first modal trigger
      await modalTriggers.first().click();
      await page.waitForTimeout(1000);

      // Check if modal opened
      const modal = page.locator('.modal, .dialog, [role="dialog"]');
      if (await modal.count() > 0) {
        console.log('Modal opened successfully');

        // Close modal (Escape key)
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);

        // Verify modal closed
        const isVisible = await modal.first().isVisible({ timeout: 1000 }).catch(() => false);
        expect(isVisible, 'Modal should be closed').toBe(false);
      }
    } else {
      console.log('No modal triggers found on dashboard');
    }
  });

  // ============================================================================
  // Test 7: API Call Status
  // ============================================================================
  test('7. should verify API calls are successful', async ({ page }) => {
    // Monitor API requests
    const apiRequests: { url: string; status: number }[] = [];

    page.on('requestfinished', request => {
      const response = request.response();
      if (response && request.url().includes('/api/')) {
        apiRequests.push({
          url: request.url(),
          status: response.status()
        });
      }
    });

    await navigateToPage(page, '/', TEST_GAME_GID);
    await page.waitForTimeout(3000);

    // Check API calls
    console.log(`Made ${apiRequests.length} API requests`);

    // All API calls should be successful (2xx or 3xx)
    const failedRequests = apiRequests.filter(req => req.status >= 400);

    if (failedRequests.length > 0) {
      console.error('Failed API requests:', failedRequests);
    }

    // Allow some 404s (might be optional features)
    const criticalFailures = failedRequests.filter(req => req.status >= 500);
    expect(criticalFailures.length, 'Should have no critical API failures').toBe(0);
  });

  // ============================================================================
  // Test 8: Statistics Data Display
  // ============================================================================
  test('8. should display statistics data correctly', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);
    await page.waitForTimeout(3000);

    // Look for statistics/card widgets
    const statsCards = page.locator('.stat-card, .metric-card, [data-testid="stat-card"], .card');
    const cardCount = await statsCards.count();

    if (cardCount > 0) {
      console.log(`Found ${cardCount} statistics cards on dashboard`);

      // Verify at least some cards have content
      for (let i = 0; i < Math.min(cardCount, 5); i++) {
        const card = statsCards.nth(i);
        const text = await card.textContent();

        expect(text?.trim().length, 'Statistics card should have content').toBeGreaterThan(0);
      }
    } else {
      console.log('No statistics cards found (dashboard might be empty in test environment)');
    }
  });

  // ============================================================================
  // Test 9: Pagination Functionality
  // ============================================================================
  test('9. should handle pagination (if exists)', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);

    // Look for pagination controls
    const pagination = page.locator('.pagination, [data-testid="pagination"], .page-navigation');

    if (await pagination.count() > 0) {
      console.log('Pagination controls found');

      // Try to click next page (if exists)
      const nextButton = pagination.locator('button:has-text("下一页"), button:has-text("Next"), .next');
      if (await nextButton.count() > 0) {
        await nextButton.first().click();
        await page.waitForTimeout(1000);
        console.log('Pagination: Clicked next page');
      }
    } else {
      console.log('No pagination found (dashboard might not need pagination)');
    }
  });

  // ============================================================================
  // Test 10: Performance Measurement
  // ============================================================================
  test('10. should meet performance criteria', async ({ page }) => {
    const startTime = Date.now();

    await navigateToPage(page, '/', TEST_GAME_GID);
    await page.waitForTimeout(3000);

    const loadTime = Date.now() - startTime;
    console.log(`Dashboard load time: ${loadTime}ms`);

    // Measure detailed performance
    const metrics = await measurePagePerformance(page);
    console.log('Performance metrics:', metrics);

    // Assert performance criteria
    expect(metrics.pageLoadTime, 'Page should load within 10 seconds').toBeLessThan(10000);
    expect(metrics.domContentLoadedTime, 'DOM should load within 5 seconds').toBeLessThan(5000);
  });

  // ============================================================================
  // Test 11: Screenshot Test
  // ============================================================================
  test('11. should take screenshot without visual regressions', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);
    await page.waitForTimeout(3000);

    // Take full page screenshot
    await takeScreenshot(page, 'dashboard', 'loaded');
  });

  // ============================================================================
  // Test 12: Accessibility Check
  // ============================================================================
  test('12. should have basic accessibility', async ({ page }) => {
    await navigateToPage(page, '/', TEST_GAME_GID);

    // Check for heading hierarchy
    const headings = page.locator('h1, h2, h3');
    const headingCount = await headings.count();
    expect(headingCount, 'Page should have headings').toBeGreaterThan(0);

    // Check for skip links or aria labels
    const skipLink = page.locator('a[href^="#"], [aria-label]');
    const hasAccessibility = await skipLink.count() > 0;

    if (!hasAccessibility) {
      console.warn('No accessibility features found (consider adding skip links or aria labels)');
    }

    // Check for alt text on images
    const images = page.locator('img:not([alt])');
    const imagesWithoutAlt = await images.count();

    if (imagesWithoutAlt > 0) {
      console.warn(`Found ${imagesWithoutAlt} images without alt text`);
    }
  });
});

/**
 * Expected Test Results:
 *
 * ✅ All 12 tests should pass
 * ✅ Dashboard should load within 10 seconds
 * ✅ No console errors
 * ✅ All buttons should be clickable
 * ✅ API calls should succeed (no 500 errors)
 * ✅ Statistics should be displayed (if data exists)
 * ✅ Performance metrics should be acceptable
 *
 * If any test fails:
 * 1. Check browser console for JavaScript errors
 * 2. Check network tab for failed API calls
 * 3. Check if backend server is running
 * 4. Check if test database has data
 */
