/**
 * ErrorToast Component
 *
 * 统一错误提示组件，支持不同错误级别和自动消失
 *
 * 功能：
 * 1. 统一错误提示样式
 * 2. 支持不同错误级别（error、warning、info）
 * 3. 自动消失
 * 4. 可配置的显示时长
 *
 * 创建日期: 2026-03-20
 */

import React, { useEffect, useState, useCallback } from 'react';

// ============================================================================
// 类型定义
// ============================================================================

/**
 * 错误级别
 */
export type ErrorLevel = 'error' | 'warning' | 'info';

/**
 * 错误提示项
 */
export interface ErrorToastItem {
  /** 唯一标识 */
  id: string;
  /** 错误级别 */
  level: ErrorLevel;
  /** 错误消息 */
  message: string;
  /** 显示时长（毫秒），0 表示不自动消失 */
  duration?: number;
  /** 时间戳 */
  timestamp: number;
}

/**
 * ErrorToast 组件属性
 */
export interface ErrorToastProps {
  /** 错误提示列表 */
  toasts: ErrorToastItem[];
  /** 移除错误提示的回调 */
  onRemove: (id: string) => void;
  /** 最大显示数量 */
  maxToasts?: number;
  /** 显示位置 */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  /** 自定义样式 */
  style?: React.CSSProperties;
}

// ============================================================================
// 样式配置
// ============================================================================

const TOAST_STYLES: Record<ErrorLevel, React.CSSProperties> = {
  error: {
    backgroundColor: '#fee2e2',
    borderLeft: '4px solid #dc2626',
    color: '#991b1b',
  },
  warning: {
    backgroundColor: '#fef3c7',
    borderLeft: '4px solid #f59e0b',
    color: '#92400e',
  },
  info: {
    backgroundColor: '#dbeafe',
    borderLeft: '4px solid #3b82f6',
    color: '#1e40af',
  },
};

const ICONS: Record<ErrorLevel, string> = {
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️',
};

const POSITION_STYLES: Record<
  ErrorToastProps['position'],
  React.CSSProperties
> = {
  'top-right': {
    top: '20px',
    right: '20px',
  },
  'top-left': {
    top: '20px',
    left: '20px',
  },
  'bottom-right': {
    bottom: '20px',
    right: '20px',
  },
  'bottom-left': {
    bottom: '20px',
    left: '20px',
  },
};

// ============================================================================
// ErrorToast 组件
// ============================================================================

/**
 * 错误提示组件
 *
 * @example
 * ```tsx
 * const [toasts, setToasts] = useState<ErrorToastItem[]>([]);
 *
 * const addToast = (message: string, level: ErrorLevel = 'error') => {
 *   const toast: ErrorToastItem = {
 *     id: Date.now().toString(),
 *     level,
 *     message,
 *     duration: 5000,
 *     timestamp: Date.now(),
 *   };
 *   setToasts(prev => [...prev, toast]);
 * };
 *
 * return (
 *   <ErrorToast
 *     toasts={toasts}
 *     onRemove={(id) => setToasts(prev => prev.filter(t => t.id !== id))}
 *   />
 * );
 * ```
 */
export const ErrorToast = React.memo(({
  toasts,
  onRemove,
  maxToasts = 5,
  position = 'top-right',
  style,
}: ErrorToastProps) => {
  // 限制显示数量
  const visibleToasts = toasts.slice(-maxToasts);

  if (visibleToasts.length === 0) {
    return null;
  }

  const containerStyle: React.CSSProperties = {
    position: 'fixed',
    zIndex: 9999,
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    maxWidth: '400px',
    width: '100%',
    pointerEvents: 'none',
    ...POSITION_STYLES[position],
    ...style,
  };

  return (
    <div style={containerStyle}>
      {visibleToasts.map((toast) => (
        <ErrorToastItem
          key={toast.id}
          toast={toast}
          onRemove={onRemove}
        />
      ))}
    </div>
  );
});

/**
 * 单个错误提示项组件
 */
