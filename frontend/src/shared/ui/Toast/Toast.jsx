/**
 * Toast Component - Cyberpunk Lab Theme
 *
 * Glassmorphism toast notifications with slide-in animations
 */

import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import './Toast.css';

/**
 * Toast Context
 */
const ToastContext = createContext(null);

/**
 * Toast Provider - Manages toast state and rendering
 */
export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const toastTimeouts = useRef(new Map());

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      toastTimeouts.current.forEach(timeout => clearTimeout(timeout));
      toastTimeouts.current.clear();
    };
  }, []);

  const removeToast = useCallback((id) => {
    const timeout = toastTimeouts.current.get(id);
    if (timeout) {
      clearTimeout(timeout);
      toastTimeouts.current.delete(id);
    }
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const showToast = useCallback((type, message, duration) => {
    const defaultDuration = type === 'error' ? 10000 : type === 'warning' ? 8000 : 5000;
    const actualDuration = duration ?? defaultDuration;
    const id = Math.random().toString(36).substring(7);
    const newToast = { id, type, message, duration: actualDuration };

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

  const success = useCallback((message, duration) => showToast('success', message, duration), [showToast]);
  const error = useCallback((message, duration) => showToast('error', message, duration), [showToast]);
  const warning = useCallback((message, duration) => showToast('warning', message, duration), [showToast]);
  const info = useCallback((message, duration) => showToast('info', message, duration), [showToast]);

  const value = {
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
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

/**
 * Toast Container - Fixed position container
 */
const ToastContainer = React.memo(({ toasts, onRemove }) => {
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
function ToastItem({ toast, onRemove }) {
  const [isExiting, setIsExiting] = useState(false);
  const exitTimeoutRef = useRef(null);

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

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
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
          {toast.type === 'success' && '成功'}
          {toast.type === 'error' && '错误'}
          {toast.type === 'warning' && '警告'}
          {toast.type === 'info' && '提示'}
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
