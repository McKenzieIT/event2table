const { TestDataManager } = require('../TestDataManager');

// Mock fetch for testing
global.fetch = jest.fn();

describe('TestDataManager', () => {
  let manager;

  beforeEach(() => {
    manager = new TestDataManager();
    jest.clearAllMocks();
  });

  describe('validateTestData', () => {
    test('returns true when both game and event exist', async () => {
      // Mock successful game and event validation
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { gid: 10000147, name: 'Test Game' } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { id: 55, event_name: 'test_event' } })
        });

      const result = await manager.validateTestData({
        game_gid: 10000147,
        event_id: 55
      });

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(global.fetch).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:5001/api/games/10000147');
      expect(global.fetch).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:5001/api/events/55');
    });

    test('returns false when game does not exist', async () => {
      // Mock game not found (404)
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404
      });

      const result = await manager.validateTestData({
        game_gid: 99999999,
        event_id: 55
      });

      expect(result).toBe(false);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    test('returns false when event does not exist', async () => {
      // Mock game exists, event not found
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { gid: 10000147 } })
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 404
        });

      const result = await manager.validateTestData({
        game_gid: 10000147,
        event_id: 999
      });

      expect(result).toBe(false);
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    test('throws TypeError when data is not an object', async () => {
      await expect(manager.validateTestData(null)).rejects.toThrow('data must be an object');
    });

    test('throws TypeError when game_gid is not a number', async () => {
      await expect(manager.validateTestData({ game_gid: 'invalid', event_id: 55 }))
        .rejects.toThrow('data.game_gid must be a number');
    });

    test('throws TypeError when event_id is not a number', async () => {
      await expect(manager.validateTestData({ game_gid: 10000147, event_id: 'invalid' }))
        .rejects.toThrow('data.event_id must be a number');
    });

    test('returns false on network error', async () => {
      // Mock network error
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await manager.validateTestData({
        game_gid: 10000147,
        event_id: 55
      });

      expect(result).toBe(false);
    });
  });

  describe('ensureTestData', () => {
    test('returns true when test data already exists', async () => {
      // Mock validation succeeds
      global.fetch
        .mockResolvedValueOnce({ ok: true })
        .mockResolvedValueOnce({ ok: true });

      const result = await manager.ensureTestData({
        game_gid: 10000147,
        event_name: 'test_event',
        event_id: 55
      });

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledTimes(2); // Only validation calls
    });

    test('creates missing test data', async () => {
      // Mock validation fails (game not found), creation succeeds
      global.fetch
        .mockResolvedValueOnce({ ok: false, status: 404 }) // Game not found (validation stops here)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { id: 1, gid: 10000147 } })
        }) // Game created
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { id: 55, event_name: 'test_event' } })
        }); // Event created

      const result = await manager.ensureTestData({
        game_gid: 10000147,
        event_name: 'test_event',
        event_id: 55
      });

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledTimes(3); // 1 validation + 2 creation
    });

    test('throws TypeError when game_gid is not a number', async () => {
      await expect(manager.ensureTestData({ game_gid: 'invalid', event_name: 'test', event_id: 55 }))
        .rejects.toThrow('data.game_gid must be a number');
    });

    test('throws TypeError when event_name is not a string', async () => {
      await expect(manager.ensureTestData({ game_gid: 10000147, event_name: 123, event_id: 55 }))
        .rejects.toThrow('data.event_name must be a string');
    });
  });

  describe('createTestData', () => {
    test('creates game and event successfully', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { id: 1, gid: 10000147 } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { id: 55, event_name: 'test_event_55' } })
        });

      const result = await manager.createTestData({
        game_gid: 10000147,
        event_name: 'test_event_55',
        event_id: 55
      });

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledTimes(2);

      // Verify game creation request
      expect(global.fetch).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:5001/api/games', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gid: 10000147,
          name: 'Test Game 10000147',
          ods_db: 'test_ods'
        })
      });

      // Verify event creation request
      expect(global.fetch).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:5001/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          game_gid: 10000147,
          event_name: 'test_event_55',
          event_name_cn: '测试事件55',
          source_table: 'ods_test',
          target_table: 'dwd_test'
        })
      });
    });

    test('creates game only when event_name is not provided', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: { id: 1, gid: 10000147 } })
      });

      const result = await manager.createTestData({
        game_gid: 10000147
      });

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledTimes(1); // Only game creation
    });

    test('returns false when game creation fails', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        text: async () => 'Game already exists'
      });

      const result = await manager.createTestData({
        game_gid: 10000147,
        event_name: 'test_event'
      });

      expect(result).toBe(false);
    });

    test('returns false when event creation fails', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { id: 1 } })
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 400,
          text: async () => 'Invalid event data'
        });

      const result = await manager.createTestData({
        game_gid: 10000147,
        event_name: 'test_event'
      });

      expect(result).toBe(false);
    });

    test('throws TypeError when data is not an object', async () => {
      await expect(manager.createTestData(null)).rejects.toThrow('data must be an object');
    });

    test('throws TypeError when game_gid is not a number', async () => {
      await expect(manager.createTestData({ game_gid: 'invalid' }))
        .rejects.toThrow('data.game_gid must be a number');
    });
  });

  describe('cleanupTestData', () => {
    test('deletes event successfully', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true })
      });

      const result = await manager.cleanupTestData({
        event_id: 55,
        game_gid: 10000147
      });

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:5001/api/events/55',
        { method: 'DELETE' }
      );
    });

    test('returns true when event_id is not provided', async () => {
      const result = await manager.cleanupTestData({
        game_gid: 10000147
      });

      expect(result).toBe(true);
      expect(global.fetch).not.toHaveBeenCalled();
    });

    test('returns false when deletion fails', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 404
      });

      const result = await manager.cleanupTestData({
        event_id: 55,
        game_gid: 10000147
      });

      expect(result).toBe(false);
    });

    test('throws TypeError when data is not an object', async () => {
      await expect(manager.cleanupTestData(null)).rejects.toThrow('data must be an object');
    });
  });

  describe('constructor', () => {
    test('creates instance with default base URL', () => {
      const defaultManager = new TestDataManager();
      expect(defaultManager.apiBaseUrl).toBe('http://127.0.0.1:5001');
    });

    test('creates instance with custom base URL', () => {
      const customManager = new TestDataManager('http://localhost:3000');
      expect(customManager.apiBaseUrl).toBe('http://localhost:3000');
    });

    test('throws TypeError when baseUrl is not a string', () => {
      expect(() => new TestDataManager(123)).toThrow('baseUrl must be a string');
    });
  });
});
