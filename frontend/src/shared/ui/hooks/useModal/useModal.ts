/**
 * useModal Hook
 * 
 * 提供Modal状态管理的便捷Hook
 * 遵循React最佳实践
 * 
 * @features
 * - 简洁的状态管理API
 * - 支持初始状态配置
 * - TypeScript类型安全
 */

import type { UseModalReturn } from '@shared/ui/components/Modal/Modal.types';
import { useState, useCallback } from 'react';

/**
 * useModal Hook选项
 */
export interface UseModalOptions {
  /** 初始是否打开，默认false */
  defaultOpen?: boolean;
  /** 关闭后的回调 */
  onClose?: () => void;
  /** 打开后的回调 */
  onOpen?: () => void;
}

/**
 * useModal Hook
 * 
 * @description 提供Modal的打开、关闭、切换功能
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const modal = useModal();
 *   
 *   return (
 *     <>
 *       <button onClick={modal.open}>打开Modal</button>
 *       <Modal
 *         isOpen={modal.isOpen}
 *         onClose={modal.close}
 *         title="示例Modal"
 *       >
 *         <p>Modal内容</p>
 *       </Modal>
 *     </>
 *   );
 * }
 * ```
 * 
 * @example 带回调
 * ```tsx
 * const modal = useModal({
 *   onOpen: () => console.log('Modal打开'),
 *   onClose: () => console.log('Modal关闭'),
 * });
 * ```
 */
export function useModal(options: UseModalOptions = {}): UseModalReturn {
  const {
    defaultOpen = false,
    onClose,
    onOpen,
  } = options;

  const [isOpen, setIsOpen] = useState(defaultOpen);

  // 打开Modal
  const open = useCallback(() => {
    setIsOpen(true);
    onOpen?.();
  }, [onOpen]);

  // 关闭Modal
  const close = useCallback(() => {
    setIsOpen(false);
    onClose?.();
  }, [onClose]);

  // 切换Modal状态
  const toggle = useCallback(() => {
    setIsOpen(prev => {
      if (prev) {
        onClose?.();
        return false;
      } else {
        onOpen?.();
        return true;
      }
    });
  }, [onOpen, onClose]);

  return {
    isOpen,
    open,
    close,
    toggle,
  };
}

export default useModal;
