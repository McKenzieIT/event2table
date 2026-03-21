import { describe, it, expect } from 'vitest';
import {
  validateRequired,
  validateEventName,
  validateGameGid,
  validateUrl,
  validateForm,
  formatDate,
  formatDateTime,
  parseDate,
  getRelativeTime,
  cleanString,
  toCamelCase,
  toSnakeCase,
  truncate,
  highlightKeyword,
  handleApiError,
  isGraphQLSuccess,
  getGraphQLErrors,
  createInitialModalState,
  calculatePagination,
  buildPaginationParams,
  isEmpty,
  safeGet,
  unique,
  groupBy,
  sortBy,
  DEFAULT_PAGINATION,
} from './commonUtils';

describe('commonUtils', () => {
  describe('validateRequired', () => {
    it('should return null for valid value', () => {
      expect(validateRequired('test', 'Field')).toBeNull();
    });

    it('should return error for empty string', () => {
      expect(validateRequired('', 'Field')).toBe('Field不能为空');
    });

    it('should return error for whitespace only', () => {
      expect(validateRequired('   ', 'Field')).toBe('Field不能为空');
    });

    it('should return error for null', () => {
      expect(validateRequired(null, 'Field')).toBe('Field不能为空');
    });

    it('should return error for undefined', () => {
      expect(validateRequired(undefined, 'Field')).toBe('Field不能为空');
    });
  });

  describe('validateEventName', () => {
    it('should return null for valid event name', () => {
      expect(validateEventName('user_login')).toBeNull();
    });

    it('should return error for empty string', () => {
      expect(validateEventName('')).toBe('事件名称（英文）不能为空');
    });

    it('should return error for uppercase letters', () => {
      expect(validateEventName('UserLogin')).toContain('只能包含小写字母和下划线');
    });

    it('should return error for numbers', () => {
      expect(validateEventName('user123')).toContain('只能包含小写字母和下划线');
    });
  });

  describe('validateGameGid', () => {
    it('should return null for valid GID', () => {
      expect(validateGameGid('10000147')).toBeNull();
      expect(validateGameGid(10000147)).toBeNull();
    });

    it('should return error for empty string', () => {
      expect(validateGameGid('')).toBe('游戏GID不能为空');
    });

    it('should return error for non-numeric', () => {
      expect(validateGameGid('abc')).toBe('游戏GID必须是正整数');
    });

    it('should return error for zero', () => {
      expect(validateGameGid(0)).toBe('游戏GID必须是正整数');
    });

    it('should return error for negative number', () => {
      expect(validateGameGid(-1)).toBe('游戏GID必须是正整数');
    });
  });

  describe('validateUrl', () => {
    it('should return null for valid URL', () => {
      expect(validateUrl('https://example.com')).toBeNull();
    });

    it('should return null for empty string (optional)', () => {
      expect(validateUrl('')).toBeNull();
    });

    it('should return error for invalid URL', () => {
      expect(validateUrl('not-a-url')).toBe('请输入有效的URL');
    });
  });

  describe('validateForm', () => {
    it('should validate all fields', () => {
      const data = { name: '', age: 25 };
      const validators = {
        name: (v: any) => (v ? null : 'Name required'),
        age: (v: any) => (v > 0 ? null : 'Age must be positive'),
      };
      const errors = validateForm(data, validators);
      expect(errors.name).toBe('Name required');
      expect(errors.age).toBeUndefined();
    });

    it('should return empty object when all valid', () => {
      const data = { name: 'John', age: 25 };
      const validators = {
        name: (v: any) => (v ? null : 'Name required'),
      };
      const errors = validateForm(data, validators);
      expect(Object.keys(errors)).toHaveLength(0);
    });
  });

  describe('formatDate', () => {
    it('should format date to YYYY-MM-DD', () => {
      const date = new Date(2026, 2, 21);
      expect(formatDate(date)).toBe('2026-03-21');
    });

    it('should handle date string', () => {
      expect(formatDate('2026-03-21')).toBe('2026-03-21');
    });

    it('should pad month and day', () => {
      const date = new Date(2026, 0, 5);
      expect(formatDate(date)).toBe('2026-01-05');
    });
  });

  describe('formatDateTime', () => {
    it('should format datetime to YYYY-MM-DD HH:mm:ss', () => {
      const date = new Date(2026, 2, 21, 14, 30, 45);
      expect(formatDateTime(date)).toBe('2026-03-21 14:30:45');
    });

    it('should pad time components', () => {
      const date = new Date(2026, 0, 1, 1, 5, 9);
      expect(formatDateTime(date)).toBe('2026-01-01 01:05:09');
    });
  });

  describe('parseDate', () => {
    it('should parse valid date string', () => {
      const date = parseDate('2026-03-21');
      expect(date).toBeInstanceOf(Date);
    });

    it('should return null for invalid date', () => {
      const date = parseDate('invalid');
      expect(date).toBeNull();
    });
  });

  describe('getRelativeTime', () => {
    it('should return "刚刚" for recent time', () => {
      const date = new Date();
      expect(getRelativeTime(date)).toBe('刚刚');
    });

    it('should return minutes ago', () => {
      const date = new Date(Date.now() - 30 * 60000);
      expect(getRelativeTime(date)).toBe('30分钟前');
    });

    it('should return hours ago', () => {
      const date = new Date(Date.now() - 2 * 3600000);
      expect(getRelativeTime(date)).toBe('2小时前');
    });

    it('should return days ago', () => {
      const date = new Date(Date.now() - 5 * 86400000);
      expect(getRelativeTime(date)).toBe('5天前');
    });

    it('should return formatted date for old dates', () => {
      const date = new Date(2026, 0, 1);
      expect(getRelativeTime(date)).toBe('2026-01-01');
    });
  });

  describe('cleanString', () => {
    it('should trim whitespace', () => {
      expect(cleanString('  test  ')).toBe('test');
    });

    it('should return null for empty string', () => {
      expect(cleanString('')).toBeNull();
    });

    it('should return null for whitespace only', () => {
      expect(cleanString('   ')).toBeNull();
    });

    it('should return null for null', () => {
      expect(cleanString(null)).toBeNull();
    });

    it('should return null for undefined', () => {
      expect(cleanString(undefined)).toBeNull();
    });

    it('should convert to string', () => {
      expect(cleanString(123)).toBe('123');
    });
  });

  describe('toCamelCase', () => {
    it('should convert snake_case to camelCase', () => {
      expect(toCamelCase('user_name')).toBe('userName');
    });

    it('should convert kebab-case to camelCase', () => {
      expect(toCamelCase('user-name')).toBe('userName');
    });

    it('should convert space separated to camelCase', () => {
      expect(toCamelCase('user name')).toBe('userName');
    });

    it('should handle first letter', () => {
      expect(toCamelCase('UserName')).toBe('userName');
    });
  });

  describe('toSnakeCase', () => {
    it('should convert camelCase to snake_case', () => {
      expect(toSnakeCase('userName')).toBe('user_name');
    });

    it('should handle multiple words', () => {
      expect(toSnakeCase('getUserName')).toBe('get_user_name');
    });
  });

  describe('truncate', () => {
    it('should truncate long text', () => {
      expect(truncate('Very long text here', 10)).toBe('Very lo...');
    });

    it('should not truncate short text', () => {
      expect(truncate('Short', 10)).toBe('Short');
    });

    it('should use custom suffix', () => {
      expect(truncate('Very long text', 10, '***')).toBe('Very lo***');
    });
  });

  describe('highlightKeyword', () => {
    it('should highlight keyword', () => {
      expect(highlightKeyword('test string', 'test')).toBe('<mark>test</mark> string');
    });

    it('should be case insensitive', () => {
      expect(highlightKeyword('TEST string', 'test')).toBe('<mark>TEST</mark> string');
    });

    it('should handle multiple occurrences', () => {
      expect(highlightKeyword('test test test', 'test')).toBe('<mark>test</mark> <mark>test</mark> <mark>test</mark>');
    });

    it('should return original text for empty keyword', () => {
      expect(highlightKeyword('test string', '')).toBe('test string');
    });
  });

  describe('handleApiError', () => {
    it('should extract error message', () => {
      expect(handleApiError({ message: 'Error occurred' })).toBe('Error occurred');
    });

    it('should handle error with errors array', () => {
      expect(handleApiError({ errors: [{ message: 'First error' }] })).toBe('First error');
    });

    it('should handle string error', () => {
      expect(handleApiError('String error')).toBe('String error');
    });

    it('should return default message', () => {
      expect(handleApiError(null)).toBe('操作失败,请稍后重试');
    });
  });

  describe('isGraphQLSuccess', () => {
    it('should return true for successful response', () => {
      expect(isGraphQLSuccess({ ok: true })).toBe(true);
    });

    it('should return true for nested success', () => {
      expect(isGraphQLSuccess({ data: { ok: true } })).toBe(true);
    });

    it('should return false for failed response', () => {
      expect(isGraphQLSuccess({ ok: false })).toBe(false);
    });
  });

  describe('getGraphQLErrors', () => {
    it('should extract errors from response', () => {
      const response = { errors: [{ message: 'Error 1' }, { message: 'Error 2' }] };
      expect(getGraphQLErrors(response)).toEqual(['Error 1', 'Error 2']);
    });

    it('should extract nested errors', () => {
      const response = { data: { errors: [{ message: 'Nested error' }] } };
      expect(getGraphQLErrors(response)).toEqual(['Nested error']);
    });

    it('should return empty array for no errors', () => {
      expect(getGraphQLErrors({})).toEqual([]);
    });
  });

  describe('createInitialModalState', () => {
    it('should create initial state', () => {
      const state = createInitialModalState();
      expect(state.isOpen).toBe(false);
      expect(state.mode).toBe('create');
    });
  });

  describe('calculatePagination', () => {
    it('should calculate pagination info', () => {
      const result = calculatePagination(100, 2, 20);
      expect(result.totalPages).toBe(5);
      expect(result.hasNext).toBe(true);
      expect(result.hasPrev).toBe(true);
      expect(result.offset).toBe(20);
    });

    it('should handle first page', () => {
      const result = calculatePagination(100, 1, 20);
      expect(result.hasPrev).toBe(false);
      expect(result.hasNext).toBe(true);
    });

    it('should handle last page', () => {
      const result = calculatePagination(100, 5, 20);
      expect(result.hasPrev).toBe(true);
      expect(result.hasNext).toBe(false);
    });
  });

  describe('buildPaginationParams', () => {
    it('should build pagination params', () => {
      const params = buildPaginationParams(2, 25);
      expect(params.page).toBe(2);
      expect(params.per_page).toBe(25);
    });

    it('should enforce minimum page', () => {
      const params = buildPaginationParams(0, 20);
      expect(params.page).toBe(1);
    });

    it('should enforce maximum per_page', () => {
      const params = buildPaginationParams(1, 200);
      expect(params.per_page).toBe(100);
    });

    it('should enforce minimum per_page', () => {
      const params = buildPaginationParams(1, 0);
      expect(params.per_page).toBe(1);
    });
  });

  describe('isEmpty', () => {
    it('should return true for null', () => {
      expect(isEmpty(null)).toBe(true);
    });

    it('should return true for undefined', () => {
      expect(isEmpty(undefined)).toBe(true);
    });

    it('should return true for empty string', () => {
      expect(isEmpty('')).toBe(true);
    });

    it('should return true for empty array', () => {
      expect(isEmpty([])).toBe(true);
    });

    it('should return true for empty object', () => {
      expect(isEmpty({})).toBe(true);
    });

    it('should return false for non-empty values', () => {
      expect(isEmpty('test')).toBe(false);
      expect(isEmpty([1])).toBe(false);
      expect(isEmpty({ a: 1 })).toBe(false);
    });
  });

  describe('safeGet', () => {
    it('should get nested value', () => {
      const obj = { a: { b: { c: 'value' } } };
      expect(safeGet(obj, 'a.b.c')).toBe('value');
    });

    it('should return default for missing path', () => {
      const obj = { a: { b: {} } };
      expect(safeGet(obj, 'a.b.c', 'default')).toBe('default');
    });

    it('should return default for null in path', () => {
      const obj = { a: null };
      expect(safeGet(obj, 'a.b', 'default')).toBe('default');
    });

    it('should return default for undefined in path', () => {
      const obj = { a: {} };
      expect(safeGet(obj, 'a.b.c', 'default')).toBe('default');
    });
  });

  describe('unique', () => {
    it('should remove duplicates from array', () => {
      expect(unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3]);
    });

    it('should remove duplicates by key', () => {
      const arr = [
        { id: 1, name: 'a' },
        { id: 2, name: 'b' },
        { id: 1, name: 'c' },
      ];
      expect(unique(arr, 'id')).toEqual([
        { id: 1, name: 'a' },
        { id: 2, name: 'b' },
      ]);
    });
  });

  describe('groupBy', () => {
    it('should group array by key', () => {
      const arr = [
        { type: 'a', value: 1 },
        { type: 'b', value: 2 },
        { type: 'a', value: 3 },
      ];
      const result = groupBy(arr, 'type');
      expect(result.a).toHaveLength(2);
      expect(result.b).toHaveLength(1);
    });
  });

  describe('sortBy', () => {
    it('should sort array in ascending order', () => {
      const arr = [
        { name: 'Charlie' },
        { name: 'Alice' },
        { name: 'Bob' },
      ];
      const result = sortBy(arr, 'name', 'asc');
      expect(result[0].name).toBe('Alice');
      expect(result[2].name).toBe('Charlie');
    });

    it('should sort array in descending order', () => {
      const arr = [
        { name: 'Charlie' },
        { name: 'Alice' },
        { name: 'Bob' },
      ];
      const result = sortBy(arr, 'name', 'desc');
      expect(result[0].name).toBe('Charlie');
      expect(result[2].name).toBe('Alice');
    });
  });

  describe('DEFAULT_PAGINATION', () => {
    it('should have default pagination values', () => {
      expect(DEFAULT_PAGINATION.page).toBe(1);
      expect(DEFAULT_PAGINATION.perPage).toBe(20);
    });
  });
});
