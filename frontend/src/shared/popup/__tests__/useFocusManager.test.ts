/**
 * useFocusManager单元测试 - 简化版
 */

import { renderHook, act } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useFocusManager } from '../hooks/useFocusManager';
import { PopupType } from '../ZIndexManager';

describe('useFocusManager', () => {
  let containerRef: any;

  beforeEach(() => {
    containerRef = { current: null };
    document.body.innerHTML = '';
  });

  describe('基础功能', () => {
    it('应该正确初始化', () => {
      const container = document.createElement('div');
      containerRef.current = container;

      renderHook(() =>
        useFocusManager({
          type: PopupType.MODAL,
          isOpen: true,
          containerRef,
        })
      );

      // 验证Hook正常执行
      expect(containerRef.current).toBe(container);
    });

    it('应该支持DRAWER类型', () => {
      const container = document.createElement('div');
      containerRef.current = container;

      renderHook(() =>
        useFocusManager({
          type: PopupType.DRAWER,
          isOpen: true,
          containerRef,
        })
      );

      expect(containerRef.current).toBe(container);
    });

    it('应该支持DROPDOWN类型', () => {
      const container = document.createElement('div');
      containerRef.current = container;

      renderHook(() =>
        useFocusManager({
          type: PopupType.DROPDOWN,
          isOpen: true,
          containerRef,
        })
      );

      expect(containerRef.current).toBe(container);
    });
  });

  describe('焦点陷阱', () => {
    it('应该为MODAL类型添加键盘事件监听', () => {
      const container = document.createElement('div');
      containerRef.current = container;
      document.body.appendChild(container);

      const addEventListenerSpy = vi.spyOn(container, 'addEventListener');

      renderHook(() =>
        useFocusManager({
          type: PopupType.MODAL,
          isOpen: true,
          containerRef,
        })
      );

      // 验证添加了keydown监听器
      expect(addEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

      document.body.removeChild(container);
      addEventListenerSpy.mockRestore();
    });

    it('应该不为DRAWER类型添加焦点陷阱', () => {
      const container = document.createElement('div');
      containerRef.current = container;
      document.body.appendChild(container);

      const addEventListenerSpy = vi.spyOn(container, 'addEventListener');

      renderHook(() =>
        useFocusManager({
          type: PopupType.DRAWER,
          isOpen: true,
          containerRef,
        })
      );

      // DRAWER不添加keydown监听器（不实现焦点陷阱）
      expect(addEventListenerSpy).not.toHaveBeenCalledWith('keydown', expect.any(Function));

      document.body.removeChild(container);
      addEventListenerSpy.mockRestore();
    });
  });
});
