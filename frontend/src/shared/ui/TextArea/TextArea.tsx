/**
 * TextArea Component - Cyberpunk Lab Theme
 *
 * Multi-line text input with focus glow
 *
 * @example
 * // Basic textarea
 * <TextArea
 *   label="Description"
 *   placeholder="Enter description..."
 *   rows={4}
 * />
 *
 * @example
 * // With error state
 * <TextArea
 *   label="Description"
 *   error="Description is required"
 *   rows={4}
 * />
 *
 * @example
 * // With character count
 * <TextArea
 *   label="Bio"
 *   maxLength={500}
 *   showCount
 *   rows={4}
 * />
 *
 * @example
 * // Disabled
 * <TextArea
 *   label="Description"
 *   disabled
 *   rows={4}
 * />
 */

import React, {
  forwardRef,
  useId,
  useCallback,
  useMemo,
  TextareaHTMLAttributes,
  ChangeEvent,
  FocusEvent,
  ReactNode
} from 'react';
import './TextArea.css';

/**
 * Resize options for textarea
 */
type TextAreaResize = 'none' | 'both' | 'horizontal' | 'vertical' | 'block' | 'inline';

/**
 * Props for the TextArea component
 *
 * Migration Notes from PropTypes:
 * - label: PropTypes.string → label?: string
 * - placeholder: PropTypes.string → placeholder?: string
 * - error: PropTypes.string → error?: string
 * - disabled: PropTypes.bool (default: false) → disabled?: boolean
 * - required: PropTypes.bool (default: false) → required?: boolean
 * - rows: PropTypes.number (default: 4) → rows?: number
 * - resize: PropTypes.oneOf(['none', 'both', 'horizontal', 'vertical']) (default: 'vertical') → resize?: TextAreaResize
 * - maxLength: PropTypes.number → maxLength?: number
 * - helperText: PropTypes.string → helperText?: string
 * - showCount: PropTypes.bool (default: false) → showCount?: boolean
 * - className: PropTypes.string (default: '') → className?: string
 * - value: PropTypes.string → value?: string
 * - onChange: PropTypes.func → onChange?: ChangeEventHandler<HTMLTextAreaElement>
 * - onBlur: PropTypes.func → onBlur?: FocusEventHandler<HTMLTextAreaElement>
 * - onFocus: PropTypes.func → onFocus?: FocusEventHandler<HTMLTextAreaElement>
 * - name: PropTypes.string → name?: string
 * - readOnly: PropTypes.bool (default: false) → readOnly?: boolean
 * - autoFocus: PropTypes.bool (default: false) → autoFocus?: boolean
 */
export interface TextAreaProps extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'onChange' | 'onBlur' | 'onFocus' | 'value' | 'resize' | 'rows'> {
  /**
   * Label text displayed above the textarea
   */
  label?: string;

  /**
   * Placeholder text shown when textarea is empty
   */
  placeholder?: string;

  /**
   * Error message to display (triggers invalid state)
   */
  error?: string;

  /**
   * Whether the textarea is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether the textarea is required (shows asterisk)
   * @default false
   */
  required?: boolean;

  /**
   * Number of visible text lines
   * @default 4
   */
  rows?: number;

  /**
   * Whether the textarea can be resized and in which directions
   * @default 'vertical'
   */
  resize?: TextAreaResize;

  /**
   * Maximum length of the textarea value
   */
  maxLength?: number;

  /**
   * Helper text displayed below the textarea
   */
  helperText?: string;

  /**
   * Whether to show character count (requires maxLength)
   * @default false
   */
  showCount?: boolean;

  /**
   * Additional CSS class names
   */
  className?: string;

  /**
   * Textarea value (controlled component)
   */
  value?: string;

  /**
   * Change event handler
   */
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>;

  /**
   * Blur event handler
   */
  onBlur?: React.FocusEventHandler<HTMLTextAreaElement>;

  /**
   * Focus event handler
   */
  onFocus?: React.FocusEventHandler<HTMLTextAreaElement>;

  /**
   * Name attribute for the textarea
   */
  name?: string;

  /**
   * Whether the textarea is read-only
   * @default false
   */
  readOnly?: boolean;

  /**
   * Whether to auto-focus the textarea on mount
   * @default false
   */
  autoFocus?: boolean;
}

