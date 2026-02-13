/**
 * TestDataManager - Manages test data validation and creation
 *
 * This class provides methods to validate, create, and clean up test data
 * (games and events) using existing backend APIs. It ensures test isolation
 * and prevents test data pollution.
 *
 * @class TestDataManager
 * @example
 * const manager = new TestDataManager('http://127.0.0.1:5001');
 * await manager.ensureTestData({ game_gid: 10000147, event_name: 'test_event', event_id: 55 });
 */
export class TestDataManager {
  /**
   * Creates a new TestDataManager instance
   *
   * @param {string} baseUrl - The base URL of the backend API (default: 'http://127.0.0.1:5001')
   * @throws {TypeError} If baseUrl is not a string
   */
  constructor(baseUrl = 'http://127.0.0.1:5001') {
    if (typeof baseUrl !== 'string') {
      throw new TypeError('baseUrl must be a string');
    }
    this.apiBaseUrl = baseUrl;
  }

  /**
   * Validates that test data exists (game and event)
   *
   * Checks if both the game and event exist in the database by calling
   * the existing GET /api/games/{game_gid} and GET /api/events/{event_id} endpoints.
   *
   * @param {Object} data - The test data to validate
   * @param {number} data.game_gid - The game GID to validate
   * @param {number} data.event_id - The event ID to validate
   * @returns {Promise<boolean>} True if both game and event exist, false otherwise
   * @throws {TypeError} If data is missing required fields
   * @example
   * const isValid = await manager.validateTestData({ game_gid: 10000147, event_id: 55 });
   * if (isValid) {
   *   console.log('Test data exists');
   * }
   */
  async validateTestData(data) {
    // Input validation
    if (!data || typeof data !== 'object') {
      throw new TypeError('data must be an object with game_gid and event_id');
    }
    if (typeof data.game_gid !== 'number') {
      throw new TypeError('data.game_gid must be a number');
    }
    if (typeof data.event_id !== 'number') {
      throw new TypeError('data.event_id must be a number');
    }

    try {
      // Check game exists: GET /api/games/{game_gid}
      const gameResponse = await fetch(`${this.apiBaseUrl}/api/games/${data.game_gid}`);
      if (!gameResponse.ok) {
        console.warn(`Game not found: game_gid=${data.game_gid}, status=${gameResponse.status}`);
        return false;
      }

      // Check event exists: GET /api/events/{event_id}?game_gid={game_gid}
      const eventResponse = await fetch(`${this.apiBaseUrl}/api/events/${data.event_id}?game_gid=${data.game_gid}`);
      if (!eventResponse.ok) {
        console.warn(`Event not found: event_id=${data.event_id}, game_gid=${data.game_gid}, status=${eventResponse.status}`);
        return false;
      }

      return true;
    } catch (error) {
      console.error(`Failed to validate test data for game_gid=${data.game_gid}, event_id=${data.event_id}:`, error);
      return false;
    }
  }

  /**
   * Ensures test data exists, creates if missing
   *
   * This is a convenience method that validates test data and creates it if missing.
   * It's useful for test setup to ensure required test data exists before running tests.
   *
   * @param {Object} data - The test data to ensure exists
   * @param {number} data.game_gid - The game GID
   * @param {string} data.event_name - The event name (used when creating event)
   * @param {number} data.event_id - The event ID (used for validation)
   * @returns {Promise<boolean>} True if test data exists or was created successfully, false otherwise
   * @throws {TypeError} If data is missing required fields
   * @example
   * await manager.ensureTestData({ game_gid: 10000147, event_name: 'test_event', event_id: 55 });
   */
  async ensureTestData(data) {
    // Input validation
    if (!data || typeof data !== 'object') {
      throw new TypeError('data must be an object');
    }
    if (typeof data.game_gid !== 'number') {
      throw new TypeError('data.game_gid must be a number');
    }
    if (typeof data.event_name !== 'string') {
      throw new TypeError('data.event_name must be a string');
    }

    const exists = await this.validateTestData(data);

    if (exists) {
      return true;
    }

    console.log(`Test data missing for game_gid=${data.game_gid}, creating...`);
    return await this.createTestData(data);
  }

