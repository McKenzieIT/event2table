/**
 * Toast Context and Provider
 * Manages toast notifications globally
 *
 * @version 1.0.0
 * @date 2026-01-29
 */

import React, { createContext, useState, useCallback, useRef } from 'react';
import ToastNotification from '@shared/ui/ToastNotification';
import './ToastContainer.css';

export const ToastContext = createContext(null);

/**
 * Toast Provider Component
 * Wraps the application to provide toast functionality
 *
 * @example
 * <ToastProvider>
 *   <App />
 * </ToastProvider>
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const toastIdCounter = useRef(0);

  /**
   * Add a new toast notification
   */
  const showToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = ++toastIdCounter.current;

    setToasts(prevToasts => [
      ...prevToasts,
      { id, message, type, duration }
    ]);

    return id;
  }, []);

  /**
   * Remove a toast notification
   */
  const removeToast = useCallback((id) => {
    setToasts(prevToasts => prevToasts.filter(toast => toast.id !== id));
  }, []);

  /**
   * Convenience methods for different toast types
   */
  const toast = {
    success: useCallback((message, duration) => {
      return showToast(message, 'success', duration);
    }, [showToast]),
    error: useCallback((message, duration) => {
      return showToast(message, 'error', duration);
    }, [showToast]),
    warning: useCallback((message, duration) => {
      return showToast(message, 'warning', duration);
    }, [showToast]),
    info: useCallback((message, duration) => {
      return showToast(message, 'info', duration);
    }, [showToast]),
    show: showToast
  };

  const contextValue = {
    ...toast,
    removeToast
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}

      {/* Toast Container */}
      <div className="toast-container">
        {toasts.map(({ id, message, type, duration }) => (
          <ToastNotification
            key={id}
            message={message}
            type={type}
            duration={duration}
            onClose={() => removeToast(id)}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
