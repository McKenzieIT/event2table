// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * API Validator Utilities Tests
 * 测试API响应验证工具函数的所有功能
 */

import { describe, it, expect } from 'vitest';

import {
  validateApiResponse,
  validateArrayResponse,
  assertApiResponse,
  assertArrayResponse,
  safeParseJSON,
  validateRequiredFields,
  type ValidationResult,
} from './apiValidator';

describe('validateApiResponse', () => {
  describe('with valid responses', () => {
    it('should validate successful API response', () => {
      const response = {
        success: true,
        data: { id: 1, name: 'Test' },
      };

      const result = validateApiResponse(response);

      expect(result.success).toBe(true);
      expect(result.data).toEqual({ id: 1, name: 'Test' });
    });

    it('should validate response with array data', () => {
      const response = {
        success: true,
        data: [1, 2, 3],
      };

      const result = validateApiResponse(response);

      expect(result.success).toBe(true);
      expect(result.data).toEqual([1, 2, 3]);
    });

    it('should validate response with null data', () => {
      const response = {
        success: true,
        data: null,
      };

      const result = validateApiResponse(response);

      expect(result.success).toBe(true);
      expect(result.data).toBeNull();
    });

    it('should validate response with additional fields', () => {
      const response = {
        success: true,
        data: { id: 1 },
        message: 'Success',
        timestamp: 1234567890,
      };

      const result = validateApiResponse(response);

      expect(result.success).toBe(true);
      expect(result.data).toEqual({ id: 1 });
    });
  });

  describe('with invalid responses', () => {
    it('should reject non-object data', () => {
      expect(validateApiResponse(null)).toEqual({
        success: false,
        error: 'API response is not an object',
      });

      expect(validateApiResponse(undefined)).toEqual({
        success: false,
        error: 'API response is not an object',
      });

      expect(validateApiResponse('string')).toEqual({
        success: false,
        error: 'API response is not an object',
      });

      expect(validateApiResponse(123)).toEqual({
        success: false,
        error: 'API response is not an object',
      });
    });

    it('should reject response missing success field', () => {
      const response = {
        data: { id: 1 },
      };

      const result = validateApiResponse(response);

      expect(result.success).toBe(false);
      expect(result.error).toBe('API response missing \'success\' field');
    });

    it('should reject response with success: false', () => {
      const response = {
        success: false,
        message: 'Error occurred',
      };

      const result = validateApiResponse(response);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Error occurred');
    });

    it('should use default error message when success: false without message', () => {
      const response = {
        success: false,
      };

      const result = validateApiResponse(response);

      expect(result.success).toBe(false);
      expect(result.error).toBe('API request failed');
    });

    it('should reject response missing data field', () => {
      const response = {
        success: true,
      };

      const result = validateApiResponse(response);

      expect(result.success).toBe(false);
      expect(result.error).toBe('API response missing \'data\' field');
    });
  });

  describe('with custom API name', () => {
    it('should use custom API name in error messages', () => {
      expect(validateApiResponse(null, 'UserService')).toEqual({
        success: false,
        error: 'UserService response is not an object',
      });

      expect(
        validateApiResponse({ success: true }, 'GameService')
      ).toEqual({
        success: false,
        error: 'GameService response missing \'data\' field',
      });
    });
  });
});

describe('validateArrayResponse', () => {
  describe('with valid array responses', () => {
    it('should validate array response', () => {
      const response = {
        success: true,
        data: [1, 2, 3],
      };

      const result = validateArrayResponse(response);

      expect(result.success).toBe(true);
      expect(result.data).toEqual([1, 2, 3]);
    });

    it('should validate empty array', () => {
      const response = {
        success: true,
        data: [],
      };

      const result = validateArrayResponse(response);

      expect(result.success).toBe(true);
      expect(result.data).toEqual([]);
    });

    it('should validate array of objects', () => {
      const response = {
        success: true,
        data: [{ id: 1 }, { id: 2 }, { id: 3 }],
      };

      const result = validateArrayResponse(response);

      expect(result.success).toBe(true);
      expect(result.data).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }]);
    });
  });

  describe('with invalid array responses', () => {
    it('should reject non-array data', () => {
      const response = {
        success: true,
        data: { id: 1 },
      };

      const result = validateArrayResponse(response);

      expect(result.success).toBe(false);
      expect(result.error).toBe('API response data is not an array');
    });

    it('should reject null data', () => {
      const response = {
        success: true,
        data: null,
      };

      const result = validateArrayResponse(response);

      expect(result.success).toBe(false);
      expect(result.error).toBe('API response data is not an array');
    });

    it('should propagate base validation errors', () => {
      expect(validateArrayResponse(null)).toEqual({
        success: false,
        error: 'API response is not an object',
      });

      expect(
        validateArrayResponse({ success: true })
      ).toEqual({
        success: false,
        error: 'API response missing \'data\' field',
      });
    });
  });

  describe('with custom API name', () => {
    it('should use custom API name in array error messages', () => {
      const response = {
        success: true,
        data: { id: 1 },
      };

      const result = validateArrayResponse(response, 'EventService');

      expect(result.success).toBe(false);
      expect(result.error).toBe('EventService response data is not an array');
    });
  });
});

