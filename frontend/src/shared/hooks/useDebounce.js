/**
 * useDebounce Hook
 * 防抖Hook
 *
 * @param {*} value - 需要防抖的值
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {*} 防抖后的值
 */
import { useState, useEffect } from 'react';

export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // 设置定时器
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // 清理函数：组件卸载或value/delay变化时清除定时器
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
