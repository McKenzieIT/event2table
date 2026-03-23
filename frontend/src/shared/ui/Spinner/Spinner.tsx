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
import { buildConditionalClasses } from '../utils/classNames';
import { compareSpinnerProps } from '../utils/memoComparators';

/**
 * Size variants for the spinner
 */
export type SpinnerSize = 'sm' | 'md' | 'lg';

/**
 * Props for the Spinner component
 */
export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Size of the spinner
   * @default 'md'
   */
  size?: SpinnerSize;

  /**
   * Optional label to display below the spinner
   */
  label?: string;

  /**
   * Additional CSS classes to apply to the spinner container
   */
  className?: string;
}

const Spinner = React.forwardRef<HTMLDivElement, SpinnerProps>(({
  size = 'md',
  label,
  className = '',
  ...props
}, ref) => {
  // 使用工具函数构建 CSS 类名
  const spinnerClass = buildConditionalClasses(
    'cyber-spinner',
    {},
    [className, `cyber-spinner--${size}`]
  );

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

// 使用共享的 memo 比较函数
const MemoizedSpinner = React.memo(Spinner, compareSpinnerProps);

MemoizedSpinner.displayName = 'MemoizedSpinner';

export default MemoizedSpinner;
export { MemoizedSpinner as Spinner };