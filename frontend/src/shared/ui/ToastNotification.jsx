import React, { useEffect } from "react";
import "./ToastNotification.css";

/**
 * Toast 通知组件
 * 显示临时消息提示
 *
 * @param {Object} props - 组件属性
 * @param {string} props.message - 通知消息
 * @param {string} props.type - 通知类型 (success, error, warning, info)
 * @param {number} props.duration - 显示时长（毫秒）
 * @param {Function} props.onClose - 关闭回调
 *
 * @example
 * <ToastNotification
 *   message="操作成功！"
 *   type="success"
 *   duration={3000}
 *   onClose={() => console.log('Toast closed')}
 * />
 */
export default function ToastNotification({
  message,
  type = "info",
  duration = 3000,
  onClose,
}) {
  useEffect(() => {
    // 自动关闭
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  // 不同类型的图标
  const icons = {
    success: "✅",
    error: "❌",
    warning: "⚠️",
    info: "ℹ️",
  };

  // 不同类型的背景色
  const colors = {
    success: "linear-gradient(135deg, #48bb78 0%, #38a169 100%)",
    error: "linear-gradient(135deg, #f56565 0%, #e53e3e 100%)",
    warning: "linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)",
    info: "linear-gradient(135deg, #4299e1 0%, #3182ce 100%)",
  };

  return (
    <div className={`toast-notification toast-${type}`}>
      <div className="toast-content">
        <span className="toast-icon">{icons[type]}</span>
        <span className="toast-message">{message}</span>
      </div>
      <button
        className="toast-close"
        onClick={onClose}
        title="关闭"
        aria-label="关闭通知"
      >
        ×
      </button>
    </div>
  );
}
