/**
 * Modal Component Types
 * 
 * 统一Modal组件的类型定义
 * 遵循WCAG 2.1 AA无障碍标准
 */

import type { ReactNode } from 'react';

/**
 * Modal尺寸类型
 * 
 * @description 定义Modal的不同尺寸预设
 */
export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

/**
 * Modal动画类型
 * 
 * @description 定义Modal的进入/退出动画效果
 */
export type ModalAnimation = 'slideUp' | 'fadeIn' | 'scale' | 'none';

/**
 * Modal变体类型
 * 
 * @description 定义不同语义的Modal样式变体
 */
export type ModalVariant = 'default' | 'danger' | 'warning' | 'success' | 'info';

/**
 * 关闭前确认配置
 * 
 * @description 配置关闭前的确认对话框
 */
export interface ModalConfirmConfig {
  /** 确认对话框标题，默认"确认关闭" */
  title?: string;
  /** 确认对话框消息，默认"有未保存的内容，确定要关闭吗？" */
  message?: string;
  /** 确认按钮文字，默认"放弃修改" */
  confirmText?: string;
  /** 取消按钮文字，默认"继续编辑" */
  cancelText?: string;
}

/**
 * Modal组件属性接口
 * 
 * @description Modal组件的主要属性定义
 * 
 * @example
 * ```tsx
 * <Modal
 *   isOpen={isOpen}
 *   onClose={handleClose}
 *   title="编辑用户"
 *   size="md"
 * >
 *   <UserForm />
 * </Modal>
 * ```
 */
export interface ModalProps {
  // ========== 核心属性 ==========
  /** 是否显示Modal */
  isOpen: boolean;
  /** 关闭回调函数 */
  onClose: () => void;
  /** Modal标题 */
  title?: string;
  /** Modal内容 */
  children: ReactNode;

  // ========== 尺寸与布局 ==========
  /** Modal尺寸，默认'md' */
  size?: ModalSize;
  /** 是否全屏显示，移动端默认为true */
  fullScreen?: boolean;

  // ========== 样式与动画 ==========
  /** 动画类型，默认'slideUp' */
  animation?: ModalAnimation;
  /** 是否启用毛玻璃效果，默认false */
  glassmorphism?: boolean;
  /** Modal变体，默认'default' */
  variant?: ModalVariant;
  /** 遮罩层className */
  overlayClassName?: string;
  /** Modal内容区域className */
  className?: string;
  /** Modal内容区域内联样式 */
  style?: React.CSSProperties;
  /** 自定义z-index */
  zIndex?: number;

  // ========== 交互控制 ==========
  /** 是否启用ESC键关闭，默认true */
  enableEscClose?: boolean;
  /** 是否启用点击遮罩层关闭，默认true */
  closeOnBackdropClick?: boolean;
  /** 关闭前的确认回调，返回true允许关闭，返回false显示确认对话框 */
  onBeforeClose?: () => boolean | Promise<boolean>;
  /** 确认对话框配置 */
  confirmConfig?: ModalConfirmConfig;

  // ========== 显示控制 ==========
  /** 是否显示头部，默认true */
  showHeader?: boolean;
  /** 是否显示关闭按钮，默认true */
  showCloseButton?: boolean;
  /** 是否显示底部，默认false */
  showFooter?: boolean;
  /** 底部内容 */
  footer?: ReactNode;

  // ========== 生命周期回调 ==========
  /** Modal打开后的回调 */
  onAfterOpen?: () => void;
  /** Modal关闭后的回调 */
  onAfterClose?: () => void;

  // ========== 无障碍性 ==========
  /** 自定义ARIA描述 */
  ariaDescribedby?: string;
  /** 自定义ARIA标签 */
  ariaLabelledby?: string;

  // ========== 拖拽功能 ==========
  /** 是否启用拖拽，或详细拖拽配置 */
  draggable?: boolean | ModalDragConfig;
}

/**
 * Modal拖拽配置
 * 
 * @description 配置Modal的拖拽行为
 */
export interface ModalDragConfig {
  /** 是否启用拖拽，默认true */
  enabled?: boolean;
  /** 拖拽边界约束：'parent', 'window', 或自定义HTMLElement */
  bounds?: 'parent' | 'window' | HTMLElement;
  /** 网格对齐：[x, y] 步进值 */
  grid?: [number, number];
}

/**
 * useModal Hook返回值类型
 * 
 * @description 提供Modal状态管理的Hook返回值
 */
export interface UseModalReturn {
  /** Modal是否打开 */
  isOpen: boolean;
  /** 打开Modal */
  open: () => void;
  /** 关闭Modal */
  close: () => void;
  /** 切换Modal状态 */
  toggle: () => void;
}
