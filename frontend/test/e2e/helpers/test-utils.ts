/**
 * Public E2E Test Utilities
 *
 * Common helper functions used across all E2E tests.
 * Includes page navigation, console monitoring, performance measurement, etc.
 */

import { Page, expect } from '@playwright/test';

// ============================================================================
// Constants
// ============================================================================

export const BASE_URL = 'http://localhost:5173';
export const TEST_GAME_GID = 10000147; // STAR001 - Production test game
export const TEST_GID_START = 90000000; // Test GID range start
export const PAGE_TIMEOUT = 60000; // 60 seconds
export const NAVIGATION_TIMEOUT = 10000; // 10 seconds

// ============================================================================
// Page Navigation Utilities
// ============================================================================

/**
 * Navigate to a page with proper game context
 */
export async function navigateToPage(
  page: Page,
  path: string,
  gameGid: number = TEST_GAME_GID
): Promise<void> {
  const url = `${BASE_URL}/#${path}?game_gid=${gameGid}`;
  await page.goto(url, { timeout: PAGE_TIMEOUT, waitUntil: 'domcontentloaded' });
  await waitForPageReady(page);
}

/**
 * Wait for page to be ready (React mounted, initial data loaded)
 */
export async function waitForPageReady(page: Page, timeout: number = 3000): Promise<void> {
  try {
    // Wait for DOM content loaded
    await page.waitForLoadState('domcontentloaded', { timeout });

    // Additional wait for React to mount and render
    await page.waitForTimeout(Math.min(timeout, 2000));
  } catch (error) {
    console.warn(`waitForPageReady timeout: ${error}`);
    // Continue anyway - page might still be usable
  }
}

/**
 * Wait for React app to mount (verify #app-root has children)
 */
export async function waitForReactMount(page: Page, timeout: number = 5000): Promise<boolean> {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const hasChildren = await page.evaluate(() => {
      const root = document.getElementById('app-root');
      return root && root.children.length > 0;
    });

    if (hasChildren) {
      return true;
    }

    await page.waitForTimeout(100);
  }

  return false;
}

// ============================================================================
// Console Error Monitoring
// ============================================================================

/**
 * Console error collector
 */
export interface ConsoleError {
  type: string;
  text: string;
  location?: string;
}

/**
 * Set up console error monitoring
 * Returns a function that returns all collected errors
 */
export function monitorConsoleErrors(page: Page): () => ConsoleError[] {
  const errors: ConsoleError[] = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();

      // Filter out non-critical errors
      const isIgnored = [
        'DevTools',
        'chrome-extension',
        'Extension',
        'favicon',
        'React DevTools',
        'analytics'
      ].some(ignored => text.includes(ignored));

      if (!isIgnored) {
        errors.push({
          type: msg.type(),
          text,
          location: msg.location()?.url
        });
      }
    }
  });

  // Return function to get collected errors
  return () => errors;
}

/**
 * Check for console errors (with timeout)
 */
export async function checkConsoleErrors(
  page: Page,
  duration: number = 2000
): Promise<ConsoleError[]> {
  const getErrors = monitorConsoleErrors(page);

  try {
    await Promise.race([
      page.waitForTimeout(duration),
      page.waitForLoadState('networkidle', { timeout: duration * 2 }).catch(() => {})
    ]);
  } catch (e) {
    // Timeout is not critical
  }

  return getErrors();
}

/**
 * Assert no console errors
 */
export async function assertNoConsoleErrors(
  page: Page,
  duration: number = 2000
): Promise<void> {
  const errors = await checkConsoleErrors(page, duration);

  if (errors.length > 0) {
    console.error('Console errors detected:', errors);
    throw new Error(
      `Expected no console errors, but found ${errors.length}:\n` +
      errors.map(e => `  - ${e.text}`).join('\n')
    );
  }
}

// ============================================================================
// Performance Monitoring
// ============================================================================

/**
 * Page performance metrics
 */
export interface PerformanceMetrics {
  pageLoadTime: number;
  domContentLoadedTime: number;
  firstPaint: number;
  firstContentfulPaint: number;
  resourceCount: number;
}

/**
 * Measure page performance
 */
export async function measurePagePerformance(page: Page): Promise<PerformanceMetrics> {
  const metrics = await page.evaluate(() => {
    const timing = performance.timing;
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

    return {
      pageLoadTime: timing.loadEventEnd - timing.navigationStart,
      domContentLoadedTime: timing.domContentLoadedEventEnd - timing.navigationStart,
      firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
      firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
      resourceCount: performance.getEntriesByType('resource').length
    };
  });

  return metrics;
}

/**
 * Assert page performance meets criteria
 */
export async function assertPagePerformance(
  page: Page,
  maxLoadTime: number = 5000 // 5 seconds
): Promise<void> {
  const metrics = await measurePagePerformance(page);

  console.log('Page performance metrics:', metrics);

  expect(metrics.pageLoadTime).toBeLessThan(maxLoadTime);
  expect(metrics.domContentLoadedTime).toBeLessThan(maxLoadTime);
}

// ============================================================================
// Network Monitoring
// ============================================================================

/**
 * API request details
 */
export interface ApiRequest {
  url: string;
  method: string;
  status: number;
  timing: number;
}

/**
 * Monitor API requests
 */
