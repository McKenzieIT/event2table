/**
 * Toast Component
 * 通知提示组件
 *
 * Displays temporary notifications for user actions (success, error, warning, info).
 * Auto-dismisses after a specified duration.
 *
 * @component Toast
 */
import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import './Toast.css';

/**
 * Toast notification component
 *
 * @param {Object} props - Component props
 * @param {string} props.type - Notification type: 'success' | 'error' | 'warning' | 'info'
 * @param {string} props.title - Notification title
 * @param {string} props.message - Notification message
 * @param {number} props.duration - Duration in milliseconds before auto-dismiss (default: 3000)
 * @param {Function} props.onClose - Callback when toast is closed
 */
export default function Toast({
  type = 'info',
  title = '',
  message = '',
  duration = 3000,
  onClose
}) {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      onClose?.();
    }, 300); // Wait for exit animation
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return 'check-circle';
      case 'error':
        return 'x-circle';
      case 'warning':
        return 'exclamation-triangle';
      case 'info':
      default:
        return 'info-circle';
    }
  };

  return (
    <div className={`toast toast-${type} ${isExiting ? 'toast-exit' : 'toast-enter'}`}>
      <i className={`toast-icon bi bi-${getIcon()}`}></i>
      <div className="toast-content">
        {title && <div className="toast-title">{title}</div>}
        {message && <div className="toast-message">{message}</div>}
      </div>
      <button
        className="toast-close"
        onClick={handleClose}
        aria-label="Close notification"
      >
        <i className="bi bi-x"></i>
      </button>
      <div
        className="toast-progress"
        style={{ animationDuration: `${duration}ms` }}
      ></div>
    </div>
  );
}

Toast.propTypes = {
  type: PropTypes.oneOf(['success', 'error', 'warning', 'info']),
  title: PropTypes.string,
  message: PropTypes.string,
  duration: PropTypes.number,
  onClose: PropTypes.func
};

Toast.defaultProps = {
  type: 'info',
  title: '',
  message: '',
  duration: 3000
};
