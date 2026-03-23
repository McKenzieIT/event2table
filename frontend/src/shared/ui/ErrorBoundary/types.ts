/**
 * Error Boundary Type Definitions
 * 错误边界组件类型定义
 */

import type { ReactNode } from 'react';

/**
 * 错误信息接口
 * 扩展React.ErrorInfo，添加额外上下文
 */
export interface ErrorInfo {
  /** 组件堆栈信息 */
  componentStack: string;
  /** 错误边界名称（可选） */
  errorBoundary?: string;
}

/**
 * 回退UI组件的Props
 * 用于自定义错误显示
 */
export interface FallbackProps {
  /** 捕获的错误 */
  error: Error;
  /** 错误信息 */
  errorInfo: ErrorInfo;
  /** 重置错误边界的函数 */
  resetErrorBoundary: () => void;
}

/**
 * ErrorBoundary组件属性
 */
export interface ErrorBoundaryProps {
  /** 子组件 */
  children: ReactNode;
  /** 
   * 自定义回退UI
   * 可以是ReactNode或渲染函数
   */
  fallback?: ReactNode | ((props: FallbackProps) => ReactNode);
  /** 
   * 错误发生时的回调
   * 用于日志记录或错误上报
   */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** 
   * 重置时的回调
   * 用于清理状态或重试操作
   */
  onReset?: () => void;
  /** 
   * 重置键数组
   * 当数组中的值变化时，自动重置错误状态
   */
  resetKeys?: unknown[];
}

/**
 * ErrorBoundary内部状态
 */
export interface ErrorBoundaryState {
  /** 是否有错误 */
  hasError: boolean;
  /** 错误对象 */
  error: Error | null;
  /** 错误信息 */
  errorInfo: ErrorInfo | null;
}

/**
 * Canvas专用错误边界属性
 */
export interface CanvasErrorBoundaryProps {
  /** 子组件 */
  children: ReactNode;
  /** 错误回调 */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

/**
 * 错误分类
 */
export type ErrorType = 
  | 'render'      // 渲染错误
  | 'network'     // 网络错误
  | 'validation'  // 验证错误
  | 'permission'  // 权限错误
  | 'unknown';    // 未知错误

/**
 * 标准化错误对象
 */
export interface StandardizedError {
  /** 原始错误 */
  originalError: Error;
  /** 错误类型 */
  type: ErrorType;
  /** 用户友好的错误消息 */
  userMessage: string;
  /** 是否可重试 */
  retryable: boolean;
  /** 额外上下文 */
  context?: Record<string, unknown>;
}

/**
 * 错误处理器函数类型
 */
export type ErrorHandler = (error: Error, errorInfo: ErrorInfo) => void;

/**
 * 错误重置处理器函数类型
 */
export type ResetHandler = () => void;
