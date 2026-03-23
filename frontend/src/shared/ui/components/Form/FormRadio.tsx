import React, { useMemo } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import type { FieldValues, FieldPath } from 'react-hook-form';

import { FormErrorMessage, FormHelperText } from './Form';
import type { RadioFieldProps } from './Form.types';

/**
 * FormRadio Component
 * 
 * Radio button group component integrated with React Hook Form.
 * Provides automatic validation, error handling, and form state management.
 * 
 * PERFORMANCE OPTIMIZATIONS:
 * - Uses Controller from react-hook-form for controlled component pattern
 * - Leverages React Hook Form's built-in optimization (uncontrolled inputs)
 * - Memoized callback functions to prevent unnecessary re-renders
 * - CSS class computations are memoized
 * 
 * @example
 * ```tsx
 * <FormRadio
 *   name="gameType"
 *   label="Game Type"
 *   options={[
 *     { value: 'football', label: 'Football' },
 *     { value: 'basketball', label: 'Basketball' }
 *   ]}
 *   required
 * />
 * ```
 */
export const FormRadio = <
  TFieldValues extends FieldValues = FieldValues
>({
  name,
  label,
  helperText,
  required = false,
  disabled = false,
  className = '',
  options,
  direction = 'column',
  ...props
}: RadioFieldProps<TFieldValues>) => {
  const {
    control,
    trigger,
    formState: { errors },
  } = useFormContext<TFieldValues>();

  // Get error message for this field
  const error = useMemo(() => {
    const fieldError = errors[name];
    return fieldError?.message as string | undefined;
  }, [errors, name]);

  // Memoize wrapper class
  const wrapperClass = useMemo(() => {
    return [
      'form-radio-wrapper',
      error && 'form-radio-wrapper--error',
      disabled && 'form-radio-wrapper--disabled',
      className
    ].filter(Boolean).join(' ');
  }, [error, disabled, className]);

  // Memoize radio group class
  const radioGroupClass = useMemo(() => {
    return [
      'form-radio-group',
      direction === 'row' && 'form-radio-group--row'
    ].filter(Boolean).join(' ');
  }, [direction]);

  // Memoize label class
  const labelClass = useMemo(() => {
    return [
      'form-label',
      required && 'form-label--required'
    ].filter(Boolean).join(' ');
  }, [required]);

  return (
    <div className={wrapperClass}>
      {label && (
        <label className={labelClass}>
          {label}
          {required && <span aria-hidden="true"> *</span>}
        </label>
      )}

      <Controller
        name={name}
        control={control}
        defaultValue=""
        render={({ field }) => (
          <div className={radioGroupClass} role="radiogroup" aria-required={required}>
            {options.map((option) => (
              <label
                key={option.value}
                className={`form-radio-label ${option.disabled ? 'form-radio-label--disabled' : ''}`}
              >
                <input
                  type="radio"
                  id={`${name as string}-${option.value}`}
                  name={name as string}
                  value={option.value}
                  checked={field.value === option.value}
                  onChange={async (e) => {
                    await field.onChange(e.target.value);
                    // Trigger validation to clear errors when a value is selected
                    await trigger(name);
                  }}
                  disabled={disabled || option.disabled}
                  aria-invalid={!!error}
                  className="form-radio-input"
                  {...props}
                />
                <span className="form-radio-text">{option.label}</span>
              </label>
            ))}
          </div>
        )}
      />

      <FormHelperText text={!error ? helperText : undefined} />
      <FormErrorMessage error={error} className="form-error-message" />
    </div>
  );
};

FormRadio.displayName = 'FormRadio';

/**
 * Memoized FormRadio component for performance
 */
const MemoizedFormRadio = React.memo(FormRadio) as typeof FormRadio;

export default MemoizedFormRadio;