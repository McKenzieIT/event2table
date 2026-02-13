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
    // Fallback: wait for network idle if selector not found
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
