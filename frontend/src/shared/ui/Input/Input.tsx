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

import React, {
  forwardRef,
  useId,
  type ChangeEventHandler,
  type FocusEventHandler,
  type InputHTMLAttributes,
} from 'react';

import './Input.css';

import type { IconComponent, LabeledComponentProps } from '@/shared/ui/types/common';

/**
 * Input HTML element types
 */
type InputType =
  | 'text'
  | 'password'
  | 'email'
  | 'number'
  | 'tel'
  | 'url'
  | 'search'
  | 'date'
  | 'time'
  | 'datetime-local'
  | 'month'
  | 'week'
  | 'file'
  | 'color'
  | 'range';

/**
 * Props for the Input component - extends common labeled component props
 *
 * Migration Notes from PropTypes:
 * - type: PropTypes.string (default: 'text') → type: InputType
 * - label: PropTypes.string → label?: string (from LabeledComponentProps)
 * - placeholder: PropTypes.string → placeholder?: string
 * - error: PropTypes.string → error?: string (from LabeledComponentProps)
 * - disabled: PropTypes.bool (default: false) → disabled?: boolean (from BaseComponentProps)
 * - required: PropTypes.bool (default: false) → required?: boolean (from LabeledComponentProps)
 * - icon: PropTypes.elementType → icon?: IconComponent
 * - helperText: PropTypes.string → helperText?: string (from LabeledComponentProps)
 * - className: PropTypes.string (default: '') → className?: string (from BaseComponentProps)
 * - value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]) → value?: string | number
 * - onChange: PropTypes.func → onChange?: ChangeEventHandler<HTMLInputElement>
 * - onBlur: PropTypes.func → onBlur?: FocusEventHandler<HTMLInputElement>
 * - onFocus: PropTypes.func → onFocus?: FocusEventHandler<HTMLInputElement>
 * - id: PropTypes.string → id?: string
 * - name: PropTypes.string → name?: string
 * - readOnly: PropTypes.bool (default: false) → readOnly?: boolean
 * - autoFocus: PropTypes.bool (default: false) → autoFocus?: boolean
 * - maxLength: PropTypes.number → maxLength?: number
 * - minLength: PropTypes.number → minLength?: number
 */
export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange' | 'onBlur' | 'onFocus' | 'value'>, LabeledComponentProps {
  /**
   * Input type (text, password, email, number, etc.)
   * @default 'text'
   */
  type?: InputType;

  /**
   * Placeholder text shown when input is empty
   */
  placeholder?: string;

  /**
   * Icon component to display inside the input
   */
  icon?: IconComponent;

  /**
   * Input value (controlled component)
   */
  value?: string | number;

  /**
   * Change event handler
   */
  onChange?: ChangeEventHandler<HTMLInputElement>;

  /**
   * Blur event handler
   */
  onBlur?: FocusEventHandler<HTMLInputElement>;

  /**
   * Focus event handler
   */
  onFocus?: FocusEventHandler<HTMLInputElement>;

  /**
   * Custom ID for the input (auto-generated if not provided)
   */
  id?: string;

  /**
   * Name attribute for the input
   */
  name?: string;

  /**
   * Whether the input is read-only
   * @default false
   */
  readOnly?: boolean;

  /**
   * Whether to auto-focus the input on mount
   * @default false
   */
  autoFocus?: boolean;

  /**
   * Maximum length of the input value
   */
  maxLength?: number;

  /**
   * Minimum length of the input value
   */
  minLength?: number;
}

/**
 * Input Component
 *
 * A cyberpunk-themed input field with support for labels, error states,
 * helper text, icons, and accessibility features.
 *
 * Uses CSS Grid layout with the .cyber-field class for optimal alignment.
 */
const Input = forwardRef<HTMLInputElement, InputProps>(({
  type = 'text' as InputType,
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
  // Generate unique ID for label-input association
  const generatedId = useId();
  const inputId = customId || generatedId;

  // Determine if input is in invalid state
  const isInvalid = Boolean(error);

  // Build wrapper CSS classes
  const wrapperClass = [
    'cyber-field__wrapper',
    isInvalid && 'cyber-field__wrapper--invalid',
    disabled && 'cyber-field__wrapper--disabled',
    Icon && 'cyber-field__wrapper--with-icon'
  ].filter(Boolean).join(' ');

  // Build input CSS classes
  const inputClass = [
    'cyber-field__input',
    isInvalid && 'cyber-field__input--invalid',
    disabled && 'cyber-field__input--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={['cyber-field', 'cyber-input', className].filter(Boolean).join(' ')}>
      {/* Label Section */}
      {label && (
        <label htmlFor={inputId} className="cyber-field__label cyber-input__label">
          {label}
          {required && (
            <span className="cyber-field__required cyber-input__required" aria-hidden="true">
              {' '}
              *
            </span>
          )}
        </label>
      )}

      {/* Input Wrapper Section */}
      <div className={wrapperClass}>
        {/* Icon (if provided) */}
        {Icon && (
          <span className="cyber-field__icon cyber-input__icon">
            <Icon />
          </span>
        )}

        {/* Input Element */}
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
          required={required}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          onFocus={onFocus}
          aria-invalid={isInvalid}
          aria-required={required}
          aria-describedby={
            isInvalid
              ? `${inputId}-error`
              : helperText
                ? `${inputId}-helper`
                : undefined
          }
          {...props}
        />
      </div>

      {/* Error Message */}
      {isInvalid && (
        <p id={`${inputId}-error`} className="cyber-field__error cyber-input__error" role="alert">
          {error}
        </p>
      )}

      {/* Helper Text */}
      {helperText && !isInvalid && (
        <p id={`${inputId}-helper`} className="cyber-field__helper cyber-input__helper">
          {helperText}
        </p>
      )}
    </div>
  );
});

// Set display name for debugging
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

// Set display name for memoized component
MemoizedInput.displayName = 'MemoizedInput';

export { MemoizedInput as Input };
export default MemoizedInput;
