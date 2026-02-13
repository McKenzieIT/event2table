/**
 * Switch Component - Cyberpunk Lab Theme
 *
 * A modern, tech-inspired toggle switch with smooth animations and cyan glow.
 * Perfect for binary on/off states like settings, toggles, and preferences.
 *
 * @example
 * // Basic switch
 * <Switch
 *   label="Enable notifications"
 *   checked={enabled}
 *   onChange={(checked) => setEnabled(checked)}
 * />
 *
 * @example
 * // With description
 * <Switch
 *   label="Auto-save"
 *   description="Automatically save changes every 30 seconds"
 *   checked={autoSave}
 *   onChange={setAutoSave}
 * />
 *
 * @example
 * // Disabled
 * <Switch
 *   label="Disabled switch"
 *   disabled
 * />
 */

import React, { useCallback, useEffect } from 'react';
import './Switch.css';

const Switch = React.forwardRef(({
  label,
  description,
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
  const switchRef = React.useRef(null);
  const inputId = id || React.useId();
  const isInvalid = Boolean(error);

  // Merge refs
  useEffect(() => {
    if (typeof ref === 'function') {
      ref(switchRef.current);
    } else if (ref) {
      ref.current = switchRef.current;
    }
  }, [ref]);

  const handleChange = useCallback((event) => {
    if (!disabled) {
      onChange?.(event.target.checked, event);
    }
  }, [disabled, onChange]);

  const wrapperClass = [
    'cyber-switch-wrapper',
    isInvalid && 'cyber-switch-wrapper--invalid',
    disabled && 'cyber-switch-wrapper--disabled',
    className
  ].filter(Boolean).join(' ');

  const switchClass = [
    'cyber-switch',
    checked && 'cyber-switch--checked',
    isInvalid && 'cyber-switch--invalid',
    disabled && 'cyber-switch--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={wrapperClass}>
      <label className="cyber-switch-label" htmlFor={inputId}>
        <input
          ref={switchRef}
          id={inputId}
          type="checkbox"
          name={name}
          value={value}
          checked={checked}
          disabled={disabled}
          onChange={handleChange}
          aria-invalid={isInvalid}
          aria-required={required}
          className="cyber-switch-input"
          role="switch"
          aria-checked={checked}
          {...props}
        />

        <span className={switchClass} aria-hidden="true">
          <span className="cyber-switch-slider">
            {checked && (
              <span className="cyber-switch-icon">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path
                    d="M2 6L4.5 8.5L10 3"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
            )}
          </span>
        </span>

        {(label || description) && (
          <div className="cyber-switch-content">
            {label && (
              <span className="cyber-switch-label-text">
                {label}
                {required && <span className="cyber-switch-required" aria-hidden="true"> *</span>}
              </span>
            )}
            {description && (
              <span className="cyber-switch-description">{description}</span>
            )}
          </div>
        )}
      </label>

      {isInvalid && (
        <p className="cyber-switch__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

Switch.displayName = 'Switch';

const MemoizedSwitch = React.memo(Switch, (prevProps, nextProps) => {
  return (
    prevProps.checked === nextProps.checked &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.error === nextProps.error &&
    prevProps.onChange === nextProps.onChange
  );
});

MemoizedSwitch.displayName = 'MemoizedSwitch';

export default MemoizedSwitch;
