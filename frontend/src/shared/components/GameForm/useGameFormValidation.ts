/**
 * useGameFormValidation Hook
 *
 * 统一的表单验证逻辑
 * 支持 touched 机制和实时验证
 */

import { useState, useCallback, Dispatch, SetStateAction } from 'react';

interface ValidationErrors {
  name?: string;
  gid?: string;
  ods_db?: string;
}

interface TouchedFields {
  name?: boolean;
  gid?: boolean;
  ods_db?: boolean;
}

interface GameFormData {
  name: string;
  gid: string;
  ods_db: string;
}

export const useGameFormValidation = () => {
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [touched, setTouched] = useState<TouchedFields>({});

  const validateField = useCallback((field: keyof GameFormData, value: string): string => {
    let error = '';

    switch (field) {
      case 'name':
        if (!value || !value.trim()) {
          error = '游戏名称不能为空';
        } else if (value.trim().length < 2) {
          error = '游戏名称至少2个字符';
        }
        break;

      case 'gid':
        if (!value || !value.trim()) {
          error = 'GID不能为空';
        } else if (!/^\d+$/.test(value.trim())) {
          error = 'GID必须是数字';
        } else {
          const gidInt = parseInt(value, 10);
          if (isNaN(gidInt) || gidInt <= 0) {
            error = 'GID必须是有效的正整数';
          }
        }
        break;

      case 'ods_db':
        if (!value) {
          error = '请选择ODS数据库';
        }
        break;

      default:
        break;
    }

    setErrors((prev: ValidationErrors) => ({
      ...prev,
      [field]: error
    }));

    return error;
  }, []);

  const validateForm = useCallback((formData: GameFormData): boolean => {
    const newErrors: ValidationErrors = {};

    if (!formData.name || !formData.name.trim()) {
      newErrors.name = '游戏名称不能为空';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = '游戏名称至少2个字符';
    }

    if (!formData.gid || !formData.gid.trim()) {
      newErrors.gid = 'GID不能为空';
    } else if (!/^\d+$/.test(formData.gid.trim())) {
      newErrors.gid = 'GID必须是数字';
    } else {
      const gidInt = parseInt(formData.gid, 10);
      if (isNaN(gidInt) || gidInt <= 0) {
        newErrors.gid = 'GID必须是有效的正整数';
      }
    }

    if (!formData.ods_db) {
      newErrors.ods_db = '请选择ODS数据库';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, []);

  const markTouched = useCallback((field: keyof TouchedFields) => {
    setTouched((prev: TouchedFields) => ({
      ...prev,
      [field]: true
    }));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors({});
    setTouched({});
  }, []);

  return {
    errors,
    touched,
    validateField,
    validateForm,
    markTouched,
    clearErrors
  };
};
