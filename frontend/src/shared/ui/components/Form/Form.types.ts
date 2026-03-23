import { UseFormReturn, FieldValues, FieldPath } from 'react-hook-form';
import { z } from 'zod';

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

/**
 * Date picker field specific props
 */
export interface DatePickerFieldProps<TFieldValues extends FieldValues = FieldValues>
  extends FormFieldProps<TFieldValues> {
  /**
   * Date format
   * @default 'YYYY-MM-DD'
   */
  format?: string;
  
  /**
   * Show time picker
   * @default false
   */
  showTime?: boolean;
  
  /**
   * Time format
   * @default 'HH:mm'
   */
  timeFormat?: string;
  
  /**
   * Minimum date
   */
  minDate?: Date;
  
  /**
   * Maximum date
   */
  maxDate?: Date;
  
  /**
   * Placeholder text
   */
  placeholder?: string;
}

/**
 * Upload file item
 */
export interface UploadFile {
  /**
   * File unique identifier
   */
  id: string;
  
  /**
   * Original file
   */
  file: File;
  
  /**
   * Upload progress (0-100)
   */
  progress?: number;
  
  /**
   * Upload status
   */
  status?: 'pending' | 'uploading' | 'success' | 'error';
  
  /**
   * Error message if upload failed
   */
  error?: string;
  
  /**
   * Preview URL for images
   */
  previewUrl?: string;
}

/**
 * Upload field specific props
 */
export interface UploadFieldProps<TFieldValues extends FieldValues = FieldValues>
  extends FormFieldProps<TFieldValues> {
  /**
   * Accepted file types
   * @example 'image/*,.pdf'
   */
  accept?: string;
  
  /**
   * Allow multiple files
   * @default false
   */
  multiple?: boolean;
  
  /**
   * Maximum file size in bytes
   * @default 5242880 (5MB)
   */
  maxSize?: number;
  
  /**
   * Maximum number of files
   * @default 10
   */
  maxFiles?: number;
  
  /**
   * Enable drag and drop
   * @default true
   */
  enableDragDrop?: boolean;
  
  /**
   * Upload handler
   */
  onUpload?: (files: File[]) => Promise<UploadFile[]>;
  
  /**
   * Custom upload button text
   */
  buttonText?: string;
  
  /**
   * Show file preview
   * @default true
   */
  showPreview?: boolean;
}

/**
 * Rich text field specific props
 */
export interface RichTextFieldProps<TFieldValues extends FieldValues = FieldValues>
  extends FormFieldProps<TFieldValues> {
  /**
   * Maximum character length
   */
  maxLength?: number;
  
  /**
   * Show character count
   * @default true
   */
  showCharCount?: boolean;
  
  /**
   * Toolbar configuration
   * @default ['bold', 'italic', 'underline', 'link', 'list']
   */
  toolbar?: ('bold' | 'italic' | 'underline' | 'link' | 'list' | 'heading')[];
  
  /**
   * Placeholder text
   */
  placeholder?: string;
  
  /**
   * Minimum height in pixels
   * @default 150
   */
  minHeight?: number;
  
  /**
   * Maximum height in pixels
   * @default 400
   */
  maxHeight?: number;
}
