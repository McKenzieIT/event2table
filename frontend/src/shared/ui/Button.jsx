import React from 'react';
import './Button.css';

/**
 * Button 组件 - 纯文字按钮
 * 统一的按钮组件，支持多种变体和尺寸
 *
 * 设计原则:
 * - 纯文字标签（不使用图标）
 * - 语义化颜色匹配操作类型
 * - WCAG AAA可访问性标准
 *
 * @example
 * // 主要操作
 * <Button variant="primary">保存</Button>
 *
 * @example
 * // 次要成功操作
 * <Button variant="outline-success" size="sm">跳转</Button>
 *
 * @example
 * // 危险操作
 * <Button variant="danger" size="sm">删除</Button>
 *
 * Props:
 * @param {string} variant - 按钮变体
 *   'primary' | 'secondary' | 'outline-primary' | 'outline-secondary' |
 *   'success' | 'danger' | 'warning' | 'info' |
 *   'outline-success' | 'outline-danger' | 'outline-warning' | 'outline-info' |
 *   'glass'
 * @param {string} size - 按钮尺寸: 'xs' | 'sm' | 'md' | 'lg'
 * @param {boolean} disabled - 禁用状态
 * @param {React.ReactNode} children - 按钮文字内容
 * @param {string} className - 自定义类名
 */
export const Button = React.forwardRef(({
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  children,
  ...props
}, ref) => {
  return (
    <button
      ref={ref}
      className={`btn btn-${variant} btn-${size} ${disabled ? 'disabled' : ''} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';

/**
 * IconButton 图标按钮组件
 *
 * @deprecated 自版本1.1.0起已废弃
 * @reason 采用纯文字按钮策略，提高可访问性和一致性
 * @alternative 使用 <Button> 组件配合纯文字标签
 *
 * 仅保留用于向后兼容，不推荐在新代码中使用
 */
export const IconButton = React.forwardRef(({
  variant = 'secondary',
  size = 'md',
  disabled = false,
  className = '',
  children,
  ...props
}, ref) => {
  return (
    <button
      ref={ref}
      className={`btn-icon btn-icon-${variant} btn-icon-${size} ${disabled ? 'disabled' : ''} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
});

IconButton.displayName = 'IconButton';
