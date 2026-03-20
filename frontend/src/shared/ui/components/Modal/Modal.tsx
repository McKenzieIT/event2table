/**
 * Modal Component
 * 
 * 统一Modal组件实现
 * 遵循React最佳实践和WCAG 2.1 AA无障碍标准
 * 
 * @features
 * - ESC键关闭
 * - 点击遮罩层关闭
 * - 焦点陷阱（Focus Trap）
 * - 焦点恢复（Focus Restoration）
 * - 键盘导航支持
 * - ARIA属性完整支持
 * - 性能优化（useCallback, useMemo, React.memo）
 */

import React, { 
  useState, 
  useEffect, 
  useRef, 
  useCallback, 
  useMemo,
  type ReactNode 
} from 'react';
import type { 
  ModalProps, 
  ModalSize, 
  ModalAnimation, 
  ModalVariant,
  ModalConfirmConfig 
} from './Modal.types';
import { MODAL_ANIMATION_DELAY } from '@shared/constants/timeouts';
import { Z_INDICES } from '@shared/constants/zIndices';
import './Modal.css';

// 默认确认对话框配置
const DEFAULT_CONFIRM_CONFIG: Required<ModalConfirmConfig> = {
  title: '确认关闭',
  message: '有未保存的内容，确定要关闭吗？',
  confirmText: '放弃修改',
  cancelText: '继续编辑',
};

/**
 * Modal组件
 * 
 * @description 提供完整的Modal功能，支持多种尺寸、动画和变体
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const [isOpen, setIsOpen] = useState(false);
 *   
 *   return (
 *     <Modal
 *       isOpen={isOpen}
 *       onClose={() => setIsOpen(false)}
 *       title="编辑用户"
 *       size="md"
 *     >
 *       <UserForm />
 *     </Modal>
 *   );
 * }
 * ```
 */
