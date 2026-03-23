import React, { useMemo, useState, useCallback, useRef } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import type { FieldValues, FieldPath } from 'react-hook-form';

import { FormErrorMessage, FormHelperText } from './Form';
import type { RichTextFieldProps } from './Form.types';

/**
 * Default toolbar configuration
 */
const DEFAULT_TOOLBAR = ['bold', 'italic', 'underline', 'link', 'list'] as const;

/**
 * Toolbar button definitions
 */
const TOOLBAR_BUTTONS = {
  bold: {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>,
    title: 'Bold (Ctrl+B)',
    command: 'bold'
  },
  italic: {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>,
    title: 'Italic (Ctrl+I)',
    command: 'italic'
  },
  underline: {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3"/><line x1="4" y1="21" x2="20" y2="21"/></svg>,
    title: 'Underline (Ctrl+U)',
    command: 'underline'
  },
  link: {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>,
    title: 'Insert Link',
    command: 'createLink'
  },
  list: {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>,
    title: 'Bullet List',
    command: 'insertUnorderedList'
  },
  heading: {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 12h8"/><path d="M4 18V6"/><path d="M12 18V6"/><path d="M17 12l3-2v8"/></svg>,
    title: 'Heading',
    command: 'formatBlock',
    value: 'h2'
  }
} as const;

/**
 * FormRichText Component
 * 
 * Rich text editor component integrated with React Hook Form.
 * Provides a customizable toolbar with character count and validation.
 * 
 * FEATURES:
 * - Customizable toolbar
 * - Character count with limit
 * - Keyboard shortcuts
 * - Cyberpunk Lab Theme styling
 * - Accessible (ARIA attributes)
 * 
 * @example
 * ```tsx
 * <FormRichText
 *   name="content"
 *   label="Content"
 *   maxLength={5000}
 *   toolbar={['bold', 'italic', 'link']}
 *   required
 * />
 * ```
 */
export const FormRichText = <
  TFieldValues extends FieldValues = FieldValues
