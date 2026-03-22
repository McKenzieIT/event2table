/**
 * Checkbox Component - Cyberpunk Lab Theme
 *
 * A modern, tech-inspired checkbox with smooth animations and glow effects.
 * Supports checked, unchecked, and indeterminate states.
 *
 * @example
 * // Basic checkbox
 * <Checkbox
 *   label="Enable notifications"
 *   checked={enabled}
 *   onChange={(checked) => setEnabled(checked)}
 * />
 *
 * @example
 * // Indeterminate state
 * <Checkbox
 *   label="Select all"
 *   checked={allSelected}
 *   indeterminate={someSelected}
 *   onChange={handleSelectAll}
 * />
 *
 * @example
 * // Disabled
 * <Checkbox
 *   label="Disabled option"
 *   disabled
 * />
 */

import React, { useEffect, forwardRef, useMemo, type ChangeEvent, type ComponentPropsWithoutRef } from 'react';

import './Checkbox.css';

import { useCheckboxField } from '../hooks/useToggleField';
import { buildConditionalClasses, buildWrapperClasses } from '../utils/classNames';
import { compareCheckboxProps } from '../utils/memoComparators';

/**
 * Props for the Checkbox component
 */
export interface CheckboxProps extends Omit<ComponentPropsWithoutRef<'input'>, 'onChange' | 'type'> {
  /**
   * Label text displayed next to the checkbox
   */
  label?: string;

  /**
   * Whether the checkbox is checked
   * @default false
   */
  checked?: boolean;

  /**
   * Whether the checkbox is in indeterminate state
   * @default false
   */
  indeterminate?: boolean;

  /**
   * Whether the checkbox is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether the checkbox is required
   * @default false
   */
  required?: boolean;

  /**
   * Error message to display
   * When provided, the checkbox will be styled as invalid
   */
  error?: string;

  /**
   * Additional CSS class names
   */
  className?: string;

  /**
   * Callback function when checkbox state changes
   * @param checked - The new checked state
   * @param event - The original change event
   */
  onChange?: (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => void;

  /**
   * Value attribute for the checkbox input
   */
  value?: string;

  /**
   * Name attribute for the checkbox input
   */
  name?: string;

  /**
   * ID attribute for the checkbox input
   * If not provided, a unique ID will be generated
   */
  id?: string;
}

/**
 * Checkbox Component - TypeScript Version
 *
 * A modern, tech-inspired checkbox with smooth animations and glow effects.
 * Supports checked, unchecked, and indeterminate states.
 */
const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(({
  label,
  checked = false,
  indeterminate = false,
  disabled = false,
  required = false,
  error,
  className = '',
  onChange,
  value,
  name,
  id,
  ...props
}, ref) => {
  // 使用自定义 Hook 管理表单字段逻辑
  const { fieldId, fieldRef, mergedRef, isInvalid, handleCheckboxChange } = useCheckboxField({
    customId: id,
    error,
    onCheckboxChange: onChange,
    disabled,
    checked,
    ref
  });

  // Handle indeterminate state
  useEffect(() => {
    if (fieldRef.current) {
      fieldRef.current.indeterminate = indeterminate;
    }
  }, [indeterminate, fieldRef]);

  // 使用工具函数构建 CSS 类名
  const wrapperClass = buildWrapperClasses('cyber-checkbox-wrapper', {
    invalid: isInvalid,
    disabled
  });

  const checkboxClass = buildConditionalClasses('cyber-checkbox', {
    checked,
    indeterminate,
    invalid: isInvalid,
    disabled
  }, [className]);

  return (
    <div className={wrapperClass}>
      <label className="cyber-checkbox-label" htmlFor={fieldId}>
        <input
          ref={mergedRef}
          id={fieldId}
          type="checkbox"
          name={name}
          value={value}
          checked={checked}
          disabled={disabled}
          onChange={handleCheckboxChange}
          aria-invalid={isInvalid}
          aria-required={required}
          aria-checked={indeterminate ? 'mixed' : checked}
          className="cyber-checkbox-input"
          {...props}
        />

        <span className={checkboxClass} aria-hidden="true">
          {(checked || indeterminate) && (
            <span className="cyber-checkbox-icon">
              {indeterminate ? (
                <span className="cyber-checkbox-indeterminate" />
              ) : (
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path
                    d="M2 7L5 10L12 3"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </span>
          )}
        </span>

        {label && (
          <span className="cyber-checkbox-text">
            {label}
            {required && <span className="cyber-checkbox-required" aria-hidden="true"> *</span>}
          </span>
        )}
      </label>

      {isInvalid && (
        <p className="cyber-checkbox__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

// 使用共享的 memo 比较函数
const MemoizedCheckbox = React.memo(Checkbox, compareCheckboxProps);

MemoizedCheckbox.displayName = 'MemoizedCheckbox';

export { MemoizedCheckbox as Checkbox };
export type { CheckboxProps };