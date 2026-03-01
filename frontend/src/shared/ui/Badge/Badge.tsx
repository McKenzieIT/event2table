/**
 * Cyberpunk Lab Theme - Badge Component
 *
 * Status badges with glowing accents
 * Optimized with React.memo for performance
 */

import React from 'react';
import './Badge.css';

/**
 * Badge variant types
 */
type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';

/**
 * Badge size types
 */
type BadgeSize = 'sm' | 'md' | 'lg';

/**
 * Badge component props
 */
export interface BadgeProps extends React.ComponentPropsWithoutRef<'span'> {
  /** Badge content */
  children: React.ReactNode;
  /** Badge variant */
  variant?: BadgeVariant;
  /** Badge size */
  size?: BadgeSize;
  /** Show colored dot */
  dot?: boolean;
  /** Rounded pill shape */
  pill?: boolean;
  /** Icon component */
  icon?: React.ComponentType<{ className?: string }>;
  /** Additional CSS classes */
  className?: string;
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  pill = false,
  icon: Icon,
  className = '',
  ...props
}, ref) => {
  const badgeClass = [
    'cyber-badge',
    `cyber-badge--${variant}`,
    `cyber-badge--${size}`,
    dot && 'cyber-badge--dot',
    pill && 'cyber-badge--pill',
    className
  ].filter(Boolean).join(' ');

  return (
    <span ref={ref} className={badgeClass} {...props}>
      {dot && <span className="cyber-badge__dot" />}
      {Icon && <span className="cyber-badge__icon"><Icon /></span>}
      <span className="cyber-badge__content">{children}</span>
    </span>
  );
});

Badge.displayName = 'Badge';

// Memoize Badge - simple component with primitive props
const MemoizedBadge = React.memo(Badge, (prevProps, nextProps) => {
  return (
    prevProps.variant === nextProps.variant &&
    prevProps.size === nextProps.size &&
    prevProps.dot === nextProps.dot &&
    prevProps.pill === nextProps.pill &&
    prevProps.className === nextProps.className &&
    prevProps.children === nextProps.children
  );
});

MemoizedBadge.displayName = 'MemoizedBadge';

export default MemoizedBadge;
