import React, { ChangeEvent, MouseEvent } from 'react';
import './Select.css';

export interface SelectSearchProps {
  searchTerm: string;
  onSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onSearchClick: (event: MouseEvent<HTMLInputElement>) => void;
  searchInputRef: React.RefObject<HTMLInputElement>;
  /** Loading state for autocomplete mode */
  loading?: boolean;
}

/**
 * SelectSearch Component
 *
 * Renders the search input for filtering options.
 * Supports loading indicator for autocomplete mode.
 */
export const SelectSearch = React.memo<SelectSearchProps>(({
  searchTerm,
  onSearchChange,
  onSearchClick,
  searchInputRef,
  loading = false
}) => {
  return (
    <div className="cyber-select-search">
      <input
        ref={searchInputRef}
        type="text"
        placeholder="Search..."
        value={searchTerm}
        onChange={onSearchChange}
        className="cyber-select-search-input"
        autoFocus
        onClick={onSearchClick}
      />
      {loading && (
        <div className="cyber-select-search-loading" aria-label="Loading">
          <svg
            className="cyber-select-spinner"
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
          >
            <circle
              cx="8"
              cy="8"
              r="6"
              stroke="currentColor"
              strokeWidth="2"
              strokeOpacity="0.3"
            />
            <path
              d="M8 2a6 6 0 0 1 6 6"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>
      )}
    </div>
  );
});

SelectSearch.displayName = 'SelectSearch';
