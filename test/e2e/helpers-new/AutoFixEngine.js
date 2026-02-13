import { TestDataManager } from './TestDataManager.js';

/**
 * AutoFixEngine - Automatic Error Fixing Engine for E2E Tests
 *
 * This class provides automatic error detection and fixing strategies
 * for common E2E test failures. It analyzes test errors and applies
 * appropriate fix strategies to recover from transient failures.
 *
 * @class AutoFixEngine
 * @example
 * const dataManager = new TestDataManager();
 * const engine = new AutoFixEngine(dataManager);
 * const result = await engine.fixError({ timeout: 5000 }, {
 *   type: 'TIMEOUT',
 *   message: 'Request timeout'
 * });
 */
class AutoFixEngine {
  /**
   * Creates a new AutoFixEngine instance
   *
   * @param {TestDataManager} dataManager - The test data manager instance
   * @param {string} [apiBaseUrl='http://127.0.0.1:5001'] - The base URL for API calls
   * @throws {TypeError} If dataManager is not a TestDataManager instance
   * @throws {TypeError} If apiBaseUrl is not a string
   * @example
   * const dataManager = new TestDataManager();
   * const engine = new AutoFixEngine(dataManager, 'http://localhost:3000');
   */
  constructor(dataManager, apiBaseUrl = 'http://127.0.0.1:5001') {
    if (!(dataManager instanceof TestDataManager)) {
      throw new TypeError('dataManager must be an instance of TestDataManager');
    }
    if (typeof apiBaseUrl !== 'string') {
      throw new TypeError('apiBaseUrl must be a string');
    }

    this.dataManager = dataManager;
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * Fixes a test error using appropriate strategy
   *
   * Analyzes the error type and dispatches to the appropriate fix strategy.
   * Supported error types:
   * - API_NOT_FOUND: Clears cache to force API re-registration
   * - DATA_MISSING: Creates missing test data via TestDataManager
   * - TIMEOUT: Increases timeout value (doubles, capped at 30s)
   * - ASSERTION_FAILED: Requires manual review (no auto-fix)
   * - NETWORK_ERROR: Clears cache and retries after sleep
   *
   * @param {Object} testContext - The test context containing timeout, testData, etc.
   * @param {number} [testContext.timeout] - Current test timeout in milliseconds
   * @param {Object} [testContext.testData] - Test data for data creation
   * @param {Array} [testContext.fixLog] - Array to log fix attempts
   * @param {Object} error - The error to fix
   * @param {string} error.type - Error type (API_NOT_FOUND, DATA_MISSING, etc.)
   * @param {string} error.message - Error message
   * @param {any} [error.details] - Additional error details
   * @returns {Promise<Object>} Fix result with success, action, and reason
   * @throws {TypeError} If error is missing required fields
   * @example
   * const result = await engine.fixError({ timeout: 5000 }, {
   *   type: 'TIMEOUT',
   *   message: 'Request timeout'
   * });
   * // { success: true, action: 'timeout_increased', details: { newTimeout: 10000 } }
   */
  async fixError(testContext, error) {
    if (!error || typeof error !== 'object') {
      throw new TypeError('error must be an object');
    }
    if (typeof error.type !== 'string') {
      throw new TypeError('error.type must be a string');
    }
    if (typeof error.message !== 'string') {
      throw new TypeError('error.message must be a string');
    }

    const startTime = Date.now();

    try {
      let result;
      switch (error.type) {
        case 'API_NOT_FOUND':
          result = await this.fixAPINotFound(testContext, error);
          break;
        case 'DATA_MISSING':
          result = await this.fixDataMissing(testContext, error);
          break;
        case 'TIMEOUT':
          result = await this.fixTimeout(testContext, error);
          break;
        case 'ASSERTION_FAILED':
          result = await this.fixAssertionFailed(testContext, error);
          break;
        case 'NETWORK_ERROR':
          result = await this.fixNetworkError(testContext, error);
          break;
        default:
          result = { success: false, reason: 'Unknown error type' };
      }

      // Log fix attempt if fixLog is provided
      if (testContext.fixLog && Array.isArray(testContext.fixLog)) {
        testContext.fixLog.push({
          timestamp: new Date().toISOString(),
          testName: testContext.testName || 'unknown',
          errorType: error.type,
          fixAction: result.action || 'none',
          success: result.success,
          duration: Date.now() - startTime
        });
      }

      return result;
    } catch (err) {
      console.error(`AutoFixEngine: Failed to fix error type ${error.type}:`, err);
      return {
        success: false,
        reason: `Fix strategy failed: ${err.message}`
      };
    }
  }

  /**
   * Fixes API_NOT_FOUND errors by clearing cache
   *
   * Clears both L1 and L2 caches to force API re-registration.
   * This helps when APIs are not found due to stale cache entries.
   *
   * @private
   * @param {Object} testContext - The test context
   * @param {Object} error - The error to fix
   * @returns {Promise<Object>} Fix result with success and action
   * @throws {Error} If cache clear API call fails
   * @example
   * const result = await engine.fixAPINotFound({}, { type: 'API_NOT_FOUND', message: 'Not found' });
   * // { success: true, action: 'cache_cleared' }
   */
  async fixAPINotFound(testContext, error) {
    try {
      await this.clearCache();
      await this.sleep(1000);
      return { success: true, action: 'cache_cleared' };
    } catch (err) {
      console.error('AutoFixEngine: Failed to clear cache:', err);
      return { success: false, reason: 'Failed to clear cache' };
    }
  }

  /**
   * Fixes DATA_MISSING errors by creating test data
   *
   * Uses TestDataManager.ensureTestData to create missing test data.
   * This handles both game and event creation if they don't exist.
   *
   * @private
   * @param {Object} testContext - The test context containing testData
   * @param {Object} testContext.testData - Test data to create
   * @param {number} testContext.testData.game_gid - Game GID
   * @param {string} testContext.testData.event_name - Event name
   * @param {number} testContext.testData.event_id - Event ID
   * @param {Object} error - The error to fix
   * @returns {Promise<Object>} Fix result with success and action
   * @throws {TypeError} If testData is missing required fields
   * @example
   * const result = await engine.fixDataMissing(
   *   { testData: { game_gid: 10000147, event_id: 55, event_name: 'test' } },
   *   { type: 'DATA_MISSING', message: 'Data not found' }
   * );
   * // { success: true, action: 'data_created' }
   */
  async fixDataMissing(testContext, error) {
    if (!testContext.testData) {
      return { success: false, reason: 'Test data not provided in context' };
    }

    try {
      const created = await this.dataManager.ensureTestData(testContext.testData);
      if (created) {
        return { success: true, action: 'data_created' };
      }
      return { success: false, reason: 'Failed to create test data' };
    } catch (err) {
      console.error('AutoFixEngine: Failed to create test data:', err);
      return { success: false, reason: 'Data creation failed' };
    }
  }

  /**
   * Fixes TIMEOUT errors by increasing timeout
   *
   * Doubles the current timeout value, capped at 30 seconds maximum.
   * Default timeout is 5000ms if not specified in test context.
   *
   * @private
   * @param {Object} testContext - The test context containing timeout
   * @param {number} [testContext.timeout] - Current timeout in milliseconds
   * @param {Object} error - The error to fix
   * @returns {Promise<Object>} Fix result with success, action, and new timeout
   * @example
   * const result = await engine.fixTimeout({ timeout: 5000 }, { type: 'TIMEOUT' });
   * // { success: true, action: 'timeout_increased', details: { newTimeout: 10000 } }
   */
  async fixTimeout(testContext, error) {
    const currentTimeout = testContext.timeout || 5000;
    const newTimeout = Math.min(currentTimeout * 2, 30000);
    return {
      success: true,
      action: 'timeout_increased',
      details: { newTimeout }
    };
  }

  /**
   * Handles ASSERTION_FAILED errors
   *
   * Assertion failures indicate test logic issues and require manual review.
   * No automatic fix is applied for this error type.
   *
   * @private
   * @param {Object} testContext - The test context
   * @param {Object} error - The error to fix
   * @returns {Promise<Object>} Fix result with manual review message
   * @example
   * const result = await engine.fixAssertionFailed({}, { type: 'ASSERTION_FAILED' });
   * // { success: false, reason: 'Assertion failures require manual review' }
   */
  async fixAssertionFailed(testContext, error) {
    return { success: false, reason: 'Assertion failures require manual review' };
  }

  /**
   * Fixes NETWORK_ERROR by clearing cache and retrying
   *
   * Sleeps for 2 seconds to allow network recovery, then clears cache
   * to force fresh API calls. This helps recover from transient network issues.
   *
   * @private
   * @param {Object} testContext - The test context
   * @param {Object} error - The error to fix
   * @returns {Promise<Object>} Fix result with success and action
   * @throws {Error} If cache clear API call fails
   * @example
   * const result = await engine.fixNetworkError({}, { type: 'NETWORK_ERROR' });
   * // { success: true, action: 'cache_cleared_and_retried' }
   */
  async fixNetworkError(testContext, error) {
    try {
      await this.sleep(2000);
      await this.clearCache();
      return { success: true, action: 'cache_cleared_and_retried' };
    } catch (err) {
      console.error('AutoFixEngine: Network recovery failed:', err);
      return { success: false, reason: 'Network recovery failed' };
    }
  }

  /**
   * Clears both L1 and L2 caches via backend API
   *
   * Calls the POST /admin/cache/clear endpoint to clear all caches.
   * This forces re-registration of APIs and fresh data fetching.
   *
   * @private
   * @returns {Promise<void>} Promise that resolves when cache is cleared
   * @throws {Error} If cache clear API call fails
   * @example
   * await engine.clearCache();
   */
  async clearCache() {
    const response = await fetch(`${this.apiBaseUrl}/admin/cache/clear`, {
      method: 'POST'
    });
    if (!response.ok) {
      throw new Error(`Failed to clear cache: ${response.status} ${response.statusText}`);
    }
  }

  /**
   * Sleeps for specified milliseconds
   *
   * Utility method for introducing delays in fix strategies.
   * Used to allow system recovery (e.g., network stabilization).
   *
   * @private
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise<void>} Promise that resolves after sleep
   * @throws {TypeError} If ms is not a number
   * @example
   * await engine.sleep(2000); // Sleep for 2 seconds
   */
  sleep(ms) {
    if (typeof ms !== 'number') {
      throw new TypeError('ms must be a number');
    }
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export { AutoFixEngine };
