/**
 * Test suite for TestExecutor class
 *
 * Tests the test execution engine with auto-retry capabilities
 *
 * @group e2e-helpers
 * @group test-executor
 */

const { TestExecutor } = require('../TestExecutor');
const { AutoFixEngine } = require('../AutoFixEngine');
const { TestDataManager } = require('../TestDataManager');

// Mock fetch for testing
global.fetch = jest.fn();

beforeEach(() => {
  jest.clearAllMocks();
});

/**
 * Verify TestExecutor runs successful test without retries
 */
test('TestExecutor: run successful test', async () => {
  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  const result = await executor.run({
    name: 'test',
    timeout: 5000,
    retries: 3
  }, async () => {
    return { success: true, data: 'test' };
  });

  expect(result.success).toBe(true);
  expect(result.data).toEqual({ success: true, data: 'test' });
  expect(result.attempts).toBe(1);
  expect(result.fixLog).toBeDefined();
});

/**
 * Verify TestExecutor retries on failure and applies auto-fix
 */
test('TestExecutor: retry on failure with auto-fix', async () => {
  // Mock cache clear API
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ success: true })
  });

  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  let attempts = 0;
  const result = await executor.run({
    name: 'test',
    timeout: 5000,
    retries: 3
  }, async () => {
    attempts++;
    if (attempts < 2) {
      throw new Error('API not found 404');
    }
    return { success: true };
  });

  expect(result.success).toBe(true);
  expect(result.attempts).toBe(2);
  expect(result.fixLog).toHaveLength(1);
  expect(result.fixLog && result.fixLog[0].success).toBe(true);
  expect(result.fixLog && result.fixLog[0].errorType).toBe('API_NOT_FOUND');
});

/**
 * Verify TestExecutor fails after max retries when fix fails
 */
test('TestExecutor: fail after max retries', async () => {
  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  const result = await executor.run({
    name: 'test',
    timeout: 5000,
    retries: 2
  }, async () => {
    throw new Error('Assertion failed: expected 200 but got 500');
  });

  expect(result.success).toBe(false);
  expect(result.attempts).toBe(1); // ASSERTION_FAILED can't be fixed
  expect(result.error && result.error.type).toBe('ASSERTION_FAILED');
  expect(result.error && result.error.message).toContain('Assertion failed');
});

/**
 * Verify TestExecutor classifies timeout errors correctly
 */
test('TestExecutor: timeout classification', async () => {
  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  const result = await executor.run({
    name: 'test',
    timeout: 100,
    retries: 1
  }, async () => {
    await new Promise(resolve => setTimeout(resolve, 200));
    return { success: true };
  });

  expect(result.success).toBe(false);
  expect(result.error && result.error.type).toBe('TIMEOUT');
  expect(result.error && result.error.message).toContain('timeout');
});

/**
 * Verify TestExecutor uses default timeout and retries
 */
test('TestExecutor: use default timeout and retries', async () => {
  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine, 5000, 2);

  const result = await executor.run({
    name: 'test'
  }, async () => {
    return { success: true };
  });

  expect(result.success).toBe(true);
  expect(result.attempts).toBe(1);
});

/**
 * Verify TestExecutor handles network errors
 */
test('TestExecutor: network error classification', async () => {
  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  const result = await executor.run({
    name: 'test',
    timeout: 5000,
    retries: 2
  }, async () => {
    throw new Error('fetch failed: network error');
  });

  expect(result.success).toBe(false);
  expect(result.error && result.error.type).toBe('NETWORK_ERROR');
});

/**
 * Verify TestExecutor handles data missing errors
 */
test('TestExecutor: data missing error classification', async () => {
  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  const result = await executor.run({
    name: 'test',
    timeout: 5000,
    retries: 2
  }, async () => {
    throw new Error('data not available');
  });

  expect(result.success).toBe(false);
  expect(result.error && result.error.type).toBe('DATA_MISSING');
});

/**
 * Verify TestExecutor accumulates fix log across retries
 */
test('TestExecutor: accumulate fix log across retries', async () => {
  // Mock cache clear API (called twice)
  global.fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    });

  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  let attempts = 0;
  const result = await executor.run({
    name: 'test',
    timeout: 5000,
    retries: 5
  }, async () => {
    attempts++;
    if (attempts < 3) {
      throw new Error('API not found 404');
    }
    return { success: true };
  });

  expect(result.success).toBe(true);
  expect(result.attempts).toBe(3);
  expect(result.fixLog).toHaveLength(2);
  expect(result.fixLog && result.fixLog[0].testName).toBe('test');
  expect(result.fixLog && result.fixLog[1].testName).toBe('test');
});

/**
 * Verify TestExecutor validates input parameters
 */
test('TestExecutor: throw TypeError for invalid test function', async () => {
  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  let threwError = false;
  try {
    await executor.run({
      name: 'test'
    }, null);
  } catch (error) {
    threwError = true;
    expect(error).toBeInstanceOf(TypeError);
  }
  expect(threwError).toBe(true);
});

/**
 * Verify TestExecutor initializes fix log if not provided
 */
test('TestExecutor: initialize fix log if not provided', async () => {
  const dataManager = new TestDataManager();
  const fixEngine = new AutoFixEngine(dataManager);
  const executor = new TestExecutor(fixEngine);

  const result = await executor.run({
    name: 'test'
  }, async () => {
    return { success: true };
  });

  expect(result.success).toBe(true);
  expect(result.fixLog).toBeDefined();
  expect(Array.isArray(result.fixLog)).toBe(true);
});
