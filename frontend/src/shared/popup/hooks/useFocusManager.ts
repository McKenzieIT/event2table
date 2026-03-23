/**
 * useFocusManager Hook
 *
 * 统一管理弹窗组件的焦点行为
 */

import React, { useEffect, useCallback, RefObject } from 'react';

import { PopupType } from '../ZIndexManager';
import { FOCUS_STRATEGIES } from '../types';

export interface UseFocusManagerOptions {
  /** 弹窗类型 */
  type: PopupType;
  /** 是否打开 */
  isOpen: boolean;
  /** 容器引用 */
  containerRef: RefObject<HTMLElement>;
}

/**
 * 焦点管理Hook
 *
 * @param config - 配置选项
 */
export function useFocusManager(config: UseFocusManagerOptions) {
  const { type, isOpen, containerRef } = config;

  const strategy = FOCUS_STRATEGIES[type];
  const triggerRef = React.useRef<HTMLElement | null>(null);

  // 焦点陷阱逻辑（仅MODAL类型）
  const enforceFocusTrap = useCallback(() => {
    if (type !== PopupType.MODAL || !strategy.trap) return;

    const container = containerRef.current;
    if (!container) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      // 获取所有可聚焦元素
      const focusableSelectors = [
        'button:not([disabled])',
        'input:not([disabled])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        'a[href]',
        '[tabindex]:not([tabindex="-1"])',
      ].join(', ');

      const focusableElements =
        container.querySelectorAll<HTMLElement>(focusableSelectors);
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (!firstElement || !lastElement) return;

      // Shift+Tab 在第一个元素
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
        return;
      }

      // Tab 在最后一个元素
      if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
        return;
      }
    };

    container.addEventListener('keydown', handleKeyDown);
    return () => container.removeEventListener('keydown', handleKeyDown);
  }, [type, containerRef, strategy.trap]);

  // 自动聚焦（打开时）
  useEffect(() => {
    if (!isOpen || !strategy.autoFocus) return;

    // 保存当前焦点元素
    triggerRef.current = document.activeElement as HTMLElement;

    // 聚焦到容器或第一个可聚焦元素
    setTimeout(() => {
      const container = containerRef.current;
      if (!container) return;

      // 尝试聚焦第一个可聚焦元素
      const firstFocusable = container.querySelector<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex="0"]'
      );

      if (firstFocusable) {
        firstFocusable.focus();
      } else {
        // 如果没有可聚焦元素，聚焦容器本身
        container.focus();
      }
    }, 50);

    // 如果是MODAL类型，启用焦点陷阱
    if (type === PopupType.MODAL) {
      const cleanup = enforceFocusTrap();
      return cleanup;
    }
  }, [isOpen, type, containerRef, strategy, enforceFocusTrap]);

  // 恢复焦点（关闭时）
  useEffect(() => {
    if (isOpen || !strategy.restoreOnClose) return;

    // 恢复到触发元素
    triggerRef.current?.focus();
    triggerRef.current = null;
  }, [isOpen, strategy.restoreOnClose]);
}

export default useFocusManager;
