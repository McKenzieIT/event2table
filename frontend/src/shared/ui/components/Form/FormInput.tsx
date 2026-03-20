import React, { useCallback, useMemo } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import type { FieldValues, FieldPath } from 'react-hook-form';
import type { InputFieldProps } from './Form.types';
import { FormErrorMessage, FormHelperText } from './Form';

/**
 * FormInput Component
 * 
 * Input field component integrated with React Hook Form.
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
 * <FormInput
 *   name="email"
 *   label="Email"
 *   type="email"
 *   placeholder="Enter your email"
 *   required
 * />
 * ```
 */
export const FormInput = <
  TFieldValues extends FieldValues = FieldValues
>({
  name,
  label,
  helperText,
  required = false,
  disabled = false,
  className = '',
  type = 'text',
  placeholder,
  autoComplete,
  ...props
}: InputFieldProps<TFieldValues>) => {
  const {
    control,
    formState: { errors },
  } = useFormContext<TFieldValues>();

  // Get error message for this field
  const error = useMemo(() => {
    const fieldError = errors[name];
    return fieldError?.message as string | undefined;
  }, [errors, name]);

  // Memoize wrapper class
  const wrapperClass = useMemo(() => {
    return ['form-field-wrapper', className].filter(Boolean).join(' ');
  }, [className]);

  // Memoize input class
  const inputClass = useMemo(() => {
    return [
      'form-input',
      error && 'form-input--error',
      disabled && 'form-input--disabled'
    ].filter(Boolean).join(' ');
  }, [error, disabled]);

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
        <label htmlFor={name as string} className={labelClass}>
          {label}
          {required && <span aria-hidden="true"> *</span>}
        </label>
      )}

      <Controller
        name={name}
        control={control}
        render={({ field }) => (
          <input
            id={name as string}
            type={type}
            className={inputClass}
            placeholder={placeholder}
            disabled={disabled}
            autoComplete={autoComplete}
            aria-invalid={!!error}
            aria-required={required}
            aria-describedby={
              error
                ? `${name as string}-error`
                : helperText
                  ? `${name as string}-helper`
                  : undefined
            }
            {...field}
            {...props}
          />
        )}
      />

      <FormErrorMessage error={error} className="form-error-message" />
      {!error && <FormHelperText text={helperText} className="form-helper-text" />}
    </div>
  );
};

FormInput.displayName = 'FormInput';

/**
 * Memoized FormInput component for performance
 */
const MemoizedFormInput = React.memo(FormInput) as typeof FormInput;

export default MemoizedFormInput;
