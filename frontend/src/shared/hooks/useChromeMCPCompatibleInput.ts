/**
 * Chrome MCP Compatible Input Hook
 *
 * Problem: Chrome DevTools MCP's fill operation updates DOM but doesn't trigger React onChange events
 * Solution: Use useEffect to monitor DOM values and sync to state when they differ
 *
 * Technical Details:
 * - Only updates when DOM value differs from state value (prevents infinite loops)
 * - Batch updates all changed fields (reduces re-renders)
 * - Works with both input and textarea elements
 *
 * @example
 * ```tsx
 * const { refs, values, handleChange, register } = useChromeMCPCompatibleInput({
 *   initialValues: { name: '', email: '' },
 *   onValuesChange: (values) => console.log('Values changed:', values),
 * });
 *
 * <Input
 *   label="Name"
 *   value={values.name}
 *   onChange={(e) => handleChange('name', e.target.value)}
 *   ref={register('name')}
 * />
 * ```
 */

import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Hook configuration options
 */
export interface UseChromeMCPCompatibleInputOptions<T extends Record<string, string>> {
  /**
   * Initial values for the form fields
   */
  initialValues?: T;

  /**
   * Callback invoked when any field value changes
   * Receives the complete values object
   */
  onValuesChange?: (values: T) => void;

  /**
   * Enable/disable DOM synchronization
   * @default true
   */
  enableDomSync?: boolean;
}

/**
 * Hook return value
 */
export interface UseChromeMCPCompatibleInputReturn<T extends Record<string, string>> {
  /**
   * React ref objects for each registered field
   * Use these to attach to input/textarea elements
   */
  refs: Record<keyof T, React.RefObject<HTMLInputElement | HTMLTextAreaElement>>;

  /**
   * Current values of all fields
   */
  values: T;

  /**
   * Handler to update a field value programmatically
   * @param field - Field name to update
   * @param value - New value for the field
   */
  handleChange: (field: keyof T, value: string) => void;

  /**
   * Register a field and get its ref
   * Call this for each input field you want to track
   * @param field - Field name to register
   * @returns React ref object for the field
   */
  register: (field: keyof T) => React.RefObject<HTMLInputElement | HTMLTextAreaElement>;

  /**
   * Reset all values to initial values or provided values
   * @param values - Optional new initial values
   */
  resetValues: (values?: T) => void;

  /**
   * Get the current DOM value for a field
   * Useful for debugging or custom sync logic
   * @param field - Field name to read
   * @returns Current DOM value or empty string if element not found
   */
  getDomValue: (field: keyof T) => string;

  /**
   * Manually trigger DOM synchronization for all fields
   * Useful after external DOM modifications
   */
  syncFromDom: () => void;
}

/**
 * Custom hook for Chrome MCP compatible input handling
 *
 * This hook solves the issue where Chrome DevTools MCP's fill operation
 * updates the DOM directly without triggering React's onChange events.
 *
 * @param options - Hook configuration options
 * @returns Hook return value with refs, values, and handlers
 *
 * @example
 * ```tsx
 * // Basic usage
 * function MyForm() {
 *   const { values, handleChange, register } = useChromeMCPCompatibleInput({
 *     initialValues: { name: '', email: '' },
 *   });
 *
 *   return (
 *     <form>
 *       <Input
 *         label="Name"
 *         value={values.name}
 *         onChange={(e) => handleChange('name', e.target.value)}
 *         ref={register('name')}
 *       />
 *       <Input
 *         label="Email"
 *         value={values.email}
 *         onChange={(e) => handleChange('email', e.target.value)}
 *         ref={register('email')}
 *       />
 *     </form>
 *   );
 * }
 * ```
 *
 * @example
 * ```tsx
 * // With change callback
 * function MyForm() {
 *   const { values, handleChange, register } = useChromeMCPCompatibleInput({
 *     initialValues: { name: '', email: '' },
 *     onValuesChange: (values) => {
 *       console.log('Form values changed:', values);
 *       // Send to API, validate, etc.
 *     },
 *   });
 *
 *   // ... rest of component
 * }
 * ```
 *
 * @example
 * ```tsx
 * // With manual reset
 * function MyForm() {
 *   const { values, handleChange, register, resetValues } = useChromeMCPCompatibleInput({
 *     initialValues: { name: '', email: '' },
 *   });
 *
 *   const handleReset = () => {
 *     resetValues(); // Reset to initial values
 *     // or
 *     resetValues({ name: 'John', email: 'john@example.com' }); // Reset to new values
 *   };
 *
 *   // ... rest of component
 * }
 * ```
 */
export function useChromeMCPCompatibleInput<
  T extends Record<string, string> = Record<string, string>
