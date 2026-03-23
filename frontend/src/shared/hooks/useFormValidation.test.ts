import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@test/test-utils';
import { useFormValidation } from './useFormValidation';

describe('useFormValidation', () => {
  describe('required validation', () => {
    it('should validate required field', () => {
      const initialValues = { name: '', age: 25 };
      const rules = {
        name: { required: true },
        age: { required: true },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.name).toBe('此字段为必填项');
      expect(result.current.errors.age).toBeNull();
    });

    it('should validate required field with custom message', () => {
      const initialValues = { name: '' };
      const rules = {
        name: { required: true, message: 'Name is required' },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.name).toBe('Name is required');
    });
  });

  describe('minLength validation', () => {
    it('should validate minLength', () => {
      const initialValues = { username: 'ab' };
      const rules = {
        username: { minLength: 3 },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.username).toBe('最少3个字符');
    });

    it('should pass minLength when valid', () => {
      const initialValues = { username: 'abc' };
      const rules = {
        username: { minLength: 3 },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.username).toBeNull();
    });
  });

  describe('maxLength validation', () => {
    it('should validate maxLength', () => {
      const initialValues = { username: 'abcdef' };
      const rules = {
        username: { maxLength: 5 },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.username).toBe('最多5个字符');
    });

    it('should pass maxLength when valid', () => {
      const initialValues = { username: 'abc' };
      const rules = {
        username: { maxLength: 5 },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.username).toBeNull();
    });
  });

  describe('pattern validation', () => {
    it('should validate pattern', () => {
      const initialValues = { email: 'invalid-email' };
      const rules = {
        email: { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.email).toBe('格式不正确');
    });

    it('should pass pattern when valid', () => {
      const initialValues = { email: 'test@example.com' };
      const rules = {
        email: { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.email).toBeNull();
    });
  });

  describe('validateAll', () => {
    it('should validate all fields and return true if valid', () => {
      const initialValues = { name: 'John', age: 25 };
      const rules = {
        name: { required: true },
        age: { required: true },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      const isValid = act(() => {
        return result.current.validateAll();
      });

      expect(isValid).toBe(true);
      expect(result.current.errors.name).toBeNull();
      expect(result.current.errors.age).toBeNull();
    });

    it('should validate all fields and return false if invalid', () => {
      const initialValues = { name: '', age: 25 };
      const rules = {
        name: { required: true },
        age: { required: true },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      const isValid = act(() => {
        return result.current.validateAll();
      });

      expect(isValid).toBe(false);
      expect(result.current.errors.name).toBe('此字段为必填项');
    });

    it('should mark all fields as touched', () => {
      const initialValues = { name: 'John', age: 25 };
      const rules = {
        name: { required: true },
        age: { required: true },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.touched.name).toBe(true);
      expect(result.current.touched.age).toBe(true);
    });
  });

  describe('handleBlur', () => {
    it('should validate field on blur', () => {
      const initialValues = { name: '' };
      const rules = {
        name: { required: true },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.handleBlur('name');
      });

      expect(result.current.touched.name).toBe(true);
      expect(result.current.errors.name).toBe('此字段为必填项');
    });

    it('should not validate if field is valid', () => {
      const initialValues = { name: 'John' };
      const rules = {
        name: { required: true },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.handleBlur('name');
      });

      expect(result.current.touched.name).toBe(true);
      expect(result.current.errors.name).toBeNull();
    });
  });

  describe('clearErrors', () => {
    it('should clear all errors', () => {
      const initialValues = { name: '', age: 25 };
      const rules = {
        name: { required: true },
        age: { required: true },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
        result.current.clearErrors();
      });

      expect(result.current.errors.name).toBeNull();
      expect(result.current.errors.age).toBeNull();
      expect(result.current.touched.name).toBe(false);
      expect(result.current.touched.age).toBe(false);
    });
  });

  describe('setErrors and setTouched', () => {
    it('should allow manual error setting', () => {
      const initialValues = { name: '' };
      const rules = {};

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.setErrors({ name: 'Custom error' });
      });

      expect(result.current.errors.name).toBe('Custom error');
    });

    it('should allow manual touched setting', () => {
      const initialValues = { name: '' };
      const rules = {};

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.setTouched({ name: true });
      });

      expect(result.current.touched.name).toBe(true);
    });
  });

  describe('combined validations', () => {
    it('should handle multiple validation rules', () => {
      const initialValues = { username: 'ab' };
      const rules = {
        username: {
          required: true,
          minLength: 3,
          maxLength: 10,
          pattern: /^[a-z]+$/,
        },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.username).toBe('最少3个字符');
    });

    it('should validate in order', () => {
      const initialValues = { username: '' };
      const rules = {
        username: {
          required: true,
          minLength: 3,
          maxLength: 10,
        },
      };

      const { result } = renderHook(() =>
        useFormValidation(initialValues, rules)
      );

      act(() => {
        result.current.validateAll();
      });

      expect(result.current.errors.username).toBe('此字段为必填项');
    });
  });
});
