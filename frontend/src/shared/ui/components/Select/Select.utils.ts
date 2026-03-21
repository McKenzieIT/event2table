/**
 * Select Component Utility Functions
 */

import { SelectOption } from './Select.types';

/**
 * Filter options based on search term
 */
export const filterOptions = (
  options: SelectOption[],
  searchTerm: string,
  searchable: boolean
): SelectOption[] => {
  if (!searchable || !searchTerm) return options;
  return options.filter(option =>
    option.label?.toLowerCase().includes(searchTerm.toLowerCase())
  );
};

/**
 * Get selected options from all options
 */
export const getSelectedOptions = (
  options: SelectOption[],
  selectedValues: (string | number)[]
): SelectOption[] => {
  return options.filter(opt => selectedValues.includes(opt.value));
};

/**
 * Calculate dropdown position based on viewport
 */
export const calculateDropdownPosition = (
  triggerRect: DOMRect,
  dropdownHeight: number,
  viewportHeight: number
): 'up' | 'down' => {
  const spaceBelow = viewportHeight - triggerRect.bottom;
  const spaceAbove = triggerRect.top;

  if (spaceBelow < dropdownHeight && spaceAbove > spaceBelow) {
    return 'up';
  }
  return 'down';
};

/**
 * Generate CSS class names for select components
 */
export const generateSelectClasses = (
  baseClass: string,
  modifiers: Record<string, boolean | undefined> = {}
): string => {
  return Object.entries(modifiers)
    .filter(([_, value]) => Boolean(value))
    .map(([key]) => `${baseClass}--${key}`)
    .join(' ');
};

/**
 * Check if option is selected
 */
export const isOptionSelected = (
  optionValue: string | number,
  selectedValues: (string | number)[]
): boolean => {
  return selectedValues.includes(optionValue);
};

/**
 * Handle keyboard navigation
 */
export const handleKeyboardNavigation = (
  event: KeyboardEvent,
  isOpen: boolean,
  focusedIndex: number,
  visibleOptions: SelectOption[],
  onToggleDropdown: () => void,
  onSelectOption: (option: SelectOption) => void,
  onCloseDropdown: () => void,
  onSetFocusedIndex: (index: number) => void
): void => {
  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault();
      if (isOpen && focusedIndex >= 0 && focusedIndex < visibleOptions.length) {
        onSelectOption(visibleOptions[focusedIndex]);
      } else {
        onToggleDropdown();
      }
      break;
    case 'Escape':
      onCloseDropdown();
      onSetFocusedIndex(-1);
      break;
    case 'ArrowDown':
      event.preventDefault();
      if (!isOpen) {
        onToggleDropdown();
      } else {
        onSetFocusedIndex(
          visibleOptions.length === 0
            ? -1
            : focusedIndex < visibleOptions.length - 1
            ? focusedIndex + 1
            : 0
        );
      }
      break;
    case 'ArrowUp':
      event.preventDefault();
      if (isOpen) {
        onSetFocusedIndex(
          visibleOptions.length === 0
            ? -1
            : focusedIndex > 0
            ? focusedIndex - 1
            : visibleOptions.length - 1
        );
      }
      break;
    case 'Tab':
      onCloseDropdown();
      break;
  }
};
