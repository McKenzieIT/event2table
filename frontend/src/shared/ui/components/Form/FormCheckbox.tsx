import React, { useMemo } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import type { FieldValues, FieldPath } from 'react-hook-form';

import { FormErrorMessage } from './Form';
import type { CheckboxFieldProps } from './Form.types';

/**
 * FormCheckbox Component
 * 
 * Checkbox component integrated with React Hook Form.
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
 * <FormCheckbox
 *   name="acceptTerms"
 *   label="I accept the terms and conditions"
 *   required
 * />
 * ```
 */
export const FormCheckbox = <
  TFieldValues extends FieldValues = FieldValues
>({
  name,
  label,
  required = false,
  disabled = false,
  className = '',
  indeterminate = false,
  ...props
}: CheckboxFieldProps<TFieldValues>) => {
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
    return [
      'form-checkbox-wrapper',
      error && 'form-checkbox-wrapper--error',
      disabled && 'form-checkbox-wrapper--disabled',
      className
    ].filter(Boolean).join(' ');
  }, [error, disabled, className]);

  // Memoize checkbox class
  const checkboxClass = useMemo(() => {
    return [
      'form-checkbox',
      error && 'form-checkbox--error',
      disabled && 'form-checkbox--disabled'
    ].filter(Boolean).join(' ');
  }, [error, disabled]);

  return (
    <div className={wrapperClass}>
      <Controller
        name={name}
        control={control}
        defaultValue={false}
        render={({ field }) => (
          <label className="form-checkbox-label">
            <input
              type="checkbox"
              id={name as string}
              className={checkboxClass}
              disabled={disabled}
              checked={field.value as boolean}
              onChange={field.onChange}
              aria-invalid={!!error}
              aria-required={required}
              aria-checked={indeterminate ? 'mixed' : field.value}
              {...props}
            />
            {label && (
              <span className="form-checkbox-text">
                {label}
                {required && <span aria-hidden="true"> *</span>}
              </span>
            )}
          </label>
        )}
      />

      <FormErrorMessage error={error} className="form-error-message" />
    </div>
  );
};

FormCheckbox.displayName = 'FormCheckbox';

/**
 * Memoized FormCheckbox component for performance
 */
const MemoizedFormCheckbox = React.memo(FormCheckbox) as typeof FormCheckbox;

export default MemoizedFormCheckbox;