function ErrorToastItem({
  toast,
  onRemove,
}: {
  toast: ErrorToastItem;
  onRemove: (id: string) => void;
}): React.JSX.Element {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  // 进入动画
  useEffect(() => {
    setIsVisible(true);
  }, []);

  // 自动移除
  useEffect(() => {
    if (toast.duration && toast.duration > 0) {
      const timer = setTimeout(() => {
        handleRemove();
      }, toast.duration);

      return () => clearTimeout(timer);
    }
  }, [toast.duration]);

  /**
   * 处理移除
   */
  const handleRemove = useCallback(() => {
    setIsExiting(true);
    setTimeout(() => {
      onRemove(toast.id);
    }, 300); // 等待退出动画完成
  }, [toast.id, onRemove]);

  const itemStyle: React.CSSProperties = {
    pointerEvents: 'auto',
    padding: '16px',
    borderRadius: '8px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    transition: 'all 0.3s ease',
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
    ...(isExiting && {
      opacity: 0,
      transform: 'translateX(100%)',
    }),
    ...TOAST_STYLES[toast.level],
  };

  const iconStyle: React.CSSProperties = {
    fontSize: '20px',
    flexShrink: 0,
    lineHeight: 1,
  };

  const contentStyle: React.CSSProperties = {
    flex: 1,
    fontSize: '14px',
    lineHeight: '1.5',
    wordBreak: 'break-word',
  };

  const closeButtonStyle: React.CSSProperties = {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '18px',
    color: 'inherit',
    opacity: 0.6,
    padding: '0',
    width: '24px',
    height: '24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'opacity 0.2s',
  };

  const timeStyle: React.CSSProperties = {
    fontSize: '12px',
    opacity: 0.7,
    marginTop: '4px',
  };

  return (
    <div style={itemStyle}>
      <span style={iconStyle}>{ICONS[toast.level]}</span>
      <div style={contentStyle}>
        <div>{toast.message}</div>
        <div style={timeStyle}>
          {new Date(toast.timestamp).toLocaleTimeString()}
        </div>
      </div>
      <button
        style={closeButtonStyle}
        onClick={handleRemove}
        onMouseEnter={(e) => {
          e.currentTarget.style.opacity = '1';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.opacity = '0.6';
        }}
        aria-label="关闭"
      >
        ×
      </button>
    </div>
  );
}

ErrorToast.displayName = 'ErrorToast';

// ============================================================================
// Hook
// ============================================================================

/**
 * 使用错误提示的 Hook
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { toasts, showError, showWarning, showInfo, clearToasts } = useErrorToast();
 *
 *   const handleClick = () => {
 *     showError('操作失败', 5000);
 *   };
 *
 *   return (
 *     <>
 *       <button onClick={handleClick}>显示错误</button>
 *       <ErrorToast
 *         toasts={toasts}
 *         onRemove={removeToast}
 *       />
 *     </>
 *   );
 * }
 * ```
 */
export function useErrorToast() {
  const [toasts, setToasts] = useState<ErrorToastItem[]>([]);

  /**
   * 添加错误提示
   */
  const addToast = useCallback(
    (
      message: string,
      level: ErrorLevel = 'error',
      duration: number = 5000
    ) => {
      const toast: ErrorToastItem = {
        id: `${Date.now()}-${Math.random()}`,
        level,
        message,
        duration,
        timestamp: Date.now(),
      };

      setToasts((prev) => [...prev, toast]);
    },
    []
  );

  /**
   * 显示错误
   */
  const showError = useCallback(
    (message: string, duration?: number) => {
      addToast(message, 'error', duration);
    },
    [addToast]
  );

  /**
   * 显示警告
   */
  const showWarning = useCallback(
    (message: string, duration?: number) => {
      addToast(message, 'warning', duration);
    },
    [addToast]
  );

  /**
   * 显示信息
   */
  const showInfo = useCallback(
    (message: string, duration?: number) => {
      addToast(message, 'info', duration);
    },
    [addToast]
  );

  /**
   * 移除错误提示
   */
  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  /**
   * 清空所有错误提示
   */
  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  return {
    toasts,
    showError,
    showWarning,
    showInfo,
    removeToast,
    clearToasts,
    addToast,
  };
}

// ============================================================================
// 导出
// ============================================================================

export default ErrorToast;
