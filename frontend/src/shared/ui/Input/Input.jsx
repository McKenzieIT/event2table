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
  onBlur,
  onFocus,
  id: customId,
  name,
  readOnly = false,
  autoFocus = false,
  maxLength,
  minLength,
  ...props
}, ref) => {
  const generatedId = React.useId();
  const inputId = customId || generatedId;
  const isInvalid = Boolean(error);

  const wrapperClass = [
    'cyber-field__wrapper',
    isInvalid && 'cyber-field__wrapper--invalid',
    disabled && 'cyber-field__wrapper--disabled',
    Icon && 'cyber-field__wrapper--with-icon'
  ].filter(Boolean).join(' ');

  const inputClass = [
    'cyber-field__input',
    isInvalid && 'cyber-field__input--invalid',
    disabled && 'cyber-field__input--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={['cyber-field', 'cyber-input', className].filter(Boolean).join(' ')}>
      {label && (
        <label htmlFor={inputId} className="cyber-field__label cyber-input__label">
          {label}
          {required && <span className="cyber-field__required cyber-input__required" aria-hidden="true"> *</span>}
        </label>
      )}

      <div className={wrapperClass}>
        {Icon && (
          <span className="cyber-field__icon cyber-input__icon">
            <Icon />
          </span>
        )}

        <input
          ref={ref}
          id={inputId}
          type={type}
          name={name}
          className={inputClass}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readOnly}
          autoFocus={autoFocus}
          maxLength={maxLength}
          minLength={minLength}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          onFocus={onFocus}
          aria-invalid={isInvalid}
          aria-describedby={
            isInvalid ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
          }
          {...props}
        />
      </div>

      {isInvalid && (
        <p id={`${inputId}-error`} className="cyber-field__error cyber-input__error" role="alert">
          {error}
        </p>
      )}

      {helperText && !isInvalid && (
        <p id={`${inputId}-helper`} className="cyber-field__helper cyber-input__helper">
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
    prevProps.onChange === nextProps.onChange &&
    prevProps.onBlur === nextProps.onBlur &&
    prevProps.onFocus === nextProps.onFocus &&
    prevProps.readOnly === nextProps.readOnly &&
    prevProps.autoFocus === nextProps.autoFocus &&
    prevProps.name === nextProps.name &&
    prevProps.maxLength === nextProps.maxLength &&
    prevProps.minLength === nextProps.minLength
  );
});

MemoizedInput.displayName = 'MemoizedInput';

export default MemoizedInput;
