import React, { MouseEvent, FocusEvent, useRef, KeyboardEvent } from 'react';
import { SelectOption } from './Select.types';
import './Select.css';

export interface SelectInputProps {
  id: string;
  label?: string;
  labelId?: string;
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
  isOpen?: boolean;
  isInvalid?: boolean;
  selectedOptions: SelectOption[];
  searchable?: boolean;
  onTriggerClick: () => void;
  onRemoveOption: (event: MouseEvent, value: string | number) => void;
  onKeyDown: (event: KeyboardEvent<HTMLDivElement>) => void;
  onFocus: (event: FocusEvent<HTMLDivElement>) => void;
  onBlur?: (event: FocusEvent<HTMLDivElement>) => void;
  triggerRef: React.RefObject<HTMLDivElement>;
  ariaDescribedBy?: string;
  required?: boolean;
}

/**
 * SelectInput Component
 *
 * Renders the trigger/input area of the Select component
 */
export const SelectInput = React.memo<SelectInputProps>(({
  id,
  label,
  labelId,
  placeholder = 'Select...',
  disabled = false,
  multiple = false,
  isOpen = false,
  isInvalid = false,
  selectedOptions = [],
  searchable = false,
  onTriggerClick,
  onRemoveOption,
  onKeyDown,
  onFocus,
  onBlur,
  triggerRef,
  ariaDescribedBy,
  required = false
}) => {
  return (
    <>
      {label && (
        <label id={labelId} className="cyber-select__label">
          {label}
          {required && <span className="cyber-select__required" aria-hidden="true">*</span>}
        </label>
      )}

      <div
        ref={triggerRef}
        id={id}
        className={`cyber-select-trigger ${isOpen ? 'cyber-select-trigger--open' : ''}`}
        tabIndex={disabled ? -1 : 0}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-disabled={disabled}
        aria-invalid={isInvalid}
        aria-labelledby={label ? labelId : undefined}
        aria-multiselectable={multiple}
        aria-describedby={ariaDescribedBy}
        onClick={onTriggerClick}
        onKeyDown={onKeyDown}
        onFocus={onFocus}
        onBlur={onBlur}
      >
        {multiple && selectedOptions.length > 0 ? (
          <div className="cyber-select-tags">
            {selectedOptions.map(option => (
              <span key={option.value} className="cyber-select-tag">
                {option.label}
                <button
                  type="button"
                  className="cyber-select-tag-remove"
                  onClick={(e) => onRemoveOption(e, option.value)}
                  aria-label={`Remove ${option.label}`}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        ) : (
          <span className="cyber-select-value" data-placeholder={placeholder}>
            {selectedOptions.length > 0 ? selectedOptions[0].label : placeholder}
          </span>
        )}
        <span className="cyber-select-arrow" aria-hidden="true">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path
              d="M2 4L6 8L10 4"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
      </div>
    </>
  );
});

SelectInput.displayName = 'SelectInput';