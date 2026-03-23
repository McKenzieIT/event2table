import React, { createContext, useContext, forwardRef, useCallback } from 'react';
import { useFormContext, FormProvider } from 'react-hook-form';

import type {
  FormProps,
  FormContextValue,
  FormErrorMessageProps,
  FormHelperTextProps,
} from './Form.types';

/**
 * Form Context
 * 
 * Provides form state and methods to all form field components.
 * This enables clean separation between form logic and UI components.
 */
const FormContext = createContext<FormContextValue | null>(null);

/**
 * Hook to access form context
 * Must be used within a Form component
 */
export const useFormContextValue = <T extends Record<string, any>>() => {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error('useFormContextValue must be used within a Form component');
  }
  return context as FormContextValue<T>;
};

/**
 * Form Component
 * 
 * Main form container that integrates React Hook Form with Zod validation.
 * Provides form context to child components and handles form submission.
 * 
 * PERFORMANCE OPTIMIZATIONS:
 * - Uses React.memo to prevent unnecessary re-renders
 * - Leverages React Hook Form's built-in optimization (uncontrolled inputs)
 * - Context value is memoized to prevent child re-renders
 * - Form submission handler is wrapped in useCallback
 * 
 * @example
 * ```tsx
 * const schema = z.object({
 *   email: z.string().email(),
 *   password: z.string().min(8),
 * });
 * 
 * const form = useForm({
 *   resolver: zodResolver(schema),
 * });
 * 
 * <Form form={form} onSubmit={handleSubmit}>
 *   <FormField name="email" label="Email" />
 *   <FormField name="password" label="Password" type="password" />
 *   <Button type="submit">Submit</Button>
 * </Form>
 * ```
 */
const Form = forwardRef<HTMLFormElement, FormProps>(({
  form,
  onSubmit,
  validationMode = 'onBlur',
  reValidateMode = 'onChange',
  children,
  className = '',
  id,
  resetAfterSubmit = false,
  ...props
}, ref) => {
  const {
    formState: { isSubmitting, isValid, isDirty },
    reset,
  } = form;

  // Handle form submission
  const handleSubmit = useCallback(async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    // Trigger validation and get form data
    const formIsValid = await form.trigger();
    
    if (!formIsValid) {
      return;
    }
    
    // Call onSubmit with form data - use handleSubmit from react-hook-form to properly handle submission state
    await form.handleSubmit(async (data) => {
      await onSubmit(data);
    })(event);
    
    // Reset form after successful submission if requested
    if (resetAfterSubmit) {
      reset();
    }
  }, [form, onSubmit, resetAfterSubmit, reset]);

  // Create context value - memoized to prevent unnecessary re-renders
  const contextValue: FormContextValue = React.useMemo(
    () => ({
      form,
      isSubmitting,
      isValid,
      isDirty,
    }),
    [form, isSubmitting, isValid, isDirty]
  );

  return (
    <FormProvider {...form}>
      <FormContext.Provider value={contextValue}>
        <form
          ref={ref}
          id={id}
          onSubmit={handleSubmit}
          className={className}
          noValidate
          role="form"
          {...props}
        >
          {children}
        </form>
      </FormContext.Provider>
    </FormProvider>
  );
});

Form.displayName = 'Form';

/**
 * FormErrorMessage Component
 * 
 * Displays validation error messages for form fields.
 * Only renders when an error is present.
 * 
 * @example
 * ```tsx
 * <FormErrorMessage error={form.formState.errors.email?.message} />
 * ```
 */
export const FormErrorMessage = React.forwardRef<
  HTMLParagraphElement,
  FormErrorMessageProps
>(({ error, className = '' }, ref) => {
  if (!error) {
    return null;
  }

  return (
    <p
      ref={ref}
      className={`form-error-message ${className}`}
      role="alert"
      aria-live="polite"
    >
      {error}
    </p>
  );
});

FormErrorMessage.displayName = 'FormErrorMessage';

/**
 * FormHelperText Component
 * 
 * Displays helper text below form fields.
 * Only renders when text is provided and there's no error.
 * 
 * @example
 * ```tsx
 * <FormHelperText text="Password must be at least 8 characters" />
 * ```
 */
export const FormHelperText = React.forwardRef<
  HTMLParagraphElement,
  FormHelperTextProps
>(({ text, className = '' }, ref) => {
  if (!text) {
    return null;
  }

  return (
    <p
      ref={ref}
      className={`form-helper-text ${className}`}
      id="form-helper-text"
    >
      {text}
    </p>
  );
});

FormHelperText.displayName = 'FormHelperText';

/**
 * Memoized Form component for performance
 */
const MemoizedForm = React.memo(Form);

export default MemoizedForm;
export type { FormProps, FormContextValue };
