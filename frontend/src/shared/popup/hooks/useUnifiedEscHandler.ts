/**
 * useUnifiedEscHandler Hook
 *
 * 统一的ESC键处理Hook，支持：
 * - 输入保护（disableOnEditable）
 * - 防抖（debounceMs）
 * - 启用/禁用开关（enabled）
 */

import { useEffect, useRef } from 'react';

export interface UseEscHandlerOptions {
  /** 是否启用ESC监听，默认true */
  enabled?: boolean;
  /** 防抖延迟（毫秒），默认200ms */
  debounceMs?: number;
  /** 是否在可编辑元素上禁用，默认true */
  disableOnEditable?: boolean;
}

/**
 * 统一的ESC键处理Hook
 *
 * @param callback - ESC键按下时的回调函数
 * @param options - Hook配置选项
 *
 * @example
 * ```tsx
 * const handleEsc = () => {
 *   console.log('ESC pressed');
 * };
 *
 * useUnifiedEscHandler(handleEsc, { enabled: true });
 * ```
 */
export function useUnifiedEscHandler(
  callback: () => void,
  options: UseEscHandlerOptions = {}
) {
  const {
    enabled = true,
    debounceMs = 200,
    disableOnEditable = true,
  } = options;

  const lastCallTime = useRef<number>(0);
  const callbackRef = useRef(callback);

  // 保持callback引用最新
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e: Event) => {
      const keyboardEvent = e as KeyboardEvent;

      // 只处理ESC键
      if (keyboardEvent.key !== 'Escape') return;

      // 如果启用可编辑元素检测，检查焦点是否在可编辑元素上
      if (disableOnEditable) {
        const target = keyboardEvent.target as HTMLElement;
        const isEditable =
          target.tagName === 'INPUT' ||
          target.tagName === 'TEXTAREA' ||
          target.tagName === 'SELECT' ||
          target.isContentEditable;

        if (isEditable) {
          // 不处理，让浏览器默认行为（如清除输入框内容）
          return;
        }
      }

      // 防抖处理
      const now = Date.now();
      if (debounceMs > 0 && now - lastCallTime.current < debounceMs) {
        return;
      }
      lastCallTime.current = now;

      // 阻止默认行为并触发回调
      keyboardEvent.preventDefault();
      callbackRef.current();
    };

    // 添加全局事件监听（使用capture确保优先处理）
    document.addEventListener('keydown', handleKeyDown, { capture: true });

    // 清理函数
    return () => {
      document.removeEventListener('keydown', handleKeyDown, { capture: true });
    };
  }, [enabled, debounceMs, disableOnEditable]);
}

export default useUnifiedEscHandler;
