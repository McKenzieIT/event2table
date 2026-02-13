/**
 * TestHealthChecker - API Health Checker for E2E Tests
 *
 * Provides API availability checks before running E2E tests to ensure
 * the backend is ready and responsive.
 *
 * @example
 * ```javascript
 * const checker = new TestHealthChecker('/hql-preview-v2', 5000);
 * const isHealthy = await checker.checkAPI('/api/generate');
 * if (!isHealthy) {
 *   console.error('API is not available');
 * }
 * ```
 */
class TestHealthChecker {
  /**
   * API base URL for health checks
   * @private
   * @type {string}
   */
  _apiBaseUrl;

  /**
   * Request timeout in milliseconds
   * @private
   * @type {number}
   */
  _timeout;

  /**
   * Create a new TestHealthChecker instance
   *
   * @param {string} [apiBaseUrl='/hql-preview-v2'] - Base URL for API endpoints
   * @param {number} [timeout=5000] - Request timeout in milliseconds
   * @throws {TypeError} If apiBaseUrl is not a string or timeout is not a positive number
   *
   * @example
   * ```javascript
   * const checker = new TestHealthChecker(); // defaults
   * const customChecker = new TestHealthChecker('/api/v1', 10000);
   * ```
   */
  constructor(apiBaseUrl = '/hql-preview-v2', timeout = 5000) {
    // Input validation with strong type checking
    if (typeof apiBaseUrl !== 'string') {
      throw new TypeError(
        `apiBaseUrl must be a string, received ${typeof apiBaseUrl}: ${apiBaseUrl}`
      );
    }

    if (typeof timeout !== 'number' || timeout <= 0) {
      throw new TypeError(
        `timeout must be a positive number, received ${typeof timeout}: ${timeout}`
      );
    }

    this._apiBaseUrl = apiBaseUrl;
    this._timeout = timeout;
  }

  /**
   * Check if an API endpoint is available and responding
   *
   * Uses HTTP HEAD request for minimal overhead. Returns false on timeout,
   * network errors, or non-OK responses.
   *
   * @param {string} endpoint - API endpoint path or full URL
   * @returns {Promise<boolean>} True if endpoint is available, false otherwise
   * @throws {TypeError} If endpoint is not a valid string
   * @throws {Error} If fetch is not available in the environment
   *
   * @example
   * ```javascript
   * const checker = new TestHealthChecker();
   * const isAvailable = await checker.checkAPI('/api/generate');
   * // true if API returns 2xx status
   *
   * const fullUrl = await checker.checkAPI('http://localhost:5001/api/status');
   * // supports full URLs
   * ```
   */
  async checkAPI(endpoint) {
    // Input validation
    if (typeof endpoint !== 'string') {
      throw new TypeError(
        `endpoint must be a string, received ${typeof endpoint}: ${endpoint}`
      );
    }

    if (endpoint.trim().length === 0) {
      throw new TypeError('endpoint cannot be an empty string');
    }

    // Check if fetch is available
    if (typeof fetch === 'undefined') {
      throw new Error('fetch is not available in this environment');
    }

    // Construct full URL
    const url = endpoint.startsWith('http') ? endpoint : `${this._apiBaseUrl}${endpoint}`;

    try {
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this._timeout);

      // Perform HEAD request (lighter than GET)
      const response = await fetch(url, {
        method: 'HEAD',
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      // Return true only if response is OK (2xx status)
      return response.ok;
    } catch (error) {
      // Log error for debugging but don't throw
      if (error.name === 'AbortError') {
        console.warn(`[TestHealthChecker] API check timeout: ${url}`);
      } else {
        console.warn(`[TestHealthChecker] API check failed: ${url}`, error.message);
      }

      // Return false for any error (timeout, network error, etc.)
      return false;
    }
  }

  /**
   * Check if the cache statistics API is available
   *
   * Verifies the /api/cache-stats endpoint is responding.
   *
   * @returns {Promise<boolean>} True if cache API is available
   * @throws {Error} Propagates errors from checkAPI
   *
   * @example
   * ```javascript
   * const checker = new TestHealthChecker();
   * if (await checker.checkCacheAPI()) {
   *   console.log('Cache API is available');
   * }
   * ```
   */
  async checkCacheAPI() {
    return await this.checkAPI('/api/cache-stats');
  }

  /**
   * Check if the HQL generation API is available
   *
   * Verifies the /api/generate endpoint is responding.
   *
   * @returns {Promise<boolean>} True if generate API is available
   * @throws {Error} Propagates errors from checkAPI
   *
   * @example
   * ```javascript
   * const checker = new TestHealthChecker();
   * if (await checker.checkGenerateAPI()) {
   *   console.log('Generate API is available');
   * }
   * ```
   */
  async checkGenerateAPI() {
    return await this.checkAPI('/api/generate');
  }

  /**
   * Measure API response time
   *
   * Returns the time in milliseconds for a HEAD request to complete.
   * Returns -1 on error or timeout.
   *
   * @param {string} endpoint - API endpoint path or full URL
   * @returns {Promise<number>} Response time in milliseconds, or -1 on error
   * @throws {TypeError} If endpoint is not a valid string
   * @throws {Error} If fetch is not available in the environment
   *
   * @example
   * ```javascript
   * const checker = new TestHealthChecker();
   * const time = await checker.getResponseTime('/api/cache-stats');
   * if (time >= 0) {
   *   console.log(`Response time: ${time}ms`);
   * } else {
   *   console.error('API unavailable');
   * }
   * ```
   */
  async getResponseTime(endpoint) {
    // Input validation
    if (typeof endpoint !== 'string') {
      throw new TypeError(
        `endpoint must be a string, received ${typeof endpoint}: ${endpoint}`
      );
    }

    if (endpoint.trim().length === 0) {
      throw new TypeError('endpoint cannot be an empty string');
    }

    // Check if fetch is available
    if (typeof fetch === 'undefined') {
      throw new Error('fetch is not available in this environment');
    }

    // Construct full URL
    const url = endpoint.startsWith('http') ? endpoint : `${this._apiBaseUrl}${endpoint}`;

    const startTime = Date.now();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this._timeout);

      await fetch(url, {
        method: 'HEAD',
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return Date.now() - startTime;
    } catch (error) {
      console.warn(`[TestHealthChecker] Response time check failed: ${url}`, error.message);
      return -1;
    }
  }

}

// Export for use in tests
export { TestHealthChecker };
