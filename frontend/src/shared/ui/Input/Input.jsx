/**
 * Input Component - Cyberpunk Lab Theme
 *
 * A sleek, tech-inspired input with subtle glow on focus.
 * Supports text, password, number, and textarea variants.
 *
 * Optimized with React.memo to prevent unnecessary re-renders.
 *
 * @example
 * // Text input
 * <Input
 *   type="text"
 *   placeholder="Enter game name..."
 *   label="Game Name"
 * />
 *
 * @example
 * // With error state
 * <Input
 *   type="text"
 *   label="Game Name"
 *   error="Game name is required"
 * />
 *
 * @example
 * // Disabled
 * <Input
 *   type="text"
 *   label="Game Name"
 *   disabled
 * />
 */

import React from 'react';
import './Input.css';

const Input = React.forwardRef(({
  type = 'text',
  label,
  placeholder,
  error,
  disabled = false,
  required = false,
  icon: Icon,
  helperText,
  className = '',
  value,
  onChange,
  ...props
}, ref) => {
  const inputId = React.useId();
  const isInvalid = Boolean(error);

  const wrapperClass = [
    'cyber-input-wrapper',
    isInvalid && 'cyber-input-wrapper--invalid',
    disabled && 'cyber-input-wrapper--disabled',
    Icon && 'cyber-input-wrapper--with-icon'
  ].filter(Boolean).join(' ');

  const inputClass = [
    'cyber-input',
    isInvalid && 'cyber-input--invalid',
    disabled && 'cyber-input--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={['cyber-input', className].filter(Boolean).join(' ')}>
      {label && (
        <label htmlFor={inputId} className="cyber-input__label">
          {label}
          {required && <span className="cyber-input__required" aria-hidden="true"> *</span>}
        </label>
      )}

      <div className={wrapperClass}>
        {Icon && (
          <span className="cyber-input__icon">
            <Icon />
          </span>
        )}

        <input
          ref={ref}
          id={inputId}
          type={type}
          className={inputClass}
          placeholder={placeholder}
          disabled={disabled}
          value={value}
          onChange={onChange}
          aria-invalid={isInvalid}
          aria-describedby={
            isInvalid ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
          }
          {...props}
        />
      </div>

      {isInvalid && (
        <p id={`${inputId}-error`} className="cyber-input__error" role="alert">
          {error}
        </p>
      )}

      {helperText && !isInvalid && (
        <p id={`${inputId}-helper`} className="cyber-input__helper">
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

// Memoize Input component to prevent unnecessary re-renders
// Custom comparison since value and onChange change frequently
const MemoizedInput = React.memo(Input, (prevProps, nextProps) => {
  return (
    prevProps.type === nextProps.type &&
    prevProps.label === nextProps.label &&
    prevProps.placeholder === nextProps.placeholder &&
    prevProps.error === nextProps.error &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.required === nextProps.required &&
    prevProps.helperText === nextProps.helperText &&
    prevProps.className === nextProps.className &&
    prevProps.value === nextProps.value &&
    prevProps.onChange === nextProps.onChange
  );
});

MemoizedInput.displayName = 'MemoizedInput';

export default MemoizedInput;
