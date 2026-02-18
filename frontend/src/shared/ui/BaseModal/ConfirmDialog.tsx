/**
 * ConfirmDialog Component
 * 确认对话框组件
 *
 * @description 用于确认操作的对话框，支持不同类型（warning/danger/info）
 */

import React from 'react';
import { Z_INDICES } from '@shared/constants/zIndices';

/**
 * 对话框类型
 */
export type ConfirmDialogType = 'warning' | 'danger' | 'info';

/**
 * 组件属性
 */
export interface ConfirmDialogProps {
  /** 是否显示对话框 */
  isOpen: boolean;
  /** 对话框标题 */
  title?: string;
  /** 对话框消息 */
  message: string;
  /** 确认按钮文字 */
  confirmText?: string;
  /** 取消按钮文字 */
  cancelText?: string;
  /** 确认回调 */
  onConfirm: () => void;
  /** 取消回调 */
  onCancel: () => void;
  /** 对话框类型 */
  type?: ConfirmDialogType;
  /** 自定义样式类名 */
  className?: string;
}

/**
 * 获取类型对应的样式配置
 */
const getTypeConfig = (type: ConfirmDialogType) => {
  switch (type) {
    case 'danger':
      return {
        icon: 'bi-exclamation-triangle-fill',
        iconClass: 'text-danger',
        btnClass: 'btn-danger',
      };
    case 'info':
      return {
        icon: 'bi-info-circle-fill',
        iconClass: 'text-info',
        btnClass: 'btn-primary',
      };
    case 'warning':
    default:
      return {
        icon: 'bi-exclamation-circle-fill',
        iconClass: 'text-warning',
        btnClass: 'btn-warning',
      };
  }
};

/**
 * 确认对话框组件
 */
export function ConfirmDialog({
  isOpen,
  title = '确认关闭',
  message,
  confirmText = '确定',
  cancelText = '取消',
  onConfirm,
  onCancel,
  type = 'warning',
  className = '',
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const typeConfig = getTypeConfig(type);

  return (
    <>
      {/* 背景遮罩 */}
      <div
        className="modal-overlay confirm-dialog-overlay"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: Z_INDICES.CONFIRM_DIALOG, // 比普通模态框更高的z-index
        }}
        onClick={onCancel}
      >
        {/* 对话框内容 */}
        <div
          className={`modal-content glass-card confirm-dialog ${className}`}
          style={{
            backgroundColor: 'var(--glass-bg)',
            borderRadius: 'var(--border-radius)',
            padding: 'var(--en-space-lg)',
            maxWidth: '500px',
            width: '90%',
            maxHeight: '90vh',
            overflow: 'auto',
            boxShadow: 'var(--shadow-lg)',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 标题栏 */}
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <i
              className={`bi ${typeConfig.icon} ${typeConfig.iconClass}`}
              style={{ fontSize: '1.5rem', marginRight: '0.75rem' }}
            ></i>
            <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>
              {title}
            </h3>
          </div>

          {/* 消息内容 */}
          <div style={{ marginBottom: '1.5rem', color: 'var(--text-color)', lineHeight: 1.6 }}>
            {message}
          </div>

          {/* 按钮组 */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '0.5rem',
            }}
          >
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onCancel}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: 'var(--border-radius-sm)',
              }}
            >
              {cancelText}
            </button>
            <button
              type="button"
              className={`btn ${typeConfig.btnClass}`}
              onClick={onConfirm}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: 'var(--border-radius-sm)',
              }}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default ConfirmDialog;
