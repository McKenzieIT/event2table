/**
 * Test Helpers for Event2Table E2E Tests
 *
 * Provides utility functions for:
 * - Test data creation (games, events, parameters)
 * - Page navigation and setup
 * - Assertions and validations
 * - Test isolation and cleanup
 *
 * @module test-helpers
 */

/**
 * ParameterTestHelpers - Helper functions for parameter management tests
 */
export class ParameterTestHelpers {
  /**
   * Create a test game via API
   * @param {Page} page - Playwright page object
   * @param {string} name - Game name
   * @param {number} gid - Game GID (use 90000000+ for tests)
   * @returns {Promise<Object>} Created game data
   */
  static async createTestGame(page, name, gid) {
    return page.evaluate(async ({ name, gid }) => {
      const response = await fetch('http://127.0.0.1:5001/api/games', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gid: String(gid),
          name,
          ods_db: 'ieu_ods'
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create game: ${response.statusText}`);
      }

      return response.json();
    }, { name, gid: 90000000 + gid });
  }

  /**
   * Create a test event via API
   * @param {Page} page - Playwright page object
   * @param {number} gameGid - Game GID
   * @param {string} eventName - Event name
   * @returns {Promise<Object>} Created event data
   */
  static async createTestEvent(page, gameGid, eventName) {
    return page.evaluate(async ({ gameGid, eventName }) => {
      const response = await fetch('http://127.0.0.1:5001/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          game_gid: gameGid,
          name: eventName,
          ods_table: `ods_${eventName}`
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create event: ${response.statusText}`);
      }

      return response.json();
    }, { gameGid, eventName });
  }

  /**
   * Create a test parameter via GraphQL mutation
   * @param {Page} page - Playwright page object
   * @param {number} eventId - Event ID
   * @param {string} paramName - Parameter name
   * @param {string} paramType - Parameter type (base/param/custom)
   * @returns {Promise<Object>} Mutation result
   */
  static async createTestParameter(page, eventId, paramName, paramType = 'param') {
    return page.evaluate(async ({ eventId, paramName, paramType }) => {
      const query = `
        mutation CreateParameter($eventId: Int!, $paramName: String!, $paramType: String!) {
          createParameter(eventId: $eventId, paramName: $paramName, paramType: $paramType) {
            ok
            parameter {
              id
              paramName
              paramType
            }
            errors
          }
        }
      `;

      const response = await fetch('http://127.0.0.1:5001/api/graphql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          variables: { eventId, paramName, paramType }
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create parameter: ${response.statusText}`);
      }

      const result = await response.json();
      return result.data.createParameter;
    }, { eventId, paramName, paramType });
  }

  /**
   * Delete test data by game GID
   * @param {Page} page - Playwright page object
   * @param {number} gameGid - Game GID to delete
   * @returns {Promise<boolean>} Success status
   */
  static async deleteTestData(page, gameGid) {
    return page.evaluate(async ({ gameGid }) => {
      try {
        const response = await fetch(`http://127.0.0.1:5001/api/games/${gameGid}`, {
          method: 'DELETE'
        });
        return response.ok;
      } catch (error) {
        console.error('Failed to delete test data:', error);
        return false;
      }
    }, { gameGid });
  }
}

/**
 * NavigationTestHelpers - Helper functions for navigation tests
 */
export class NavigationTestHelpers {
  /**
   * Navigate to a page with game context
   * @param {Page} page - Playwright page object
   * @param {string} path - Route path (e.g., '/parameters', '/event-node-builder')
   * @param {number} gameGid - Game GID
   */
  static async navigateWithGame(page, path, gameGid) {
    const url = `http://localhost:5173/#${path}?game_gid=${gameGid}`;
    await page.goto(url);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Allow React to settle
  }

  /**
   * Wait for page to stabilize (no network activity for 500ms)
   * @param {Page} page - Playwright page object
   */
  static async waitForStabilization(page) {
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  }

  /**
   * Take screenshot on test failure
   * @param {Page} page - Playwright page object
   * @param {string} testName - Test name for filename
   */
  static async screenshotOnFailure(page, testName) {
    const filename = `test-failure-${testName}-${Date.now()}.png`;
    await page.screenshot({
      path: `test/e2e/output/screenshots/${filename}`,
      fullPage: true
    });
  }
}

/**
 * AssertionTestHelpers - Helper functions for custom assertions
 */
