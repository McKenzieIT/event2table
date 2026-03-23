/**
 * Cyberpunk Lab Theme - Badge Component
 *
 * Status badges with glowing accents
 * Optimized with React.memo for performance
 */

import React, { type ComponentPropsWithoutRef } from 'react';

import './Badge.css';

import { buildConditionalClasses } from '../utils/classNames';
import { compareBadgeProps } from '../utils/memoComparators';

/**
 * Badge variant types
 */
type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'secondary';

/**
 * Badge size types
 */
type BadgeSize = 'sm' | 'md' | 'lg';

/**
 * Badge component props
 */
export interface BadgeProps extends ComponentPropsWithoutRef<'span'> {
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
  // 使用工具函数构建 CSS 类名
  const badgeClass = buildConditionalClasses(
    'cyber-badge',
    { dot, pill },
    [className, `cyber-badge--${variant}`, `cyber-badge--${size}`]
  );

  return (
    <span ref={ref} className={badgeClass} {...props}>
      {dot && <span className="cyber-badge__dot" />}
      {Icon && <span className="cyber-badge__icon"><Icon /></span>}
      <span className="cyber-badge__content">{children}</span>
    </span>
  );
});

Badge.displayName = 'Badge';

// 使用共享的 memo 比较函数
const MemoizedBadge = React.memo(Badge, compareBadgeProps);

MemoizedBadge.displayName = 'MemoizedBadge';

export { MemoizedBadge as Badge };
export default MemoizedBadge;