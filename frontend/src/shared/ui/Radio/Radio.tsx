/**
 * Radio Component - Cyberpunk Lab Theme
 *
 * A modern, tech-inspired radio button with smooth animations and glow effects.
 * Designed to be used in radio groups for single-select options.
 *
 * @example
 * // Single radio
 * <Radio
 *   label="Football"
 *   name="game"
 *   value="football"
 *   checked={selectedGame === 'football'}
 *   onChange={(value) => setSelectedGame(value)}
 * />
 *
 * @example
 * // Radio group
 * {[
 *   { value: 'football', label: 'Football' },
 *   { value: 'basketball', label: 'Basketball' }
 * ].map(option => (
 *   <Radio
 *     key={option.value}
 *     label={option.label}
 *     name="game"
 *     value={option.value}
 *     checked={selectedGame === option.value}
 *     onChange={(value) => setSelectedGame(value)}
 *   />
 * ))}
 *
 * @example
 * // Disabled
 * <Radio
 *   label="Disabled option"
 *   name="game"
 *   value="tennis"
 *   disabled
 * />
 */

import React, { forwardRef, type ChangeEvent, type ComponentPropsWithoutRef } from 'react';

import './Radio.css';

import { useRadioField } from '../hooks/useToggleField';
import { buildConditionalClasses, buildWrapperClasses } from '../utils/classNames';
import { compareToggleProps } from '../utils/memoComparators';

/**
 * Props for the Radio component
 */
export interface RadioProps extends Omit<ComponentPropsWithoutRef<'input'>, 'onChange' | 'type'> {
  /**
   * Label text displayed next to the radio button
   */
  label?: string;

  /**
   * Whether the radio button is checked
   * @default false
   */
  checked?: boolean;

  /**
   * Whether the radio button is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether the radio button is required
   * @default false
   */
  required?: boolean;

  /**
   * Error message to display
   * When provided, the radio button will be styled as invalid
   */
  error?: string;

  /**
   * Additional CSS class names
   */
  className?: string;

  /**
   * Callback function when radio state changes
   * @param value - The value of the selected radio
   * @param event - The original change event
   */
  onChange?: (value: string, event: React.ChangeEvent<HTMLInputElement>) => void;

  /**
   * Value attribute for the radio input
   */
  value?: string;

  /**
   * Name attribute for the radio input
   * Used to group radio buttons together
   */
  name?: string;

  /**
   * ID attribute for the radio input
   * If not provided, a unique ID will be generated
   */
  id?: string;
}

/**
 * Radio Component - TypeScript Version
 *
 * A modern, tech-inspired radio button with smooth animations and glow effects.
 * Designed to be used in radio groups for single-select options.
 */
const Radio = forwardRef<HTMLInputElement, RadioProps>(({
  label,
  checked = false,
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
  const { fieldId, fieldRef, mergedRef, isInvalid, handleRadioChange } = useRadioField({
    customId: id,
    error,
    onRadioChange: onChange,
    disabled,
    ref
  });

  // 使用工具函数构建 CSS 类名
  const wrapperClass = buildWrapperClasses('cyber-radio-wrapper', {
    invalid: isInvalid,
    disabled
  });

  const radioClass = buildConditionalClasses('cyber-radio', {
    checked,
    invalid: isInvalid,
    disabled
  }, [className]);

  return (
    <div className={wrapperClass}>
      <label className="cyber-radio-label" htmlFor={fieldId}>
        <input
          ref={mergedRef}
          id={fieldId}
          type="radio"
          name={name}
          value={value}
          checked={checked}
          disabled={disabled}
          onChange={handleRadioChange}
          aria-invalid={isInvalid}
          aria-required={required}
          className="cyber-radio-input"
          {...props}
        />

        <span className={radioClass} aria-hidden="true">
          {checked && (
            <span className="cyber-radio-dot" />
          )}
        </span>

        {label && (
          <span className="cyber-radio-text">
            {label}
            {required && <span className="cyber-radio-required" aria-hidden="true"> *</span>}
          </span>
        )}
      </label>

      {isInvalid && (
        <p className="cyber-radio__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

Radio.displayName = 'Radio';

// 使用共享的 memo 比较函数
const MemoizedRadio = React.memo(Radio, compareToggleProps);

MemoizedRadio.displayName = 'MemoizedRadio';

export { MemoizedRadio as Radio };
export type { RadioProps };