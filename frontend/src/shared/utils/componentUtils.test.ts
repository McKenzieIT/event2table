// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * Component Utilities Tests
 * 测试组件工具函数的所有功能
 */

import { describe, it, expect } from 'vitest';
import {
  ensureArray,
  safeLength,
  safeFilter,
  safeMap,
  safeIsEmpty,
} from './componentUtils';

describe('ensureArray', () => {
  describe('with array input', () => {
    it('should return the same array', () => {
      const input = [1, 2, 3];
      const result = ensureArray(input);
      expect(result).toBe(input);
      expect(result).toEqual([1, 2, 3]);
    });

    it('should work with empty array', () => {
      const input: number[] = [];
      const result = ensureArray(input);
      expect(result).toBe(input);
      expect(result).toEqual([]);
    });

    it('should work with array of objects', () => {
      const input = [{ id: 1 }, { id: 2 }];
      const result = ensureArray(input);
      expect(result).toBe(input);
      expect(result).toEqual([{ id: 1 }, { id: 2 }]);
    });

    it('should work with array of strings', () => {
      const input = ['a', 'b', 'c'];
      const result = ensureArray(input);
      expect(result).toBe(input);
    });
  });

  describe('with non-array input', () => {
    it('should return default array for null', () => {
      const result = ensureArray<number>(null);
      expect(result).toEqual([]);
    });

    it('should return default array for undefined', () => {
      const result = ensureArray<number>(undefined);
      expect(result).toEqual([]);
    });

    it('should return default array for string', () => {
      const result = ensureArray<number>('test');
      expect(result).toEqual([]);
    });

    it('should return default array for number', () => {
      const result = ensureArray<number[]>(123);
      expect(result).toEqual([]);
    });

    it('should return default array for object', () => {
      const result = ensureArray<number[]>({ key: 'value' });
      expect(result).toEqual([]);
    });
  });

  describe('with custom default value', () => {
    it('should return custom default for null', () => {
      const customDefault = [1, 2, 3];
      const result = ensureArray<number>(null, customDefault);
      expect(result).toEqual(customDefault);
    });

    it('should return custom default for undefined', () => {
      const customDefault = ['a', 'b'];
      const result = ensureArray<string>(undefined, customDefault);
      expect(result).toEqual(customDefault);
    });

    it('should return custom default for non-array', () => {
      const customDefault = [1, 2, 3];
      const result = ensureArray<number>('test', customDefault);
      expect(result).toEqual(customDefault);
    });

    it('should not use custom default when input is array', () => {
      const input = [4, 5, 6];
      const customDefault = [1, 2, 3];
      const result = ensureArray(input, customDefault);
      expect(result).toBe(input);
      expect(result).toEqual([4, 5, 6]);
    });

    it('should work with empty custom default', () => {
      const result = ensureArray<number>(null, []);
      expect(result).toEqual([]);
    });
  });

  describe('type safety', () => {
    it('should preserve type with generic', () => {
      const result: number[] = ensureArray<number>([1, 2, 3]);
      expect(result).toEqual([1, 2, 3]);
    });

    it('should work with complex types', () => {
      interface User {
        id: number;
        name: string;
      }
      const users: User[] = [{ id: 1, name: 'Alice' }];
      const result = ensureArray<User>(users);
      expect(result).toEqual(users);
    });
  });
});

describe('safeLength', () => {
  describe('with array input', () => {
    it('should return array length', () => {
      expect(safeLength([1, 2, 3])).toBe(3);
    });

    it('should return 0 for empty array', () => {
      expect(safeLength([])).toBe(0);
    });

    it('should work with array of objects', () => {
      const users = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];
      expect(safeLength(users)).toBe(4);
    });

    it('should work with array of strings', () => {
      expect(safeLength(['a', 'b', 'c', 'd', 'e'])).toBe(5);
    });
  });

  describe('with non-array input', () => {
    it('should return 0 for null', () => {
      expect(safeLength(null)).toBe(0);
    });

    it('should return 0 for undefined', () => {
      expect(safeLength(undefined)).toBe(0);
    });

    it('should return 0 for string', () => {
      expect(safeLength('test')).toBe(0);
    });

    it('should return 0 for number', () => {
      expect(safeLength(123)).toBe(0);
    });

    it('should return 0 for object', () => {
      expect(safeLength({ key: 'value' })).toBe(0);
    });

    it('should return 0 for boolean', () => {
      expect(safeLength(true)).toBe(0);
      expect(safeLength(false)).toBe(0);
    });
  });

  describe('edge cases', () => {
    it('should handle large arrays', () => {
      const largeArray = Array(10000).fill(0);
      expect(safeLength(largeArray)).toBe(10000);
    });

    it('should handle sparse arrays', () => {
      const sparseArray: number[] = [];
      sparseArray[10] = 1;
      expect(safeLength(sparseArray)).toBe(11);
    });
  });
});