export class AssertionTestHelpers {
  /**
   * Assert no console errors (except whitelisted ones)
   * @param {Page} page - Playwright page object
   * @param {Array<string>} whitelist - Whitelisted error patterns
   * @returns {Promise<Array<string>>} Array of critical errors
   */
  static async assertNoConsoleErrors(page, whitelist = ['DevTools', 'chrome-extension', 'Extension']) {
    const errors = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Wait a bit to collect errors
    await page.waitForTimeout(2000);

    const criticalErrors = errors.filter(err =>
      !whitelist.some(pattern => err.includes(pattern))
    );

    return criticalErrors;
  }

  /**
   * Assert element is visible and has text
   * @param {Page} page - Playwright page object
   * @param {string} selector - Element selector
   * @param {string} text - Expected text content
   */
  static async assertElementWithText(page, selector, text) {
    const element = page.locator(selector);
    await expect(element).toBeVisible();
    await expect(element).toContainText(text);
  }

  /**
   * Assert modal is open
   * @param {Page} page - Playwright page object
   */
  static async assertModalOpen(page) {
    const modal = page.locator('.modal-content, [role="dialog"]');
    await expect(modal.first()).toBeVisible();
  }

  /**
   * Assert modal is closed
   * @param {Page} page - Playwright page object
   */
  static async assertModalClosed(page) {
    const modal = page.locator('.modal-content, [role="dialog"]');
    const isVisible = await modal.first().isVisible().catch(() => false);
    expect(isVisible).toBeFalsy();
  }

  /**
   * Assert toast notification appears
   * @param {Page} page - Playwright page object
   * @param {string} message - Expected toast message
   */
  static async assertToastNotification(page, message) {
    const toast = page.locator(`text=${message}`).or(
      page.locator('[data-testid="toast"]')
    );
    await expect(toast.first()).toBeVisible();
  }
}

/**
 * PerformanceTestHelpers - Helper functions for performance tests
 */
export class PerformanceTestHelpers {
  /**
   * Measure page load time
   * @param {Page} page - Playwright page object
   * @param {string} url - URL to navigate to
   * @returns {Promise<number>} Load time in milliseconds
   */
  static async measureLoadTime(page, url) {
    const startTime = Date.now();
    await page.goto(url);
    await page.waitForLoadState('networkidle');
    return Date.now() - startTime;
  }

  /**
   * Measure action response time
   * @param {Page} page - Playwright page object
   * @param {Function} action - Action to perform
   * @returns {Promise<number>} Response time in milliseconds
   */
  static async measureActionTime(page, action) {
    const startTime = Date.now();
    await action();
    await page.waitForTimeout(500); // Allow UI to update
    return Date.now() - startTime;
  }

  /**
   * Assert action completes within time limit
   * @param {number} actualTime - Actual time taken
   * @param {number} maxTime - Maximum allowed time
   * @param {string} actionName - Action name for error message
   */
  static async assertPerformance(actualTime, maxTime, actionName) {
    expect(actualTime).toBeLessThan(maxTime);
  }
}

/**
 * GraphQLTestHelpers - Helper functions for GraphQL tests
 */
export class GraphQLTestHelpers {
  /**
   * Execute GraphQL query
   * @param {Page} page - Playwright page object
   * @param {string} query - GraphQL query
   * @param {Object} variables - Query variables
   * @returns {Promise<Object>} Query result
   */
  static async executeQuery(page, query, variables = {}) {
    return page.evaluate(async ({ query, variables }) => {
      const response = await fetch('http://127.0.0.1:5001/api/graphql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, variables })
      });

      if (!response.ok) {
        throw new Error(`GraphQL query failed: ${response.statusText}`);
      }

      return response.json();
    }, { query, variables });
  }

  /**
   * Execute GraphQL mutation
   * @param {Page} page - Playwright page object
   * @param {string} mutation - GraphQL mutation
   * @param {Object} variables - Mutation variables
   * @returns {Promise<Object>} Mutation result
   */
  static async executeMutation(page, mutation, variables = {}) {
    return this.executeQuery(page, mutation, variables);
  }

  /**
   * Get all parameters for a game
   * @param {Page} page - Playwright page object
   * @param {number} gameGid - Game GID
   * @returns {Promise<Array>} Array of parameters
   */
  static async getParameters(page, gameGid) {
    const query = `
      query GetParameters($gameGid: Int!) {
        parameters(gameGid: $gameGid) {
          id
          paramName
          paramNameCn
          paramType
          isCommon
        }
      }
    `;

    const result = await this.executeQuery(page, query, { gameGid });
    return result.data?.parameters || [];
  }

  /**
   * Get all events for a game
   * @param {Page} page - Playwright page object
   * @param {number} gameGid - Game GID
   * @returns {Promise<Array>} Array of events
   */
  static async getEvents(page, gameGid) {
    const query = `
      query GetEvents($gameGid: Int!) {
        events(gameGid: $gameGid) {
          id
          eventName
          eventNameCn
        }
      }
    `;

    const result = await this.executeQuery(page, query, { gameGid });
    return result.data?.events || [];
  }
}

