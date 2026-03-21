import React from 'react';
import { SelectOption as SelectOptionType } from './Select.types';
import { SelectOption } from './SelectOption';
import './Select.css';

export interface SelectOptionGroupProps {
  label: string;
  options: SelectOptionType[];
  selectedValues: (string | number)[];
  focusedIndex: number;
  multiple: boolean;
  onSelectOption: (value: string | number) => void;
  optionsRef: React.MutableRefObject<(HTMLDivElement | null)[]>;
  startIndex: number;
}

/**
 * SelectOptionGroup Component
 *
 * Renders a group of options with a label
 * (Optional component for future use)
 */
export const SelectOptionGroup: React.FC<SelectOptionGroupProps> = ({
  label,
  options,
  selectedValues,
  focusedIndex,
  multiple,
  onSelectOption,
  optionsRef,
  startIndex
}) => {
  return (
    <div className="cyber-select-option-group">
      <div className="cyber-select-option-group-label">{label}</div>
      {options.map((option, index) => (
        <SelectOption
          key={option.value}
          option={option}
          isSelected={selectedValues.includes(option.value)}
          isFocused={startIndex + index === focusedIndex}
          multiple={multiple}
          onClick={onSelectOption}
          optionRef={(el) => {
            if (el) optionsRef.current[startIndex + index] = el;
          }}
        />
      ))}
    </div>
  );
};
