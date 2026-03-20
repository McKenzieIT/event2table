import { useRef, useCallback, useEffect } from 'react';
import type { UseFormReturn } from 'react-hook-form';

/**
 * Debounced Validation Hook
 * 
 * Provides debounced form validation to reduce unnecessary validation calls.
 * Useful for fields that trigger expensive validation (e.g., async validation).
 * 
 * @param form - React Hook Form instance
 * @param delay - Debounce delay in milliseconds (default: 300ms)
 * 
 * @example
 * ```tsx
 * const form = useForm({ resolver: zodResolver(schema) });
 * const { validateField, validateFields } = useDebouncedValidation(form, 300);
 * 
 * // Validate single field with debounce
 * <input onChange={() => validateField('email')} />
 * 
 * // Validate multiple fields with debounce
 * <button onClick={() => validateFields(['email', 'password'])}>Validate</button>
 * ```
 */
export function useDebouncedValidation<TFieldValues extends Record<string, unknown>>(
  form: UseFormReturn<TFieldValues>,
  delay: number = 300
) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingFieldsRef = useRef<string[]>([]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Debounced validation for a single field
  const validateField = useCallback((fieldName: string) => {
    // Add to pending fields
    if (!pendingFieldsRef.current.includes(fieldName)) {
      pendingFieldsRef.current.push(fieldName);
    }

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout
    timeoutRef.current = setTimeout(async () => {
      const fieldsToValidate = [...pendingFieldsRef.current];
      pendingFieldsRef.current = [];
      
      // Trigger validation for all pending fields
      await form.trigger(fieldsToValidate as keyof TFieldValues);
    }, delay);
  }, [form, delay]);

  // Debounced validation for multiple fields
  const validateFields = useCallback((fieldNames: string[]) => {
    // Add all fields to pending
    for (const field of fieldNames) {
      if (!pendingFieldsRef.current.includes(field)) {
        pendingFieldsRef.current.push(field);
      }
    }

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout
    timeoutRef.current = setTimeout(async () => {
      const fieldsToValidate = [...pendingFieldsRef.current];
      pendingFieldsRef.current = [];
      
      await form.trigger(fieldsToValidate as keyof TFieldValues);
    }, delay);
  }, [form, delay]);

  // Validate all fields
  const validateAll = useCallback(() => {
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout
    timeoutRef.current = setTimeout(async () => {
      await form.trigger();
    }, delay);
  }, [form, delay]);

  // Cancel pending validation
  const cancelValidation = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    pendingFieldsRef.current = [];
  }, []);

  return {
    validateField,
    validateFields,
    validateAll,
    cancelValidation,
  };
}

export default useDebouncedValidation;
