import { describe, it, expect, beforeEach } from 'vitest';
import { ValidationCache, validationCache } from './validationCache';

describe('ValidationCache', () => {
  let cache: ValidationCache;

  beforeEach(() => {
    cache = new ValidationCache(5);
  });

  describe('get and set', () => {
    it('should set and get validation result', () => {
      cache.set('test-key', 'value1', true);
      const result = cache.get('test-key', 'value1');
      expect(result).toBe(true);
    });

    it('should return undefined for non-existent key', () => {
      const result = cache.get('nonexistent', 'value');
      expect(result).toBeUndefined();
    });

    it('should return undefined when value has changed', () => {
      cache.set('test-key', 'value1', true);
      const result = cache.get('test-key', 'value2');
      expect(result).toBeUndefined();
    });

    it('should update existing key', () => {
      cache.set('test-key', 'value1', true);
      cache.set('test-key', 'value1', false);
      const result = cache.get('test-key', 'value1');
      expect(result).toBe(false);
    });
  });

  describe('LRU eviction', () => {
    it('should evict oldest entry when at capacity', () => {
      cache.set('key1', 'value1', true);
      cache.set('key2', 'value2', true);
      cache.set('key3', 'value3', true);
      cache.set('key4', 'value4', true);
      cache.set('key5', 'value5', true);
      cache.set('key6', 'value6', true); // Should evict key1

      expect(cache.get('key1', 'value1')).toBeUndefined();
      expect(cache.get('key6', 'value6')).toBe(true);
    });

    it('should move accessed key to end', () => {
      cache.set('key1', 'value1', true);
      cache.set('key2', 'value2', true);
      cache.set('key3', 'value3', true);
      
      cache.get('key1', 'value1'); // Access key1
      
      cache.set('key4', 'value4', true);
      cache.set('key5', 'value5', true);
      cache.set('key6', 'value6', true); // Should evict key2

      expect(cache.get('key1', 'value1')).toBe(true);
      expect(cache.get('key2', 'value2')).toBeUndefined();
    });
  });

  describe('clear', () => {
    it('should clear all cached results', () => {
      cache.set('key1', 'value1', true);
      cache.set('key2', 'value2', false);
      cache.clear();
      
      expect(cache.size).toBe(0);
      expect(cache.get('key1', 'value1')).toBeUndefined();
      expect(cache.get('key2', 'value2')).toBeUndefined();
    });
  });

  describe('size', () => {
    it('should return correct cache size', () => {
      expect(cache.size).toBe(0);
      
      cache.set('key1', 'value1', true);
      expect(cache.size).toBe(1);
      
      cache.set('key2', 'value2', true);
      expect(cache.size).toBe(2);
      
      cache.clear();
      expect(cache.size).toBe(0);
    });
  });

  describe('value comparison', () => {
    it('should handle primitive values', () => {
      cache.set('key', 123, true);
      expect(cache.get('key', 123)).toBe(true);
      expect(cache.get('key', 456)).toBeUndefined();
    });

    it('should handle object values', () => {
      const obj1 = { a: 1, b: 2 };
      const obj2 = { a: 1, b: 2 };
      cache.set('key', obj1, true);
      expect(cache.get('key', obj2)).toBe(true);
    });

    it('should handle array values', () => {
      const arr1 = [1, 2, 3];
      const arr2 = [1, 2, 3];
      cache.set('key', arr1, true);
      expect(cache.get('key', arr2)).toBe(true);
    });

    it('should handle null values', () => {
      cache.set('key', null, true);
      expect(cache.get('key', null)).toBe(true);
      expect(cache.get('key', undefined)).toBeUndefined();
    });

    it('should handle string result', () => {
      cache.set('key', 'value', 'error message');
      expect(cache.get('key', 'value')).toBe('error message');
    });
  });

  describe('global instance', () => {
    it('should provide global validation cache instance', () => {
      expect(validationCache).toBeInstanceOf(ValidationCache);
    });

    it('should work with global instance', () => {
      validationCache.set('global-key', 'value', true);
      const result = validationCache.get('global-key', 'value');
      expect(result).toBe(true);
      validationCache.clear();
    });
  });
});
