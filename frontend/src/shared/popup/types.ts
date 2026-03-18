/**
 * 统一弹窗管理系统 - 类型定义
 */

import { PopupType } from './ZIndexManager';

/**
 * 弹窗配置接口
 */
export interface PopupConfig {
  /** 唯一标识 */
  id: string;
  /** 弹窗类型 */
  type: PopupType;
  /** 开关状态 */
  isOpen: boolean;
  /** 优先级（影响z-index） */
  priority: number;
  /** 是否启用ESC */
  enableEsc: boolean;
  /** 是否启用焦点陷阱 */
  enableFocusTrap: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 计算后的z-index（由Manager分配） */
  zIndex?: number;
}

/**
 * 全局状态接口
 */
export interface PopupState {
  /** 所有活跃弹窗 */
  popups: Map<string, PopupConfig>;
  /** 最顶层弹窗ID */
  topmostId: string | null;
}

/**
 * PopupContext值接口
 */
export interface PopupContextValue {
  /** 注册弹窗 */
  register: (config: PopupConfig) => void;
  /** 注销弹窗 */
  unregister: (id: string) => void;
  /** 获取z-index */
  getZIndex: (id: string) => number;
  /** 获取最顶层弹窗ID */
  getTopmostId: () => string | null;
}

/**
 * 焦点策略接口
 */
export interface FocusStrategy {
  /** 是否启用焦点陷阱 */
  trap: boolean;
  /** 关闭时是否恢复焦点 */
  restoreOnClose: boolean;
  /** 是否自动聚焦 */
  autoFocus: boolean;
  /** Tab键是否循环 */
  tabCycle: boolean;
  /** 是否支持箭头键 */
  arrowKeys?: boolean;
}

/**
 * 各组件类型的焦点策略
 */
export const FOCUS_STRATEGIES: Record<PopupType, FocusStrategy> = {
  [PopupType.MODAL]: {
    trap: true,
    restoreOnClose: true,
    autoFocus: true,
    tabCycle: true,
  },
  [PopupType.DRAWER]: {
    trap: false,
    restoreOnClose: true,
    autoFocus: true,
    tabCycle: false,
  },
  [PopupType.DROPDOWN]: {
    trap: false,
    restoreOnClose: true,
    autoFocus: true,
    tabCycle: true,
    arrowKeys: true,
  },
};
