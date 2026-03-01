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

import React, { useCallback, useEffect, forwardRef, useRef } from 'react';
import './Radio.css';

/**
 * Props for the Radio component
 */
export interface RadioProps extends Omit<React.ComponentPropsWithoutRef<'input'>, 'onChange' | 'type'> {
  /**
   * Label text displayed next to the radio button
   */
  label?: string;

  /**
   * Whether the radio button is checked
   * @default false
   */
  checked?: boolean;

  /**
   * Whether the radio button is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether the radio button is required
   * @default false
   */
  required?: boolean;

  /**
   * Error message to display
   * When provided, the radio button will be styled as invalid
   */
  error?: string;

  /**
   * Additional CSS class names
   */
  className?: string;

  /**
   * Callback function when radio state changes
   * @param value - The value of the selected radio
   * @param event - The original change event
   */
  onChange?: (value: string, event: React.ChangeEvent<HTMLInputElement>) => void;

  /**
   * Value attribute for the radio input
   */
  value?: string;

  /**
   * Name attribute for the radio input
   * Used to group radio buttons together
   */
  name?: string;

  /**
   * ID attribute for the radio input
   * If not provided, a unique ID will be generated
   */
  id?: string;
}

/**
 * Radio Component - TypeScript Version
 *
 * A modern, tech-inspired radio button with smooth animations and glow effects.
 * Designed to be used in radio groups for single-select options.
 */
const Radio = forwardRef<HTMLInputElement, RadioProps>(({
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
  const radioRef = useRef<HTMLInputElement>(null);
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

  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
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
export type { RadioProps };
