/**
 * ZIndexManager单元测试
 *
 * TDD Cycle 1: Red阶段
 */

import { describe, it, expect, beforeEach } from 'vitest';

import { ZIndexManager, PopupType } from '../ZIndexManager';

describe('ZIndexManager', () => {
  let manager: ZIndexManager;

  beforeEach(() => {
    manager = new ZIndexManager();
  });

  describe('基础层级分配', () => {
    it('应该为第一个MODAL分配z-index 1200', () => {
      const zIndex = manager.getNext(PopupType.MODAL);
      expect(zIndex).toBe(1200);
    });

    it('应该为第一个DRAWER分配z-index 1100', () => {
      const zIndex = manager.getNext(PopupType.DRAWER);
      expect(zIndex).toBe(1100);
    });

    it('应该为第一个DROPDOWN分配z-index 1050', () => {
      const zIndex = manager.getNext(PopupType.DROPDOWN);
      expect(zIndex).toBe(1050);
    });
  });

  describe('嵌套弹窗层级递增', () => {
    it('应该为第二个MODAL分配z-index 1210', () => {
      manager.getNext(PopupType.MODAL);
      const zIndex = manager.getNext(PopupType.MODAL);
      expect(zIndex).toBe(1210);
    });

    it('应该为第三个MODAL分配z-index 1220', () => {
      manager.getNext(PopupType.MODAL);
      manager.getNext(PopupType.MODAL);
      const zIndex = manager.getNext(PopupType.MODAL);
      expect(zIndex).toBe(1220);
    });

    it('应该为嵌套的DRAWER递增层级', () => {
      manager.getNext(PopupType.DRAWER);
      const zIndex = manager.getNext(PopupType.DRAWER);
      expect(zIndex).toBe(1110);
    });

    it('应该为嵌套的DROPDOWN递增层级', () => {
      manager.getNext(PopupType.DROPDOWN);
      const zIndex = manager.getNext(PopupType.DROPDOWN);
      expect(zIndex).toBe(1060);
    });
  });

  describe('不同类型层级隔离', () => {
    it('应该隔离MODAL和DRAWER的层级计数', () => {
      const modalZ = manager.getNext(PopupType.MODAL);
      const drawerZ = manager.getNext(PopupType.DRAWER);
      const modalZ2 = manager.getNext(PopupType.MODAL);

      expect(modalZ).toBe(1200);
      expect(drawerZ).toBe(1100);
      expect(modalZ2).toBe(1210); // MODAL独立计数
    });

    it('应该隔离所有三种类型的层级计数', () => {
      const m1 = manager.getNext(PopupType.MODAL);
      const d1 = manager.getNext(PopupType.DRAWER);
      const dd1 = manager.getNext(PopupType.DROPDOWN);
      const m2 = manager.getNext(PopupType.MODAL);
      const d2 = manager.getNext(PopupType.DRAWER);
      const dd2 = manager.getNext(PopupType.DROPDOWN);

      expect(m1).toBe(1200);
      expect(d1).toBe(1100);
      expect(dd1).toBe(1050);
      expect(m2).toBe(1210);
      expect(d2).toBe(1110);
      expect(dd2).toBe(1060);
    });
  });

  describe('释放层级', () => {
    it('应该在释放MODAL后重置计数器', () => {
      manager.getNext(PopupType.MODAL);
      manager.getNext(PopupType.MODAL);
      manager.release(PopupType.MODAL);

      const zIndex = manager.getNext(PopupType.MODAL);
      expect(zIndex).toBe(1210); // 第二个MODAL的层级
    });

    it('应该在多次释放后正确计数', () => {
      manager.getNext(PopupType.MODAL);
      manager.getNext(PopupType.MODAL);
      manager.getNext(PopupType.MODAL);
      manager.release(PopupType.MODAL);
      manager.release(PopupType.MODAL);

      const zIndex = manager.getNext(PopupType.MODAL);
      expect(zIndex).toBe(1210);
    });

    it('应该在计数为0时释放不报错', () => {
      expect(() => {
        manager.release(PopupType.MODAL);
      }).not.toThrow();
    });

    it('应该独立释放不同类型的计数器', () => {
      manager.getNext(PopupType.MODAL);
      manager.getNext(PopupType.MODAL);
      manager.getNext(PopupType.DRAWER);

      manager.release(PopupType.MODAL);

      const mZ = manager.getNext(PopupType.MODAL);
      const dZ = manager.getNext(PopupType.DRAWER);

      expect(mZ).toBe(1210); // MODAL计数-1
      expect(dZ).toBe(1110); // DRAWER计数不变
    });
  });

  describe('获取最顶层类型', () => {
    it('应该在没有弹窗时返回null', () => {
      const topmost = manager.getTopmostType();
      expect(topmost).toBeNull();
    });

    it('应该返回单个弹窗的类型', () => {
      manager.getNext(PopupType.MODAL);
      const topmost = manager.getTopmostType();
      expect(topmost).toBe(PopupType.MODAL);
    });

    it('应该返回z-index最大的类型', () => {
      manager.getNext(PopupType.DROPDOWN); // 1050
      manager.getNext(PopupType.DRAWER);   // 1100
      manager.getNext(PopupType.MODAL);    // 1200

      const topmost = manager.getTopmostType();
      expect(topmost).toBe(PopupType.MODAL);
    });

    it('应该正确处理相同类型嵌套', () => {
      manager.getNext(PopupType.MODAL); // 1200
      manager.getNext(PopupType.MODAL); // 1210
      manager.getNext(PopupType.DRAWER); // 1100

      const topmost = manager.getTopmostType();
      expect(topmost).toBe(PopupType.MODAL);
    });

    it('应该在释放后返回正确的顶层类型', () => {
      manager.getNext(PopupType.DROPDOWN); // 1050
      manager.getNext(PopupType.DRAWER);   // 1100
      manager.getNext(PopupType.MODAL);    // 1200

      manager.release(PopupType.MODAL);

      const topmost = manager.getTopmostType();
      expect(topmost).toBe(PopupType.DRAWER);
    });
  });
});