export function monitorApiRequests(page: Page): {
  getRequests: () => ApiRequest[];
  clear: () => void;
} {
  const requests: ApiRequest[] = [];

  page.on('requestfinished', request => {
    const response = request.response();
    if (response) {
      requests.push({
        url: request.url(),
        method: request.method(),
        status: response.status(),
        timing: request.timing().responseEnd
      });
    }
  });

  return {
    getRequests: () => [...requests],
    clear: () => requests.length = 0
  };
}

/**
 * Wait for API request to complete
 */
export async function waitForApiRequest(
  page: Page,
  urlPattern: RegExp,
  timeout: number = 10000
): Promise<ApiRequest | null> {
  const { getRequests } = monitorApiRequests(page);

  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const requests = getRequests();
    const matchingRequest = requests.find(req => urlPattern.test(req.url));

    if (matchingRequest) {
      return matchingRequest;
    }

    await page.waitForTimeout(100);
  }

  return null;
}

// ============================================================================
// Test Data Generation
// ============================================================================

/**
 * Generate a unique test GID
 */
export function generateTestGid(): number {
  return TEST_GID_START + Math.floor(Math.random() * 9999);
}

/**
 * Generate a unique test game name
 */
export function generateTestGameName(): string {
  return `E2E Test Game ${Date.now()}`;
}

/**
 * Generate a unique test event name
 */
export function generateTestEventName(): string {
  return `e2e_test_event_${Date.now()}`;
}

// ============================================================================
// Element Interaction Helpers
// ============================================================================

/**
 * Click all visible buttons on page (for testing)
 */
export async function clickAllButtons(page: Page): Promise<number> {
  const buttons = page.locator('button:visible');
  const count = await buttons.count();

  let clickCount = 0;

  for (let i = 0; i < count; i++) {
    try {
      const button = buttons.nth(i);
      await button.scrollIntoViewIfNeeded();
      await button.click({ timeout: 5000 });
      clickCount++;

      // Wait a bit for any modal/panel to open
      await page.waitForTimeout(500);

      // Close any modals/panels that might have opened
      await page.keyboard.press('Escape');
      await page.waitForTimeout(200);
    } catch (error) {
      console.warn(`Failed to click button ${i}:`, error);
    }
  }

  return clickCount;
}

/**
 * Fill all visible inputs on page (for testing)
 */
export async function fillAllInputs(page: Page, value: string = 'test'): Promise<number> {
  const inputs = page.locator('input:visible, textarea:visible');
  const count = await inputs.count();

  let fillCount = 0;

  for (let i = 0; i < count; i++) {
    try {
      const input = inputs.nth(i);
      const inputType = await input.getAttribute('type');

      // Skip password, file, and submit inputs
      if (['password', 'file', 'submit', 'button'].includes(inputType || '')) {
        continue;
      }

      await input.scrollIntoViewIfNeeded();
      await input.fill(value);
      fillCount++;
    } catch (error) {
      console.warn(`Failed to fill input ${i}:`, error);
    }
  }

  return fillCount;
}

// ============================================================================
// Modal/Dialog Helpers
// ============================================================================

/**
 * Handle dialog/confirm box
 */
export async function acceptDialog(page: Page): Promise<void> {
  await page.evaluate(() => {
    window.confirm = () => true;
  });
}

/**
 * Handle dialog/confirm box (dismiss)
 */
export async function dismissDialog(page: Page): Promise<void> {
  await page.evaluate(() => {
    window.confirm = () => false;
  });
}

// ============================================================================
// Screenshot Helpers
// ============================================================================

/**
 * Take screenshot with automatic naming
 */
export async function takeScreenshot(
  page: Page,
  testName: string,
  action: string
): Promise<void> {
  const filename = `${testName}-${action}-${Date.now()}.png`;
  await page.screenshot({
    path: `frontend/test/e2e/screenshots/${filename}`,
    fullPage: true
  });
}

// ============================================================================
// Assertion Helpers
// ============================================================================

/**
 * Assert page contains text (with timeout)
 */
export async function assertPageContainsText(
  page: Page,
  text: string | RegExp,
  timeout: number = 5000
): Promise<void> {
  await expect(page.locator('body'), `Page should contain "${text}"`)
    .toHaveText(text, { timeout });
}

/**
 * Assert page does NOT contain text (with timeout)
 */
export async function assertPageNotContainsText(
  page: Page,
  text: string | RegExp,
  timeout: number = 5000
): Promise<void> {
  await expect(page.locator('body'), `Page should NOT contain "${text}"`)
    .not.toHaveText(text, { timeout });
}

/**
 * Assert element is visible
 */
export async function assertElementVisible(
  page: Page,
  selector: string,
  timeout: number = 5000
): Promise<void> {
  await expect(page.locator(selector), `Element "${selector}" should be visible`)
    .toBeVisible({ timeout });
}

/**
 * Assert element is NOT visible
 */
export async function assertElementNotVisible(
  page: Page,
  selector: string,
  timeout: number = 5000
): Promise<void> {
  await expect(page.locator(selector), `Element "${selector}" should NOT be visible`)
    .not.toBeVisible({ timeout });
}

// ============================================================================
// Test Cleanup Helpers
// ============================================================================

/**
 * Clean up test data (delete test games, events, etc.)
 */
export async function cleanupTestData(
  page: Page,
  testGids: number[]
): Promise<void> {
  for (const gid of testGids) {
    try {
      const response = await page.request.delete(`/api/games/${gid}`);
      if (response.ok()) {
        console.log(`Cleaned up test game ${gid}`);
      }
    } catch (error) {
      console.warn(`Failed to clean up test game ${gid}:`, error);
    }
  }
}
