// @ts-nocheck - TypeScript检查暂禁用
/**
 * BaseModal Component
 * 统一基础模态框组件
 *
 * @description 提供ESC关闭、点击背景关闭、焦点管理等功能的模态框基础组件
 */

import React, { useState, useEffect, useRef, ReactNode } from 'react';
import { useEscHandlerWithClosing } from './useEscHandler';
import ConfirmDialog from './ConfirmDialog';
import { MODAL_ANIMATION_DELAY } from '@shared/constants/timeouts';
import { Z_INDICES } from '@shared/constants/zIndices';
import './BaseModal.css';

/**
 * 动画类型
 */
export type ModalAnimation = 'slideUp' | 'fadeIn' | 'none';

/**
 * 尺寸类型
 */
export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

/**
 * 变体类型
 */
export type ModalVariant = 'default' | 'danger' | 'warning';

/**
 * 确认对话框配置
 */
export interface ConfirmConfig {
  /** 对话框标题，默认"确认关闭" */
  title?: string;
  /** 对话框消息，默认"有未保存的内容，确定要关闭吗？" */
  message?: string;
  /** 确认按钮文字，默认"放弃修改" */
  confirmText?: string;
  /** 取消按钮文字，默认"继续编辑" */
  cancelText?: string;
}

/**
 * 组件属性
 */
export interface BaseModalProps {
  /** 是否显示模态框 */
  isOpen: boolean;
  /** 关闭回调函数 */
  onClose: () => void;
  /** 子组件 */
  children: ReactNode;
  /** 模态框标题 */
  title?: string;

  // ESC关闭控制
  /** 是否启用ESC键关闭，默认true */
  enableEscClose?: boolean;
  /** 关闭前确认回调，返回true允许关闭，返回false显示确认对话框 */
  onBeforeClose?: () => boolean | Promise<boolean>;
  /** 确认对话框配置 */
  confirmConfig?: ConfirmConfig;

  // 样式
  /** 背景遮罩的className */
  overlayClassName?: string;
  /** 内容区域的className (别名，与contentClassName相同) */
  className?: string;
  /** 内容区域的className */
  contentClassName?: string;
  /** 内容区域的内联样式 */
  contentStyle?: React.CSSProperties;
  /** 背景遮罩的z-index，默认1050 */
  zIndex?: number;

  // 新增样式属性
  /** 动画类型，默认slideUp */
  animation?: ModalAnimation;
  /** 是否启用毛玻璃效果，默认false */
  glassmorphism?: boolean;
  /** 模态框尺寸，默认md */
  size?: ModalSize;
  /** 模态框变体，默认default */
  variant?: ModalVariant;

  // 其他
  /** 点击背景是否关闭，默认true */
  closeOnBackdropClick?: boolean;
  /** 模态框关闭时的回调 */
  onAfterClose?: () => void;
  /** 是否显示header，默认true */
  showHeader?: boolean;
  /** 是否显示关闭按钮，默认true */
  showCloseButton?: boolean;
}

/**
 * BaseModal组件
 */
