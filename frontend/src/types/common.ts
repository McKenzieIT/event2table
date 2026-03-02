/**
 * Common Type Definitions
 *
 * 共享类型定义，提供全应用可复用的类型
 * 避免重复定义，提升类型安全性
 */

import type { ReactNode, ComponentType, MouseEvent, ChangeEvent, FocusEvent } from 'react';

// ============================================================================
// API Response Types
// ============================================================================

/**
 * 标准API响应格式
 * @template T - 响应数据类型
 */
export interface ApiResponse<T = unknown> {
  /** 请求是否成功 */
  success: boolean;
  /** 响应数据 */
  data?: T;
  /** 错误信息 */
  error?: string;
  /** 提示消息 */
  message?: string;
  /** 时间戳 */
  timestamp?: string;
}

/**
 * 分页响应格式
 * @template T - 列表项类型
 */
export interface PaginatedApiResponse<T = unknown> extends ApiResponse<T[]> {
  /** 分页信息 */
  pagination?: {
    /** 当前页码 */
    page: number;
    /** 每页数量 */
    page_size: number;
    /** 总记录数 */
    total: number;
    /** 总页数 */
    total_pages: number;
  };
}

// ============================================================================
// Game & Domain Types
// ============================================================================

/**
 * 游戏上下文类型
 */
export interface GameContext {
  /** 游戏业务GID */
  gid: number;
  /** 游戏名称 */
  name: string;
  /** ODS数据库名称 */
  ods_db: string;
  /** 游戏描述 */
  description?: string;
  /** DWD表前缀 */
  dwd_prefix?: string;
}

/**
 * 路由上下文类型
 */
export interface RouterContext {
  /** 当前选中的游戏 */
  currentGame?: GameContext;
  /** 当前游戏GID (向后兼容) */
  currentGameGid?: number;
}

// ============================================================================
// Event Handler Types
// ============================================================================

/**
 * 事件处理器类型 - 泛型版本
 * @template TEvent - 事件类型
 * @template TReturn - 返回值类型
 */
export type EventHandler<TEvent = Event, TReturn = void> = (event: TEvent) => TReturn;

/**
 * 异步函数类型
 * @template T - 返回值类型
 * @template P - 参数类型元组
 */
export type AsyncFunction<T = void, P extends unknown[] = []> = (...args: P) => Promise<T>;

/**
 * 鼠标事件处理器
 */
export type MouseEventHandler = EventHandler<MouseEvent>;

/**
 * 变更事件处理器
 * @template T - 目标元素类型
 */
export type ChangeEventHandler<T = Element> = EventHandler<ChangeEvent<T>>;

/**
 * 焦点事件处理器
 */
export type FocusEventHandler = EventHandler<FocusEvent>;

/**
 * 点击回调函数类型
 */
export type ClickCallback = (event: MouseEvent) => void | Promise<void>;

/**
 * 值变更回调函数类型
 * @template T - 值类型
 */
export type ValueChangeCallback<T = string | number> = (value: T) => void;

// ============================================================================
// UI Component Types
// ============================================================================

/**
 * 基础尺寸类型
 */
export type Size = 'sm' | 'md' | 'lg';

/**
 * 变体类型
 */
export type Variant =
  | 'primary'
  | 'secondary'
  | 'ghost'
  | 'danger'
  | 'outline-primary'
  | 'outline-danger'
  | 'success'
  | 'warning'
  | 'info';

/**
 * 优先级类型
 */
export type Priority = 'high' | 'medium' | 'low';

/**
 * 状态类型
 */
export type Status = 'idle' | 'loading' | 'success' | 'error';

/**
 * 图标组件类型
 */
export type IconComponent = ComponentType<{ className?: string }>;

/**
 * 可选项类型
 * @template T - 值类型
 */
export interface SelectOption<T = string | number> {
  /** 选项值 */
  value: T;
  /** 显示标签 */
  label: string;
  /** 是否禁用 */
  disabled?: boolean;
  /** 额外数据 */
  meta?: Record<string, unknown>;
}

/**
 * 加载状态类型
 */