describe('safeFilter', () => {
  describe('with array input', () => {
    it('should filter array based on predicate', () => {
      const result = safeFilter([1, 2, 3, 4, 5], (x) => x % 2 === 0);
      expect(result).toEqual([2, 4]);
    });

    it('should filter array of objects', () => {
      const users = [
        { id: 1, active: true },
        { id: 2, active: false },
        { id: 3, active: true },
      ];
      const result = safeFilter(users, (user) => user.active);
      expect(result).toEqual([
        { id: 1, active: true },
        { id: 3, active: true },
      ]);
    });

    it('should pass index to predicate', () => {
      const result = safeFilter([10, 20, 30], (value, index) => index > 0);
      expect(result).toEqual([20, 30]);
    });

    it('should pass array to predicate', () => {
      const result = safeFilter([1, 2, 3, 4], (value, index, array) => {
        return array.length === 4 && value === 4;
      });
      expect(result).toEqual([4]);
    });

    it('should return empty array when no elements match', () => {
      const result = safeFilter([1, 3, 5], (x) => x % 2 === 0);
      expect(result).toEqual([]);
    });

    it('should return all elements when all match', () => {
      const result = safeFilter([2, 4, 6], (x) => x % 2 === 0);
      expect(result).toEqual([2, 4, 6]);
    });
  });

  describe('with non-array input', () => {
    it('should return empty array for null', () => {
      const result = safeFilter(null, (x) => x > 0);
      expect(result).toEqual([]);
    });

    it('should return empty array for undefined', () => {
      const result = safeFilter(undefined, (x) => x > 0);
      expect(result).toEqual([]);
    });

    it('should return empty array for string', () => {
      const result = safeFilter('test' as any, (x: any) => x > 0);
      expect(result).toEqual([]);
    });

    it('should return empty array for number', () => {
      const result = safeFilter(123 as any, (x: any) => x > 0);
      expect(result).toEqual([]);
    });
  });

  describe('type safety', () => {
    it('should work with generic types', () => {
      interface Product {
        id: number;
        price: number;
      }
      const products: Product[] = [
        { id: 1, price: 100 },
        { id: 2, price: 200 },
        { id: 3, price: 50 },
      ];
      const result = safeFilter(products, (product) => product.price > 100);
      expect(result).toEqual([{ id: 2, price: 200 }]);
    });
  });
});

describe('safeMap', () => {
  describe('with array input', () => {
    it('should map array based on mapper function', () => {
      const result = safeMap([1, 2, 3], (x) => x * 2);
      expect(result).toEqual([2, 4, 6]);
    });

    it('should map array of objects', () => {
      const users = [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' },
      ];
      const result = safeMap(users, (user) => user.name);
      expect(result).toEqual(['Alice', 'Bob']);
    });

    it('should pass index to mapper', () => {
      const result = safeMap([10, 20, 30], (value, index) => `${index}: ${value}`);
      expect(result).toEqual(['0: 10', '1: 20', '2: 30']);
    });

    it('should pass array to mapper', () => {
      const result = safeMap([1, 2, 3], (value, index, array) => value + array.length);
      expect(result).toEqual([4, 5, 6]);
    });

    it('should change type during mapping', () => {
      const result = safeMap([1, 2, 3], (x) => x.toString());
      expect(result).toEqual(['1', '2', '3']);
    });

    it('should handle complex transformations', () => {
      const users = [
        { firstName: 'John', lastName: 'Doe' },
        { firstName: 'Jane', lastName: 'Smith' },
      ];
      const result = safeMap(users, (user) => `${user.firstName} ${user.lastName}`);
      expect(result).toEqual(['John Doe', 'Jane Smith']);
    });
  });

  describe('with non-array input', () => {
    it('should return empty array for null', () => {
      const result = safeMap(null, (x) => x * 2);
      expect(result).toEqual([]);
    });

    it('should return empty array for undefined', () => {
      const result = safeMap(undefined, (x) => x * 2);
      expect(result).toEqual([]);
    });

    it('should return empty array for string', () => {
      const result = safeMap('test' as any, (x: any) => x * 2);
      expect(result).toEqual([]);
    });

    it('should return empty array for number', () => {
      const result = safeMap(123 as any, (x: any) => x * 2);
      expect(result).toEqual([]);
    });
  });

  describe('type safety', () => {
    it('should support type transformation', () => {
      const numbers = [1, 2, 3, 4, 5];
      const result: string[] = safeMap(numbers, (n) => `Number: ${n}`);
      expect(result).toEqual(['Number: 1', 'Number: 2', 'Number: 3', 'Number: 4', 'Number: 5']);
    });

    it('should work with complex generic types', () => {
      interface Input {
        value: number;
      }
      interface Output {
        doubled: number;
      }
      const inputs: Input[] = [{ value: 10 }, { value: 20 }];
      const result: Output[] = safeMap(inputs, (input) => ({ doubled: input.value * 2 }));
      expect(result).toEqual([{ doubled: 20 }, { doubled: 40 }]);
    });
  });
});

