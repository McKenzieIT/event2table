/**
 * Select Component - Cyberpunk Lab Theme
 *
 * A modern, tech-inspired dropdown selector with search functionality.
 * Features glassmorphism styling, focus glow effects, and smooth animations.
 *
 * @example
 * // Basic select
 * <Select
 *   label="Game Type"
 *   options={[
 *     { value: 'football', label: 'Football' },
 *     { value: 'basketball', label: 'Basketball' }
 *   ]}
 *   onChange={(value) => console.log(value)}
 * />
 *
 * @example
 * // With search
 * <Select
 *   label="Player"
 *   options={players}
 *   searchable
 *   placeholder="Search player..."
 * />
 *
 * @example
 * // Disabled
 * <Select
 *   label="Status"
 *   options={options}
 *   disabled
 * />
 *
 * Migration Notes from PropTypes:
 * - label: PropTypes.string → label?: string (from LabeledComponentProps)
 * - options: PropTypes.arrayOf(PropTypes.shape({ value, label, disabled })) → options?: SelectOption[]
 * - value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]) → value?: string | number
 * - onChange: PropTypes.func → onChange?: ValueChangeCallback<string | number>
 * - placeholder: PropTypes.string (default: 'Select...') → placeholder?: string
 * - searchable: PropTypes.bool (default: false) → searchable?: boolean
 * - disabled: PropTypes.bool (default: false) → disabled?: boolean (from BaseComponentProps)
 * - required: PropTypes.bool (default: false) → required?: boolean (from LabeledComponentProps)
 * - error: PropTypes.string → error?: string (from LabeledComponentProps)
 * - helperText: PropTypes.string → helperText?: string (from LabeledComponentProps)
 * - className: PropTypes.string (default: '') → className?: string (from BaseComponentProps)
 */

import React, {
  forwardRef,
  useState,
  useRef,
  useEffect,
  useCallback,
  useMemo,
  KeyboardEvent,
  MouseEvent,
  ChangeEvent
} from 'react';
import type {
  SelectOption,
  LabeledComponentProps,
  ValueChangeCallback,
} from '@/types/common';
import './Select.css';

/**
 * Dropdown position type
 */
type DropdownPosition = 'down' | 'up';

/**
 * Props for the Select component - extends common labeled component props
 */
export interface SelectProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange' | 'value'>, LabeledComponentProps {
  /**
   * Array of options to display
   */
  options?: SelectOption[];

  /**
   * Current selected value
   */
  value?: string | number;

  /**
   * Change handler called when an option is selected
   */
  onChange?: ValueChangeCallback<string | number>;

  /**
   * Placeholder text shown when no option is selected
   * @default 'Select...'
   */
  placeholder?: string;

  /**
   * Enable search functionality for filtering options
   * @default false
   */
  searchable?: boolean;
}

/**
 * Select Component
 *
 * A cyberpunk-themed dropdown select with support for labels, search,
 * error states, helper text, and accessibility features.
 *
 * Features:
 * - Search/filter functionality
 * - Keyboard navigation (Enter, Space, Escape, Arrow keys)
 * - Intelligent dropdown positioning (up/down based on viewport)
 * - Click outside to close
 * - Accessibility attributes (ARIA)
 */
