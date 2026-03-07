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

import React, { useCallback, useEffect, forwardRef, useRef, useMemo, useId } from 'react';
import './Switch.css';

/**
 * Props for the Switch component
 */
export interface SwitchProps extends Omit<React.ComponentPropsWithoutRef<'input'>, 'type' | 'onChange'> {
  /**
   * Label text for the switch
   */
  label?: string;

  /**
   * Additional description text displayed below the label
   */
  description?: string;

  /**
   * Whether the switch is checked (on)
   * @default false
   */
  checked?: boolean;

  /**
   * Whether the switch is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether the switch is required (shows asterisk)
   * @default false
   */
  required?: boolean;

  /**
   * Error message to display (invalidates the switch)
   */
  error?: string;

  /**
   * Additional CSS class name
   */
  className?: string;

  /**
   * Callback when the switch state changes
   * @param checked - The new checked state
   * @param event - The original change event
   */
  onChange?: (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => void;

  /**
   * Value attribute for the input (useful for forms)
   */
  value?: string;

  /**
   * Name attribute for the input (useful for forms)
   */
  name?: string;

  /**
   * ID attribute for the input (auto-generated if not provided)
   */
  id?: string;
}

export interface SwitchRefHandle {
  focus: () => void;
  blur: () => void;
}

const Switch = forwardRef<HTMLInputElement, SwitchProps>(({
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
  const switchRef = useRef<HTMLInputElement>(null);
  const inputId = id || useId();
  const isInvalid = Boolean(error);

  // Merge refs
  useEffect(() => {
    if (typeof ref === 'function') {
      ref(switchRef.current);
    } else if (ref) {
      ref.current = switchRef.current;
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
      'cyber-switch-wrapper',
      isInvalid && 'cyber-switch-wrapper--invalid',
      disabled && 'cyber-switch-wrapper--disabled',
      className
    ].filter(Boolean).join(' ');
  }, [isInvalid, disabled, className]);

  // PERFORMANCE: useMemo to cache CSS class computations
  // Prevents re-creation of class strings on every render
  const switchClass = useMemo(() => {
    return [
      'cyber-switch',
      checked && 'cyber-switch--checked',
      isInvalid && 'cyber-switch--invalid',
      disabled && 'cyber-switch--disabled'
    ].filter(Boolean).join(' ');
  }, [checked, isInvalid, disabled]);

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
