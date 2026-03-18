import { useEffect, useState } from 'react';

/**
 * 防抖Hook - 延迟更新值，减少频繁的计算和请求
 *
 * @param value - 需要防抖的值
 * @param delay - 延迟时间（毫秒），默认300ms
 * @returns 防抖后的值
 *
 * @example
 * const [searchTerm, setSearchTerm] = useState('');
 * const debouncedSearchTerm = useDebounce(searchTerm, 300);
 *
 * // searchTerm会立即更新
 * // debouncedSearchTerm会在300ms后更新（如果searchTerm没有再次变化）
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // 设置定时器
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // 清理函数：如果value在delay时间内变化，清除之前的定时器
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
