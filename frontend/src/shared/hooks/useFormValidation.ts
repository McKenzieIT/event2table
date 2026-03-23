import { useState, useCallback } from 'react';

export interface ValidationRules {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  message?: string;
}

export interface UseFormValidationReturn<T extends Record<string, unknown>> {
  errors: Record<keyof T, string | null>;
  touched: Record<keyof T, boolean>;
  handleBlur: (name: keyof T) => void;
  validateField: (name: keyof T, value: unknown) => string | null;
  validateAll: () => boolean;
  clearErrors: () => void;
  setErrors: React.Dispatch<React.SetStateAction<Record<keyof T, string | null>>>;
  setTouched: React.Dispatch<React.SetStateAction<Record<keyof T, boolean>>>;
}

export function useFormValidation<T extends Record<string, unknown>>(
  initialValues: T,
  rules: Partial<Record<keyof T, ValidationRules>>
): UseFormValidationReturn<T> {
  const [errors, setErrors] = useState<Record<keyof T, string | null>>({} as Record<keyof T, string | null>);
  const [touched, setTouched] = useState<Record<keyof T, boolean>>({} as Record<keyof T, boolean>);

  const validateField = useCallback((name: keyof T, value: unknown): string | null => {
    const rule = rules[name];
    if (!rule) return null;
    
    if (rule.required && (!value || (typeof value === 'string' && !value.trim()))) {
      return rule.message || '此字段为必填项';
    }
    if (rule.minLength && typeof value === 'string' && value.length < rule.minLength) {
      return rule.message || `最少${rule.minLength}个字符`;
    }
    if (rule.maxLength && typeof value === 'string' && value.length > rule.maxLength) {
      return rule.message || `最多${rule.maxLength}个字符`;
    }
    if (rule.pattern && typeof value === 'string' && !rule.pattern.test(value)) {
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
    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;
    (Object.keys(rules) as Array<keyof T>).forEach(name => {
      const error = validateField(name, initialValues[name]);
      if (error) {
        newErrors[name] = error;
        isValid = false;
      }
    });
    setErrors(newErrors as Record<keyof T, string | null>);
    setTouched(prev => {
      const newTouched = { ...prev };
      Object.keys(rules).forEach(key => { 
        newTouched[key as keyof T] = true; 
      });
      return newTouched;
    });
    return isValid;
  }, [initialValues, rules, validateField]);

  const clearErrors = useCallback(() => {
    setErrors({} as Record<keyof T, string | null>);
    setTouched({} as Record<keyof T, boolean>);
  }, []);

  return { errors, touched, handleBlur, validateField, validateAll, clearErrors, setErrors, setTouched };
}
