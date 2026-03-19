// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * FieldAutocomplete - 智能字段推荐组件
 *
 * 功能：
 * - 基于事件类型推荐常用字段
 * - 支持搜索过滤
 * - 显示字段类型标签
 */

import React, { useState, useEffect } from 'react';
import { Input } from '@shared/ui';
import './FieldAutocomplete.css';

// ========== 类型定义 ==========

/** 字段建议 */
export interface FieldSuggestion {
  name: string;
  type: string;
  description?: string;
  frequency?: number;
  [key: string]: any;
}

/** API响应 */
interface FieldSuggestionsResponse {
  success: boolean;
  data?: {
    suggestions?: FieldSuggestion[];
  };
  [key: string]: any;
}

/** 组件Props */
export interface FieldAutocompleteProps {
  /** 事件名称 */
  eventName?: string;
  /** 字段选择回调 */
  onFieldSelect?: (field: FieldSuggestion) => void;
  /** API基础URL */
  apiBaseUrl?: string;
}

// ========== 组件 ==========

export default function FieldAutocomplete({
  eventName,
  onFieldSelect,
  apiBaseUrl = '/hql-preview-v2'
}: FieldAutocompleteProps) {
  const [suggestions, setSuggestions] = useState<FieldSuggestion[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [showDropdown, setShowDropdown] = useState<boolean>(false);

  useEffect(() => {
    if (eventName) {
      fetchFieldSuggestions();
    }
  }, [eventName]);

  const fetchFieldSuggestions = async (search = '') => {
    setLoading(true);
    try {
      const url = search
        ? `${apiBaseUrl}/api/recommend-fields?partial=${search}`
        : `${apiBaseUrl}/api/recommend-fields`;

      const response = await fetch(url);
      const result: FieldSuggestionsResponse = await response.json();

      if (result.success && result.data) {
        setSuggestions(result.data.suggestions || []);
      }
    } catch (error) {
      console.error('Failed to fetch field suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    if (value.length >= 2) {
      fetchFieldSuggestions(value);
    }
    setShowDropdown(true);
  };

  const handleSelectField = (field: FieldSuggestion) => {
    onFieldSelect?.(field);
    setShowDropdown(false);
    setSearchTerm('');
  };

  const getFieldTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      'base': '基础',
      'param': '参数',
      'custom': '自定义',
      'fixed': '固定'
    };
    return labels[type] || type;
  };

  const getFieldTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      'base': '#3b82f6',
      'param': '#8b5cf6',
      'custom': '#f59e0b',
      'fixed': '#6b7280'
    };
    return colors[type] || '#9ca3af';
  };

  return (
    <div className="field-autocomplete">
      <div className="search-input-wrapper">
        <Input
          type="text"
          className="search-input"
          placeholder="搜索字段..."
          value={searchTerm}
          onChange={(e) => handleSearch((e.target as HTMLInputElement).value)}
          onFocus={() => setShowDropdown(true)}
        />
        {loading && <span className="loading-spinner">⏳</span>}
      </div>

      {showDropdown && (
        <div className="suggestions-dropdown">
          <div className="dropdown-header">
            <span>推荐字段</span>
            <button
              className="close-button"
              onClick={() => setShowDropdown(false)}
            >
              ✕
            </button>
          </div>

          <div className="suggestions-list">
            {suggestions.length === 0 ? (
              <div className="no-suggestions">未找到匹配字段</div>
            ) : (
              suggestions.map((field, index) => (
                <div
                  key={index}
                  className="suggestion-item"
                  onClick={() => handleSelectField(field)}
                >
                  <div className="field-info">
                    <span className="field-name">{field.name}</span>
                    <span
                      className="field-type-badge"
                      style={{ backgroundColor: getFieldTypeColor(field.type) }}
                    >
                      {getFieldTypeLabel(field.type)}
                    </span>
                  </div>

                  {field.description && (
                    <div className="field-description">
                      {field.description}
                    </div>
                  )}

                  {field.frequency && (
                    <div className="field-frequency">
                      使用频率: {field.frequency}次
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
