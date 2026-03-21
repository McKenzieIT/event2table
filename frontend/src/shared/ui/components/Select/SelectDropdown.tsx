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
}

/**
 * SelectDropdown Component
 *
 * Renders the dropdown with search and options
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
  optionsRef
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

  return (
    <div className={dropdownClass} role="listbox">
      {searchable && (
        <SelectSearch
          searchTerm={searchTerm}
          onSearchChange={onSearchChange}
          onSearchClick={onSearchClick}
          searchInputRef={searchInputRef}
        />
      )}

      <div className="cyber-select-options">
        {filteredOptions.length === 0 ? (
          <div className="cyber-select-option cyber-select-option--empty">
            No options found
          </div>
        ) : (
          filteredOptions.map((option, index) => (
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
          ))
        )}
      </div>
    </div>
  );
});

SelectDropdown.displayName = 'SelectDropdown';