/**
 * Test Data Fixtures
 * Phase 3: Automated E2E Testing
 *
 * Provides test data generation and fixtures for E2E tests.
 * Uses GID range 90000000-99999999 to avoid production data conflicts.
 */

/**
 * Test data for games
 */
export const testData = {
  games: {
    valid: {
      gid: 90000001,
      name: 'E2E测试游戏',
      ods_db: 'ieu_ods'
    },
    duplicate: {
      gid: 10000147, // STAR001 - should fail
      name: '重复GID测试',
      ods_db: 'ieu_ods'
    },
    invalidGid: {
      gid: -1,
      name: '无效GID测试',
      ods_db: 'ieu_ods'
    },
    emptyName: {
      gid: 90000002,
      name: '',
      ods_db: 'ieu_ods'
    }
  },

  events: {
    valid: {
      event_name: 'test.event.e2e',
      event_name_cn: 'E2E测试事件',
      game_gid: 90000001
    },
    emptyName: {
      event_name: '',
      event_name_cn: '',
      game_gid: 90000001
    }
  },

  credentials: {
    validUser: {
      username: 'e2e-test-user',
      password: 'TestPassword123!'
    }
  }
};

/**
 * Generate a unique test GID in the safe range (90000000-99999999)
 * @returns {number} A unique test GID
 */
export const generateTestGid = () => {
  return Math.floor(Math.random() * 10000000) + 90000000;
};

/**
 * Generate test game data with random GID
 * @param {Object} overrides - Optional data overrides
 * @returns {Object} Test game data
 */
export const generateTestGameData = (overrides = {}) => {
  const gid = generateTestGid();
  return {
    gid: gid,
    name: `测试游戏_${gid}`,
    ods_db: 'ieu_ods',
    ...overrides
  };
};

/**
 * Generate test event data
 * @param {Object} overrides - Optional data overrides
 * @returns {Object} Test event data
 */
export const generateTestData = (overrides = {}) => {
  return {
    event_name: `test.event.${Date.now()}`,
    event_name_cn: `测试事件_${Date.now()}`,
    game_gid: generateTestGid(),
    ...overrides
  };
};

/**
 * Wait helper for dynamic content
 * @param {number} ms - Milliseconds to wait
 */
export const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Retry helper for flaky operations
 * @param {Function} fn - Function to retry
 * @param {number} maxRetries - Maximum retry attempts
 * @param {number} delay - Delay between retries in ms
 */
export const retry = async (fn, maxRetries = 3, delay = 1000) => {
  let lastError;
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (i < maxRetries - 1) {
        await wait(delay);
      }
    }
  }
  throw lastError;
};

/**
 * Cleanup helper - removes test data after test
 * Note: This is a placeholder. Implement based on your cleanup strategy.
 * @param {string} type - Data type ('game', 'event', etc.)
 * @param {number} gid - GID to cleanup
 */
export const cleanupTestData = async (type, gid) => {
  // Implementation depends on your cleanup strategy:
  // Option 1: Direct database cleanup
  // Option 2: API call to delete
  // Option 3: Leave data for debugging, clean periodically
  console.log(`Cleanup ${type} with GID ${gid}`);
};
