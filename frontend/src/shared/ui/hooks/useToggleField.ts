/**
 * 切换字段通用 Hook
 * 
 * 为 Checkbox、Radio、Switch 等切换组件提供公共逻辑
 */

import { useCallback, useRef, useEffect } from 'react';
import { useFormField, UseFormFieldOptions } from './useFormField';

/**
 * 切换字段 Hook 返回值
 */
export interface UseToggleFieldReturn {
  /** 字段 ID */
  fieldId: string;
  /** 字段引用 */
  fieldRef: React.RefObject<HTMLInputElement>;
  /** 合并后的 ref */
  mergedRef: (node: any) => void;
  /** 是否无效 */
  isInvalid: boolean;
  /** 处理变更事件 */
  handleChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

/**
 * Checkbox 切换字段 Hook 返回值
 */
export interface UseCheckboxFieldReturn extends UseToggleFieldReturn {
  /** 处理变更事件（Checkbox 特有） */
  handleCheckboxChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

/**
 * Radio 切换字段 Hook 返回值
 */
export interface UseRadioFieldReturn extends UseToggleFieldReturn {
  /** 处理变更事件（Radio 特有） */
  handleRadioChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

/**
 * Switch 切换字段 Hook 返回值
 */
export interface UseSwitchFieldReturn extends UseToggleFieldReturn {
  /** 处理变更事件（Switch 特有） */
  handleSwitchChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** 处理键盘事件 */
  handleKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void;
}

/**
 * 切换字段 Hook 选项
 */
export interface UseToggleFieldOptions extends Omit<UseFormFieldOptions, 'onChange'> {
  /** Checkbox 变更处理器 */
  onCheckboxChange?: (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Radio 变更处理器 */
  onRadioChange?: (value: string, event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Switch 变更处理器 */
  onSwitchChange?: (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => void;
  /** 是否禁用 */
  disabled?: boolean;
  /** 当前选中状态 */
  checked?: boolean;
}

/**
 * Checkbox 字段 Hook
 * 
 * @example
 * const { fieldId, fieldRef, isInvalid, handleCheckboxChange } = useCheckboxField({
 *   customId: props.id,
 *   error: props.error,
 *   onCheckboxChange: props.onChange,
 *   disabled: props.disabled,
 *   checked: props.checked,
 *   ref: ref
 * });
 */
export function useCheckboxField(options: UseToggleFieldOptions = {}): UseCheckboxFieldReturn {
  const {
    customId,
    error,
    onCheckboxChange,
    disabled = false,
    checked = false,
    ref: externalRef
  } = options;

  // 使用基础表单字段 Hook
  const { fieldId, fieldRef, mergedRef, isInvalid } = useFormField({
    customId,
    error,
    disabled,
    ref: externalRef
  });

  // 处理 Checkbox 变更
  const handleCheckboxChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (!disabled) {
      onCheckboxChange?.(event.target.checked, event);
    }
  }, [disabled, onCheckboxChange]);

  return {
    fieldId,
    fieldRef,
    mergedRef,
    isInvalid,
    handleChange: handleCheckboxChange,
    handleCheckboxChange
  };
}

/**
 * Radio 字段 Hook
 * 
 * @example
 * const { fieldId, fieldRef, isInvalid, handleRadioChange } = useRadioField({
 *   customId: props.id,
 *   error: props.error,
 *   onRadioChange: props.onChange,
 *   disabled: props.disabled,
 *   checked: props.checked,
 *   ref: ref
 * });
 */
export function useRadioField(options: UseToggleFieldOptions = {}): UseRadioFieldReturn {
  const {
    customId,
    error,
    onRadioChange,
    disabled = false,
    ref: externalRef
  } = options;

  // 使用基础表单字段 Hook
  const { fieldId, fieldRef, mergedRef, isInvalid } = useFormField({
    customId,
    error,
    disabled,
    ref: externalRef
  });

  // 处理 Radio 变更
  const handleRadioChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (!disabled) {
      onRadioChange?.(event.target.value, event);
    }
  }, [disabled, onRadioChange]);

  return {
    fieldId,
    fieldRef,
    mergedRef,
    isInvalid,
    handleChange: handleRadioChange,
    handleRadioChange
  };
}

/**
 * Switch 字段 Hook
 * 
 * @example
 * const { fieldId, fieldRef, isInvalid, handleSwitchChange, handleKeyDown } = useSwitchField({
 *   customId: props.id,
 *   error: props.error,
 *   onSwitchChange: props.onChange,
 *   disabled: props.disabled,
 *   checked: props.checked,
 *   ref: ref
 * });
 */
export function useSwitchField(options: UseToggleFieldOptions = {}): UseSwitchFieldReturn {
  const {
    customId,
    error,
    onSwitchChange,
    disabled = false,
    checked = false,
    ref: externalRef
  } = options;

  // 使用基础表单字段 Hook
  const { fieldId, fieldRef, mergedRef, isInvalid } = useFormField({
    customId,
    error,
    disabled,
    ref: externalRef
  });

  // 处理 Switch 变更
  const handleSwitchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (!disabled) {
      onSwitchChange?.(event.target.checked, event);
    }
  }, [disabled, onSwitchChange]);

  // 处理键盘事件（Enter 键切换）
  const handleKeyDown = useCallback((event: React.KeyboardEvent<HTMLInputElement>) => {
    if (!disabled && event.key === 'Enter') {
      event.preventDefault();
      // 创建合成变更事件
      const syntheticEvent = {
        target: event.target,
        currentTarget: event.currentTarget,
      } as React.ChangeEvent<HTMLInputElement>;
      onSwitchChange?.(!checked, syntheticEvent);
    }
  }, [disabled, onSwitchChange, checked]);

  return {
    fieldId,
    fieldRef,
    mergedRef,
    isInvalid,
    handleChange: handleSwitchChange,
    handleSwitchChange,
    handleKeyDown
  };
}
