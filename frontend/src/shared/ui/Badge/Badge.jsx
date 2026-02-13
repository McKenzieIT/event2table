/**
 * Cyberpunk Lab Theme - Badge Component
 *
 * Status badges with glowing accents
 * Optimized with React.memo for performance
 */

import React from 'react';
import './Badge.css';

const Badge = React.forwardRef(({
  children,
  variant = 'default',      // default, primary, success, warning, danger, info
  size = 'md',              // sm, md, lg
  dot = false,              // Show colored dot
  pill = false,             // Rounded pill shape
  icon: Icon,               // Icon component
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
