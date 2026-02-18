import { useState, useCallback } from 'react';

interface ValidationRules {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  message?: string;
}

export function useFormValidation<T extends Record<string, any>>(
  initialValues: T,
  rules: Record<keyof T, ValidationRules>
) {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateField = useCallback((name: keyof T, value: any): string | null => {
    const rule = rules[name];
    if (!rule) return null;
    
    if (rule.required && (!value || (typeof value === 'string' && !value.trim()))) {
      return rule.message || '此字段为必填项';
    }
    if (rule.minLength && value && value.length < rule.minLength) {
      return rule.message || `最少${rule.minLength}个字符`;
    }
    if (rule.maxLength && value && value.length > rule.maxLength) {
      return rule.message || `最多${rule.maxLength}个字符`;
    }
    if (rule.pattern && value && !rule.pattern.test(value)) {
      return rule.message || '格式不正确';
    }
    return null;
  }, [rules]);

  const handleBlur = useCallback((name: keyof T) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    const value = initialValues[name];
    const error = validateField(name, value);
    setErrors(prev => ({ ...prev, [name]: error }));
  }, [initialValues, validateField]);

  const validateAll = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};
    let isValid = true;
    (Object.keys(rules) as Array<keyof T>).forEach(name => {
      const error = validateField(name, initialValues[name]);
      if (error) {
        newErrors[name as string] = error;
        isValid = false;
      }
    });
    setErrors(newErrors);
    setTouched(prev => {
      const newTouched = { ...prev };
      Object.keys(rules).forEach(key => { newTouched[key] = true; });
      return newTouched;
    });
    return isValid;
  }, [initialValues, rules, validateField]);

  const clearErrors = useCallback(() => {
    setErrors({});
    setTouched({});
  }, []);

  return { errors, touched, handleBlur, validateField, validateAll, clearErrors, setErrors, setTouched };
}
