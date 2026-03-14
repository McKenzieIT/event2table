/**
 * 全局类型定义
 *
 * 这些类型定义在整个应用中可用，无需导入
 * 为JavaScript文件提供类型提示（通过JSDoc）和TypeScript文件提供类型支持
 */

import { ReactNode, ButtonHTMLAttributes, ForwardRefRenderFunction } from 'react';

/**
 * API响应标准格式
 */
export interface APIResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  timestamp?: string;
}

/**
 * Button组件属性
 */
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children?: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline-primary' | 'outline-danger' | 'success' | 'warning' | 'info';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ComponentType;
  className?: string;
}

/**
 * 声明Button组件类型
 */
declare module 'react' {
  function forwardRef<T extends HTMLButtonElement, P = {}>(
    render: (props: P, ref: React.Ref<T>) => React.ReactElement | null
  ): ForwardRefRenderFunction<T, P>;
}

/**
 * 分页响应格式
 */
export interface PaginatedResponse<T> extends APIResponse<T[]> {
  pagination?: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

/**
 * 游戏对象 - Import from @/shared/types/game-types
 * Re-exporting for global availability
 */
export type { Game } from '../shared/types/game-types';

/**
 * 事件对象 - Import from @/shared/types/event-types
 * Re-exporting for global availability
 */
export type { Event } from '../shared/types/event-types';

/**
 * 参数对象 - Import from @/shared/types/parameter-types
 * Re-exporting for global availability
 */
export type { Parameter } from '../shared/types/parameter-types';

/**
 * Canvas节点对象
 */
export interface CanvasNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

/**
 * HQL生成结果
 */
export interface HQLResult {
  hql: string;
  success: boolean;
  message?: string;
  execution_time?: number;
}

/**
 * 全局window对象扩展
 */
declare global {
  interface Window {
    /**
     * 当前游戏数据
     */
    gameData?: Game;

    /**
     * 事件列表数据
     */
    eventsData?: Event[];

    /**
     * 参数列表数据
     */
    parametersData?: Parameter[];

    /**
     * Canvas节点数据
     */
    canvasNodes?: CanvasNode[];

    /**
     * 当前选中的游戏GID
     */
    currentGameGid?: number;

    /**
     * API基础URL
     */
    API_BASE?: string;

    /**
     * 传统API基础URL（向后兼容）
     */
    LEGACY_API_BASE?: string;
  }
}

/**
 * 导出空对象以启用全局类型扩展
 */
export {};
