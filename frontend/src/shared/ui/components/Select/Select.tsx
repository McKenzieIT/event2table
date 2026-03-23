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
import { filterOptions, getSelectedOptions, calculateDropdownPosition } from './Select.utils';
import { SelectDropdown } from './SelectDropdown';
import { SelectInput } from './SelectInput';

import { useDebounce } from '@/shared/ui/hooks/useDebounce';
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
 * - Autocomplete mode with remote search
 * - Create new options
 * - Loading state
 * - Debounced search
 */
const Select = React.memo(forwardRef<HTMLDivElement, SelectProps>(({
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
  mode = 'default',
  allowCreate = false,
  onSearch,
  onCreate,
  loading = false,
  searchDebounce = 300,
  noOptionsMessage = 'No options found',
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

    setDropdownPosition(calculateDropdownPosition(triggerRect, dropdownHeight, viewportHeight));
  }, [isOpen]);

  // Debounce search term for autocomplete mode
  const debouncedSearchTerm = useDebounce(searchTerm, searchDebounce);

  // Call onSearch when debounced search term changes (autocomplete mode)
  useEffect(() => {
    if (mode === 'autocomplete' && onSearch && debouncedSearchTerm !== undefined) {
      onSearch(debouncedSearchTerm);
    }
  }, [mode, onSearch, debouncedSearchTerm]);

  // Filter options based on search term
  // In autocomplete mode, we don't filter locally - the parent controls options
  const filteredOptions = useMemo(() => {
    if (mode === 'autocomplete') {
      return options;
    }
    return filterOptions(options, searchTerm, searchable);
  }, [mode, options, searchTerm, searchable]);

  // Handle creating a new option
  const handleCreateOption = useCallback((label: string) => {
    if (onCreate && label.trim()) {
      onCreate(label.trim());
    }
    setSearchTerm('');
    setFocusedIndex(-1);
  }, [onCreate]);

  // Get selected option(s) label(s)
  const selectedOptions = useMemo(() => {
    return getSelectedOptions(options, selectedValues);
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
      onChange?.(newValues);
      // Close dropdown after selection in multiple mode
      setIsOpen(false);
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
    onChange?.(newValues);
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
    if (focusedIndex >= 0) {
      // Scroll the focused visible option into view
      const visibleOptions = filteredOptions.filter(opt => !opt.disabled);
      if (focusedIndex < visibleOptions.length) {
        const focusedOption = visibleOptions[focusedIndex];
        const optionIndex = filteredOptions.findIndex(opt => opt.value === focusedOption.value);
        const optionElement = optionsRef.current[optionIndex];
        if (optionElement && typeof optionElement.scrollIntoView === 'function') {
          optionElement.scrollIntoView({ block: 'nearest' });
        }
      }
    }
  }, [focusedIndex, filteredOptions]);

  const wrapperClass = [
    'cyber-select-wrapper',
    `cyber-select-wrapper--${size}`,
    isInvalid && 'cyber-select-wrapper--invalid',
    disabled && 'cyber-select-wrapper--disabled',
    isOpen && 'cyber-select-wrapper--open'
  ].filter(Boolean).join(' ');

  const containerClass = [
    'cyber-select',
    className
  ].filter(Boolean).join(' ');

  // Determine aria-describedby value
  const ariaDescribedBy = [
    isInvalid ? `${triggerId}-error` : null,
    helperText && !isInvalid ? `${triggerId}-helper` : null
  ].filter(Boolean).join(' ') || undefined;

  // Render with React Hook Form Controller if control is provided
  if (control) {
    return (
      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field: { onChange: controllerOnChange, value: controllerValue, onBlur }, fieldState: { error: fieldError } }) => (
          <div className={containerClass} ref={ref} {...props}>
            <div className={wrapperClass} ref={dropdownRef}>
              <SelectInput
                id={triggerId}
                label={label}
                labelId={labelId}
                placeholder={placeholder}
                disabled={disabled}
                multiple={multiple}
                isOpen={isOpen}
                isInvalid={isInvalid}
                selectedOptions={selectedOptions}
                searchable={searchable}
                onTriggerClick={handleTriggerClick}
                onRemoveOption={handleRemoveOption}
                onKeyDown={handleKeyDown}
                onFocus={handleFocus}
                onBlur={onBlur}
                triggerRef={triggerRef}
                ariaDescribedBy={ariaDescribedBy}
                required={required}
              />

              <SelectDropdown
                isOpen={isOpen}
                position={dropdownPosition}
                searchable={searchable}
                searchTerm={searchTerm}
                filteredOptions={filteredOptions}
                selectedValues={selectedValues}
                focusedIndex={focusedIndex}
                multiple={multiple}
                onSearchChange={handleSearchChange}
                onSearchClick={handleSearchClick}
                onSelectOption={handleSelectOption}
                searchInputRef={searchInputRef}
                optionsRef={optionsRef}
                allowCreate={allowCreate && !multiple}
                onCreate={handleCreateOption}
                noOptionsMessage={noOptionsMessage}
                loading={loading}
              />
            </div>

            {fieldError && (
              <p id={`${triggerId}-error`} className="cyber-select__error" role="alert">
                {fieldError.message}
              </p>
            )}

            {helperText && !fieldError && (
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
      <div className={wrapperClass} ref={dropdownRef}>
        <SelectInput
          id={triggerId}
          label={label}
          labelId={labelId}
          placeholder={placeholder}
          disabled={disabled}
          multiple={multiple}
          isOpen={isOpen}
          isInvalid={isInvalid}
          selectedOptions={selectedOptions}
          searchable={searchable}
          onTriggerClick={handleTriggerClick}
          onRemoveOption={handleRemoveOption}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          triggerRef={triggerRef}
          ariaDescribedBy={ariaDescribedBy}
          required={required}
        />

        <SelectDropdown
          isOpen={isOpen}
          position={dropdownPosition}
          searchable={searchable}
          searchTerm={searchTerm}
          filteredOptions={filteredOptions}
          selectedValues={selectedValues}
          focusedIndex={focusedIndex}
          multiple={multiple}
          onSearchChange={handleSearchChange}
          onSearchClick={handleSearchClick}
          onSelectOption={handleSelectOption}
          searchInputRef={searchInputRef}
          optionsRef={optionsRef}
          allowCreate={allowCreate && !multiple}
          onCreate={handleCreateOption}
          noOptionsMessage={noOptionsMessage}
          loading={loading}
        />
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
}));

// Set display name for debugging
Select.displayName = 'Select';

export default Select;