/**
 * TestExecutor - Test Execution Engine with Auto-Retry
 *
 * Executes tests with automatic retry logic and integrates with AutoFixEngine
 * to apply fixes when tests fail. Provides comprehensive error classification
 * and maintains a fix log for debugging.
 *
 * @class TestExecutor
 * @example
 * const executor = new TestExecutor(fixEngine, 10000, 3);
 * const result = await executor.run(
 *   { name: 'myTest', timeout: 5000, retries: 2 },
 *   async () => { return await api.call(); }
 * );
 */

import { AutoFixEngine } from './AutoFixEngine.js';

/**
 * @typedef {Function} TestFunction
 * @returns {Promise<any>} Test result
 */

/**
 * @typedef {Object} TestContext
 * @property {string} name - Test name
 * @property {number} [timeout] - Test timeout in milliseconds
 * @property {number} [retries] - Maximum retry attempts
 * @property {any} [testData] - Optional test data
 * @property {Array<FixLogEntry>} [fixLog] - Fix log accumulator
 */

/**
 * @typedef {Object} TestError
 * @property {string} type - Error type (API_NOT_FOUND, TIMEOUT, NETWORK_ERROR, ASSERTION_FAILED, DATA_MISSING)
 * @property {string} message - Error message
 */

/**
 * @typedef {Object} TestResult
 * @property {boolean} success - Whether test succeeded
 * @property {any} [data] - Test result data
 * @property {TestError} [error] - Error if failed
 * @property {number} attempts - Number of attempts made
 * @property {Array<FixLogEntry>} [fixLog] - Fix log entries
 */

/**
 * @typedef {import('./AutoFixEngine').FixLogEntry} FixLogEntry
 */

class TestExecutor {
  /**
   * Create a new TestExecutor
   *
   * @param {AutoFixEngine} fixEngine - Auto-fix engine instance
   * @param {number} [defaultTimeout=10000] - Default test timeout in milliseconds
   * @param {number} [defaultRetries=3] - Default maximum retry attempts
   * @throws {TypeError} If fixEngine is not an instance of AutoFixEngine
   */
  constructor(fixEngine, defaultTimeout = 10000, defaultRetries = 3) {
    if (!(fixEngine instanceof AutoFixEngine)) {
      throw new TypeError('fixEngine must be an instance of AutoFixEngine');
    }

    if (typeof defaultTimeout !== 'number' || defaultTimeout <= 0) {
      throw new TypeError('defaultTimeout must be a positive number');
    }

    if (typeof defaultRetries !== 'number' || defaultRetries < 0) {
      throw new TypeError('defaultRetries must be a non-negative number');
    }

    /**
     * @private
     * @type {AutoFixEngine}
     */
    this.fixEngine = fixEngine;

    /**
     * @private
     * @type {number}
     */
    this.defaultTimeout = defaultTimeout;

    /**
     * @private
     * @type {number}
     */
    this.defaultRetries = defaultRetries;
  }

  /**
   * Execute a test with automatic retry and fix logic
   *
   * @param {TestContext} testContext - Test context configuration
   * @param {TestFunction} testFn - Test function to execute
   * @returns {Promise<TestResult>} Test execution result
   * @throws {TypeError} If testFn is not a function
   *
   * @example
   * const result = await executor.run(
   *   { name: 'test', timeout: 5000, retries: 3 },
   *   async () => { return await fetchData(); }
   * );
   */
  async run(testContext, testFn) {
    // Input validation
    if (typeof testFn !== 'function') {
      throw new TypeError('testFn must be a function');
    }

    if (!testContext || typeof testContext.name !== 'string') {
      throw new TypeError('testContext must have a valid name property');
    }

    /**
     * @type {TestError | null}
     */
    let lastError = null;

    /**
     * @type {number}
     */
    let attempts = 0;

    const maxAttempts = testContext.retries || this.defaultRetries;
    const timeout = testContext.timeout || this.defaultTimeout;

    // Initialize fix log if not provided
    if (!testContext.fixLog) {
      testContext.fixLog = [];
    }

    // Add testName to testContext for AutoFixEngine logging
    testContext.testName = testContext.name;

    // Retry loop
    while (attempts < maxAttempts) {
      try {
        // Execute test with timeout
        const result = await this.executeWithTimeout(testFn, timeout);

        return {
          success: true,
          data: result,
          attempts: attempts + 1,
          fixLog: testContext.fixLog
        };
      } catch (error) {
        // Classify error
        lastError = this.classifyError(error);
        attempts++;

        // Try to fix the error (AutoFixEngine will log to fixLog)
        const fixResult = await this.fixEngine.fixError(testContext, lastError);

        // If fix failed, return failure result
        if (!fixResult.success) {
          return {
            success: false,
            error: lastError,
            attempts: attempts,
            fixLog: testContext.fixLog
          };
        }
      }
    }

    // Max retries exceeded
    return {
      success: false,
      error: lastError,
      attempts: maxAttempts,
      fixLog: testContext.fixLog
    };
  }

  /**
   * Execute a function with timeout
   *
   * @private
   * @param {TestFunction} fn - Function to execute
   * @param {number} timeout - Timeout in milliseconds
   * @returns {Promise<any>} Function result
   *
   * @example
   * const result = await executor.executeWithTimeout(
   *   async () => { return await fetchData(); },
   *   5000
   * );
   */
  async executeWithTimeout(fn, timeout) {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Test timeout after ${timeout}ms`));
      }, timeout);

      fn()
        .then(result => {
          clearTimeout(timeoutId);
          resolve(result);
        })
        .catch(error => {
          clearTimeout(timeoutId);
          reject(error);
        });
    });
  }

  /**
   * Classify an error into a known error type
   *
   * @private
   * @param {Error|any} error - Error to classify
   * @returns {TestError} Classified error
   *
   * @example
   * const classified = executor.classifyError(new Error('404 not found'));
   * // Returns: { type: 'API_NOT_FOUND', message: '404 not found' }
   */
  classifyError(error) {
    const message = error?.message || String(error);

    // Check for API not found errors
    if (message.includes('404') || message.includes('not found')) {
      return { type: 'API_NOT_FOUND', message };
    }

    // Check for timeout errors
    if (message.includes('timeout') || message.includes('timed out')) {
      return { type: 'TIMEOUT', message };
    }

    // Check for network errors
    if (message.includes('fetch failed') || message.includes('network')) {
      return { type: 'NETWORK_ERROR', message };
    }

    // Check for assertion failures
    if (message.includes('assert') || message.includes('expect')) {
      return { type: 'ASSERTION_FAILED', message };
    }

    // Default to data missing
    return { type: 'DATA_MISSING', message };
  }
}

export { TestExecutor };
