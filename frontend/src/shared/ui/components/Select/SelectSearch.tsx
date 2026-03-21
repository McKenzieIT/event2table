import React, { ChangeEvent, MouseEvent, useRef } from 'react';
import './Select.css';

export interface SelectSearchProps {
  searchTerm: string;
  onSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onSearchClick: (event: MouseEvent<HTMLInputElement>) => void;
  searchInputRef: React.RefObject<HTMLInputElement>;
}

/**
 * SelectSearch Component
 *
 * Renders the search input for filtering options
 */
export const SelectSearch = React.memo<SelectSearchProps>(({
  searchTerm,
  onSearchChange,
  onSearchClick,
  searchInputRef
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
    </div>
  );
});

SelectSearch.displayName = 'SelectSearch';
