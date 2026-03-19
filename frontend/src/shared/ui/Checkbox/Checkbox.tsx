/**
 * Checkbox Component - Cyberpunk Lab Theme
 *
 * A modern, tech-inspired checkbox with smooth animations and glow effects.
 * Supports checked, unchecked, and indeterminate states.
 *
 * @example
 * // Basic checkbox
 * <Checkbox
 *   label="Enable notifications"
 *   checked={enabled}
 *   onChange={(checked) => setEnabled(checked)}
 * />
 *
 * @example
 * // Indeterminate state
 * <Checkbox
 *   label="Select all"
 *   checked={allSelected}
 *   indeterminate={someSelected}
 *   onChange={handleSelectAll}
 * />
 *
 * @example
 * // Disabled
 * <Checkbox
 *   label="Disabled option"
 *   disabled
 * />
 */

import React, { useCallback, useEffect, forwardRef, useRef, useMemo, RefObject } from 'react';
import './Checkbox.css';

/**
 * Props for the Checkbox component
 */
export interface CheckboxProps extends Omit<React.ComponentPropsWithoutRef<'input'>, 'onChange' | 'type'> {
  /**
   * Label text displayed next to the checkbox
   */
  label?: string;

  /**
   * Whether the checkbox is checked
   * @default false
   */
  checked?: boolean;

  /**
   * Whether the checkbox is in indeterminate state
   * @default false
   */
  indeterminate?: boolean;

  /**
   * Whether the checkbox is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether the checkbox is required
   * @default false
   */
  required?: boolean;

  /**
   * Error message to display
   * When provided, the checkbox will be styled as invalid
   */
  error?: string;

  /**
   * Additional CSS class names
   */
  className?: string;

  /**
   * Callback function when checkbox state changes
   * @param checked - The new checked state
   * @param event - The original change event
   */
  onChange?: (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => void;

  /**
   * Value attribute for the checkbox input
   */
  value?: string;

  /**
   * Name attribute for the checkbox input
   */
  name?: string;

  /**
   * ID attribute for the checkbox input
   * If not provided, a unique ID will be generated
   */
  id?: string;
}

/**
 * Checkbox Component - TypeScript Version
 *
 * A modern, tech-inspired checkbox with smooth animations and glow effects.
 * Supports checked, unchecked, and indeterminate states.
 */
const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(({
  label,
  checked = false,
  indeterminate = false,
  disabled = false,
  required = false,
  error,
  className = '',
  onChange,
  value,
  name,
  id,
  ...props
}, ref) => {
  const checkboxRef = useRef<HTMLInputElement>(null);
  const inputId = id || React.useId();
  const isInvalid = Boolean(error);

  // Handle indeterminate state
  useEffect(() => {
    if (checkboxRef.current) {
      checkboxRef.current.indeterminate = indeterminate;
    }
  }, [indeterminate]);

  // Merge refs
  useEffect(() => {
    if (typeof ref === 'function') {
      ref(checkboxRef.current);
    } else if (ref) {
      ref.current = checkboxRef.current;
    }
  }, [ref]);

  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (!disabled) {
      onChange?.(event.target.checked, event);
    }
  }, [disabled, onChange]);

  // PERFORMANCE: useMemo to cache CSS class computations
  // Prevents re-creation of class strings on every render
  const wrapperClass = useMemo(() => {
    return [
      'cyber-checkbox-wrapper',
      isInvalid && 'cyber-checkbox-wrapper--invalid',
      disabled && 'cyber-checkbox-wrapper--disabled',
      className
    ].filter(Boolean).join(' ');
  }, [isInvalid, disabled, className]);

  // PERFORMANCE: useMemo to cache CSS class computations
  // Prevents re-creation of class strings on every render
  const checkboxClass = useMemo(() => {
    return [
      'cyber-checkbox',
      checked && 'cyber-checkbox--checked',
      indeterminate && 'cyber-checkbox--indeterminate',
      isInvalid && 'cyber-checkbox--invalid',
      disabled && 'cyber-checkbox--disabled'
    ].filter(Boolean).join(' ');
  }, [checked, indeterminate, isInvalid, disabled]);

  return (
    <div className={wrapperClass}>
      <label className="cyber-checkbox-label" htmlFor={inputId}>
        <input
          ref={checkboxRef}
          id={inputId}
          type="checkbox"
          name={name}
          value={value}
          checked={checked}
          disabled={disabled}
          onChange={handleChange}
          aria-invalid={isInvalid}
          aria-required={required}
          aria-checked={indeterminate ? 'mixed' : checked}
          className="cyber-checkbox-input"
          {...props}
        />

        <span className={checkboxClass} aria-hidden="true">
          {(checked || indeterminate) && (
            <span className="cyber-checkbox-icon">
              {indeterminate ? (
                <span className="cyber-checkbox-indeterminate" />
              ) : (
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path
                    d="M2 7L5 10L12 3"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </span>
          )}
        </span>

        {label && (
          <span className="cyber-checkbox-text">
            {label}
            {required && <span className="cyber-checkbox-required" aria-hidden="true"> *</span>}
          </span>
        )}
      </label>

      {isInvalid && (
        <p className="cyber-checkbox__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

const MemoizedCheckbox = React.memo(Checkbox, (prevProps, nextProps) => {
  return (
    prevProps.checked === nextProps.checked &&
    prevProps.indeterminate === nextProps.indeterminate &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.error === nextProps.error &&
    prevProps.onChange === nextProps.onChange
  );
});

MemoizedCheckbox.displayName = 'MemoizedCheckbox';

export default MemoizedCheckbox;
export type { CheckboxProps };
