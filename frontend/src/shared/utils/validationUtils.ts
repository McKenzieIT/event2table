// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Form Validation Utilities
 * 表单验证工具函数
 */

export type ValidatorFn = (value: unknown, param?: unknown, message?: string) => string | null;

export interface ValidationRuleItem {
  validator: ValidatorFn;
  param?: unknown;
  message?: string;
}

export interface ValidationRulesMap {
  [field: string]: ValidationRuleItem[];
}

export interface ValidationErrors {
  [field: string]: string;
}

export interface ValidationResult {
  errors: ValidationErrors;
  isValid: boolean;
}

export const validationRules = {
  required: (value: unknown, _param?: unknown, message: string = '此字段不能为空'): string | null => {
    // Allow 0 and false as valid values
    if (value === 0 || value === false) {
      return null;
    }
    if (!value || (typeof value === 'string' && !value.trim())) {
      return message;
    }
    return null;
  },
  
  minLength: (value: unknown, min?: number | unknown, message?: string): string | null => {
    const minLength = typeof min === 'number' ? min : 0;
    if (value && typeof value === 'string' && value.length < minLength) {
      return message || `至少需要${minLength}个字符`;
    }
    return null;
  },
  
  maxLength: (value: unknown, max?: number | unknown, message?: string): string | null => {
    const maxLength = typeof max === 'number' ? max : Infinity;
    if (value && typeof value === 'string' && value.length > maxLength) {
      return message || `最多${maxLength}个字符`;
    }
    return null;
  },
  
  pattern: (value: unknown, regex?: RegExp | unknown, message?: string): string | null => {
    const pattern = regex instanceof RegExp ? regex : /.*/;
    if (value && typeof value === 'string' && !pattern.test(value)) {
      return message || '格式不正确';
    }
    return null;
  },
  
  number: (value: unknown, _param?: unknown, message?: string): string | null => {
    if (value && typeof value === 'string' && !/^\d+$/.test(value)) {
      return message || '必须是数字';
    }
    return null;
  },
  
  email: (value: unknown, _param?: unknown, message?: string): string | null => {
    if (value && typeof value === 'string' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      return message || '邮箱格式不正确';
    }
    return null;
  },
};

export const gameValidationRules: ValidationRulesMap = {
  gid: [
    { validator: validationRules.required, message: 'GID不能为空' },
    { validator: validationRules.number, message: 'GID必须是数字' },
  ],
  name: [
    { validator: validationRules.required, message: '游戏名称不能为空' },
    { validator: validationRules.minLength, param: 2, message: '游戏名称至少2个字符' },
  ],
  ods_db: [
    { validator: validationRules.required, message: '请选择ODS数据库' },
  ],
  name_en: [
    { validator: validationRules.required, message: '英文名称不能为空' },
    { validator: validationRules.pattern, param: /^[a-z][a-z0-9_]*$/, message: '只能包含小写字母、数字和下划线，且以字母开头' },
  ],
  name_cn: [
    { validator: validationRules.required, message: '中文名称不能为空' },
  ],
};

export function validateField(value: unknown, rules?: ValidationRuleItem[]): string | null {
  if (!rules || !Array.isArray(rules)) {
    return null;
  }
  
  for (const rule of rules) {
    // Pass custom message to validator if provided
    const error = rule.validator(value, rule.param, rule.message);
    if (error) {
      return error;
    }
  }
  
  return null;
}

export function validateAll(formData: Record<string, unknown>, rules: ValidationRulesMap): ValidationResult {
  const errors: ValidationErrors = {};
  let isValid = true;
  
  for (const [field, fieldRules] of Object.entries(rules)) {
    const error = validateField(formData[field], fieldRules);
    if (error) {
      errors[field] = error;
      isValid = false;
    }
  }
  
  return { errors, isValid };
}

export function createFieldValidator(rules: ValidationRuleItem[]): (value: unknown) => string | null {
  return (value: unknown) => validateField(value, rules);
}
