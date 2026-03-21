/**
 * Validation Cache Utility
 * 
 * Caches validation results to avoid redundant validation calls.
 * Uses LRU (Least Recently Used) eviction strategy.
 */

export class ValidationCache {
  private cache: Map<string, { value: unknown; result: boolean | string }>;
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  /**
   * Get cached validation result
   * Returns undefined if not cached or value has changed
   */
  get(key: string, value: unknown): boolean | string | undefined {
    const cached = this.cache.get(key);
    if (cached && this.isEqual(cached.value, value)) {
      // Move to end (most recently used)
      this.cache.delete(key);
      this.cache.set(key, cached);
      return cached.result;
    }
    return undefined;
  }

  /**
   * Set validation result in cache
   */
  set(key: string, value: unknown, result: boolean | string): void {
    // Remove if exists (to update position)
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    
    // Evict oldest if at capacity
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey !== undefined) {
        this.cache.delete(firstKey);
      }
    }
    
    this.cache.set(key, { value, result });
  }

  /**
   * Clear all cached results
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache size
   */
  get size(): number {
    return this.cache.size;
  }

  /**
   * Compare two values for equality
   * Uses JSON serialization for deep comparison
   */
  private isEqual(a: unknown, b: unknown): boolean {
    if (a === b) return true;
    if (typeof a !== typeof b) return false;
    if (a === null || b === null) return a === b;
    
    // Fast path for primitives
    if (typeof a !== 'object' && typeof b !== 'object') {
      return a === b;
    }
    
    // Deep comparison for objects/arrays
    try {
      return JSON.stringify(a) === JSON.stringify(b);
    } catch {
      return false;
    }
  }
}

/**
 * Global validation cache instance
 */
export const validationCache = new ValidationCache();