export interface LoadingState {
  /** 是否加载中 */
  isLoading: boolean;
  /** 错误信息 */
  error?: string | null;
  /** 是否成功 */
  isSuccess: boolean;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * 可选类型 - 所有属性变为可选
 * @template T - 原始类型
 */
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * 必需类型 - 指定属性变为必需
 * @template T - 原始类型
 * @template K - 属性键
 */
export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

/**
 * 提取类型 - 仅保留指定属性
 * @template T - 原始类型
 * @template K - 属性键
 */
export type ExtractType<T, K extends keyof T> = Pick<T, K>;

/**
 * 排除类型 - 排除指定属性
 * @template T - 原始类型
 * @template K - 属性键
 */
export type ExcludeType<T, K extends keyof T> = Omit<T, K>;

/**
 * 只读类型 - 指定属性变为只读
 * @template T - 原始类型
 * @template K - 属性键
 */
export type ReadonlyBy<T, K extends keyof T> = Omit<T, K> & Readonly<Pick<T, K>>;

/**
 * 可写类型 - 指定属性变为可写
 * @template T - 原始类型
 * @template K - 属性键
 */
export type WritableBy<T, K extends keyof T> = Omit<T, K> & { [P in K]-?: T[P] };

// ============================================================================
// Type Guards
// ============================================================================

/**
 * 检查值是否为GameContext
 * @param value - 待检查的值
 */
export function isGameContext(value: unknown): value is GameContext {
  return (
    typeof value === 'object' &&
    value !== null &&
    'gid' in value &&
    'name' in value &&
    'ods_db' in value
  );
}

/**
 * 检查值是否为SelectOption
 * @param value - 待检查的值
 */
export function isSelectOption(value: unknown): value is SelectOption {
  return (
    typeof value === 'object' &&
    value !== null &&
    'value' in value &&
    'label' in value
  );
}

/**
 * 检查值是否为ApiResponse
 * @param value - 待检查的值
 */
export function isApiResponse(value: unknown): value is ApiResponse {
  return (
    typeof value === 'object' &&
    value !== null &&
    'success' in value &&
    typeof (value as ApiResponse).success === 'boolean'
  );
}

/**
 * 检查值是否为非null
 * @param value - 待检查的值
 */
export function isNotNull<T>(value: T | null): value is T {
  return value !== null;
}

/**
 * 检查值是否为非undefined
 * @param value - 待检查的值
 */
export function isNotUndefined<T>(value: T | undefined): value is T {
  return value !== undefined;
}

/**
 * 检查值是否已定义（非null且非undefined）
 * @param value - 待检查的值
 */
export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

// ============================================================================
// Performance Types
// ============================================================================

/**
 * 性能指标基础接口
 */
export interface PerformanceMetric {
  /** 时间戳 */
  timestamp: number;
  /** 持续时间(毫秒) */
  duration: number;
}

/**
 * 请求指标
 */
export interface RequestMetric extends PerformanceMetric {
  /** 请求名称或端点 */
  name: string;
  /** 请求方法 */
  method?: string;
  /** 是否来自缓存 */
  fromCache?: boolean;
  /** 请求大小(字节) */
  size?: number;
}

/**
 * 缓存统计
 */
export interface CacheStats {
  /** 缓存命中次数 */
  hits: number;
  /** 缓存未命中次数 */
  misses: number;
  /** 命中率 */
  hitRate: number;
  /** 缓存数量 */
  size: number;
}

/**
 * 性能报告
 */
export interface PerformanceReport {
  /** 报告时间戳 */
  timestamp: string;
  /** 总请求数 */
  totalRequests: number;
  /** 平均持续时间 */
  averageDuration: number;
  /** 缓存统计 */
  cacheStats: CacheStats;
  /** 优化建议 */
  recommendations: Recommendation[];
}

/**
 * 优化建议
 */
export interface Recommendation {
  /** 建议类型 */
  type: 'caching' | 'performance' | 'requests' | 'code';
  /** 优先级 */
  priority: Priority;
  /** 建议消息 */
  message: string;
  /** 相关代码位置 */
  location?: string;
}

// ============================================================================
// Common Props Types
// ============================================================================

/**
 * 基础组件Props - 包含通用属性
 */
export interface BaseComponentProps {
  /** CSS类名 */
  className?: string;
  /** 子元素 */
  children?: ReactNode;
  /** 是否禁用 */
  disabled?: boolean;
  /** 加载状态 */
  loading?: boolean;
}

/**
 * 带标签的组件Props
 */
export interface LabeledComponentProps extends BaseComponentProps {
  /** 标签文本 */
  label?: string;
  /** 是否必填 */
  required?: boolean;
  /** 提示文本 */
  helperText?: string;
  /** 错误信息 */
  error?: string;
}

/**
 * 带图标的组件Props
 */
export interface IconComponentProps extends BaseComponentProps {
  /** 图标组件 */
  icon?: IconComponent;
  /** 图标位置 */
  iconPosition?: 'left' | 'right';
}

/**
 * 可选择组件Props
 */
export interface SelectableComponentProps<T = string | number> extends BaseComponentProps {
  /** 当前值 */
  value?: T;
  /** 值变更回调 */
  onChange?: ValueChangeCallback<T>;
  /** 占位文本 */
  placeholder?: string;
  /** 选项列表 */
  options?: SelectOption<T>[];
}

// ============================================================================
// Export All
// ============================================================================

// All types are already exported above with 'export type' or 'export' keywords
// No need to re-export them here
