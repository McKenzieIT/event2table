/**
 * Radio Component - Cyberpunk Lab Theme
 *
 * A modern, tech-inspired radio button with smooth animations and glow effects.
 * Designed to be used in radio groups for single-select options.
 *
 * @example
 * // Single radio
 * <Radio
 *   label="Football"
 *   name="game"
 *   value="football"
 *   checked={selectedGame === 'football'}
 *   onChange={(value) => setSelectedGame(value)}
 * />
 *
 * @example
 * // Radio group
 * {[
 *   { value: 'football', label: 'Football' },
 *   { value: 'basketball', label: 'Basketball' }
 * ].map(option => (
 *   <Radio
 *     key={option.value}
 *     label={option.label}
 *     name="game"
 *     value={option.value}
 *     checked={selectedGame === option.value}
 *     onChange={(value) => setSelectedGame(value)}
 *   />
 * ))}
 *
 * @example
 * // Disabled
 * <Radio
 *   label="Disabled option"
 *   name="game"
 *   value="tennis"
 *   disabled
 * />
 */

import React, { useCallback, useEffect } from 'react';
import './Radio.css';

const Radio = React.forwardRef(({
  label,
  checked = false,
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
  const radioRef = React.useRef(null);
  const inputId = id || React.useId();
  const isInvalid = Boolean(error);

  // Merge refs
  useEffect(() => {
    if (typeof ref === 'function') {
      ref(radioRef.current);
    } else if (ref) {
      ref.current = radioRef.current;
    }
  }, [ref]);

  const handleChange = useCallback((event) => {
    if (!disabled) {
      onChange?.(event.target.value, event);
    }
  }, [disabled, onChange]);

  const wrapperClass = [
    'cyber-radio-wrapper',
    isInvalid && 'cyber-radio-wrapper--invalid',
    disabled && 'cyber-radio-wrapper--disabled',
    className
  ].filter(Boolean).join(' ');

  const radioClass = [
    'cyber-radio',
    checked && 'cyber-radio--checked',
    isInvalid && 'cyber-radio--invalid',
    disabled && 'cyber-radio--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={wrapperClass}>
      <label className="cyber-radio-label" htmlFor={inputId}>
        <input
          ref={radioRef}
          id={inputId}
          type="radio"
          name={name}
          value={value}
          checked={checked}
          disabled={disabled}
          onChange={handleChange}
          aria-invalid={isInvalid}
          aria-required={required}
          className="cyber-radio-input"
          {...props}
        />

        <span className={radioClass} aria-hidden="true">
          {checked && (
            <span className="cyber-radio-dot" />
          )}
        </span>

        {label && (
          <span className="cyber-radio-text">
            {label}
            {required && <span className="cyber-radio-required" aria-hidden="true"> *</span>}
          </span>
        )}
      </label>

      {isInvalid && (
        <p className="cyber-radio__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

Radio.displayName = 'Radio';

const MemoizedRadio = React.memo(Radio, (prevProps, nextProps) => {
  return (
    prevProps.checked === nextProps.checked &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.error === nextProps.error &&
    prevProps.onChange === nextProps.onChange
  );
});

MemoizedRadio.displayName = 'MemoizedRadio';

export default MemoizedRadio;
