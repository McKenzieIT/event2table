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
  required: (value: unknown, message: string = '此字段不能为空'): string | null => {
    if (!value || (typeof value === 'string' && !value.trim())) {
      return message;
    }
    return null;
  },
  
  minLength: (value: unknown, min: number, message?: string): string | null => {
    if (value && typeof value === 'string' && value.length < min) {
      return message || `至少需要${min}个字符`;
    }
    return null;
  },
  
  maxLength: (value: unknown, max: number, message?: string): string | null => {
    if (value && typeof value === 'string' && value.length > max) {
      return message || `最多${max}个字符`;
    }
    return null;
  },
  
  pattern: (value: unknown, regex: RegExp, message?: string): string | null => {
    if (value && typeof value === 'string' && !regex.test(value)) {
      return message || '格式不正确';
    }
    return null;
  },
  
  number: (value: unknown, message?: string): string | null => {
    if (value && typeof value === 'string' && !/^\d+$/.test(value)) {
      return message || '必须是数字';
    }
    return null;
  },
  
  email: (value: unknown, message?: string): string | null => {
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
