// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Button } from '@shared/ui';
import './SearchBar.css';
import type { SearchBarProps } from './types';

/**
 * 搜索栏组件
 * 可折叠的搜索输入框
 *
 * @param props - Component props
 *
 * @example
 * <SearchBar onSearch={(term) => console.log(term)} />
 */
export default function SearchBar({ onSearch }: SearchBarProps): React.JSX.Element {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  const handleToggle = (): void => {
    setIsExpanded(!isExpanded);
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const value = e.target.value;
    setSearchTerm(value);

    // Clear previous timeout
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Debounce search - 300ms delay
    debounceRef.current = setTimeout(() => {
      onSearch(value);
    }, 300);
  };

  const handleClear = (): void => {
    setSearchTerm('');
    onSearch('');
  };

  const searchIcon = (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"></circle>
      <path d="m21 21-4.35-4.35"></path>
    </svg>
  );

  const clearIcon = (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
  );

  return (
    <div className={`search-bar ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <Button
        variant="ghost"
        size="sm"
        className="search-toggle"
        onClick={handleToggle}
        title="搜索节点"
        type="button"
      >
        {searchIcon}
      </Button>
      {isExpanded && (
        <div className="search-input-container">
          <input
            type="text"
            className="search-input"
            placeholder="搜索中文名称或英文名称..."
            value={searchTerm}
            onChange={handleInputChange}
            autoFocus
          />
          {searchTerm && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={handleClear}
              aria-label="清除搜索"
            >
              {clearIcon}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
