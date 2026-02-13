const { TestHealthChecker } = require('../TestHealthChecker');

// Mock fetch for testing
global.fetch = jest.fn();

describe('TestHealthChecker', () => {
  let checker;

  beforeEach(() => {
    checker = new TestHealthChecker();
    jest.clearAllMocks();
  });

  describe('checkAPI', () => {
    test('returns true when API is available', async () => {
      // Mock successful HEAD request
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const result = await checker.checkAPI('/api/generate');

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        '/hql-preview-v2/api/generate',
        expect.objectContaining({
          method: 'HEAD'
        })
      );
    });

    test('returns false when API returns error status', async () => {
      // Mock failed HEAD request
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      });

      const result = await checker.checkAPI('/api/generate');

      expect(result).toBe(false);
    });

    test('returns false on timeout', async () => {
      const timeoutChecker = new TestHealthChecker('/hql-preview-v2', 10); // 10ms timeout

      // Mock fetch that respects AbortController signal
      global.fetch.mockImplementationOnce((url, options) => {
        return new Promise((resolve, reject) => {
          // Listen for abort event
          if (options?.signal) {
            options.signal.addEventListener('abort', () => {
              const error = new Error('Request timeout');
              error.name = 'AbortError';
              reject(error);
            });
          }

          // Never resolve - will timeout
          setTimeout(() => resolve({ ok: true }), 1000);
        });
      });

      const result = await timeoutChecker.checkAPI('/api/slow-endpoint');

      expect(result).toBe(false);
    });

    test('returns false on network error', async () => {
      // Mock network error
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await checker.checkAPI('/api/generate');

      expect(result).toBe(false);
    });

    test('accepts full URLs', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const result = await checker.checkAPI('http://localhost:5001/hql-preview-v2/api/status');

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5001/hql-preview-v2/api/status',
        expect.objectContaining({
          method: 'HEAD'
        })
      );
    });

    test('throws TypeError for invalid endpoint', async () => {
      await expect(checker.checkAPI(null)).rejects.toThrow(TypeError);
      await expect(checker.checkAPI(undefined)).rejects.toThrow(TypeError);
      await expect(checker.checkAPI(123)).rejects.toThrow(TypeError);
    });
  });

  describe('checkCacheAPI', () => {
    test('checks cache endpoint', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const result = await checker.checkCacheAPI();

      expect(typeof result).toBe('boolean');
      expect(global.fetch).toHaveBeenCalledWith(
        '/hql-preview-v2/api/cache-stats',
        expect.objectContaining({
          method: 'HEAD'
        })
      );
    });
  });

  describe('checkGenerateAPI', () => {
    test('checks generate endpoint', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const result = await checker.checkGenerateAPI();

      expect(typeof result).toBe('boolean');
      expect(global.fetch).toHaveBeenCalledWith(
        '/hql-preview-v2/api/generate',
        expect.objectContaining({
          method: 'HEAD'
        })
      );
    });
  });

  describe('getResponseTime', () => {
    test('returns response time in milliseconds', async () => {
      global.fetch.mockImplementationOnce(() =>
        new Promise((resolve) => setTimeout(() => resolve({ ok: true }), 50))
      );

      const time = await checker.getResponseTime('/api/cache-stats');

      expect(time).toBeGreaterThanOrEqual(0);
      expect(time).toBeLessThan(1000); // Should be fast
    });

    test('returns -1 on network error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const time = await checker.getResponseTime('/api/nonexistent');

      expect(time).toBe(-1);
    });

    test('throws TypeError for invalid endpoint', async () => {
      await expect(checker.getResponseTime(null)).rejects.toThrow(TypeError);
      await expect(checker.getResponseTime(undefined)).rejects.toThrow(TypeError);
      await expect(checker.getResponseTime(123)).rejects.toThrow(TypeError);
    });

    test('respects timeout on slow requests', async () => {
      const timeoutChecker = new TestHealthChecker('/hql-preview-v2', 10); // 10ms timeout

      // Mock fetch that respects AbortController signal
      global.fetch.mockImplementationOnce((url, options) => {
        return new Promise((resolve, reject) => {
          // Listen for abort event
          if (options?.signal) {
            options.signal.addEventListener('abort', () => {
              const error = new Error('Request timeout');
              error.name = 'AbortError';
              reject(error);
            });
          }

          // Never resolve - will timeout
          setTimeout(() => resolve({ ok: true }), 1000);
        });
      });

      const time = await timeoutChecker.getResponseTime('/api/slow-endpoint');

      expect(time).toBe(-1); // Should return -1 on timeout
    });
  });
});
