/**
 * Toast Component - Cyberpunk Lab Theme
 *
 * PERF: React Performance Optimization - Phase 3
 * - React.memo for ToastContainer and ToastItem
 * - useCallback for all event handlers
 * - Conditional rendering (return null when no toasts)
 * See: docs/reports/2026-03-06/REACT-PERFORMANCE-OPTIMIZATION-REPORT.md
 *
 * Glassmorphism toast notifications with slide-in animations
 */

import React, { createContext, useContext, useState, useCallback, useEffect, useRef, ReactNode, HTMLAttributes } from 'react';
import './Toast.css';

/**
 * Toast notification types
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';

/**
 * Individual toast item
 */
export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration: number;
}

/**
 * Props for ToastProvider
 */
export interface ToastProviderProps {
  children: ReactNode;
}

/**
 * Context value for toast operations
 */
export interface ToastContextValue {
  toasts: Toast[];
  showToast: (type: ToastType, message: string, duration?: number) => string;
  success: (message: string, duration?: number) => string;
  error: (message: string, duration?: number) => string;
  warning: (message: string, duration?: number) => string;
  info: (message: string, duration?: number) => string;
  removeToast: (id: string) => void;
}

/**
 * Props for ToastContainer
 */
interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

/**
 * Props for ToastItem
 */
interface ToastItemProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

/**
 * Toast Context
 */
const ToastContext = createContext<ToastContextValue | null>(null);

/**
 * Toast Provider - Manages toast state and rendering
 */
export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const toastTimeouts = useRef(new Map<string, NodeJS.Timeout>());

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      toastTimeouts.current.forEach(timeout => clearTimeout(timeout));
      toastTimeouts.current.clear();
    };
  }, []);

  const removeToast = useCallback((id: string) => {
    const timeout = toastTimeouts.current.get(id);
    if (timeout) {
      clearTimeout(timeout);
      toastTimeouts.current.delete(id);
    }
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const showToast = useCallback((type: ToastType, message: string, duration?: number): string => {
    const defaultDuration = type === 'error' ? 10000 : type === 'warning' ? 8000 : 5000;
    const actualDuration = duration ?? defaultDuration;
    const id = Math.random().toString(36).substring(7);
    const newToast: Toast = { id, type, message, duration: actualDuration };

    setToasts(prev => [...prev, newToast]);

    if (actualDuration > 0) {
      const timeout = setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
        toastTimeouts.current.delete(id);
      }, actualDuration);
      toastTimeouts.current.set(id, timeout);
    }

    return id;
  }, []);

  const success = useCallback((message: string, duration?: number) => showToast('success', message, duration), [showToast]);
  const error = useCallback((message: string, duration?: number) => showToast('error', message, duration), [showToast]);
  const warning = useCallback((message: string, duration?: number) => showToast('warning', message, duration), [showToast]);
  const info = useCallback((message: string, duration?: number) => showToast('info', message, duration), [showToast]);

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
};

/**
 * useToast Hook
 */
export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

/**
 * Toast Container - Fixed position container
 */
const ToastContainer = React.memo<ToastContainerProps>(({ toasts, onRemove }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="cyber-toast-container" role="region" aria-live="polite" aria-label="Toast notifications">
      {toasts.map(toast => (
        <MemoizedToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
});

ToastContainer.displayName = 'ToastContainer';

/**
 * Toast Item - Individual toast notification
 */
function ToastItem({ toast, onRemove }: ToastItemProps) {
  const [isExiting, setIsExiting] = useState(false);
  const exitTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleRemove = useCallback(() => {
    setIsExiting(true);
    exitTimeoutRef.current = setTimeout(() => onRemove(toast.id), 300);
  }, [onRemove, toast.id]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (exitTimeoutRef.current) {
        clearTimeout(exitTimeoutRef.current);
      }
    };
  }, []);

  const icons: Record<ToastType, string> = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  const titles: Record<ToastType, string> = {
    success: '成功',
    error: '错误',
    warning: '警告',
    info: '提示',
  };

  return (
    <div
      className={[
        'cyber-toast',
        `cyber-toast--${toast.type}`,
        isExiting && 'cyber-toast--exiting'
      ].filter(Boolean).join(' ')}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="cyber-toast__icon">
        {icons[toast.type]}
      </div>
      <div className="cyber-toast__content">
        <div className="cyber-toast__title">
          {titles[toast.type]}
        </div>
        <div className="cyber-toast__message">
          {toast.message}
        </div>
      </div>
      <button
        type="button"
        className="cyber-toast__close"
        onClick={handleRemove}
        aria-label="关闭通知"
      >
        ×
      </button>
      {toast.duration > 0 && (
        <div
          className="cyber-toast__progress"
          style={{
            animation: `toastProgress ${toast.duration}ms linear forwards`
          }}
        />
      )}
    </div>
  );
}

const MemoizedToastItem = React.memo(ToastItem, (prevProps, nextProps) => {
  // Only re-render if toast object or onRemove changes
  return prevProps.toast === nextProps.toast && prevProps.onRemove === nextProps.onRemove;
});

MemoizedToastItem.displayName = 'MemoizedToastItem';

ToastItem.displayName = 'ToastItem';

export default ToastProvider;
