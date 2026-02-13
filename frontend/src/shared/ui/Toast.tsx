/**
 * Toast通知组件
 * Toast Notification Component
 *
 * @description 替代alert()，提供更好的用户体验
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

/**
 * Toast类型
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';

/**
 * Toast消息接口
 */
export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

/**
 * Toast上下文接口
 */
interface ToastContextValue {
  toasts: ToastMessage[];
  showToast: (type: ToastType, message: string, duration?: number) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
  removeToast: (id: string) => void;
}

/**
 * Toast上下文
 */
const ToastContext = createContext<ToastContextValue | null>(null);

/**
 * Toast Provider属性
 */
interface ToastProviderProps {
  children: ReactNode;
}

/**
 * Toast Provider组件
 */
export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const showToast = useCallback((type: ToastType, message: string, duration: number = 3000) => {
    const id = Math.random().toString(36).substring(7);
    const newToast: ToastMessage = { id, type, message, duration };

    setToasts(prev => [...prev, newToast]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, duration);
    }
  }, []);

  const success = useCallback((message: string, duration?: number) => {
    showToast('success', message, duration);
  }, [showToast]);

  const error = useCallback((message: string, duration?: number) => {
    showToast('error', message, duration);
  }, [showToast]);

  const warning = useCallback((message: string, duration?: number) => {
    showToast('warning', message, duration);
  }, [showToast]);

  const info = useCallback((message: string, duration?: number) => {
    showToast('info', message, duration);
  }, [showToast]);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const value: ToastContextValue = {
    toasts,
    showToast,
    success,
    error,
    warning,
    info,
    removeToast,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

/**
 * 使用Toast的Hook
 */
export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  return context;
}

/**
 * Toast容器组件
 */
function ToastContainer({
  toasts,
  onRemove,
}: {
  toasts: ToastMessage[];
  onRemove: (id: string) => void;
}) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      className="toast-container position-fixed top-0 end-0 p-3"
      style={{ zIndex: 9999, maxHeight: '100vh', overflowY: 'auto' }}
    >
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}

/**
 * 单个Toast项组件
 */
function ToastItem({ toast, onRemove }: { toast: ToastMessage; onRemove: (id: string) => void }) {
  const [isExiting, setIsExiting] = useState(false);

  const handleRemove = () => {
    setIsExiting(true);
    setTimeout(() => onRemove(toast.id), 300);
  };

  const typeConfig = {
    success: {
      icon: 'bi-check-circle-fill',
      bgColor: 'bg-success',
      textColor: 'text-white',
    },
    error: {
      icon: 'bi-exclamation-triangle-fill',
      bgColor: 'bg-danger',
      textColor: 'text-white',
    },
    warning: {
      icon: 'bi-exclamation-circle-fill',
      bgColor: 'bg-warning',
      textColor: 'text-dark',
    },
    info: {
      icon: 'bi-info-circle-fill',
      bgColor: 'bg-info',
      textColor: 'text-white',
    },
  };

  const config = typeConfig[toast.type];

  return (
    <div
      className={`toast show ${isExiting ? 'fade-out' : ''}`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      style={{
        transition: 'opacity 0.3s, transform 0.3s',
        opacity: isExiting ? 0 : 1,
        transform: isExiting ? 'translateX(100%)' : 'translateX(0)',
      }}
    >
      <div className={`toast-header ${config.bgColor} ${config.textColor}`}>
        <i className={`bi ${config.icon} me-2`}></i>
        <strong className="me-auto">
          {toast.type === 'success' && '成功'}
          {toast.type === 'error' && '错误'}
          {toast.type === 'warning' && '警告'}
          {toast.type === 'info' && '提示'}
        </strong>
        <button
          type="button"
          className="btn-close"
          onClick={handleRemove}
          aria-label="关闭"
        ></button>
      </div>
      <div className="toast-body">
        {toast.message}
      </div>
    </div>
  );
}