describe('safeIsEmpty', () => {
  describe('with array input', () => {
    it('should return true for empty array', () => {
      expect(safeIsEmpty([])).toBe(true);
    });

    it('should return false for non-empty array', () => {
      expect(safeIsEmpty([1])).toBe(false);
      expect(safeIsEmpty([1, 2, 3])).toBe(false);
    });

    it('should work with array of objects', () => {
      expect(safeIsEmpty([{ id: 1 }])).toBe(false);
    });

    it('should work with array containing null/undefined', () => {
      expect(safeIsEmpty([null, undefined])).toBe(false);
    });

    it('should work with array containing zeros', () => {
      expect(safeIsEmpty([0])).toBe(false);
    });

    it('should work with array containing empty strings', () => {
      expect(safeIsEmpty([''])).toBe(false);
    });
  });

  describe('with non-array input', () => {
    it('should return true for null', () => {
      expect(safeIsEmpty(null)).toBe(true);
    });

    it('should return true for undefined', () => {
      expect(safeIsEmpty(undefined)).toBe(true);
    });

    it('should return true for string', () => {
      expect(safeIsEmpty('test')).toBe(true);
    });

    it('should return true for number', () => {
      expect(safeIsEmpty(123)).toBe(true);
    });

    it('should return true for object', () => {
      expect(safeIsEmpty({ key: 'value' })).toBe(true);
    });

    it('should return true for boolean', () => {
      expect(safeIsEmpty(true)).toBe(true);
      expect(safeIsEmpty(false)).toBe(true);
    });
  });

  describe('edge cases', () => {
    it('should handle large arrays', () => {
      const largeArray = Array(10000).fill(0);
      expect(safeIsEmpty(largeArray)).toBe(false);
    });

    it('should handle sparse arrays', () => {
      const sparseArray: number[] = [];
      sparseArray[10] = 1;
      expect(safeIsEmpty(sparseArray)).toBe(false);
    });
  });
});

describe('Integration Tests', () => {
  it('should chain operations safely', () => {
    const data = [1, 2, 3, 4, 5];

    // Filter even numbers, double them, check if not empty
    const filtered = safeFilter(data, (x) => x % 2 === 0);
    const mapped = safeMap(filtered, (x) => x * 2);
    const isEmpty = safeIsEmpty(mapped);

    expect(filtered).toEqual([2, 4]);
    expect(mapped).toEqual([4, 8]);
    expect(isEmpty).toBe(false);
  });

  it('should handle null gracefully in chain', () => {
    const data = null;

    const filtered = safeFilter(data, (x: any) => x > 0);
    const mapped = safeMap(filtered, (x: any) => x * 2);
    const isEmpty = safeIsEmpty(mapped);

    expect(filtered).toEqual([]);
    expect(mapped).toEqual([]);
    expect(isEmpty).toBe(true);
  });

  it('should work with complex data structures', () => {
    interface User {
      id: number;
      name: string;
      active: boolean;
    }

    const users: User[] = [
      { id: 1, name: 'Alice', active: true },
      { id: 2, name: 'Bob', active: false },
      { id: 3, name: 'Charlie', active: true },
    ];

    // Filter active users and get their names
    const activeUsers = safeFilter(users, (user) => user.active);
    const names = safeMap(activeUsers, (user) => user.name);

    expect(names).toEqual(['Alice', 'Charlie']);
    expect(safeLength(names)).toBe(2);
  });

  it('should handle array-like objects', () => {
    const arrayLike = { 0: 'a', 1: 'b', 2: 'c', length: 3 } as any;

    expect(safeIsEmpty(arrayLike)).toBe(true); // Not a real array
    expect(safeLength(arrayLike)).toBe(0);
  });

  it('should work with typed arrays', () => {
    const int8Array = new Int8Array([1, 2, 3]);

    // Typed arrays are not regular arrays, so these should return default values
    expect(safeIsEmpty(int8Array)).toBe(true);
    expect(safeLength(int8Array)).toBe(0);
  });
});
