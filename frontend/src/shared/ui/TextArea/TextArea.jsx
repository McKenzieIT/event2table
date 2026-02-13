/**
 * TextArea Component - Cyberpunk Lab Theme
 *
 * Multi-line text input with focus glow
 */

import React, { useCallback } from 'react';
import './TextArea.css';

const TextArea = React.forwardRef(({
  label,
  placeholder,
  error,
  disabled = false,
  required = false,
  rows = 4,
  resize = 'vertical',
  maxLength,
  helperText,
  showCount = false,
  className = '',
  value,
  onChange,
  ...props
}, ref) => {
  const inputId = React.useId();
  const isInvalid = Boolean(error);
  const currentLength = value?.length || 0;

  const handleChange = useCallback((event) => {
    onChange?.(event);
  }, [onChange]);

  const wrapperClass = [
    'cyber-textarea-wrapper',
    isInvalid && 'cyber-textarea-wrapper--invalid',
    disabled && 'cyber-textarea-wrapper--disabled'
  ].filter(Boolean).join(' ');

  const textareaClass = [
    'cyber-textarea',
    isInvalid && 'cyber-textarea--invalid',
    disabled && 'cyber-textarea--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={['cyber-textarea', className].filter(Boolean).join(' ')}>
      {label && (
        <label htmlFor={inputId} className="cyber-textarea__label">
          {label}
          {required && <span className="cyber-textarea__required" aria-hidden="true"> *</span>}
        </label>
      )}

      <div className={wrapperClass}>
        <textarea
          ref={ref}
          id={inputId}
          className={textareaClass}
          placeholder={placeholder}
          disabled={disabled}
          rows={rows}
          maxLength={maxLength}
          value={value}
          onChange={handleChange}
          style={{ resize }}
          aria-invalid={isInvalid}
          aria-describedby={
            isInvalid ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
          }
          {...props}
        />
      </div>

      {showCount && maxLength && (
        <div className="cyber-textarea__count">
          {currentLength}/{maxLength}
        </div>
      )}

      {isInvalid && (
        <p id={`${inputId}-error`} className="cyber-textarea__error" role="alert">
          {error}
        </p>
      )}

      {helperText && !isInvalid && (
        <p id={`${inputId}-helper`} className="cyber-textarea__helper">
          {helperText}
        </p>
      )}
    </div>
  );
});

TextArea.displayName = 'TextArea';

const MemoizedTextArea = React.memo(TextArea, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.error === nextProps.error &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.onChange === nextProps.onChange
  );
});

MemoizedTextArea.displayName = 'MemoizedTextArea';

export default MemoizedTextArea;