/**
 * TextArea Component
 *
 * A cyberpunk-themed multi-line text input field with support for labels,
 * error states, helper text, character count, and accessibility features.
 *
 * Optimized with React.memo to prevent unnecessary re-renders.
 */
const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(({
  label,
  placeholder,
  error,
  disabled = false,
  required = false,
  rows = 4,
  resize = 'vertical',
  maxLength,
  helperText,
  showCount = false,
  className = '',
  value,
  onChange,
  onBlur,
  onFocus,
  name,
  readOnly = false,
  autoFocus = false,
  ...props
}, ref) => {
  // Generate unique ID for label-textarea association
  const inputId = useId();

  // Determine if textarea is in invalid state
  const isInvalid = Boolean(error);

  // Calculate current length for character count
  const currentLength = value?.length || 0;

  // PERFORMANCE: useCallback to stable event handlers
  // Prevents re-creation of functions on every render
  const handleChange = useCallback((event: ChangeEvent<HTMLTextAreaElement>) => {
    onChange?.(event);
  }, [onChange]);

  // PERFORMANCE: useCallback to stable event handlers
  // Prevents re-creation of functions on every render
  const handleBlur = useCallback((event: FocusEvent<HTMLTextAreaElement>) => {
    onBlur?.(event);
  }, [onBlur]);

  // PERFORMANCE: useCallback to stable event handlers
  // Prevents re-creation of functions on every render
  const handleFocus = useCallback((event: FocusEvent<HTMLTextAreaElement>) => {
    onFocus?.(event);
  }, [onFocus]);

  // PERFORMANCE: useMemo to cache CSS class computations
  // Prevents re-creation of class strings on every render
  const wrapperClass = useMemo(() => {
    return [
      'cyber-textarea-wrapper',
      isInvalid && 'cyber-textarea-wrapper--invalid',
      disabled && 'cyber-textarea-wrapper--disabled'
    ].filter(Boolean).join(' ');
  }, [isInvalid, disabled]);

  // PERFORMANCE: useMemo to cache CSS class computations
  // Prevents re-creation of class strings on every render
  const textareaClass = useMemo(() => {
    return [
      'cyber-textarea',
      isInvalid && 'cyber-textarea--invalid',
      disabled && 'cyber-textarea--disabled'
    ].filter(Boolean).join(' ');
  }, [isInvalid, disabled]);

  return (
    <div className={['cyber-textarea', className].filter(Boolean).join(' ')}>
      {/* Label Section */}
      {label && (
        <label htmlFor={inputId} className="cyber-textarea__label">
          {label}
          {required && (
            <span className="cyber-textarea__required" aria-hidden="true">
              {' '}
              *
            </span>
          )}
        </label>
      )}

      {/* Textarea Wrapper Section */}
      <div className={wrapperClass}>
        <textarea
          ref={ref}
          id={inputId}
          name={name}
          className={textareaClass}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readOnly}
          autoFocus={autoFocus}
          rows={rows}
          maxLength={maxLength}
          value={value}
          onChange={handleChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          style={{ resize }}
          aria-invalid={isInvalid}
          aria-required={required}
          aria-describedby={
            isInvalid
              ? `${inputId}-error`
              : helperText
                ? `${inputId}-helper`
                : undefined
          }
          {...props}
        />
      </div>

      {/* Character Count */}
      {showCount && maxLength && (
        <div className="cyber-textarea__count">
          {currentLength}/{maxLength}
        </div>
      )}

      {/* Error Message */}
      {isInvalid && (
        <p id={`${inputId}-error`} className="cyber-textarea__error" role="alert">
          {error}
        </p>
      )}

      {/* Helper Text */}
      {helperText && !isInvalid && (
        <p id={`${inputId}-helper`} className="cyber-textarea__helper">
          {helperText}
        </p>
      )}
    </div>
  );
});

// Set display name for debugging
TextArea.displayName = 'TextArea';

// Memoize TextArea component to prevent unnecessary re-renders
// Custom comparison since value and onChange change frequently
const MemoizedTextArea = React.memo(TextArea, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.error === nextProps.error &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.onChange === nextProps.onChange
  );
});

// Set display name for memoized component
MemoizedTextArea.displayName = 'MemoizedTextArea';

export default MemoizedTextArea;
