// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * Validation Utilities Tests
 * 测试表单验证工具函数的所有功能
 */

import { describe, it, expect } from 'vitest';
import {
  validationRules,
  gameValidationRules,
  validateField,
  validateAll,
  createFieldValidator,
  type ValidatorFn,
  type ValidationRuleItem,
  type ValidationResult,
} from './validationUtils';

describe('validationRules', () => {
  describe('required', () => {
    it('should return error for empty string', () => {
      expect(validationRules.required('')).toBe('此字段不能为空');
    });

    it('should return error for whitespace only', () => {
      expect(validationRules.required('   ')).toBe('此字段不能为空');
    });

    it('should return error for null', () => {
      expect(validationRules.required(null)).toBe('此字段不能为空');
    });

    it('should return error for undefined', () => {
      expect(validationRules.required(undefined)).toBe('此字段不能为空');
    });

    it('should return null for valid string', () => {
      expect(validationRules.required('valid')).toBeNull();
    });

    it('should return null for zero', () => {
      expect(validationRules.required(0)).toBeNull();
    });

    it('should return null for false', () => {
      expect(validationRules.required(false)).toBeNull();
    });

    it('should use custom error message', () => {
      expect(validationRules.required('', undefined, 'Custom message')).toBe('Custom message');
    });
  });

  describe('minLength', () => {
    it('should return error for string shorter than min', () => {
      expect(validationRules.minLength('ab', 3)).toBe('至少需要3个字符');
    });

    it('should return null for string equal to min', () => {
      expect(validationRules.minLength('abc', 3)).toBeNull();
    });

    it('should return null for string longer than min', () => {
      expect(validationRules.minLength('abcd', 3)).toBeNull();
    });

    it('should return null for non-string value', () => {
      expect(validationRules.minLength(null, 3)).toBeNull();
      expect(validationRules.minLength(123, 3)).toBeNull();
      expect(validationRules.minLength(undefined, 3)).toBeNull();
    });

    it('should use custom error message', () => {
      expect(validationRules.minLength('ab', 3, 'Too short')).toBe('Too short');
    });
  });

  describe('maxLength', () => {
    it('should return error for string longer than max', () => {
      expect(validationRules.maxLength('abcd', 3)).toBe('最多3个字符');
    });

    it('should return null for string equal to max', () => {
      expect(validationRules.maxLength('abc', 3)).toBeNull();
    });

    it('should return null for string shorter than max', () => {
      expect(validationRules.maxLength('ab', 3)).toBeNull();
    });

    it('should return null for non-string value', () => {
      expect(validationRules.maxLength(null, 3)).toBeNull();
      expect(validationRules.maxLength(123, 3)).toBeNull();
      expect(validationRules.maxLength(undefined, 3)).toBeNull();
    });

    it('should use custom error message', () => {
      expect(validationRules.maxLength('abcd', 3, 'Too long')).toBe('Too long');
    });
  });

  describe('pattern', () => {
    it('should return error when pattern does not match', () => {
      expect(validationRules.pattern('abc', /^\d+$/)).toBe('格式不正确');
    });

    it('should return null when pattern matches', () => {
      expect(validationRules.pattern('123', /^\d+$/)).toBeNull();
    });

    it('should return null for non-string value', () => {
      expect(validationRules.pattern(null, /^\d+$/)).toBeNull();
      expect(validationRules.pattern(123, /^\d+$/)).toBeNull();
      expect(validationRules.pattern(undefined, /^\d+$/)).toBeNull();
    });

    it('should use custom error message', () => {
      expect(validationRules.pattern('abc', /^\d+$/, 'Numbers only')).toBe('Numbers only');
    });

    it('should support complex patterns', () => {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      expect(validationRules.pattern('test@example.com', emailPattern)).toBeNull();
      expect(validationRules.pattern('invalid', emailPattern)).toBe('格式不正确');
    });
  });

  describe('number', () => {
    it('should return error for non-numeric string', () => {
      expect(validationRules.number('abc')).toBe('必须是数字');
    });

    it('should return null for numeric string', () => {
      expect(validationRules.number('123')).toBeNull();
    });

    it('should return null for non-string value', () => {
      expect(validationRules.number(null)).toBeNull();
      expect(validationRules.number(123)).toBeNull();
      expect(validationRules.number(undefined)).toBeNull();
    });

    it('should return null for empty string', () => {
      expect(validationRules.number('')).toBeNull();
    });

    it('should use custom error message', () => {
      expect(validationRules.number('abc', undefined, 'Invalid number')).toBe('Invalid number');
    });
  });

  describe('email', () => {
    it('should return error for invalid email', () => {
      expect(validationRules.email('invalid')).toBe('邮箱格式不正确');
      expect(validationRules.email('test@')).toBe('邮箱格式不正确');
      expect(validationRules.email('@example.com')).toBe('邮箱格式不正确');
      expect(validationRules.email('test@.com')).toBe('邮箱格式不正确');
    });

    it('should return null for valid email', () => {
      expect(validationRules.email('test@example.com')).toBeNull();
      expect(validationRules.email('user.name@domain.co.uk')).toBeNull();
      expect(validationRules.email('test+tag@example.com')).toBeNull();
    });

    it('should return null for non-string value', () => {
      expect(validationRules.email(null)).toBeNull();
      expect(validationRules.email(123)).toBeNull();
      expect(validationRules.email(undefined)).toBeNull();
    });

    it('should return null for empty string', () => {
      expect(validationRules.email('')).toBeNull();
    });

    it('should use custom error message', () => {
      expect(validationRules.email('invalid', undefined, 'Invalid email')).toBe('Invalid email');
    });
  });
});

