import React from 'react';
import { SelectOption as SelectOptionType } from './Select.types';
import { SelectOption } from './SelectOption';
import { SelectSearch } from './SelectSearch';
import './Select.css';

export interface SelectDropdownProps {
  isOpen: boolean;
  position: 'up' | 'down';
  searchable: boolean;
  searchTerm: string;
  filteredOptions: SelectOptionType[];
  selectedValues: (string | number)[];
  focusedIndex: number;
  multiple: boolean;
  onSearchChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSearchClick: (event: React.MouseEvent<HTMLInputElement>) => void;
  onSelectOption: (value: string | number) => void;
  searchInputRef: React.RefObject<HTMLInputElement>;
  optionsRef: React.MutableRefObject<(HTMLDivElement | null)[]>;
  /** Allow creating new options */
  allowCreate?: boolean;
  /** Callback when creating a new option */
  onCreate?: (label: string) => void;
  /** Custom message when no options match */
  noOptionsMessage?: string;
  /** Loading state for autocomplete mode */
  loading?: boolean;
}

/**
 * SelectDropdown Component
 *
 * Renders the dropdown with search and options.
 * Supports allowCreate for creating new options and loading state.
 */
export const SelectDropdown = React.memo<SelectDropdownProps>(({
  isOpen,
  position,
  searchable,
  searchTerm,
  filteredOptions,
  selectedValues,
  focusedIndex,
  multiple,
  onSearchChange,
  onSearchClick,
  onSelectOption,
  searchInputRef,
  optionsRef,
  allowCreate = false,
  onCreate,
  noOptionsMessage = 'No options found',
  loading = false
}) => {
  if (!isOpen) return null;

  const dropdownClass = [
    'cyber-select-dropdown',
    'cyber-select-dropdown--open',
    position === 'up' && 'cyber-select-dropdown--up'
  ].filter(Boolean).join(' ');

  // Calculate isFocused for each option based on visible (non-disabled) options
  const getIsFocused = (option: SelectOptionType, index: number) => {
    if (option.disabled) return false;
    const visibleOptions = filteredOptions.filter(opt => !opt.disabled);
    const visibleIndex = visibleOptions.findIndex(opt => opt.value === option.value);
    return visibleIndex === focusedIndex;
  };

  // Check if we should show "Create" option
  const showCreateOption = allowCreate && searchTerm.trim() && !loading;
  const exactMatch = filteredOptions.some(
    opt => opt.label.toLowerCase() === searchTerm.toLowerCase()
  );
  const shouldShowCreate = showCreateOption && !exactMatch;

  // Handle create option click
  const handleCreate = () => {
    if (onCreate && searchTerm.trim()) {
      onCreate(searchTerm.trim());
    }
  };

  // Calculate total options count for refs array
  const totalOptions = filteredOptions.length + (shouldShowCreate ? 1 : 0);

  return (
    <div className={dropdownClass} role="listbox">
      {searchable && (
        <SelectSearch
          searchTerm={searchTerm}
          onSearchChange={onSearchChange}
          onSearchClick={onSearchClick}
          searchInputRef={searchInputRef}
          loading={loading}
        />
      )}

      <div className="cyber-select-options">
        {loading ? (
          <div className="cyber-select-option cyber-select-option--loading">
            <span className="cyber-select-spinner-text">Loading...</span>
          </div>
        ) : filteredOptions.length === 0 && !shouldShowCreate ? (
          <div className="cyber-select-option cyber-select-option--empty">
            {noOptionsMessage}
          </div>
        ) : (
          <>
            {filteredOptions.map((option, index) => (
              <SelectOption
                key={option.value}
                option={option}
                isSelected={selectedValues.includes(option.value)}
                isFocused={getIsFocused(option, index)}
                multiple={multiple}
                onClick={onSelectOption}
                optionRef={(el) => {
                  if (el) optionsRef.current[index] = el;
                }}
              />
            ))}
            {shouldShowCreate && (
              <div
                className="cyber-select-option cyber-select-option--create"
                onClick={handleCreate}
                role="option"
                aria-selected={false}
                ref={(el) => {
                  if (el) optionsRef.current[totalOptions - 1] = el;
                }}
              >
                <span className="cyber-select-create-icon">+</span>
                Create &quot;{searchTerm}&quot;
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
});

SelectDropdown.displayName = 'SelectDropdown';