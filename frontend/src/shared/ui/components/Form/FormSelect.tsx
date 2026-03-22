import React, { useMemo } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import type { FieldValues, FieldPath } from 'react-hook-form';
import type { SelectFieldProps } from './Form.types';
import { FormErrorMessage, FormHelperText } from './Form';

/**
 * FormSelect Component
 * 
 * Select dropdown component integrated with React Hook Form.
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
 * <FormSelect
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
export const FormSelect = <
  TFieldValues extends FieldValues = FieldValues
>({
  name,
  label,
  helperText,
  required = false,
  disabled = false,
  className = '',
  options,
  placeholder = 'Select...',
  searchable = false,
  ...props
}: SelectFieldProps<TFieldValues>) => {
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

  // Memoize select class
  const selectClass = useMemo(() => {
    return [
      'form-select',
      error && 'form-select--error',
      disabled && 'form-select--disabled'
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
        defaultValue=""
        render={({ field }) => (
          <select
            id={name as string}
            className={selectClass}
            disabled={disabled}
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
            value={field.value ?? ''}
            onChange={(e) => {
              field.onChange(e);
            }}
            onBlur={field.onBlur}
            {...props}
          >
            {placeholder && (
              <option value="">{placeholder}</option>
            )}
            {(options || []).map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
          </select>
        )}
      />

      <FormErrorMessage error={error} className="form-error-message" />
      {!error && <FormHelperText text={helperText} className="form-helper-text" />}
    </div>
  );
};

FormSelect.displayName = 'FormSelect';

/**
 * Memoized FormSelect component for performance
 */
const MemoizedFormSelect = React.memo(FormSelect) as typeof FormSelect;

export default MemoizedFormSelect;
