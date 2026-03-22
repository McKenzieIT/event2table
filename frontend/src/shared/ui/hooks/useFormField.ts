/**
 * 表单字段通用 Hook
 * 
 * 提取表单字段组件中的公共逻辑：
 * - ID 生成
 * - 状态管理
 * - 事件处理器包装
 */

import { useId, useCallback, useRef, useEffect } from 'react';

/**
 * 表单字段 Hook 返回值
 */
export interface UseFormFieldReturn {
  /** 字段 ID */
  fieldId: string;
  /** 字段引用 */
  fieldRef: React.RefObject<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>;
  /** 合并后的 ref */
  mergedRef: (node: any) => void;
  /** 是否无效 */
  isInvalid: boolean;
  /** 处理变更事件 */
  handleChange: (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  /** 处理失焦事件 */
  handleBlur: (event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  /** 处理聚焦事件 */
  handleFocus: (event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
}

/**
 * 表单字段 Hook 配置
 */
export interface UseFormFieldOptions {
  /** 自定义 ID */
  customId?: string;
  /** 错误信息 */
  error?: string;
  /** 变更处理器 */
  onChange?: (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  /** 失焦处理器 */
  onBlur?: (event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  /** 聚焦处理器 */
  onFocus?: (event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  /** 是否禁用 */
  disabled?: boolean;
  /** 外部 ref */
  ref?: React.Ref<any>;
}

/**
 * 表单字段 Hook
 * 
 * 为表单字段组件提供统一的 ID 生成、ref 合并和事件处理器
 * 
 * @example
 * const { fieldId, fieldRef, isInvalid, handleChange, handleBlur, handleFocus } = useFormField({
 *   customId: props.id,
 *   error: props.error,
 *   onChange: props.onChange,
 *   onBlur: props.onBlur,
 *   onFocus: props.onFocus,
 *   disabled: props.disabled,
 *   ref: ref
 * });
 */
export function useFormField(options: UseFormFieldOptions = {}): UseFormFieldReturn {
  const {
    customId,
    error,
    onChange,
    onBlur,
    onFocus,
    disabled = false,
    ref: externalRef
  } = options;

  // 生成唯一 ID
  const generatedId = useId();
  const fieldId = customId || generatedId;

  // 创建内部 ref
  const fieldRef = useRef<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(null);

  // 合并外部 ref 和内部 ref
  const mergedRef = useCallback((node: any) => {
    if (node) {
      fieldRef.current = node;
    }

    if (typeof externalRef === 'function') {
      externalRef(node);
    } else if (externalRef) {
      (externalRef as React.MutableRefObject<any>).current = node;
    }
  }, [externalRef]);

  // 是否无效
  const isInvalid = Boolean(error);

  // 处理变更事件
  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    onChange?.(event);
  }, [onChange]);

  // 处理失焦事件
  const handleBlur = useCallback((event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    onBlur?.(event);
  }, [onBlur]);

  // 处理聚焦事件
  const handleFocus = useCallback((event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    onFocus?.(event);
  }, [onFocus]);

  return {
    fieldId,
    fieldRef,
    mergedRef,
    isInvalid,
    handleChange,
    handleBlur,
    handleFocus
  };
}