/**
 * TestDataBuilder - Builder pattern for test data
 */
export class TestDataBuilder {
  constructor() {
    this.gameData = {
      name: 'Test Game',
      gid: 90000001,
      ods_db: 'ieu_ods'
    };

    this.eventData = {
      name: 'test_event',
      ods_table: 'ods_test_event'
    };

    this.parameterData = {
      paramName: 'testParam',
      paramNameCn: '测试参数',
      paramType: 'param'
    };
  }

  withGameName(name) {
    this.gameData.name = name;
    return this;
  }

  withGameGid(gid) {
    this.gameData.gid = gid;
    return this;
  }

  withEventName(name) {
    this.eventData.name = name;
    this.eventData.ods_table = `ods_${name}`;
    return this;
  }

  withParameterName(name) {
    this.parameterData.paramName = name;
    return this;
  }

  withParameterType(type) {
    this.parameterData.paramType = type;
    return this;
  }

  build() {
    return {
      game: this.gameData,
      event: this.eventData,
      parameter: this.parameterData
    };
  }
}

/**
 * WaitHelpers - Advanced wait helpers
 */
export class WaitHelpers {
  /**
   * Wait for element to appear
   * @param {Page} page - Playwright page object
   * @param {string} selector - Element selector
   * @param {number} timeout - Timeout in milliseconds
   */
  static async waitForElement(page, selector, timeout = 5000) {
    await page.waitForSelector(selector, { timeout, state: 'visible' });
  }

  /**
   * Wait for element to disappear
   * @param {Page} page - Playwright page object
   * @param {string} selector - Element selector
   * @param {number} timeout - Timeout in milliseconds
   */
  static async waitForElementToDisappear(page, selector, timeout = 5000) {
    await page.waitForSelector(selector, { timeout, state: 'hidden' });
  }

  /**
   * Wait for text to appear
   * @param {Page} page - Playwright page object
   * @param {string} text - Text to wait for
   * @param {number} timeout - Timeout in milliseconds
   */
  static async waitForText(page, text, timeout = 5000) {
    await page.waitForSelector(`text=${text}`, { timeout });
  }

  /**
   * Wait for loading to complete
   * @param {Page} page - Playwright page object
   */
  static async waitForLoading(page) {
    await page.waitForLoadState('networkidle');
    await page.waitForLoadState('domcontentloaded');
  }
}

/**
 * Page-level helper functions (exported for use in tests)
 */

/**
 * Wait for page to be fully ready
 * @param {Page} page - Playwright page object
 */
export async function waitForPageReady(page) {
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');
  // Wait for React to settle
  await page.waitForTimeout(1000);
}

/**
 * Check console errors on page
 * @param {Page} page - Playwright page object
 * @returns {Promise<Array<string>>} Array of console error messages
 */
export async function checkConsoleErrors(page) {
  const errors = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // Filter out non-critical errors
      if (!text.includes('DevTools') && 
          !text.includes('chrome-extension') &&
          !text.includes('Extension') &&
          !text.includes('favicon')) {
        errors.push(text);
      }
    }
  });
  
  // Wait to collect any errors
  await page.waitForTimeout(2000);
  
  return errors;
}

/**
 * Take a snapshot of the current page
 * @param {Page} page - Playwright page object
 * @param {string} name - Snapshot name
 * @returns {Promise<string>} Path to snapshot
 */
export async function takeSnapshot(page, name) {
  const path = `frontend/test/e2e/output/snapshots/${name}-${Date.now()}.png`;
  await page.screenshot({ path, fullPage: true });
  return path;
}

/**
 * Measure page performance metrics
 * @param {Page} page - Playwright page object
 * @returns {Promise<Object>} Performance metrics
 */
export async function measurePerformance(page) {
  const metrics = await page.evaluate(() => {
    const perfData = performance.getEntriesByType('navigation')[0] || {};
    return {
      domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
      loadComplete: perfData.loadEventEnd - perfData.fetchStart,
      firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
      firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0,
    };
  });
  return metrics;
}
