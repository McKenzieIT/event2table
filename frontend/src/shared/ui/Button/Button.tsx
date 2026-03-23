/**
 * Button Component - "Cyberpunk Lab" Theme
 *
 * A modern, tech-inspired button with subtle glow effects and smooth transitions.
 * Supports multiple variants: primary, secondary, ghost, danger.
 *
 * Optimized with React.memo to prevent unnecessary re-renders.
 *
 * @example
 * // Primary button with hover glow
 * <Button variant="primary">Generate HQL</Button>
 *
 * // Ghost button with border glow
 * <Button variant="ghost">Cancel</Button>
 *
 * @example
 * // Disabled state
 * <Button disabled>Processing...</Button>
 */

import React, { forwardRef, type ComponentPropsWithoutRef, type ForwardedRef } from 'react';

import './Button.css';

import { buildCompoundClasses } from '../utils/classNames';
import { compareButtonProps } from '../utils/memoComparators';
import type { BaseComponentProps, IconComponent, MouseEventHandler } from '@/shared/ui/types/common';

/**
 * Button variant types (extended to support all used variants)
 */
type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'ghost'
  | 'danger'
  | 'outline-primary'
  | 'outline-danger'
  | 'outline-secondary'
  | 'success'
  | 'warning'
  | 'info'
  | 'outline-success'
  | 'text';

/**
 * Button component props - extends common base props
 */
export interface ButtonProps extends Omit<ComponentPropsWithoutRef<'button'>, 'size' | 'onClick'>, BaseComponentProps {
  /** Button variant */
  variant?: ButtonVariant;
  /** Button size */
  size?: Size;
  /** Icon component */
  icon?: IconComponent;
  /** Loading state */
  loading?: boolean;
  /** Click handler */
  onClick?: MouseEventHandler;
}

/**
 * Button component with TypeScript types
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  icon: Icon,
  onClick,
  className = '',
  ...props
}, ref) => {
  // 使用工具函数构建 CSS 类名
  const buttonClass = buildCompoundClasses(
    'cyber-button',
    variant,
    size,
    { disabled, loading },
    className
  );

  return (
    <button
      ref={ref}
      type="button"
      className={buttonClass}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading && (
        <span className="cyber-button__spinner" aria-hidden="true" />
      )}
      {Icon && (
        <span className="cyber-button__icon">
          <Icon />
        </span>
      )}
      <span>{children}</span>
    </button>
  );
});

Button.displayName = 'Button';

// 使用共享的 memo 比较函数
const MemoizedButton = React.memo(Button, compareButtonProps);

MemoizedButton.displayName = 'MemoizedButton';

export { MemoizedButton as Button };
export default MemoizedButton;