  /**
   * Creates test data via existing backend APIs
   *
   * Creates both game and event using the existing POST endpoints:
   * - POST /api/games (creates game with gid, name, ods_db)
   * - POST /api/events (creates event with game_gid, event_name, source_table, target_table)
   *
   * @param {Object} data - The test data to create
   * @param {number} data.game_gid - The game GID to create
   * @param {string} [data.event_name] - The event name (optional, defaults to 'test_event_{game_gid}')
   * @param {number} [data.event_id] - The event ID (optional, only used for logging)
   * @returns {Promise<boolean>} True if creation succeeded, false otherwise
   * @throws {TypeError} If data is missing required fields
   * @example
   * const success = await manager.createTestData({
   *   game_gid: 10000147,
   *   event_name: 'test_event_55',
   *   event_id: 55
   * });
   */
  async createTestData(data) {
    // Input validation
    if (!data || typeof data !== 'object') {
      throw new TypeError('data must be an object');
    }
    if (typeof data.game_gid !== 'number') {
      throw new TypeError('data.game_gid must be a number');
    }

    try {
      // Step 1: Create game using POST /api/games
      const gameResponse = await fetch(`${this.apiBaseUrl}/api/games`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gid: data.game_gid,
          name: `Test Game ${data.game_gid}`,
          ods_db: 'test_ods'
        })
      });

      if (!gameResponse.ok) {
        const errorText = await gameResponse.text();
        console.error(`Failed to create game: status=${gameResponse.status}, error=${errorText}`);
        return false;
      }

      // Step 2: Create event using POST /api/events (if event_name provided)
      if (data.event_name) {
        const eventResponse = await fetch(`${this.apiBaseUrl}/api/events`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            game_gid: data.game_gid,
            event_name: data.event_name,
            event_name_cn: `测试事件${data.event_id || data.game_gid}`,
            source_table: 'ods_test',
            target_table: 'dwd_test'
          })
        });

        if (!eventResponse.ok) {
          const errorText = await eventResponse.text();
          console.error(`Failed to create event: status=${eventResponse.status}, error=${errorText}`);
          return false;
        }
      }

      console.log(`Successfully created test data: game_gid=${data.game_gid}`);
      return true;
    } catch (error) {
      console.error(`Error creating test data for game_gid=${data.game_gid}:`, error);
      return false;
    }
  }

  /**
   * Deletes test data (cleanup)
   *
   * Deletes the specified event using the DELETE /api/events/{event_id} endpoint.
   * Games are not automatically deleted to avoid affecting other tests.
   *
   * @param {Object} data - The test data to delete
   * @param {number} [data.event_id] - The event ID to delete (optional)
   * @param {number} [data.game_gid] - The game GID (optional, only used for logging)
   * @returns {Promise<boolean>} True if deletion succeeded or no event_id provided, false on error
   * @throws {TypeError} If data is not an object
   * @example
   * await manager.cleanupTestData({ event_id: 55, game_gid: 10000147 });
   */
  async cleanupTestData(data) {
    // Input validation
    if (!data || typeof data !== 'object') {
      throw new TypeError('data must be an object');
    }

    try {
      if (data.event_id) {
        const response = await fetch(`${this.apiBaseUrl}/api/events/${data.event_id}`, {
          method: 'DELETE'
        });

        if (!response.ok) {
          console.warn(`Failed to delete event: event_id=${data.event_id}, status=${response.status}`);
          return false;
        }

        console.log(`Successfully deleted test data: event_id=${data.event_id}`);
      }

      return true;
    } catch (error) {
      console.error(`Error cleaning up test data for event_id=${data.event_id}, game_gid=${data.game_gid}:`, error);
      return false;
    }
  }
}
