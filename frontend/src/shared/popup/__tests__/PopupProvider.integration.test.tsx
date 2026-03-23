/**
 * PopupProvider集成测试
 */

import { renderHook, act } from '@test/test-utils';
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { PopupProvider, usePopupContext } from '../PopupProvider';
import { PopupType } from '../ZIndexManager';

describe('PopupProvider集成测试', () => {
  let wrapper: ({ children }: { children: React.ReactNode }) => JSX.Element;

  beforeEach(() => {
    wrapper = ({ children }) => <PopupProvider>{children}</PopupProvider>;
  });

  describe('注册弹窗', () => {
    it('应该成功注册MODAL弹窗并分配z-index', () => {
      const { result } = renderHook(() => usePopupContext(), { wrapper });

      act(() => {
        result.current.register({
          id: 'modal-1',
          type: PopupType.MODAL,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: true,
          onClose: vi.fn(),
        });
      });

      const zIndex = result.current.getZIndex('modal-1');
      expect(zIndex).toBe(1200);
    });

    it('应该为多个MODAL分配递增的z-index', () => {
      const { result } = renderHook(() => usePopupContext(), { wrapper });

      act(() => {
        result.current.register({
          id: 'modal-1',
          type: PopupType.MODAL,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: true,
          onClose: vi.fn(),
        });

        result.current.register({
          id: 'modal-2',
          type: PopupType.MODAL,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: true,
          onClose: vi.fn(),
        });
      });

      const zIndex1 = result.current.getZIndex('modal-1');
      const zIndex2 = result.current.getZIndex('modal-2');

      expect(zIndex1).toBe(1200);
      expect(zIndex2).toBe(1210);
    });

    it('应该为不同类型分配独立的z-index范围', () => {
      const { result } = renderHook(() => usePopupContext(), { wrapper });

      act(() => {
        result.current.register({
          id: 'dropdown-1',
          type: PopupType.DROPDOWN,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: false,
          onClose: vi.fn(),
        });

        result.current.register({
          id: 'drawer-1',
          type: PopupType.DRAWER,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: false,
          onClose: vi.fn(),
        });

        result.current.register({
          id: 'modal-1',
          type: PopupType.MODAL,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: true,
          onClose: vi.fn(),
        });
      });

      const dropdownZ = result.current.getZIndex('dropdown-1');
      const drawerZ = result.current.getZIndex('drawer-1');
      const modalZ = result.current.getZIndex('modal-1');

      expect(dropdownZ).toBe(1050);
      expect(drawerZ).toBe(1100);
      expect(modalZ).toBe(1200);
    });
  });

  describe('注销弹窗', () => {
    it('应该成功注销弹窗并释放层级', () => {
      const { result } = renderHook(() => usePopupContext(), { wrapper });

      act(() => {
        result.current.register({
          id: 'modal-1',
          type: PopupType.MODAL,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: true,
          onClose: vi.fn(),
        });

        result.current.register({
          id: 'modal-2',
          type: PopupType.MODAL,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: true,
          onClose: vi.fn(),
        });

        result.current.unregister('modal-1');
      });

      // 第二个MODAL应该获得1210（第一个已被释放）
      const zIndex = result.current.getZIndex('modal-2');
      expect(zIndex).toBe(1210);
    });
  });

  describe('获取最顶层弹窗', () => {
    it('应该返回z-index最大的弹窗ID', () => {
      const { result } = renderHook(() => usePopupContext(), { wrapper });

      act(() => {
        result.current.register({
          id: 'dropdown-1',
          type: PopupType.DROPDOWN,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: false,
          onClose: vi.fn(),
        });

        result.current.register({
          id: 'modal-1',
          type: PopupType.MODAL,
          isOpen: true,
          priority: 1,
          enableEsc: true,
          enableFocusTrap: true,
          onClose: vi.fn(),
        });
      });

      const topmostId = result.current.getTopmostId();
      expect(topmostId).toBe('modal-1'); // MODAL的z-index更大
    });

    it('应该在没有弹窗时返回null', () => {
      const { result } = renderHook(() => usePopupContext(), { wrapper });

      const topmostId = result.current.getTopmostId();
      expect(topmostId).toBeNull();
    });
  });

  describe('Context错误处理', () => {
    it('应该在Provider外使用时抛出错误', () => {
      // 不使用wrapper来模拟Provider外
      expect(() => {
        renderHook(() => usePopupContext());
      }).toThrow('usePopupContext must be used within PopupProvider');
    });
  });
});
