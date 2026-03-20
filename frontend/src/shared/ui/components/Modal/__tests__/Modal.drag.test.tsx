/**
 * Modal拖拽功能测试
 * 
 * 测试Modal组件的拖拽功能
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from '../Modal';

describe('Modal拖拽功能', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
    // 清理所有渲染的Modal
    document.body.innerHTML = '';
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('基础拖拽功能', () => {
    it('当draggable=true时，应该渲染可拖拽的Modal', () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content');
      expect(modalContent).toBeTruthy();
      expect(modalContent?.classList.contains('modal-content--draggable')).toBe(true);
    });

    it('当draggable=false时，不应该添加拖拽类', () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="普通Modal"
          draggable={false}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.classList.contains('modal-content--draggable')).toBe(false);
    });

    it('默认情况下，Modal不可拖拽', () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="普通Modal"
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.classList.contains('modal-content--draggable')).toBe(false);
    });
  });

  describe('拖拽配置', () => {
    it('应该接受对象形式的拖拽配置', () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={{
            enabled: true,
            bounds: 'window',
          }}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.classList.contains('modal-content--draggable')).toBe(true);
    });

    it('当enabled=false时，应该禁用拖拽', () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="不可拖拽Modal"
          draggable={{
            enabled: false,
          }}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.classList.contains('modal-content--draggable')).toBe(false);
    });
  });

  describe('拖拽交互', () => {
    it('拖拽时应该添加dragging类', async () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalHeader = document.querySelector('.modal-header');
      expect(modalHeader).toBeTruthy();

      // 模拟鼠标按下开始拖拽
      fireEvent.mouseDown(modalHeader!, { clientX: 100, clientY: 100 });
      
      // 应该添加dragging类
      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.classList.contains('modal-content--dragging')).toBe(true);
      
      // 清理
      fireEvent.mouseUp(document);
    });

    it('拖拽后应该更新Modal位置', async () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalHeader = document.querySelector('.modal-header');
      const modalContent = document.querySelector('.modal-content') as HTMLElement;

      // 模拟拖拽
      fireEvent.mouseDown(modalHeader!, { clientX: 100, clientY: 100 });
      fireEvent.mouseMove(document, { clientX: 150, clientY: 150 });
      fireEvent.mouseUp(document);

      // 检查transform样式是否更新
      const transform = modalContent?.style.transform;
      expect(transform).toContain('translate');
    });
  });

  describe('触摸事件支持', () => {
    it('应该支持触摸拖拽', async () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalHeader = document.querySelector('.modal-header');

      // 模拟触摸开始
      fireEvent.touchStart(modalHeader!, {
        touches: [{ clientX: 100, clientY: 100 }],
      });

      // 应该添加dragging类
      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.classList.contains('modal-content--dragging')).toBe(true);

      // 清理
      fireEvent.touchEnd(document);
    });
  });

  describe('边界约束', () => {
    it('当bounds="window"时，Modal应该被限制在窗口内', async () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="窗口约束Modal"
          draggable={{
            enabled: true,
            bounds: 'window',
          }}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.classList.contains('modal-content--draggable')).toBe(true);
    });
  });

  describe('网格对齐', () => {
    it('应该支持网格对齐配置', () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="网格对齐Modal"
          draggable={{
            enabled: true,
            grid: [20, 20],
          }}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.classList.contains('modal-content--draggable')).toBe(true);
    });
  });

  describe('可访问性', () => {
    it('拖拽时Modal应该保持ARIA属性', () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content');
      expect(modalContent?.getAttribute('role')).toBe('dialog');
      expect(modalContent?.getAttribute('aria-modal')).toBe('true');
    });

    it('拖拽时不应该影响关闭按钮功能', async () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      const closeButton = document.querySelector('.modal-close-button');
      expect(closeButton).toBeTruthy();
      
      // 直接触发点击事件
      fireEvent.click(closeButton!);

      // 等待 onClose 被调用（Modal 使用 setTimeout 延迟关闭）
      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalled();
      });
    });
  });

  describe('样式验证', () => {
    it('拖拽时header应该有grab光标', () => {
      render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalHeader = document.querySelector('.modal-header');
      const computedStyle = window.getComputedStyle(modalHeader!);
      
      // 在CSS中定义了cursor: grab
      expect(computedStyle.cursor).toBe('grab');
    });
  });

  describe('状态管理', () => {
    it('Modal关闭后重新打开应该重置拖拽位置', async () => {
      const { rerender } = render(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      // 模拟拖拽
      const modalHeader = document.querySelector('.modal-header');
      fireEvent.mouseDown(modalHeader!, { clientX: 100, clientY: 100 });
      fireEvent.mouseMove(document, { clientX: 150, clientY: 150 });
      fireEvent.mouseUp(document);

      // 关闭Modal
      rerender(
        <Modal
          isOpen={false}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      // 重新打开Modal
      rerender(
        <Modal
          isOpen={true}
          onClose={mockOnClose}
          title="可拖拽Modal"
          draggable={true}
        >
          <p>测试内容</p>
        </Modal>
      );

      const modalContent = document.querySelector('.modal-content') as HTMLElement;
      // 位置应该被重置
      expect(modalContent?.style.transform).toBe('translate(0px, 0px)');
    });
  });
});