describe('assertApiResponse', () => {
  describe('with valid responses', () => {
    it('should return data for successful response', () => {
      const response = {
        success: true,
        data: { id: 1, name: 'Test' },
      };

      const result = assertApiResponse(response);

      expect(result).toEqual({ id: 1, name: 'Test' });
    });

    it('should return data for array response', () => {
      const response = {
        success: true,
        data: [1, 2, 3],
      };

      const result = assertApiResponse(response);

      expect(result).toEqual([1, 2, 3]);
    });
  });

  describe('with invalid responses', () => {
    it('should throw error for non-object', () => {
      expect(() => assertApiResponse(null)).toThrow('API response is not an object');
      expect(() => assertApiResponse(undefined)).toThrow('API response is not an object');
    });

    it('should throw error for missing success field', () => {
      const response = { data: { id: 1 } };

      expect(() => assertApiResponse(response)).toThrow('API response missing \'success\' field');
    });

    it('should throw error for success: false', () => {
      const response = {
        success: false,
        message: 'Error occurred',
      };

      expect(() => assertApiResponse(response)).toThrow('Error occurred');
    });

    it('should throw error for missing data field', () => {
      const response = { success: true };

      expect(() => assertApiResponse(response)).toThrow('API response missing \'data\' field');
    });
  });

  describe('with custom API name', () => {
    it('should include API name in error message', () => {
      expect(() => assertApiResponse(null, 'UserService'))
        .toThrow('UserService response is not an object');
    });
  });
});

describe('assertArrayResponse', () => {
  describe('with valid array responses', () => {
    it('should return array data', () => {
      const response = {
        success: true,
        data: [1, 2, 3],
      };

      const result = assertArrayResponse(response);

      expect(result).toEqual([1, 2, 3]);
    });

    it('should return empty array', () => {
      const response = {
        success: true,
        data: [],
      };

      const result = assertArrayResponse(response);

      expect(result).toEqual([]);
    });
  });

  describe('with invalid array responses', () => {
    it('should throw error for non-array data', () => {
      const response = {
        success: true,
        data: { id: 1 },
      };

      expect(() => assertArrayResponse(response)).toThrow('API response data is not an array');
    });

    it('should propagate base validation errors', () => {
      expect(() => assertArrayResponse(null)).toThrow('API response is not an object');
      expect(() => assertArrayResponse({ success: true }))
        .toThrow('API response missing \'data\' field');
    });
  });

  describe('with custom API name', () => {
    it('should include API name in error message', () => {
      const response = {
        success: true,
        data: { id: 1 },
      };

      expect(() => assertArrayResponse(response, 'GameService'))
        .toThrow('GameService response data is not an array');
    });
  });
});

describe('safeParseJSON', () => {
  describe('with valid JSON', () => {
    it('should parse object JSON', () => {
      const jsonString = '{"id":1,"name":"Test"}';

      const result = safeParseJSON(jsonString);

      expect(result.success).toBe(true);
      expect(result.data).toEqual({ id: 1, name: 'Test' });
    });

    it('should parse array JSON', () => {
      const jsonString = '[1,2,3]';

      const result = safeParseJSON(jsonString);

      expect(result.success).toBe(true);
      expect(result.data).toEqual([1, 2, 3]);
    });

    it('should parse string JSON', () => {
      const jsonString = '"test string"';

      const result = safeParseJSON(jsonString);

      expect(result.success).toBe(true);
      expect(result.data).toBe('test string');
    });

    it('should parse number JSON', () => {
      const jsonString = '123';

      const result = safeParseJSON(jsonString);

      expect(result.success).toBe(true);
      expect(result.data).toBe(123);
    });

    it('should parse boolean JSON', () => {
      expect(safeParseJSON('true')).toEqual({ success: true, data: true });
      expect(safeParseJSON('false')).toEqual({ success: true, data: false });
    });

    it('should parse null JSON', () => {
      const result = safeParseJSON('null');

      expect(result.success).toBe(true);
      expect(result.data).toBeNull();
    });
  });

  describe('with invalid JSON', () => {
    it('should handle malformed JSON', () => {
      const result = safeParseJSON('{invalid json}');

      expect(result.success).toBe(false);
      expect(result.error).toContain('API response is not valid JSON');
    });

    it('should handle empty string', () => {
      const result = safeParseJSON('');

      expect(result.success).toBe(false);
      expect(result.error).toContain('API response is not valid JSON');
    });

    it('should handle truncated JSON', () => {
      const result = safeParseJSON('{"id":1');

      expect(result.success).toBe(false);
      expect(result.error).toContain('API response is not valid JSON');
    });
  });

  describe('with custom API name', () => {
    it('should use custom API name in error', () => {
      const result = safeParseJSON('{invalid}', 'UserService');

      expect(result.success).toBe(false);
      expect(result.error).toContain('UserService response is not valid JSON');
    });
  });
});

