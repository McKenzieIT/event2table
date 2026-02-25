/**
 * Spinner Component - Cyberpunk Lab Theme
 *
 * A CSS-only loading spinner with smooth animations and cyan glow.
 * Perfect for loading states, async operations, and content placeholders.
 *
 * @example
 * // Medium size (default)
 * <Spinner />
 *
 * @example
 * // Small size
 * <Spinner size="sm" />
 *
 * @example
 * // Large size
 * <Spinner size="lg" />
 *
 * @example
 * // With custom label
 * <Spinner label="Loading data..." />
 *
 * @example
 * // Full page loader
 * <div className="flex-center">
 *   <Spinner size="lg" label="Processing..." />
 * </div>
 */

import React from 'react';
import './Spinner.css';

const Spinner = React.forwardRef(({
  size = 'md',
  label,
  className = '',
  ...props
}, ref) => {
  const spinnerClass = [
    'cyber-spinner',
    `cyber-spinner--${size}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={ref}
      className={spinnerClass}
      role="status"
      aria-live="polite"
      aria-busy="true"
      {...props}
    >
      <span className="cyber-spinner-circle" aria-hidden="true" />
      <span className="cyber-spinner-circle" aria-hidden="true" />
      <span className="cyber-spinner-circle" aria-hidden="true" />
      {label && (
        <span className="cyber-spinner-label">{label}</span>
      )}
      <span className="sr-only">Loading...</span>
    </div>
  );
});

Spinner.displayName = 'Spinner';

const MemoizedSpinner = React.memo(Spinner, (prevProps, nextProps) => {
  return (
    prevProps.size === nextProps.size &&
    prevProps.label === nextProps.label
  );
});

MemoizedSpinner.displayName = 'MemoizedSpinner';

export default MemoizedSpinner;
export { MemoizedSpinner as Spinner };