export const Modal = React.memo(function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  fullScreen = false,
  animation = 'slideUp',
  glassmorphism = false,
  variant = 'default',
  overlayClassName = '',
  className = '',
  style,
  zIndex = Z_INDICES.MODAL,
  enableEscClose = true,
  closeOnBackdropClick = true,
  onBeforeClose,
  confirmConfig = {},
  showHeader = true,
  showCloseButton = true,
  showFooter = false,
  footer,
  onAfterOpen,
  onAfterClose,
  ariaDescribedby,
  ariaLabelledby,
}: ModalProps) {
  // ========== 状态管理 ==========
  const [showConfirm, setShowConfirm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [wasOpen, setWasOpen] = useState(false);

  // ========== Refs ==========
  const triggerElementRef = useRef<HTMLElement | null>(null);
  const modalContentRef = useRef<HTMLDivElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  // ========== 性能优化：useMemo ==========
  
  // 缓存确认对话框配置
  const finalConfirmConfig = useMemo<Required<ModalConfirmConfig>>(() => ({
    title: confirmConfig.title || DEFAULT_CONFIRM_CONFIG.title,
    message: confirmConfig.message || DEFAULT_CONFIRM_CONFIG.message,
    confirmText: confirmConfig.confirmText || DEFAULT_CONFIRM_CONFIG.confirmText,
    cancelText: confirmConfig.cancelText || DEFAULT_CONFIRM_CONFIG.cancelText,
  }), [confirmConfig]);

  // 缓存遮罩层className
  const overlayClasses = useMemo(() => {
    const classes = ['modal-overlay'];
    
    // 添加动画类
    if (animation !== 'none') {
      classes.push(`modal-overlay--${animation}`);
    }
    
    // 添加毛玻璃效果
    if (glassmorphism) {
      classes.push('modal-overlay--glassmorphism');
    }
    
    // 添加自定义className
    if (overlayClassName) {
      classes.push(overlayClassName);
    }
    
    return classes.join(' ');
  }, [animation, glassmorphism, overlayClassName]);

  // 缓存Modal内容className
  const modalClasses = useMemo(() => {
    const classes = ['modal-content'];
    
    // 添加尺寸类
    if (!fullScreen) {
      classes.push(`modal-content--${size}`);
    } else {
      classes.push('modal-content--full');
    }
    
    // 添加动画类
    if (animation !== 'none') {
      classes.push(`modal-content--${animation}`);
    }
    
    // 添加毛玻璃效果
    if (glassmorphism) {
      classes.push('modal-content--glassmorphism');
    }
    
    // 添加变体类
    if (variant !== 'default') {
      classes.push(`modal-content--${variant}`);
    }
    
    // 添加自定义className
    if (className) {
      classes.push(className);
    }
    
    return classes.join(' ');
  }, [size, fullScreen, animation, glassmorphism, variant, className]);

  // ========== 性能优化：useCallback ==========
  
  // 处理关闭请求
  const handleClose = useCallback(async () => {
    // 如果正在关闭中，忽略关闭请求
    if (isClosing) return;

    // 如果有关闭前确认回调
    if (onBeforeClose) {
      try {
        const canClose = await onBeforeClose();
        if (!canClose) {
          // 不能关闭，显示确认对话框
          setShowConfirm(true);
          return;
        }
      } catch (error) {
        console.error('Error in onBeforeClose:', error);
        // 出错时允许关闭
      }
    }

    // 执行关闭
    performClose();
  }, [isClosing, onBeforeClose]);

  // 执行关闭操作
  const performClose = useCallback(() => {
    setIsClosing(true);
    setShowConfirm(false);

    // 延迟关闭以播放动画
    setTimeout(() => {
      onClose();
      setIsClosing(false);
      onAfterClose?.();
    }, MODAL_ANIMATION_DELAY);
  }, [onClose, onAfterClose]);

  // 确认关闭
  const handleConfirm = useCallback(() => {
    setShowConfirm(false);
    performClose();
  }, [performClose]);

  // 取消确认
  const handleCancelConfirm = useCallback(() => {
    setShowConfirm(false);
  }, []);

  // 处理遮罩层点击
  const handleBackdropClick = useCallback((e: React.MouseEvent) => {
    // 只有点击遮罩层本身才关闭，点击Modal内容不关闭
    if (closeOnBackdropClick && !isClosing && e.target === overlayRef.current) {
      handleClose();
    }
  }, [closeOnBackdropClick, isClosing, handleClose]);

  // ========== ESC键处理 ==========
  useEffect(() => {
    if (!enableEscClose || !isOpen || showConfirm || isClosing) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        handleClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown, { capture: true });
    return () => document.removeEventListener('keydown', handleKeyDown, { capture: true });
  }, [enableEscClose, isOpen, showConfirm, isClosing, handleClose]);

  // ========== 焦点陷阱（Focus Trap）==========
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      const modal = modalContentRef.current;
      if (!modal) return;

      // 获取所有可聚焦元素
      const focusableSelectors = [
        'button:not([disabled])',
        'input:not([disabled])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        'a[href]',
        '[tabindex]:not([tabindex="-1"])',
      ].join(', ');

      const focusableElements = modal.querySelectorAll<HTMLElement>(focusableSelectors);
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (!firstElement || !lastElement) return;

      // Shift+Tab: 焦点在第一个元素时，跳到最后一个
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
      // Tab: 焦点在最后一个元素时，跳到第一个
      else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // ========== 焦点管理 ==========
  useEffect(() => {
    if (isOpen) {
      // 保存当前焦点元素
      triggerElementRef.current = document.activeElement as HTMLElement;

      // 将焦点移到Modal
      // 使用setTimeout确保DOM已更新
      setTimeout(() => {
        modalContentRef.current?.focus();
      }, 50);

      setWasOpen(true);
      onAfterOpen?.();
    } else if (wasOpen) {
      // Modal关闭时，恢复焦点到触发元素
      triggerElementRef.current?.focus();
      setWasOpen(false);
    }
  }, [isOpen, wasOpen, onAfterOpen]);

  // ========== 滚动锁定 ==========
  useEffect(() => {
    if (isOpen) {
      // 禁用body滚动
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${window.innerWidth - document.body.clientWidth}px`;
    } else {
      // 恢复body滚动
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }

    return () => {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    };
  }, [isOpen]);

  // ========== 渲染 ==========
  
  // 如果Modal未打开，不渲染任何内容
  if (!isOpen) return null;

  // 生成ARIA属性
  const ariaProps = {
    'role': 'dialog' as const,
    'aria-modal': 'true' as const,
    'aria-labelledby': ariaLabelledby || (title ? 'modal-title' : undefined),
    'aria-describedby': ariaDescribedby,
  };

  return (
    <>
      {/* 遮罩层 */}
      <div
        ref={overlayRef}
        className={overlayClasses}
        style={{ zIndex }}
        onClick={handleBackdropClick}
        aria-hidden="true"
      >
        {/* Modal内容 */}
        <div
          ref={modalContentRef}
          className={modalClasses}
          style={style}
          onClick={(e) => e.stopPropagation()}
          tabIndex={-1}
          {...ariaProps}
        >
          {/* Header */}
          {showHeader && (
            <div className="modal-header">
              <h2 
                className="modal-title" 
                id="modal-title"
              >
                {title}
              </h2>
              {showCloseButton && (
                <button
                  className="modal-close-button"
                  onClick={handleClose}
                  aria-label="关闭对话框"
                  type="button"
                >
                  <span aria-hidden="true">✕</span>
                </button>
              )}
            </div>
          )}

          {/* Body */}
          <div className="modal-body">
            {children}
          </div>

          {/* Footer */}
          {showFooter && (
            <div className="modal-footer">
              {footer}
            </div>
          )}
        </div>
      </div>

      {/* 确认对话框 */}
      {showConfirm && (
        <div className="modal-confirm-backdrop" style={{ zIndex: zIndex + 1 }}>
          <div className="modal-confirm" role="alertdialog" aria-modal="true">
            <h3 className="modal-confirm-title">{finalConfirmConfig.title}</h3>
            <p className="modal-confirm-message">{finalConfirmConfig.message}</p>
            <div className="modal-confirm-actions">
              <button
                className="modal-confirm-button modal-confirm-button--cancel"
                onClick={handleCancelConfirm}
                type="button"
              >
                {finalConfirmConfig.cancelText}
              </button>
              <button
                className="modal-confirm-button modal-confirm-button--confirm"
                onClick={handleConfirm}
                type="button"
              >
                {finalConfirmConfig.confirmText}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
});

Modal.displayName = 'Modal';

export default Modal;
