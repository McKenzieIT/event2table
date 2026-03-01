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

/**
 * Button variant types
 */
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline-primary' | 'outline-danger';

/**
 * Button size types
 */
type ButtonSize = 'sm' | 'md' | 'lg';

/**
 * Button component props
 */
export interface ButtonProps extends React.ComponentPropsWithoutRef<'button'> {
  /** Button text or content */
  children?: React.ReactNode;
  /** Button variant */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Disabled state */
  disabled?: boolean;
  /** Loading state */
  loading?: boolean;
  /** Icon component */
  icon?: React.ComponentType<{ className?: string }>;
  /** Click handler */
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Button component with TypeScript types
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
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

export { MemoizedButton as Button };
export default MemoizedButton;
