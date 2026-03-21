import React from 'react';
import { SelectOption as SelectOptionType } from './Select.types';
import './Select.css';

export interface SelectOptionProps {
  option: SelectOptionType;
  isSelected: boolean;
  isFocused: boolean;
  multiple: boolean;
  onClick: (value: string | number) => void;
  optionRef: (el: HTMLDivElement | null) => void;
}

/**
 * SelectOption Component
 *
 * Renders a single option in the dropdown
 */
export const SelectOption = React.memo<SelectOptionProps>(({
  option,
  isSelected,
  isFocused,
  multiple,
  onClick,
  optionRef
}) => {
  const optionClass = [
    'cyber-select-option',
    isSelected && 'cyber-select-option--selected',
    isFocused && 'cyber-select-option--focused',
    option.disabled && 'cyber-select-option--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={optionRef}
      className={optionClass}
      role="option"
      aria-selected={isSelected}
      aria-disabled={option.disabled}
      onClick={() => !option.disabled && onClick(option.value)}
    >
      {multiple && isSelected && (
        <span className="cyber-select-check" aria-hidden="true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M3 8L6 11L13 4"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
      )}
      {option.label}
      {!multiple && isSelected && (
        <span className="cyber-select-check" aria-hidden="true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M3 8L6 11L13 4"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
      )}
    </div>
  );
});

SelectOption.displayName = 'SelectOption';
