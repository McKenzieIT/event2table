import React, {
  forwardRef,
  useState,
  useRef,
  useEffect,
  useCallback,
  useMemo,
  KeyboardEvent,
  MouseEvent,
  ChangeEvent,
  FocusEvent
} from 'react';
import { Controller } from 'react-hook-form';
import type { SelectProps, SelectOption } from './Select.types';
import './Select.css';

/**
 * Dropdown position type
 */
type DropdownPosition = 'down' | 'up';

/**
 * Select Component
 *
 * A cyberpunk-themed dropdown select with support for:
 * - Single/multiple selection
 * - Search/filter functionality
 * - Keyboard navigation (Enter, Space, Escape, Arrow keys)
 * - Intelligent dropdown positioning (up/down based on viewport)
 * - Click outside to close
 * - Accessibility attributes (ARIA)
 * - React Hook Form integration
 */
const Select = forwardRef<HTMLDivElement, SelectProps>(({
  name,
  label,
  options = [],
  value,
  onChange,
  placeholder = 'Select...',
  disabled = false,
  required = false,
  searchable = false,
  multiple = false,
  error,
  helperText,
  className = '',
  size = 'medium',
  control,
  rules,
  ...props
}, ref) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [dropdownPosition, setDropdownPosition] = useState<DropdownPosition>('down');
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const [selectedValues, setSelectedValues] = useState<(string | number)[]>(
    multiple ? (Array.isArray(value) ? value : []) : (value !== undefined ? [value] : [])
  );

  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const optionsRef = useRef<HTMLDivElement[]>([]);

  const labelId = React.useId();
  const triggerId = React.useId();
  const isInvalid = Boolean(error);

  // Update selected values when value prop changes
  useEffect(() => {
    if (multiple) {
      setSelectedValues(Array.isArray(value) ? value : []);
    } else if (value !== undefined) {
      setSelectedValues([value]);
    }
  }, [value, multiple]);

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

  // Get selected option(s) label(s)
  const selectedOptions = useMemo(() => {
    return options.filter(opt => selectedValues.includes(opt.value));
  }, [options, selectedValues]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: Event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
        setFocusedIndex(-1);
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
    let newValues: (string | number)[];

    if (multiple) {
      if (selectedValues.includes(optionValue)) {
        newValues = selectedValues.filter(v => v !== optionValue);
      } else {
        newValues = [...selectedValues, optionValue];
      }
      setSelectedValues(newValues);
      onChange?.(newValues as any);
    } else {
      newValues = [optionValue];
      setSelectedValues(newValues);
      onChange?.(optionValue);
      setIsOpen(false);
    }
    setSearchTerm('');
    setFocusedIndex(-1);
  }, [selectedValues, multiple, onChange]);

  // Handle removing selected option (for multiple select)
  const handleRemoveOption = useCallback((event: MouseEvent, optionValue: string | number) => {
    event.stopPropagation();
    const newValues = selectedValues.filter(v => v !== optionValue);
    setSelectedValues(newValues);
    onChange?.(newValues as any);
  }, [selectedValues, onChange]);

  // Handle search term change
  const handleSearchChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setFocusedIndex(-1);
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

    const visibleOptions = filteredOptions.filter(opt => !opt.disabled);

    switch (event.key) {
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (isOpen && focusedIndex >= 0 && focusedIndex < visibleOptions.length) {
          handleSelectOption(visibleOptions[focusedIndex].value);
        } else {
          setIsOpen(prev => !prev);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSearchTerm('');
        setFocusedIndex(-1);
        break;
      case 'ArrowDown':
        event.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setFocusedIndex(prev => {
            if (visibleOptions.length === 0) return -1;
            return prev < visibleOptions.length - 1 ? prev + 1 : 0;
          });
        }
        break;
      case 'ArrowUp':
        event.preventDefault();
        if (isOpen) {
          setFocusedIndex(prev => {
            if (visibleOptions.length === 0) return -1;
            return prev > 0 ? prev - 1 : visibleOptions.length - 1;
          });
        }
        break;
      case 'Tab':
        setIsOpen(false);
        break;
    }
  }, [disabled, isOpen, focusedIndex, filteredOptions, handleSelectOption]);

  // Handle focus
  const handleFocus = useCallback((e: FocusEvent<HTMLDivElement>) => {
    if (searchable && isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [searchable, isOpen]);

  // Scroll focused option into view
  useEffect(() => {
    if (focusedIndex >= 0 && optionsRef.current[focusedIndex]) {
      optionsRef.current[focusedIndex]?.scrollIntoView({
        block: 'nearest',
        behavior: 'smooth'
      });
    }
  }, [focusedIndex]);

  const wrapperClass = [
    'cyber-select-wrapper',
    `cyber-select-wrapper--${size}`,
    isInvalid && 'cyber-select-wrapper--invalid',
    disabled && 'cyber-select-wrapper--disabled',
    isOpen && 'cyber-select-wrapper--open'
  ].filter(Boolean).join(' ');

  const dropdownClass = [
    'cyber-select-dropdown',
    isOpen && 'cyber-select-dropdown--open',
    dropdownPosition === 'up' && 'cyber-select-dropdown--up'
  ].filter(Boolean).join(' ');

  const containerClass = [
    'cyber-select',
    className
  ].filter(Boolean).join(' ');

  // Render with React Hook Form Controller if control is provided
  if (control) {
    return (
      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field: { onChange: controllerOnChange, value: controllerValue } }) => (
          <div className={containerClass} ref={ref} {...props}>
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
                aria-multiselectable={multiple}
                onClick={handleTriggerClick}
                onKeyDown={handleKeyDown}
                onFocus={handleFocus}
              >
                {multiple && selectedOptions.length > 0 ? (
                  <div className="cyber-select-tags">
                    {selectedOptions.map(option => (
                      <span key={option.value} className="cyber-select-tag">
                        {option.label}
                        <button
                          type="button"
                          className="cyber-select-tag-remove"
                          onClick={(e) => handleRemoveOption(e, option.value)}
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
                      filteredOptions.map((option, index) => {
                        const isSelected = selectedValues.includes(option.value);
                        const isFocused = index === focusedIndex;
                        const optionClass = [
                          'cyber-select-option',
                          isSelected && 'cyber-select-option--selected',
                          isFocused && 'cyber-select-option--focused',
                          option.disabled && 'cyber-select-option--disabled'
                        ].filter(Boolean).join(' ');

                        return (
                          <div
                            key={option.value}
                            ref={el => { if (el) optionsRef.current[index] = el; }}
                            className={optionClass}
                            role="option"
                            aria-selected={isSelected}
                            aria-disabled={option.disabled}
                            onClick={() => !option.disabled && handleSelectOption(option.value)}
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
        )}
      />
    );
  }

  // Render without React Hook Form Controller
  return (
    <div className={containerClass} ref={ref} {...props}>
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
          aria-multiselectable={multiple}
          onClick={handleTriggerClick}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
        >
          {multiple && selectedOptions.length > 0 ? (
            <div className="cyber-select-tags">
              {selectedOptions.map(option => (
                <span key={option.value} className="cyber-select-tag">
                  {option.label}
                  <button
                    type="button"
                    className="cyber-select-tag-remove"
                    onClick={(e) => handleRemoveOption(e, option.value)}
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
                filteredOptions.map((option, index) => {
                  const isSelected = selectedValues.includes(option.value);
                  const isFocused = index === focusedIndex;
                  const optionClass = [
                    'cyber-select-option',
                    isSelected && 'cyber-select-option--selected',
                    isFocused && 'cyber-select-option--focused',
                    option.disabled && 'cyber-select-option--disabled'
                  ].filter(Boolean).join(' ');

                  return (
                    <div
                      key={option.value}
                      ref={el => { if (el) optionsRef.current[index] = el; }}
                      className={optionClass}
                      role="option"
                      aria-selected={isSelected}
                      aria-disabled={option.disabled}
                      onClick={() => !option.disabled && handleSelectOption(option.value)}
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

export default Select;
