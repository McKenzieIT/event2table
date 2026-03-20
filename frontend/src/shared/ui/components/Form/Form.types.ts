import { z } from 'zod';
import { UseFormReturn, FieldValues, FieldPath } from 'react-hook-form';

/**
 * Form validation mode options
 */
export type FormValidationMode = 'onBlur' | 'onChange' | 'onSubmit' | 'onTouched' | 'all';

/**
 * Form submission state
 */
export interface FormSubmissionState {
  isSubmitting: boolean;
  isValid: boolean;
  isDirty: boolean;
  submitCount: number;
}

/**
 * Common field props for all form fields
 */
export interface FormFieldProps<TFieldValues extends FieldValues = FieldValues> {
  /**
   * Field name - must match a key in the form schema
   */
  name: FieldPath<TFieldValues>;
  
  /**
   * Field label
   */
  label?: string;
  
  /**
   * Helper text displayed below the field
   */
  helperText?: string;
  
  /**
   * Whether the field is required
   */
  required?: boolean;
  
  /**
   * Whether the field is disabled
   */
  disabled?: boolean;
  
  /**
   * Additional CSS class names
   */
  className?: string;
}

/**
 * Form component props
 */
export interface FormProps<TFieldValues extends FieldValues = FieldValues, TContext = any> {
  /**
   * React Hook Form instance
   */
  form: UseFormReturn<TFieldValues, TContext>;
  
  /**
   * Form submission handler
   */
  onSubmit: (data: TFieldValues) => void | Promise<void>;
  
  /**
   * Validation mode
   * @default 'onBlur'
   */
  validationMode?: FormValidationMode;
  
  /**
   * Re-validate mode when data changes
   * @default 'onChange'
   */
  reValidateMode?: FormValidationMode;
  
  /**
   * Children components
   */
  children: React.ReactNode;
  
  /**
   * Additional CSS class names
   */
  className?: string;
  
  /**
   * Form ID
   */
  id?: string;
  
  /**
   * Whether to reset form after successful submission
   * @default false
   */
  resetAfterSubmit?: boolean;
}

/**
 * Form context type
 */
export interface FormContextValue<TFieldValues extends FieldValues = FieldValues, TContext = any> {
  form: UseFormReturn<TFieldValues, TContext>;
  isSubmitting: boolean;
  isValid: boolean;
  isDirty: boolean;
}

/**
 * Input field specific props
 */
export interface InputFieldProps<TFieldValues extends FieldValues = FieldValues>
  extends FormFieldProps<TFieldValues> {
  /**
   * Input type
   * @default 'text'
   */
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search';
  
  /**
   * Placeholder text
   */
  placeholder?: string;
  
  /**
   * Auto-complete attribute
   */
  autoComplete?: string;
}

/**
 * Select option
 */
export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

/**
 * Select field specific props
 */
export interface SelectFieldProps<TFieldValues extends FieldValues = FieldValues>
  extends FormFieldProps<TFieldValues> {
  /**
   * Available options
   */
  options: SelectOption[];
  
  /**
   * Placeholder text
   */
  placeholder?: string;
  
  /**
   * Enable search functionality
   */
  searchable?: boolean;
}

/**
 * Checkbox field specific props
 */
export interface CheckboxFieldProps<TFieldValues extends FieldValues = FieldValues>
  extends Omit<FormFieldProps<TFieldValues>, 'label'> {
  /**
   * Checkbox label
   */
  label?: string;
  
  /**
   * Indeterminate state
   */
  indeterminate?: boolean;
}

/**
 * Radio option
 */
export interface RadioOption {
  value: string;
  label: string;
  disabled?: boolean;
}

/**
 * Radio field specific props
 */
export interface RadioFieldProps<TFieldValues extends FieldValues = FieldValues>
  extends FormFieldProps<TFieldValues> {
  /**
   * Available options
   */
  options: RadioOption[];
  
  /**
   * Layout direction
   * @default 'column'
   */
  direction?: 'row' | 'column';
}

/**
 * Form error message component props
 */
export interface FormErrorMessageProps {
  /**
   * Error message to display
   */
  error?: string;
  
  /**
   * Additional CSS class names
   */
  className?: string;
}

/**
 * Form helper text component props
 */
export interface FormHelperTextProps {
  /**
   * Helper text to display
   */
  text?: string;
  
  /**
   * Additional CSS class names
   */
  className?: string;
}
