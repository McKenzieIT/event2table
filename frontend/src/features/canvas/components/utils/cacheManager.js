/**
 * Cache Manager Utility
 * Provides localStorage wrapper with auto-expiration and space management
 *
 * Features:
 * - Auto-expiration (default 1 hour)
 * - QuotaExceededError handling
 * - Storage space management
 * - Cache statistics
 *
 * @version 1.0.0
 * @date 2026-01-29
 */

/**
 * Cache Manager Class
 */
class CacheManager {
  constructor(prefix = 'dwd_generator_canvas_') {
    this.prefix = prefix;
    this.DEFAULT_DURATION = 3600000; // 1 hour in milliseconds
  }

  /**
   * Set cache with expiration
   * @param {string} key - Cache key
   * @param {*} data - Data to cache
   * @param {number} duration - Cache duration in milliseconds (default: 1 hour)
   * @returns {boolean} Success status
   */
  set(key, data, duration = this.DEFAULT_DURATION) {
    try {
      const cacheData = {
        data,
        timestamp: Date.now(),
        duration
      };

      const cacheString = JSON.stringify(cacheData);

      localStorage.setItem(
        this._getKey(key),
        cacheString
      );

      return true;
    } catch (e) {
      if (e.name === 'QuotaExceededError') {
        this.clear();
        try {
          localStorage.setItem(this._getKey(key), JSON.stringify({
            data,
            timestamp: Date.now(),
            duration
          }));
          return true;
        } catch (retryError) {
          console.error('[CacheManager] Still cannot save after clearing:', retryError);
          return false;
        }
      }
      console.error('[CacheManager] Set error:', e);
      return false;
    }
  }

  /**
   * Get cached data (returns null if not exists or expired)
   * @param {string} key - Cache key
   * @returns {*} Cached data or null
   */
  get(key) {
    try {
      const cached = localStorage.getItem(this._getKey(key));
      if (!cached) return null;

      const cacheData = JSON.parse(cached);
      const now = Date.now();

      // Check if expired
      if (now - cacheData.timestamp > cacheData.duration) {
        this.remove(key);
        return null;
      }

      return cacheData.data;
    } catch (e) {
      console.error('[CacheManager] Get error:', e);
      return null;
    }
  }

  /**
   * Check if cache exists and is valid
   * @param {string} key - Cache key
   * @returns {boolean} True if cache exists and is not expired
   */
  has(key) {
    return this.get(key) !== null;
  }

  /**
   * Remove specific cache
   * @param {string} key - Cache key
   */
  remove(key) {
    localStorage.removeItem(this._getKey(key));
  }

  /**
   * Clear all caches with the prefix
   * @returns {number} Number of items cleared
   */
  clear() {
    const keys = Object.keys(localStorage);
    let cleared = 0;

    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        localStorage.removeItem(key);
        cleared++;
      }
    });

    return cleared;
  }

  /**
   * Clear expired caches
   * @returns {number} Number of expired items removed
   */
  clearExpired() {
    const keys = Object.keys(localStorage);
    let cleared = 0;
    const now = Date.now();

    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        try {
          const cached = localStorage.getItem(key);
          if (cached) {
            const cacheData = JSON.parse(cached);
            if (now - cacheData.timestamp > cacheData.duration) {
              localStorage.removeItem(key);
              cleared++;
            }
          }
        } catch (e) {
          // Invalid cache entry, remove it
          localStorage.removeItem(key);
          cleared++;
        }
      }
    });

    return cleared;
  }

  /**
   * Check if storage space is available
   * @returns {boolean} True if storage space is available
   */
  checkQuota() {
    try {
      const testKey = this._getKey('__storage_test__');
      const testValue = 'x'.repeat(1024 * 100); // 100KB
      localStorage.setItem(testKey, testValue);
      localStorage.removeItem(testKey);
      return true;
    } catch (e) {
      return false;
    }
  }

  /**
   * Get cache statistics
   * @returns {Object} Cache statistics
   */
  getStats() {
    const keys = Object.keys(localStorage).filter(k => k.startsWith(this.prefix));
    const items = keys.map(key => {
      const value = localStorage.getItem(key);
      const size = new Blob([value]).size;
      return { key, size };
    });

    const totalSize = items.reduce((sum, item) => sum + item.size, 0);

    return {
      count: items.length,
      totalSize,
      totalSizeKB: (totalSize / 1024).toFixed(2),
      totalSizeMB: (totalSize / 1024 / 1024).toFixed(2),
      items
    };
  }

  /**
   * Get all cache keys (without prefix)
   * @returns {Array<string>} Array of cache keys
   */
  keys() {
    const allKeys = Object.keys(localStorage);
    return allKeys
      .filter(k => k.startsWith(this.prefix))
      .map(k => k.substring(this.prefix.length));
  }

  /**
   * Get cache size for a specific key
   * @param {string} key - Cache key
   * @returns {number} Size in bytes, or 0 if not exists
   */
  getSize(key) {
    try {
      const cached = localStorage.getItem(this._getKey(key));
      if (!cached) return 0;
      return new Blob([cached]).size;
    } catch (e) {
      return 0;
    }
  }

  /**
   * Format size for display
   * @private
   */
  _formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }

  /**
   * Get full localStorage key with prefix
   * @private
   */
  _getKey(key) {
    return `${this.prefix}${key}`;
  }
}

// Singleton export
const cacheManager = new CacheManager();
export default cacheManager;
export { cacheManager, CacheManager };
