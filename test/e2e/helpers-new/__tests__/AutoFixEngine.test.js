const { AutoFixEngine } = require('../AutoFixEngine');
const { TestDataManager } = require('../TestDataManager');

// Mock fetch for testing
global.fetch = jest.fn();

/**
 * AutoFixEngine Test Suite
 *
 * Tests the automatic error fixing engine for E2E tests
 * @module AutoFixEngineTests
 */
describe('AutoFixEngine', () => {
  let dataManager;
  let engine;

  beforeEach(() => {
    dataManager = new TestDataManager();
    engine = new AutoFixEngine(dataManager);
    jest.clearAllMocks();
  });

  describe('fixError - API_NOT_FOUND', () => {
    test('clears cache and returns success', async () => {
      // Mock cache clear API
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

      const result = await engine.fixError({}, {
        type: 'API_NOT_FOUND',
        message: 'API endpoint not found'
      });

      expect(result.success).toBe(true);
      expect(result.action).toBe('cache_cleared');
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:5001/admin/cache/clear',
        { method: 'POST' }
      );
    });

    test('returns failure when cache clear fails', async () => {
      // Mock cache clear failure
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await engine.fixError({}, {
        type: 'API_NOT_FOUND',
        message: 'API endpoint not found'
      });

      expect(result.success).toBe(false);
      expect(result.reason).toBe('Failed to clear cache');
    });
  });

  describe('fixError - DATA_MISSING', () => {
    test('creates test data when missing', async () => {
      // Mock ensureTestData returns true (data created)
      global.fetch
        .mockResolvedValueOnce({ ok: false, status: 404 }) // Validation fails
        .mockResolvedValueOnce({ ok: true }) // Game created
        .mockResolvedValueOnce({ ok: true }); // Event created

      const result = await engine.fixError({
        testData: { game_gid: 10000147, event_id: 55, event_name: 'test_event' }
      }, {
        type: 'DATA_MISSING',
        message: 'Test data not found'
      });

      expect(result.success).toBe(true);
      expect(result.action).toBe('data_created');
    });

    test('returns failure when data creation fails', async () => {
      // Mock ensureTestData returns false
      global.fetch.mockResolvedValueOnce({ ok: false, status: 404 });

      const result = await engine.fixError({
        testData: { game_gid: 10000147, event_id: 55, event_name: 'test_event' }
      }, {
        type: 'DATA_MISSING',
        message: 'Test data not found'
      });

      expect(result.success).toBe(false);
      expect(result.reason).toBe('Failed to create test data');
    });
  });

  describe('fixError - TIMEOUT', () => {
    test('doubles timeout up to 30s max', async () => {
      const result = await engine.fixError({ timeout: 5000 }, {
        type: 'TIMEOUT',
        message: 'Request timeout'
      });

      expect(result.success).toBe(true);
      expect(result.action).toBe('timeout_increased');
      expect(result.details.newTimeout).toBe(10000);
    });

    test('caps timeout at 30 seconds', async () => {
      const result = await engine.fixError({ timeout: 20000 }, {
        type: 'TIMEOUT',
        message: 'Request timeout'
      });

      expect(result.success).toBe(true);
      expect(result.action).toBe('timeout_increased');
      expect(result.details.newTimeout).toBe(30000);
    });

    test('uses default 5000ms timeout when not specified', async () => {
      const result = await engine.fixError({}, {
        type: 'TIMEOUT',
        message: 'Request timeout'
      });

      expect(result.success).toBe(true);
      expect(result.action).toBe('timeout_increased');
      expect(result.details.newTimeout).toBe(10000); // 5000 * 2
    });
  });

  describe('fixError - ASSERTION_FAILED', () => {
    test('returns manual review message', async () => {
      const result = await engine.fixError({}, {
        type: 'ASSERTION_FAILED',
        message: 'Expected 200 but got 500'
      });

      expect(result.success).toBe(false);
      expect(result.reason).toBe('Assertion failures require manual review');
    });
  });

  describe('fixError - NETWORK_ERROR', () => {
    test('clears cache after sleep', async () => {
      // Mock cache clear API
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

      const startTime = Date.now();
      const result = await engine.fixError({}, {
        type: 'NETWORK_ERROR',
        message: 'Network error'
      });
      const endTime = Date.now();

      expect(result.success).toBe(true);
      expect(result.action).toBe('cache_cleared_and_retried');
      expect(endTime - startTime).toBeGreaterThanOrEqual(2000); // At least 2s sleep
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:5001/admin/cache/clear',
        { method: 'POST' }
      );
    });

    test('returns failure when cache clear fails', async () => {
      // Mock cache clear failure
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await engine.fixError({}, {
        type: 'NETWORK_ERROR',
        message: 'Network error'
      });

      expect(result.success).toBe(false);
      expect(result.reason).toBe('Network recovery failed');
    });
  });

  describe('fixError - unknown error type', () => {
    test('returns failure with unknown error type message', async () => {
      const result = await engine.fixError({}, {
        type: 'UNKNOWN',
        message: 'Unknown error'
      });

      expect(result.success).toBe(false);
      expect(result.reason).toBe('Unknown error type');
    });
  });

  describe('constructor', () => {
    test('creates instance with TestDataManager', () => {
      const customDataManager = new TestDataManager('http://localhost:3000');
      const customEngine = new AutoFixEngine(customDataManager);

      expect(customEngine.dataManager).toBe(customDataManager);
    });

    test('uses default API base URL', () => {
      expect(engine.apiBaseUrl).toBe('http://127.0.0.1:5001');
    });

    test('uses custom API base URL', () => {
      const customEngine = new AutoFixEngine(dataManager, 'http://localhost:3000');
      expect(customEngine.apiBaseUrl).toBe('http://localhost:3000');
    });
  });
});
