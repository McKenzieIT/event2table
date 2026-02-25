interface CacheData<T> {
  data: T;
  timestamp: number;
  duration: number;
}

interface CacheStats {
  count: number;
  totalSize: number;
  totalSizeKB: string;
  totalSizeMB: string;
  items: { key: string; size: number }[];
}

class CacheManager {
  private prefix: string;
  private DEFAULT_DURATION: number;

  constructor(prefix = 'dwd_generator_canvas_') {
    this.prefix = prefix;
    this.DEFAULT_DURATION = 3600000;
  }

  set<T>(key: string, data: T, duration: number = this.DEFAULT_DURATION): boolean {
    try {
      const cacheData: CacheData<T> = {
        data,
        timestamp: Date.now(),
        duration
      };

      const cacheString = JSON.stringify(cacheData);
      localStorage.setItem(this._getKey(key), cacheString);
      return true;
    } catch (e) {
      if (e instanceof DOMException && e.name === 'QuotaExceededError') {
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

  get<T>(key: string): T | null {
    try {
      const cached = localStorage.getItem(this._getKey(key));
      if (!cached) return null;

      const cacheData = JSON.parse(cached) as CacheData<T>;
      const now = Date.now();

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

  has(key: string): boolean {
    return this.get(key) !== null;
  }

  remove(key: string): void {
    localStorage.removeItem(this._getKey(key));
  }

  clear(): number {
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

  clearExpired(): number {
    const keys = Object.keys(localStorage);
    let cleared = 0;
    const now = Date.now();

    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        try {
          const cached = localStorage.getItem(key);
          if (cached) {
            const cacheData = JSON.parse(cached) as CacheData<unknown>;
            if (now - cacheData.timestamp > cacheData.duration) {
              localStorage.removeItem(key);
              cleared++;
            }
          }
        } catch {
          localStorage.removeItem(key);
          cleared++;
        }
      }
    });

    return cleared;
  }

  checkQuota(): boolean {
    try {
      const testKey = this._getKey('__storage_test__');
      const testValue = 'x'.repeat(1024 * 100);
      localStorage.setItem(testKey, testValue);
      localStorage.removeItem(testKey);
      return true;
    } catch {
      return false;
    }
  }

  getStats(): CacheStats {
    const keys = Object.keys(localStorage).filter(k => k.startsWith(this.prefix));
    const items = keys.map(key => {
      const value = localStorage.getItem(key);
      const size = value ? new Blob([value]).size : 0;
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

  keys(): string[] {
    const allKeys = Object.keys(localStorage);
    return allKeys
      .filter(k => k.startsWith(this.prefix))
      .map(k => k.substring(this.prefix.length));
  }

  getSize(key: string): number {
    try {
      const cached = localStorage.getItem(this._getKey(key));
      if (!cached) return 0;
      return new Blob([cached]).size;
    } catch {
      return 0;
    }
  }

  private _formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }

  private _getKey(key: string): string {
    return `${this.prefix}${key}`;
  }
}

const cacheManager = new CacheManager();
export default cacheManager;
export { cacheManager, CacheManager };
