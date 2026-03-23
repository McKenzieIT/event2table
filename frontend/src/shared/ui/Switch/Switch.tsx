/**
 * Switch Component - Cyberpunk Lab Theme
 *
 * A modern, tech-inspired toggle switch with smooth animations and cyan glow.
 * Perfect for binary on/off states like settings, toggles, and preferences.
 *
 * @example
 * // Basic switch
 * <Switch
 *   label="Enable notifications"
 *   checked={enabled}
 *   onChange={(checked) => setEnabled(checked)}
 * />
 *
 * @example
 * // With description
 * <Switch
 *   label="Auto-save"
 *   description="Automatically save changes every 30 seconds"
 *   checked={autoSave}
 *   onChange={setAutoSave}
 * />
 *
 * @example
 * // Disabled
 * <Switch
 *   label="Disabled switch"
 *   disabled
 * />
 */

import React, { forwardRef, type ChangeEvent, type ComponentPropsWithoutRef } from 'react';

import './Switch.css';

import { useSwitchField } from '../hooks/useToggleField';
import { buildConditionalClasses, buildWrapperClasses } from '../utils/classNames';
import { compareToggleProps } from '../utils/memoComparators';

/**
 * Props for the Switch component
 */
export interface SwitchProps extends Omit<ComponentPropsWithoutRef<'input'>, 'type' | 'onChange'> {
  /**
   * Label text for the switch
   */
  label?: string;

  /**
   * Additional description text displayed below the label
   */
  description?: string;

  /**
   * Whether the switch is checked (on)
   * @default false
   */
  checked?: boolean;

  /**
   * Whether the switch is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether the switch is required (shows asterisk)
   * @default false
   */
  required?: boolean;

  /**
   * Error message to display (invalidates the switch)
   */
  error?: string;

  /**
   * Additional CSS class name
   */
  className?: string;

  /**
   * Callback when the switch state changes
   * @param checked - The new checked state
   * @param event - The original change event
   */
  onChange?: (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => void;

  /**
   * Value attribute for the input (useful for forms)
   */
  value?: string;

  /**
   * Name attribute for the input (useful for forms)
   */
  name?: string;

  /**
   * ID attribute for the input (auto-generated if not provided)
   */
  id?: string;
}

export interface SwitchRefHandle {
  focus: () => void;
  blur: () => void;
}

const Switch = forwardRef<HTMLInputElement, SwitchProps>(({
  label,
  description,
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
  const { fieldId, fieldRef, mergedRef, isInvalid, handleSwitchChange, handleKeyDown } = useSwitchField({
    customId: id,
    error,
    onSwitchChange: onChange,
    disabled,
    checked,
    ref
  });

  // 使用工具函数构建 CSS 类名
  const wrapperClass = buildWrapperClasses('cyber-switch-wrapper', {
    invalid: isInvalid,
    disabled
  }, [className]);

  const switchClass = buildConditionalClasses('cyber-switch', {
    checked,
    invalid: isInvalid,
    disabled
  });

  return (
    <div className={wrapperClass}>
      <label className="cyber-switch-label" htmlFor={fieldId}>
        <input
          ref={mergedRef}
          id={fieldId}
          type="checkbox"
          name={name}
          value={value}
          checked={checked}
          disabled={disabled}
          onChange={handleSwitchChange}
          onKeyDown={handleKeyDown}
          aria-invalid={isInvalid}
          aria-required={required}
          className="cyber-switch-input"
          role="switch"
          aria-checked={checked}
          {...props}
        />

        <span className={switchClass} aria-hidden="true">
          <span className="cyber-switch-slider">
            {checked && (
              <span className="cyber-switch-icon">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path
                    d="M2 6L4.5 8.5L10 3"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
            )}
          </span>
        </span>

        {(label || description) && (
          <div className="cyber-switch-content">
            {label && (
              <span className="cyber-switch-label-text">
                {label}
                {required && <span className="cyber-switch-required" aria-hidden="true"> *</span>}
              </span>
            )}
            {description && (
              <span className="cyber-switch-description">{description}</span>
            )}
          </div>
        )}
      </label>

      {isInvalid && (
        <p className="cyber-switch__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

Switch.displayName = 'Switch';

// 使用共享的 memo 比较函数
const MemoizedSwitch = React.memo(Switch, compareToggleProps);

MemoizedSwitch.displayName = 'MemoizedSwitch';

export { MemoizedSwitch as Switch };
export default MemoizedSwitch;