/**
 * 防抖Hook
 * Debounce Hook
 *
 * 延迟更新值，避免频繁触发（如搜索输入）
 */

import { useState, useEffect } from 'react';

/**
 * 防抖Hook
 *
 * @param value - 需要防抖的值
 * @param delay - 延迟时间（毫秒），默认300ms
 * @returns 防抖后的值
 *
 * @example
 * ```tsx
 * const [input, setInput] = useState('');
 * const debouncedInput = useDebounce(input, 300);
 *
 * useEffect(() => {
 *   // 使用debouncedInput进行API调用
 *   searchApi(debouncedInput);
 * }, [debouncedInput]);
 * ```
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // 设置定时器
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // 清除定时器（cleanup）
    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}
