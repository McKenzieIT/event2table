import React, { MouseEvent } from 'react';
import './Select.css';

export interface SelectClearButtonProps {
  onClear: (event: MouseEvent) => void;
  disabled?: boolean;
}

/**
 * SelectClearButton Component
 *
 * Renders a clear button for the Select component
 * (Optional component for future use)
 */
export const SelectClearButton = React.memo<SelectClearButtonProps>(({
  onClear,
  disabled = false
}) => {
  return (
    <button
      type="button"
      className="cyber-select-clear"
      onClick={onClear}
      disabled={disabled}
      aria-label="Clear selection"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path
          d="M12 4L4 12M4 4L12 12"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
});

SelectClearButton.displayName = 'SelectClearButton';