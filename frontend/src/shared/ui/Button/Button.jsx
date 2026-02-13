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

import React from 'react';
import './Button.css';

const Button = React.forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon: Icon,
  onClick,
  className = '',
  ...props
}, ref) => {
  const buttonClass = [
    'cyber-button',
    `cyber-button--${variant}`,
    `cyber-button--${size}`,
    disabled && 'cyber-button--disabled',
    loading && 'cyber-button--loading',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      ref={ref}
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

// Memoize to prevent unnecessary re-renders
// Only re-render if props actually change
Button.displayName = 'Button';

const MemoizedButton = React.memo(Button, (prevProps, nextProps) => {
  // Custom comparison for better performance
  return (
    prevProps.variant === nextProps.variant &&
    prevProps.size === nextProps.size &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.loading === nextProps.loading &&
    prevProps.className === nextProps.className &&
    prevProps.children === nextProps.children &&
    prevProps.onClick === nextProps.onClick
  );
});

MemoizedButton.displayName = 'MemoizedButton';

export default MemoizedButton;
