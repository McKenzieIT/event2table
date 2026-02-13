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
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import './Select.css';

const Select = React.forwardRef(({
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
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef(null);
  const inputRef = useRef(ref);

  const inputId = React.useId();
  const isInvalid = Boolean(error);

  // Filter options based on search term
  const filteredOptions = React.useMemo(() => {
    if (!searchable || !searchTerm) return options;
    return options.filter(option =>
      option.label?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [options, searchTerm, searchable]);

  // Get selected option label
  const selectedOption = React.useMemo(() => {
    return options.find(opt => opt.value === value);
  }, [options, value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
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
  const handleSelectOption = useCallback((optionValue) => {
    onChange?.(optionValue);
    setIsOpen(false);
    setSearchTerm('');
  }, [onChange]);

  // Handle search term change
  const handleSearchChange = useCallback((e) => {
    setSearchTerm(e.target.value);
  }, []);

  // Handle search input click
  const handleSearchClick = useCallback((e) => {
    e.stopPropagation();
  }, []);

  // Handle trigger click
  const handleTriggerClick = useCallback(() => {
    if (!disabled) {
      setIsOpen(prev => !prev);
    }
  }, [disabled]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event) => {
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
    isOpen && 'cyber-select-dropdown--open'
  ].filter(Boolean).join(' ');

  return (
    <div className={['cyber-select', className].filter(Boolean).join(' ')}>
      {label && (
        <label htmlFor={inputId} className="cyber-select__label">
          {label}
          {required && <span className="cyber-select__required" aria-hidden="true"> *</span>}
        </label>
      )}

      <div className={wrapperClass} ref={dropdownRef}>
        <div
          ref={inputRef}
          id={inputId}
          className="cyber-select-trigger"
          tabIndex={disabled ? -1 : 0}
          role="combobox"
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-disabled={disabled}
          aria-invalid={isInvalid}
          aria-labelledby={label ? inputId : undefined}
          onClick={handleTriggerClick}
          onKeyDown={handleKeyDown}
        >
          <span className="cyber-select-value">
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
        <p className="cyber-select__error" role="alert">
          {error}
        </p>
      )}

      {helperText && !isInvalid && (
        <p className="cyber-select__helper">
          {helperText}
        </p>
      )}
    </div>
  );
});

Select.displayName = 'Select';

const MemoizedSelect = React.memo(Select, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.error === nextProps.error &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.onChange === nextProps.onChange &&
    prevProps.options === nextProps.options
  );
});

MemoizedSelect.displayName = 'MemoizedSelect';

export default MemoizedSelect;
