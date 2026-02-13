/**
 * Game Context Helper Functions for E2E Tests
 *
 * Provides utilities for setting and managing game context in tests
 */

/**
 * Navigate to a page and set game context
 *
 * @param page - Playwright Page object
 * @param path - Path to navigate to (e.g., "/events")
 * @param gameGid - Game GID to set as context
 * @returns Promise that resolves when navigation and context setting complete
 */
export async function navigateAndSetGameContext(
  page: any,
  path: string,
  gameGid: string
): Promise<void> {
  // Set game context in localStorage before navigation
  await page.goto('/#/');
  await page.evaluate((gid: string) => {
    localStorage.setItem('selectedGameGid', gid);
  }, gameGid);

  // Navigate to target page
  await page.goto(`/#${path}`);

  // Wait for page to load
  await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
}

/**
 * Set game context without navigation
 *
 * @param page - Playwright Page object
 * @param gameGid - Game GID to set as context
 * @param gameData - Optional game data object
 * @returns Promise that resolves when context is set
 */
export async function setGameContext(
  page: any,
  gameGid: string,
  gameData?: any
): Promise<void> {
  await page.evaluate(
    ({ gid, data }) => {
      localStorage.setItem('selectedGameGid', gid);
      if (data) {
        (window as any).gameData = data;
      }
    },
    { gid: gameGid, data: gameData }
  );
}

/**
 * Clear game context
 *
 * @param page - Playwright Page object
 * @returns Promise that resolves when context is cleared
 */
export async function clearGameContext(page: any): Promise<void> {
  await page.evaluate(() => {
    localStorage.removeItem('selectedGameGid');
    if ((window as any).gameData) {
      delete (window as any).gameData;
    }
  });
}