>(
  options: UseChromeMCPCompatibleInputOptions<T> = {}
): UseChromeMCPCompatibleInputReturn<T> {
  const {
    initialValues = {} as T,
    onValuesChange,
    enableDomSync = true,
  } = options;

  // State for all field values
  const [values, setValues] = useState<T>(initialValues);

  // Store refs for all registered fields
  const refsRef = useRef<Record<keyof T, React.RefObject<HTMLInputElement | HTMLTextAreaElement>>>(
    {} as Record<keyof T, React.RefObject<HTMLInputElement | HTMLTextAreaElement>>
  );

  // Store initial values for reset functionality
  const initialValuesRef = useRef<T>(initialValues);

  /**
   * Update initial values ref when initialValues prop changes
   */
  useEffect(() => {
    initialValuesRef.current = initialValues;
  }, [initialValues]);

  /**
   * Chrome MCP兼容性: 监听DOM值变化并同步到state
   *
   * 问题: Chrome DevTools MCP的fill操作只更新DOM，不触发React onChange事件
   * 解决: 使用useEffect监听DOM值，当DOM与state不同时自动同步
   *
   * 技术细节:
   * - 只在DOM值与state值不同时才更新（避免无限循环）
   * - 批量更新所有变化的字段（减少re-render次数）
   * - 支持input和textarea元素
   */
  useEffect(() => {
    if (!enableDomSync) {
      return;
    }

    const refs = refsRef.current;
    const fieldNames = Object.keys(refs) as Array<keyof T>;

    // Early return if no refs registered
    if (fieldNames.length === 0) {
      return;
    }

    // Check if all refs are ready
    const allRefsReady = fieldNames.every(
      (fieldName) => refs[fieldName]?.current !== null && refs[fieldName]?.current !== undefined
    );

    if (!allRefsReady) {
      return;
    }

    // Read current DOM values
    const domValues: Partial<Record<keyof T, string>> = {};
    fieldNames.forEach((fieldName) => {
      const element = refs[fieldName]?.current;
      if (element) {
        domValues[fieldName] = element.value;
      }
    });

    // Collect updates (only if DOM differs from state)
    const updates: Partial<T> = {};
    let hasChanges = false;

    fieldNames.forEach((fieldName) => {
      const domValue = domValues[fieldName] || '';
      const stateValue = values[fieldName] || '';

      if (domValue !== stateValue) {
        updates[fieldName] = domValue as T[keyof T];
        hasChanges = true;
      }
    });

    // Batch updates to prevent multiple re-renders
    if (hasChanges) {
      setValues((prev) => {
        const newValues = { ...prev, ...updates };
        return newValues;
      });
    }
  }, [values, enableDomSync]);

  /**
   * Notify parent component when values change
   */
  useEffect(() => {
    if (onValuesChange) {
      onValuesChange(values);
    }
  }, [values, onValuesChange]);

  /**
   * Register a field and get its ref
   * Note: Uses createRef() instead of useRef() because this is called dynamically
   * inside a callback, and useRef() can only be called at the top level of a component.
   */
  const register = useCallback(
    (field: keyof T): React.RefObject<HTMLInputElement | HTMLTextAreaElement> => {
      if (!refsRef.current[field]) {
        // Use createRef() instead of useRef() because we're inside a callback
        // useRef() can only be called at the top level of a component
        refsRef.current[field] = React.createRef<HTMLInputElement | HTMLTextAreaElement>();
      }
      return refsRef.current[field];
    },
    []
  );

  /**
   * Handle field value change
   */
  const handleChange = useCallback((field: keyof T, value: string): void => {
    setValues((prev) => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  /**
   * Reset all values to initial values or provided values
   */
  const resetValues = useCallback((newValues?: T): void => {
    const resetTo = newValues || initialValuesRef.current;
    setValues(resetTo);
  }, []);

  /**
   * Get the current DOM value for a field
   */
  const getDomValue = useCallback((field: keyof T): string => {
    const ref = refsRef.current[field];
    return ref?.current?.value || '';
  }, []);

  /**
   * Manually trigger DOM synchronization for all fields
   * Note: Respects the enableDomSync option - will not sync if disabled
   */
  const syncFromDom = useCallback((): void => {
    // Respect the enableDomSync option
    if (!enableDomSync) {
      return;
    }

    const refs = refsRef.current;
    const fieldNames = Object.keys(refs) as Array<keyof T>;

    const updates: Partial<T> = {};
    let hasChanges = false;

    fieldNames.forEach((fieldName) => {
      const element = refs[fieldName]?.current;
      if (element) {
        const domValue = element.value;
        const stateValue = values[fieldName] || '';

        if (domValue !== stateValue) {
          updates[fieldName] = domValue as T[keyof T];
          hasChanges = true;
        }
      }
    });

    if (hasChanges) {
      setValues((prev) => ({ ...prev, ...updates }));
    }
  }, [values, enableDomSync]);

  return {
    refs: refsRef.current,
    values,
    handleChange,
    register,
    resetValues,
    getDomValue,
    syncFromDom,
  };
}

/**
 * Type helper for creating a form values object from field names
 *
 * @example
 * ```tsx
 * type FormValues = FormValuesFromFields<'name' | 'email' | 'phone'>;
 * // Result: { name: string; email: string; phone: string }
 * ```
 */
export type FormValuesFromFields<T extends string> = {
  [K in T]: string;
};

/**
 * Convenience hook for typed form fields
 *
 * @example
 * ```tsx
 * type MyFormFields = 'name' | 'email' | 'phone';
 *
 * function MyForm() {
 *   const { values, handleChange, register } = useChromeMCPForm<MyFormFields>({
 *     initialValues: { name: '', email: '', phone: '' },
 *   });
 *
 *   return (
 *     <form>
 *       <Input
 *         label="Name"
 *         value={values.name}
 *         onChange={(e) => handleChange('name', e.target.value)}
 *         ref={register('name')}
 *       />
 *     </form>
 *   );
 * }
 * ```
 */
export function useChromeMCPForm<T extends string>(
  options: UseChromeMCPCompatibleInputOptions<FormValuesFromFields<T>>
): UseChromeMCPCompatibleInputReturn<FormValuesFromFields<T>> {
  return useChromeMCPCompatibleInput<FormValuesFromFields<T>>(options);
}

export default useChromeMCPCompatibleInput;