describe('validateRequiredFields', () => {
  describe('with valid objects', () => {
    it('should validate object with all required fields', () => {
      const obj = { id: 1, name: 'Test', email: 'test@example.com' };
      const requiredFields = ['id', 'name', 'email'];

      const result = validateRequiredFields(obj, requiredFields);

      expect(result.success).toBe(true);
      expect(result.data).toEqual(obj);
    });

    it('should validate object with additional fields', () => {
      const obj = {
        id: 1,
        name: 'Test',
        email: 'test@example.com',
        extra: 'ignored',
      };
      const requiredFields = ['id', 'name'];

      const result = validateRequiredFields(obj, requiredFields);

      expect(result.success).toBe(true);
      expect(result.data).toEqual(obj);
    });

    it('should validate empty required fields list', () => {
      const obj = { id: 1, name: 'Test' };
      const requiredFields: string[] = [];

      const result = validateRequiredFields(obj, requiredFields);

      expect(result.success).toBe(true);
      expect(result.data).toEqual(obj);
    });

    it('should accept fields with null/undefined values', () => {
      const obj = { id: 1, name: null, email: undefined };
      const requiredFields = ['id', 'name', 'email'];

      const result = validateRequiredFields(obj, requiredFields);

      expect(result.success).toBe(true);
    });
  });

  describe('with invalid objects', () => {
    it('should reject non-object', () => {
      expect(validateRequiredFields(null, ['id'])).toEqual({
        success: false,
        error: 'Object is not an object',
      });

      expect(validateRequiredFields(undefined, ['id'])).toEqual({
        success: false,
        error: 'Object is not an object',
      });

      expect(validateRequiredFields('string' as any, ['id'])).toEqual({
        success: false,
        error: 'Object is not an object',
      });
    });

    it('should reject object missing required fields', () => {
      const obj = { id: 1, name: 'Test' };
      const requiredFields = ['id', 'name', 'email'];

      const result = validateRequiredFields(obj, requiredFields);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Object is missing required fields: email');
    });

    it('should reject object missing multiple required fields', () => {
      const obj = { id: 1 };
      const requiredFields = ['id', 'name', 'email', 'phone'];

      const result = validateRequiredFields(obj, requiredFields);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Object is missing required fields: name, email, phone');
    });
  });

  describe('with custom object name', () => {
    it('should use custom object name in error messages', () => {
      const obj = { id: 1 };
      const requiredFields = ['id', 'name'];

      const result = validateRequiredFields(obj, requiredFields, 'User');

      expect(result.success).toBe(false);
      expect(result.error).toBe('User is missing required fields: name');
    });
  });
});

describe('Integration Tests', () => {
  it('should validate complex API response flow', () => {
    const apiResponse = {
      success: true,
      data: [
        { id: 1, name: 'Game 1', gid: '10000147' },
        { id: 2, name: 'Game 2', gid: '10000148' },
      ],
    };

    // Step 1: Validate API response
    const validated = validateArrayResponse(apiResponse, 'GameAPI');
    expect(validated.success).toBe(true);

    // Step 2: Validate each item has required fields
    if (validated.success && validated.data) {
      validated.data.forEach((game: any) => {
        const fieldValidation = validateRequiredFields(game, ['id', 'name', 'gid'], 'Game');
        expect(fieldValidation.success).toBe(true);
      });
    }
  });

  it('should handle error scenarios in API flow', () => {
    // Scenario 1: Invalid JSON
    const jsonResult = safeParseJSON('{invalid}', 'GameAPI');
    expect(jsonResult.success).toBe(false);

    // Scenario 2: Valid JSON but invalid structure
    const validJson = safeParseJSON('{"success": false, "message": "Error"}');
    expect(validJson.success).toBe(true);
    if (validJson.data) {
      const apiResult = validateApiResponse(validJson.data, 'GameAPI');
      expect(apiResult.success).toBe(false);
      expect(apiResult.error).toBe('Error');
    }
  });

  it('should work with assertion functions', () => {
    const response = {
      success: true,
      data: { id: 1, name: 'Test' },
    };

    // Should not throw
    const data = assertApiResponse(response, 'TestAPI');
    expect(data).toEqual({ id: 1, name: 'Test' });

    // Should throw for invalid response
    expect(() => assertApiResponse(null, 'TestAPI')).toThrow();
  });

  it('should validate nested data structures', () => {
    const nestedData = {
      success: true,
      data: {
        user: {
          id: 1,
          name: 'Test User',
          profile: {
            email: 'test@example.com',
          },
        },
      },
    };

    const validated = validateApiResponse(nestedData, 'UserAPI');
    expect(validated.success).toBe(true);

    if (validated.success && validated.data) {
      const fieldValidation = validateRequiredFields(
        (validated.data as any).user,
        ['id', 'name'],
        'User'
      );
      expect(fieldValidation.success).toBe(true);
    }
  });
});