>({
  name,
  label,
  helperText,
  required = false,
  disabled = false,
  className = '',
  maxLength,
  showCharCount = true,
  toolbar = [...DEFAULT_TOOLBAR],
  placeholder = 'Write your content...',
  minHeight = 150,
  maxHeight = 400,
  ...props
}: RichTextFieldProps<TFieldValues>) => {
  const {
    control,
    formState: { errors },
  } = useFormContext<TFieldValues>();

  const editorRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [charCount, setCharCount] = useState(0);

  // Get error message for this field
  const error = useMemo(() => {
    const fieldError = errors[name];
    return fieldError?.message as string | undefined;
  }, [errors, name]);

  // Memoize wrapper class
  const wrapperClass = useMemo(() => {
    return ['form-field-wrapper', 'form-richtext-wrapper', className].filter(Boolean).join(' ');
  }, [className]);

  // Memoize editor container class
  const editorContainerClass = useMemo(() => {
    return [
      'form-richtext-container',
      isFocused && 'form-richtext-container--focused',
      error && 'form-richtext-container--error',
      disabled && 'form-richtext-container--disabled'
    ].filter(Boolean).join(' ');
  }, [isFocused, error, disabled]);

  // Memoize label class
  const labelClass = useMemo(() => {
    return [
      'form-label',
      required && 'form-label--required'
    ].filter(Boolean).join(' ');
  }, [required]);

  // Execute toolbar command
  const executeCommand = useCallback((command: string, value?: string) => {
    if (disabled) return;
    
    document.execCommand(command, false, value);
    editorRef.current?.focus();
    
    // Update character count
    const text = editorRef.current?.innerText || '';
    setCharCount(text.length);
  }, [disabled]);

  // Handle link insertion
  const handleLinkInsert = useCallback(() => {
    if (disabled) return;
    
    const url = prompt('Enter URL:');
    if (url) {
      executeCommand('createLink', url);
    }
  }, [disabled, executeCommand]);

  // Handle toolbar button click
  const handleToolbarClick = useCallback((buttonKey: string) => {
    const button = TOOLBAR_BUTTONS[buttonKey as keyof typeof TOOLBAR_BUTTONS];
    if (!button) return;
    
    if (buttonKey === 'link') {
      handleLinkInsert();
    } else if (button.value) {
      executeCommand(button.command, button.value);
    } else {
      executeCommand(button.command);
    }
  }, [handleLinkInsert, executeCommand]);

  // Handle editor input
  const handleInput = useCallback((
    e: React.FormEvent<HTMLDivElement>,
    onChange: (value: string) => void
  ) => {
    const html = e.currentTarget.innerHTML;
    const text = e.currentTarget.innerText || '';
    
    // Check max length
    if (maxLength && text.length > maxLength) {
      // Truncate content
      const selection = window.getSelection();
      const range = selection?.getRangeAt(0);
      
      if (range) {
        // Restore previous content
        e.currentTarget.innerHTML = html.substring(0, html.length - 1);
      }
      return;
    }
    
    setCharCount(text.length);
    onChange(html);
  }, [maxLength]);

  // Handle keyboard shortcuts
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.ctrlKey || e.metaKey) {
      switch (e.key.toLowerCase()) {
        case 'b':
          e.preventDefault();
          executeCommand('bold');
          break;
        case 'i':
          e.preventDefault();
          executeCommand('italic');
          break;
        case 'u':
          e.preventDefault();
          executeCommand('underline');
          break;
      }
    }
  }, [executeCommand]);

  // Check if character count exceeds limit
  const isOverLimit = maxLength ? charCount > maxLength : false;

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
        render={({ field }) => {
          // Sync editor content with form value
          const handleEditorRef = (el: HTMLDivElement | null) => {
            editorRef.current = el;
            if (el && field.value && !el.innerHTML) {
              el.innerHTML = field.value;
              setCharCount(el.innerText?.length || 0);
            }
          };

          return (
            <div className={editorContainerClass}>
              {/* Toolbar */}
              <div className="form-richtext-toolbar" role="toolbar" aria-label="Text formatting">
                {toolbar.map((buttonKey) => {
                  const button = TOOLBAR_BUTTONS[buttonKey as keyof typeof TOOLBAR_BUTTONS];
                  if (!button) return null;
                  
                  return (
                    <button
                      key={buttonKey}
                      type="button"
                      className="form-richtext-toolbar-button"
                      onClick={() => handleToolbarClick(buttonKey)}
                      disabled={disabled}
                      title={button.title}
                      aria-label={button.title}
                    >
                      {button.icon}
                    </button>
                  );
                })}
              </div>

              {/* Editor */}
              <div
                ref={handleEditorRef}
                className="form-richtext-editor"
                contentEditable={!disabled}
                data-placeholder={placeholder}
                onInput={(e) => handleInput(e, field.onChange)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                onKeyDown={handleKeyDown}
                style={{
                  minHeight: `${minHeight}px`,
                  maxHeight: `${maxHeight}px`
                }}
                role="textbox"
                aria-multiline="true"
                aria-disabled={disabled}
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

              {/* Character count */}
              {showCharCount && (
                <div className={`form-richtext-footer ${isOverLimit ? 'form-richtext-footer--error' : ''}`}>
                  <span className="form-richtext-charcount">
                    {charCount}
                    {maxLength && ` / ${maxLength}`}
                  </span>
                </div>
              )}
            </div>
          );
        }}
      />

      <FormErrorMessage error={error} className="form-error-message" />
      {!error && <FormHelperText text={helperText} className="form-helper-text" />}
    </div>
  );
};

FormRichText.displayName = 'FormRichText';

/**
 * Memoized FormRichText component for performance
 */
const MemoizedFormRichText = React.memo(FormRichText) as typeof FormRichText;

export default MemoizedFormRichText;