describe('validateField', () => {
  it('should return null when no rules provided', () => {
    expect(validateField('test')).toBeNull();
    expect(validateField('test', undefined)).toBeNull();
    expect(validateField('test', null as any)).toBeNull();
  });

  it('should return null when rules array is empty', () => {
    expect(validateField('test', [])).toBeNull();
  });

  it('should return first error encountered', () => {
    const rules: ValidationRuleItem[] = [
      { validator: validationRules.required, message: 'Required' },
      { validator: validationRules.minLength, param: 5, message: 'Too short' },
      { validator: validationRules.maxLength, param: 10, message: 'Too long' },
    ];

    expect(validateField('', rules)).toBe('Required');
  });

  it('should return null when all rules pass', () => {
    const rules: ValidationRuleItem[] = [
      { validator: validationRules.required },
      { validator: validationRules.minLength, param: 2 },
      { validator: validationRules.maxLength, param: 10 },
    ];

    expect(validateField('test', rules)).toBeNull();
  });

  it('should pass param to validator', () => {
    const rules: ValidationRuleItem[] = [
      { validator: validationRules.minLength, param: 5, message: 'Min 5' },
    ];

    expect(validateField('test', rules)).toBe('Min 5');
    expect(validateField('testing', rules)).toBeNull();
  });

  it('should use custom message from rule', () => {
    const rules: ValidationRuleItem[] = [
      { validator: validationRules.required, message: 'Custom required' },
    ];

    expect(validateField('', rules)).toBe('Custom required');
  });

  it('should handle multiple rules with different types', () => {
    const rules: ValidationRuleItem[] = [
      { validator: validationRules.required },
      { validator: validationRules.pattern, param: /^[a-z]+$/, message: 'Lowercase only' },
      { validator: validationRules.minLength, param: 3 },
    ];

    expect(validateField('AB', rules)).toBe('Lowercase only');
    expect(validateField('ABC', rules)).toBe('Lowercase only');
    expect(validateField('abc', rules)).toBeNull();
  });
});

describe('validateAll', () => {
  it('should validate all fields in form data', () => {
    const formData = {
      username: 'ab',
      email: 'invalid',
      age: '25',
    };

    const rules = {
      username: [
        { validator: validationRules.required },
        { validator: validationRules.minLength, param: 3, message: 'Username too short' },
      ],
      email: [
        { validator: validationRules.required },
        { validator: validationRules.email },
      ],
      age: [
        { validator: validationRules.number },
      ],
    };

    const result = validateAll(formData, rules);

    expect(result.isValid).toBe(false);
    expect(result.errors.username).toBe('Username too short');
    expect(result.errors.email).toBe('邮箱格式不正确');
    expect(result.errors.age).toBeUndefined();
  });

  it('should return isValid true when all fields pass', () => {
    const formData = {
      username: 'testuser',
      email: 'test@example.com',
      age: '25',
    };

    const rules = {
      username: [
        { validator: validationRules.required },
        { validator: validationRules.minLength, param: 3 },
      ],
      email: [
        { validator: validationRules.required },
        { validator: validationRules.email },
      ],
      age: [
        { validator: validationRules.number },
      ],
    };

    const result = validateAll(formData, rules);

    expect(result.isValid).toBe(true);
    expect(Object.keys(result.errors)).toHaveLength(0);
  });

  it('should handle empty form data', () => {
    const formData = {};
    const rules = {};

    const result = validateAll(formData, rules);

    expect(result.isValid).toBe(true);
    expect(result.errors).toEqual({});
  });

  it('should include error for field that fails validation', () => {
    const formData = {
      password: '123',
    };

    const rules = {
      password: [
        { validator: validationRules.minLength, param: 8, message: 'Password too weak' },
      ],
    };

    const result = validateAll(formData, rules);

    expect(result.isValid).toBe(false);
    expect(result.errors.password).toBe('Password too weak');
  });

  it('should skip validation for fields not in rules', () => {
    const formData = {
      username: 'test',
      email: 'test@example.com',
      extraField: 'ignored',
    };

    const rules = {
      username: [{ validator: validationRules.required }],
      email: [{ validator: validationRules.email }],
    };

    const result = validateAll(formData, rules);

    expect(result.isValid).toBe(true);
    expect(result.errors.extraField).toBeUndefined();
  });
});