export const BaseModal = React.memo(function BaseModal({
  isOpen,
  onClose,
  title,
  children,
  enableEscClose = true,
  onBeforeClose,
  confirmConfig = {},
  overlayClassName = '',
  className = '',
  contentClassName = '',
  contentStyle,
  zIndex = Z_INDICES.MODAL,
  animation = 'slideUp',
  glassmorphism = false,
  size = 'md',
  variant = 'default',
  closeOnBackdropClick = true,
  onAfterClose,
  showHeader = true,
  showCloseButton = true,
}: BaseModalProps) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [wasOpen, setWasOpen] = useState(false);
  const triggerElementRef = useRef<HTMLElement | null>(null);
  const modalContentRef = useRef<HTMLDivElement>(null);

  // 构建遮罩层className
  const overlayClasses = [
    'modal-overlay',
    animation === 'fadeIn' && 'modal-overlay--fadeIn',
    glassmorphism && 'modal-overlay--glassmorphism',
    overlayClassName,
  ].filter(Boolean).join(' ');

  // 构建内容className
  const contentClasses = [
    'modal-content',
    `modal-content--${animation}`,
    glassmorphism && 'modal-content--glassmorphism',
    `modal-content--${size}`,
    `modal-content--${variant}`,
    className, // 支持通用的 className prop
    contentClassName, // 支持特定的 contentClassName prop
  ].filter(Boolean).join(' ');

  // 确认对话框默认配置
  const defaultConfirmConfig: Required<ConfirmConfig> = {
    title: confirmConfig.title || '确认关闭',
    message: confirmConfig.message || '有未保存的内容，确定要关闭吗？',
    confirmText: confirmConfig.confirmText || '放弃修改',
    cancelText: confirmConfig.cancelText || '继续编辑',
  };

  // 处理关闭逻辑
  const handleClose = async () => {
    // 如果正在关闭中，忽略关闭请求
    if (isClosing) return;

    // 如果有关闭前确认回调
    if (onBeforeClose) {
      const canClose = await onBeforeClose();
      if (!canClose) {
        // 不能关闭，显示确认对话框
        setShowConfirm(true);
        return;
      }
    }

    // 执行关闭
    performClose();
  };

  // 执行实际的关闭操作
  const performClose = () => {
    setIsClosing(true);
    setShowConfirm(false);

    // 延迟一点时间让关闭动画播放
    setTimeout(() => {
      onClose();
      setIsClosing(false);
      onAfterClose?.();
    }, MODAL_ANIMATION_DELAY);
  };

  // 处理确认对话框的确认操作
  const handleConfirm = () => {
    setShowConfirm(false);
    performClose();
  };

  // 处理确认对话框的取消操作
  const handleCancelConfirm = () => {
    setShowConfirm(false);
  };

  // 处理背景点击
  const handleBackdropClick = () => {
    if (closeOnBackdropClick && !isClosing) {
      handleClose();
    }
  };

  // ESC键处理
  useEscHandlerWithClosing(isClosing, handleClose, {
    enabled: enableEscClose && isOpen && !showConfirm,
  });

  // 焦点陷阱 - 防止Tab键焦点跳出模态框
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      const modal = modalContentRef.current;
      if (!modal) return;

      // 获取模态框内所有可聚焦元素
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

      // 如果焦点在最后一个元素且按Tab，则跳到第一个
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement?.focus();
      } 
      // 如果焦点在第一个元素且按Shift+Tab，则跳到最后一个
      else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // 焦点管理
  useEffect(() => {
    if (isOpen) {
      // 保存当前焦点元素
      triggerElementRef.current = document.activeElement as HTMLElement;

      // 将焦点移到模态框
      setTimeout(() => {
        modalContentRef.current?.focus();
      }, 50);

      setWasOpen(true);
    } else if (wasOpen) {
      // 模态框关闭时，恢复焦点到触发元素
      triggerElementRef.current?.focus();
      setWasOpen(false);
    }
  }, [isOpen, wasOpen]);

  // 如果模态框未打开，不渲染任何内容
  if (!isOpen) return null;

  return (
    <>
      {/* 背景遮罩 */}
      <div
        className={overlayClasses}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex,
        }}
        onClick={handleBackdropClick}
      >
        {/* 模态框内容 */}
        <div
          ref={modalContentRef}
          className={contentClasses}
          style={{
            outline: 'none',
            display: 'flex',
            flexDirection: 'column',
            ...contentStyle,
          }}
          onClick={(e) => e.stopPropagation()}
          tabIndex={-1}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? "modal-title" : undefined}
        >
          {/* Header: 标题 + 关闭按钮 */}
          {showHeader && (
            <div className="modal-header">
              <h2 className="modal-title" id="modal-title">
                {title}
              </h2>
              {showCloseButton && (
                <button
                  className="modal-close"
                  onClick={handleClose}
                  aria-label="关闭对话框"
                  type="button"
                >
                  ✕
                </button>
              )}
            </div>
          )}
          
          {/* Body: 内容区域 */}
          <div className="modal-body">
            {children}
          </div>
        </div>
      </div>

      {/* 确认对话框 */}
      <ConfirmDialog
        isOpen={showConfirm}
        title={defaultConfirmConfig.title}
        message={defaultConfirmConfig.message}
        confirmText={defaultConfirmConfig.confirmText}
        cancelText={defaultConfirmConfig.cancelText}
        onConfirm={handleConfirm}
        onCancel={handleCancelConfirm}
        type="warning"
      />
    </>
  );
});

export default BaseModal;
