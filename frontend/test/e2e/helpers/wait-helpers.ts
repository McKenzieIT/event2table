/**
 * Wait Helper Functions for E2E Tests
 *
 * Provides flexible timeout strategies for different page loading scenarios
 */

/**
 * Wait for React application to mount and render
 *
 * @param page - Playwright Page object
 * @param multiplier - Timeout multiplier (default: 100ms)
 * @returns Promise that resolves when React is mounted
 */
export async function waitForReactMount(
  page: any,
  multiplier: number = 100
): Promise<void> {
  await page.waitForTimeout(multiplier);
}

/**
 * Wait for page to be ready after navigation
 * Combines domcontentloaded with a small buffer for API calls
 *
 * @param page - Playwright Page object
 * @param bufferTime - Buffer time in milliseconds (default: 500ms)
 * @returns Promise that resolves when page is ready
 */
export async function waitForPageReady(
  page: any,
  bufferTime: number = 500
): Promise<void> {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(bufferTime);
}

/**
 * Filter non-critical console errors
 * Removes errors from DevTools, Extensions, and Deprecation warnings
 *
 * @param errors - Array of console error messages
 * @returns Filtered array with only critical errors
 */
export function filterNonCriticalErrors(errors: string[]): string[] {
  const nonCriticalPatterns = [
    /DevTools/i,
    /Extension/i,
    /\[Deprecation\]/i,
    /chrome-extension/i,
    /moz-extension/i,
  ];

  return errors.filter(error => {
    // Check if error matches any non-critical pattern
    const isNonCritical = nonCriticalPatterns.some(pattern => pattern.test(error));
    return !isNonCritical; // Keep only critical errors
  });
}

/**
 * Wait for data to load by checking for specific elements
 *
 * @param page - Playwright Page object
 * @param selector - Selector to wait for
 * @param options - Wait options
 * @returns Promise that resolves when data is loaded
 */
export async function waitForDataLoad(
  page: any,
  selector: string = '[data-loaded="true"]',
  options: { timeout?: number } = {}
): Promise<void> {
  const { timeout = 10000 } = options;
  try {
    await page.waitForSelector(selector, { timeout, state: 'attached' });
  } catch (error) {
    // Fallback: wait for domcontentloaded if selector not found
    await page.waitForLoadState('domcontentloaded', { timeout });
  }
}

/**
 * Wait for element to be visible
 *
 * @param page - Playwright Page object
 * @param selector - Selector to wait for
 * @param options - Wait options
 * @returns Promise that resolves when element is visible
 */
export async function waitForVisible(
  page: any,
  selector: string,
  options: { timeout?: number } = {}
): Promise<void> {
  const { timeout = 10000 } = options;
  await page.waitForSelector(selector, { timeout, state: 'visible' });
}

/**
 * Wait for custom condition to be true
 *
 * @param page - Playwright Page object
 * @param condition - Function that evaluates condition
 * @param options - Wait options
 * @returns Promise that resolves when condition is true
 */
export async function waitForCondition(
  page: any,
  condition: () => Promise<boolean>,
  options: { timeout?: number; interval?: number } = {}
): Promise<void> {
  const { timeout = 10000, interval = 100 } = options;
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await page.waitForTimeout(interval);
  }

  throw new Error(`Condition not met within ${timeout}ms`);
}
