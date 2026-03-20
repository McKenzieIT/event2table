import React, { useMemo, useState, useCallback, useRef, useEffect } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import type { FieldValues, FieldPath } from 'react-hook-form';
import type { DatePickerFieldProps } from './Form.types';
import { FormErrorMessage, FormHelperText } from './Form';

/**
 * FormDatePicker Component
 * 
 * Date picker component integrated with React Hook Form.
 * Provides date/time selection with validation and Cyberpunk Lab Theme styling.
 * 
 * FEATURES:
 * - Native date/time input with fallback
 * - Date format support
 * - Min/max date validation
 * - Time picker option
 * - Keyboard accessible
 * - ARIA attributes for accessibility
 * 
 * @example
 * ```tsx
 * <FormDatePicker
 *   name="birthDate"
 *   label="Birth Date"
 *   required
 *   maxDate={new Date()}
 * />
 * ```
 */
export const FormDatePicker = <
  TFieldValues extends FieldValues = FieldValues
>({
  name,
  label,
  helperText,
  required = false,
  disabled = false,
  className = '',
  format = 'YYYY-MM-DD',
  showTime = false,
  timeFormat = 'HH:mm',
  minDate,
  maxDate,
  placeholder = 'Select date...',
  ...props
}: DatePickerFieldProps<TFieldValues>) => {
  const {
    control,
    formState: { errors },
  } = useFormContext<TFieldValues>();

  const inputRef = useRef<HTMLInputElement>(null);

  // Get error message for this field
  const error = useMemo(() => {
    const fieldError = errors[name];
    return fieldError?.message as string | undefined;
  }, [errors, name]);

  // Memoize wrapper class
  const wrapperClass = useMemo(() => {
    return ['form-field-wrapper', 'form-datepicker-wrapper', className].filter(Boolean).join(' ');
  }, [className]);

  // Memoize input class
  const inputClass = useMemo(() => {
    return [
      'form-input',
      'form-datepicker',
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

  // Convert Date to input value string
  const dateToInputValue = useCallback((date: Date | string | null | undefined): string => {
    if (!date) return '';
    
    const d = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(d.getTime())) return '';
    
    if (showTime) {
      return d.toISOString().slice(0, 16);
    }
    return d.toISOString().slice(0, 10);
  }, [showTime]);

  // Convert input value string to Date
  const inputValueToDate = useCallback((value: string): Date | null => {
    if (!value) return null;
    return new Date(value);
  }, []);

  // Format date for display
  const formatDisplayDate = useCallback((date: Date | null): string => {
    if (!date) return '';
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    if (showTime) {
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return format
        .replace('YYYY', String(year))
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes);
    }
    
    return format
      .replace('YYYY', String(year))
      .replace('MM', month)
      .replace('DD', day);
  }, [format, showTime]);

  // Validate date against min/max
  const validateDate = useCallback((date: Date): boolean => {
    if (minDate && date < minDate) return false;
    if (maxDate && date > maxDate) return false;
    return true;
  }, [minDate, maxDate]);

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
        render={({ field }) => {
          const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
            const value = e.target.value;
            const date = inputValueToDate(value);
            
            if (date && validateDate(date)) {
              field.onChange(date);
            } else if (!value) {
              field.onChange(null);
            }
          };

          return (
            <div className="form-datepicker-container">
              <input
                ref={inputRef}
                id={name as string}
                type={showTime ? 'datetime-local' : 'date'}
                className={inputClass}
                placeholder={placeholder}
                disabled={disabled}
                min={minDate ? dateToInputValue(minDate) : undefined}
                max={maxDate ? dateToInputValue(maxDate) : undefined}
                value={field.value ? dateToInputValue(field.value) : ''}
                onChange={handleChange}
                aria-invalid={!!error}
                aria-required={required}
                aria-describedby={
                  error
                    ? `${name as string}-error`
                    : helperText
                      ? `${name as string}-helper`
                      : undefined
                }
                {...props}
              />
              
              {/* Calendar icon */}
              <span className="form-datepicker-icon" aria-hidden="true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
              </span>
            </div>
          );
        }}
      />

      <FormErrorMessage error={error} className="form-error-message" />
      {!error && <FormHelperText text={helperText} className="form-helper-text" />}
    </div>
  );
};

FormDatePicker.displayName = 'FormDatePicker';

/**
 * Memoized FormDatePicker component for performance
 */
const MemoizedFormDatePicker = React.memo(FormDatePicker) as typeof FormDatePicker;

export default MemoizedFormDatePicker;