const Select = forwardRef<HTMLDivElement, SelectProps>(({
  label,
  options = [],
  value,
  onChange,
  placeholder = 'Select...',
  searchable = false,
  disabled = false,
  required = false,
  error,
  helperText,
  className = '',
  ...props
}, ref) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [dropdownPosition, setDropdownPosition] = useState<DropdownPosition>('down');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const labelId = React.useId();
  const triggerId = React.useId();
  const isInvalid = Boolean(error);

  // Calculate dropdown position based on viewport
  useEffect(() => {
    if (!isOpen || !dropdownRef.current || !triggerRef.current) return;

    const dropdown = dropdownRef.current;
    const trigger = triggerRef.current;

    const triggerRect = trigger.getBoundingClientRect();
    const dropdownHeight = dropdown.offsetHeight || 240;
    const viewportHeight = window.innerHeight;
    const spaceBelow = viewportHeight - triggerRect.bottom;
    const spaceAbove = triggerRect.top;

    // If not enough space below and more space above, flip up
    if (spaceBelow < dropdownHeight && spaceAbove > spaceBelow) {
      setDropdownPosition('up');
    } else {
      setDropdownPosition('down');
    }
  }, [isOpen]);

  // Filter options based on search term
  const filteredOptions = useMemo(() => {
    if (!searchable || !searchTerm) return options;
    return options.filter(option =>
      option.label?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [options, searchTerm, searchable]);

  // Get selected option label
  const selectedOption = useMemo(() => {
    return options.find(opt => opt.value === value);
  }, [options, value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: Event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Handle option selection
  const handleSelectOption = useCallback((optionValue: string | number) => {
    onChange?.(optionValue);
    setIsOpen(false);
    setSearchTerm('');
  }, [onChange]);

  // Handle search term change
  const handleSearchChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  }, []);

  // Handle search input click
  const handleSearchClick = useCallback((e: MouseEvent<HTMLInputElement>) => {
    e.stopPropagation();
  }, []);

  // Handle trigger click
  const handleTriggerClick = useCallback(() => {
    if (!disabled) {
      setIsOpen(prev => !prev);
    }
  }, [disabled]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: KeyboardEvent<HTMLDivElement>) => {
    if (disabled) return;

    switch (event.key) {
      case 'Enter':
      case ' ':
        event.preventDefault();
        setIsOpen(prev => !prev);
        break;
      case 'Escape':
        setIsOpen(false);
        setSearchTerm('');
        break;
      case 'ArrowDown':
      case 'ArrowUp':
        if (!isOpen) {
          event.preventDefault();
          setIsOpen(true);
        }
        break;
    }
  }, [disabled, isOpen]);

  const wrapperClass = [
    'cyber-select-wrapper',
    isInvalid && 'cyber-select-wrapper--invalid',
    disabled && 'cyber-select-wrapper--disabled',
    isOpen && 'cyber-select-wrapper--open'
  ].filter(Boolean).join(' ');

  const dropdownClass = [
    'cyber-select-dropdown',
    isOpen && 'cyber-select-dropdown--open',
    dropdownPosition === 'up' && 'cyber-select-dropdown--up'
  ].filter(Boolean).join(' ');

  return (
    <div className={['cyber-select', className].filter(Boolean).join(' ')} ref={ref} {...props}>
      {label && (
        <label id={labelId} className="cyber-select__label">
          {label}
          {required && <span className="cyber-select__required" aria-hidden="true"> *</span>}
        </label>
      )}

      <div className={wrapperClass} ref={dropdownRef}>
        <div
          ref={triggerRef}
          id={triggerId}
          className="cyber-select-trigger"
          tabIndex={disabled ? -1 : 0}
          role="combobox"
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-disabled={disabled}
          aria-invalid={isInvalid}
          aria-labelledby={label ? labelId : undefined}
          aria-describedby={
            isInvalid ? `${triggerId}-error` : helperText ? `${triggerId}-helper` : undefined
          }
          onClick={handleTriggerClick}
          onKeyDown={handleKeyDown}
        >
          <span className="cyber-select-value" data-placeholder={placeholder}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
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

        {isOpen && (
          <div className={dropdownClass} role="listbox">
            {searchable && (
              <div className="cyber-select-search">
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="cyber-select-search-input"
                  autoFocus
                  onClick={handleSearchClick}
                />
              </div>
            )}

            <div className="cyber-select-options">
              {filteredOptions.length === 0 ? (
                <div className="cyber-select-option cyber-select-option--empty">
                  No options found
                </div>
              ) : (
                filteredOptions.map((option) => {
                  const isSelected = option.value === value;
                  const optionClass = [
                    'cyber-select-option',
                    isSelected && 'cyber-select-option--selected',
                    option.disabled && 'cyber-select-option--disabled'
                  ].filter(Boolean).join(' ');

                  return (
                    <div
                      key={option.value}
                      className={optionClass}
                      role="option"
                      aria-selected={isSelected}
                      onClick={() => !option.disabled && handleSelectOption(option.value)}
                    >
                      {option.label}
                      {isSelected && (
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
                })
              )}
            </div>
          </div>
        )}
      </div>

      {isInvalid && (
        <p id={`${triggerId}-error`} className="cyber-select__error" role="alert">
          {error}
        </p>
      )}

      {helperText && !isInvalid && (
        <p id={`${triggerId}-helper`} className="cyber-select__helper">
          {helperText}
        </p>
      )}
    </div>
  );
});

// Set display name for debugging
Select.displayName = 'Select';

// Memoize Select component to prevent unnecessary re-renders
// Custom comparison since value and onChange change frequently
const MemoizedSelect = React.memo(Select, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.error === nextProps.error &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.onChange === nextProps.onChange &&
    prevProps.options === nextProps.options
  );
});

// Set display name for memoized component
MemoizedSelect.displayName = 'MemoizedSelect';

export default MemoizedSelect;