describe('gameValidationRules', () => {
  it('should validate gid field', () => {
    expect(validateField('', gameValidationRules.gid)).toBe('GID不能为空');
    expect(validateField('abc', gameValidationRules.gid)).toBe('GID必须是数字');
    expect(validateField('123', gameValidationRules.gid)).toBeNull();
  });

  it('should validate name field', () => {
    expect(validateField('', gameValidationRules.name)).toBe('游戏名称不能为空');
    expect(validateField('a', gameValidationRules.name)).toBe('游戏名称至少2个字符');
    expect(validateField('ab', gameValidationRules.name)).toBeNull();
  });

  it('should validate ods_db field', () => {
    expect(validateField('', gameValidationRules.ods_db)).toBe('请选择ODS数据库');
    expect(validateField('ieu_ods', gameValidationRules.ods_db)).toBeNull();
  });

  it('should validate name_en field', () => {
    expect(validateField('', gameValidationRules.name_en)).toBe('英文名称不能为空');
    expect(validateField('123_abc', gameValidationRules.name_en)).toBe('只能包含小写字母、数字和下划线，且以字母开头');
    expect(validateField('ABC', gameValidationRules.name_en)).toBe('只能包含小写字母、数字和下划线，且以字母开头');
    expect(validateField('valid_name_123', gameValidationRules.name_en)).toBeNull();
  });

  it('should validate name_cn field', () => {
    expect(validateField('', gameValidationRules.name_cn)).toBe('中文名称不能为空');
    expect(validateField('游戏名称', gameValidationRules.name_cn)).toBeNull();
  });
});

describe('createFieldValidator', () => {
  it('should create a validator function from rules', () => {
    const rules: ValidationRuleItem[] = [
      { validator: validationRules.required },
      { validator: validationRules.minLength, param: 3 },
    ];

    const validator = createFieldValidator(rules);

    expect(validator('')).toBe('此字段不能为空');
    expect(validator('ab')).toBe('至少需要3个字符');
    expect(validator('test')).toBeNull();
  });

  it('should create reusable validator', () => {
    const emailValidator = createFieldValidator([
      { validator: validationRules.required, message: 'Email is required' },
      { validator: validationRules.email },
    ]);

    expect(emailValidator('')).toBe('Email is required');
    expect(emailValidator('invalid')).toBe('邮箱格式不正确');
    expect(emailValidator('test@example.com')).toBeNull();
  });

  it('should create validator for custom patterns', () => {
    const usernameValidator = createFieldValidator([
      { validator: validationRules.required },
      { validator: validationRules.pattern, param: /^[a-zA-Z0-9_]+$/, message: 'Invalid username' },
    ]);

    expect(usernameValidator('valid_user123')).toBeNull();
    expect(usernameValidator('invalid-user!')).toBe('Invalid username');
  });
});

describe('Integration Tests', () => {
  it('should handle complex form validation scenario', () => {
    const formData = {
      username: '',
      email: 'invalid-email',
      password: '123',
      age: 'not-a-number',
      bio: 'This is a very long biography that exceeds the maximum allowed length',
    };

    const rules = {
      username: [
        { validator: validationRules.required },
        { validator: validationRules.minLength, param: 3 },
      ],
      email: [
        { validator: validationRules.required },
        { validator: validationRules.email },
      ],
      password: [
        { validator: validationRules.required },
        { validator: validationRules.minLength, param: 8 },
      ],
      age: [
        { validator: validationRules.number },
      ],
      bio: [
        { validator: validationRules.maxLength, param: 50 },
      ],
    };

    const result = validateAll(formData, rules);

    expect(result.isValid).toBe(false);
    expect(result.errors.username).toBe('此字段不能为空');
    expect(result.errors.email).toBe('邮箱格式不正确');
    expect(result.errors.password).toBe('至少需要8个字符');
    expect(result.errors.age).toBe('必须是数字');
    expect(result.errors.bio).toBe('最多50个字符');
  });

  it('should validate successful form submission', () => {
    const formData = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'securepassword123',
      age: '25',
      bio: 'Short bio',
    };

    const rules = {
      username: [
        { validator: validationRules.required },
        { validator: validationRules.minLength, param: 3 },
        { validator: validationRules.maxLength, param: 20 },
      ],
      email: [
        { validator: validationRules.required },
        { validator: validationRules.email },
      ],
      password: [
        { validator: validationRules.required },
        { validator: validationRules.minLength, param: 8 },
      ],
      age: [
        { validator: validationRules.number },
      ],
      bio: [
        { validator: validationRules.maxLength, param: 50 },
      ],
    };

    const result = validateAll(formData, rules);

    expect(result.isValid).toBe(true);
    expect(Object.keys(result.errors)).toHaveLength(0);
  });

  it('should support conditional validation', () => {
    const formData = {
      phone: '1234567890',
      email: 'test@example.com',
    };

    // Phone is optional, email is required
    const rules = {
      phone: [
        { validator: validationRules.pattern, param: /^\d{10}$/, message: 'Invalid phone' },
      ],
      email: [
        { validator: validationRules.required },
        { validator: validationRules.email },
      ],
    };

    const result = validateAll(formData, rules);

    expect(result.isValid).toBe(true);
    expect(result.errors.phone).toBeUndefined();
    expect(result.errors.email).toBeUndefined();
  });
});
