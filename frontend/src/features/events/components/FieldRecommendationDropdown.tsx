/**
 * FieldRecommendationDropdown Component
 *
 * Dropdown selector for field recommendations with search and filtering
 *
 * @module FieldRecommendationDropdown
 */

import React, { useState, useCallback, useMemo } from 'react';

import type { FieldPattern } from '../api/fieldRecommendationApi';
import { useCommonPatterns } from '../hooks/useCommonPatterns';

interface FieldRecommendationDropdownProps {
  /** Currently selected pattern */
  selectedPattern?: FieldPattern;
  /** Callback when pattern is selected */
  onSelectPattern: (pattern: FieldPattern) => void;
  /** Optional: filter patterns by type */
  filterByType?: string;
  /** Optional: placeholder text */
  placeholder?: string;
}

/**
 * Dropdown component for selecting from common field patterns
 */
export const FieldRecommendationDropdown: React.FC<FieldRecommendationDropdownProps> = React.memo(function FieldRecommendationDropdown({
  selectedPattern,
  onSelectPattern,
  filterByType,
  placeholder = '选择字段模式...',
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch common patterns
  const { data: patterns, isLoading, error } = useCommonPatterns();

  // Filter patterns based on search term and type filter
  const filteredPatterns = useMemo(() => {
    if (!patterns) return [];

    return patterns.filter((pattern) => {
      // Type filter
      if (filterByType && pattern.fieldType !== filterByType) {
        return false;
      }

      // Search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          pattern.name.toLowerCase().includes(searchLower) ||
          pattern.description.toLowerCase().includes(searchLower)
        );
      }

      return true;
    });
  }, [patterns, searchTerm, filterByType]);

  // Handle pattern selection
  const handleSelectPattern = useCallback(
    (pattern: FieldPattern) => {
      onSelectPattern(pattern);
      setIsOpen(false);
      setSearchTerm('');
    },
    [onSelectPattern]
  );

  // Toggle dropdown
  const toggleDropdown = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  // Handle click outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.field-recommendation-dropdown')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="field-recommendation-dropdown relative">
      {/* Dropdown Trigger */}
      <button
        onClick={toggleDropdown}
        className="w-full px-3 py-2 text-left bg-slate-800 border border-slate-700 rounded-lg hover:border-slate-600 transition-colors flex items-center justify-between"
        disabled={isLoading}
      >
        <div className="flex items-center gap-2">
          {selectedPattern ? (
            <>
              <div className="text-sm text-slate-300">{selectedPattern.name}</div>
              <div className="text-xs text-purple-400">({selectedPattern.fieldType})</div>
            </>
          ) : (
            <div className="text-sm text-slate-400">{placeholder}</div>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-slate-800 border border-slate-700 rounded-lg shadow-xl max-h-80 overflow-hidden">
          {/* Search Input */}
          <div className="p-2 border-b border-slate-700">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="搜索字段模式..."
              className="w-full px-3 py-2 text-sm bg-slate-700 border border-slate-600 rounded-lg text-slate-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Pattern List */}
          <div className="overflow-y-auto max-h-64">
            {isLoading ? (
              <div className="p-4 text-center text-sm text-slate-400">加载中...</div>
            ) : error ? (
              <div className="p-4 text-center text-sm text-red-400">
                加载失败: {error.message}
              </div>
            ) : filteredPatterns.length === 0 ? (
              <div className="p-4 text-center text-sm text-slate-400">未找到匹配的模式</div>
            ) : (
              <div className="divide-y divide-slate-700">
                {filteredPatterns.map((pattern) => (
                  <button
                    key={pattern.name}
                    onClick={() => handleSelectPattern(pattern)}
                    className={`w-full px-3 py-3 text-left hover:bg-slate-700 transition-colors ${
                      selectedPattern?.name === pattern.name ? 'bg-cyan-500/10' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="text-sm font-medium text-slate-300">
                            {pattern.name}
                          </div>
                          <div className="text-xs px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded">
                            {pattern.fieldType}
                          </div>
                        </div>
                        <div className="text-xs text-slate-400 mb-2">
                          {pattern.description}
                        </div>
                        {pattern.examples.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {pattern.examples.slice(0, 3).map((example, index) => (
                              <span
                                key={index}
                                className="text-xs px-2 py-0.5 bg-slate-700 text-slate-400 rounded"
                              >
                                {example}
                              </span>
                            ))}
                            {pattern.examples.length > 3 && (
                              <span className="text-xs text-slate-500">
                                +{pattern.examples.length - 3} 更多
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                      {selectedPattern?.name === pattern.name && (
                        <svg className="w-5 h-5 text-cyan-400 ml-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
});

export default FieldRecommendationDropdown;
