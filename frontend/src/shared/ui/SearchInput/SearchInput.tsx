/**
 * SearchInput Component - 全功能搜索输入组件
 *
 * 功能：
 * - 继承Input组件样式
 * - 搜索图标
 * - 300ms防抖
 * - Ctrl+K / Cmd+K 快捷键
 * - 清除按钮（有内容时显示）
 *
 * @example
 * // 基础使用
 * <SearchInput
 *   value={searchTerm}
 *   onChange={setSearchTerm}
 *   placeholder="搜索参数..."
 *   debounceMs={300}
 * />
 *
 * // 带清除按钮
 * <SearchInput
 *   value={searchTerm}
 *   onChange={setSearchTerm}
 *   onClear={handleClear}
 *   placeholder="搜索参数..."
 * />
 */

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import './SearchInput.css';

/**
 * SearchInput Props Interface
 */
interface SearchInputProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  onClear?: () => void;
  debounceMs?: number;
  icon?: React.ComponentType<any>;
  disabled?: boolean;
  className?: string;
}

/**
 * SearchInput Component
 */
function SearchInput({
  value = '',
  onChange,
  placeholder = '搜索...',
  onClear,
  debounceMs = 300,
  icon: SearchIcon,
  disabled = false,
  className = '',
}: SearchInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [showClearButton, setShowClearButton] = useState(false);
  const [internalValue, setInternalValue] = useState(value);

  // 300ms防抖实现
  const debounce = useCallback((fn: Function) => {
    const timeoutRef = useRef<NodeJS.Timeout>();

    return (...args: any[]) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => {
        fn(...args);
        timeoutRef.current = null;
      }, debounceMs);
    };
  }, [debounceMs]);

  // 处理输入变化（带防抖）
  const debouncedOnChange = useCallback(
    (newValue: string) => {
      setInternalValue(newValue);
      setShowClearButton(newValue.length > 0);
      debounce.onChange?.(newValue);
    },
    [debounce, debounce.onChange]
  );

  // 处理清除操作
  const handleClear = useCallback(() => {
    setInternalValue('');
    setShowClearButton(false);
    onClear?.();
    debounce.onChange?.('');
    inputRef.current?.focus();
  }, [onClear, debounce.onChange]);

  // 处理焦点变化
  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  // 处理快捷键
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      inputRef.current?.focus();
    }
  }, []);

  // 同步内部value和外部value
  useEffect(() => {
    setInternalValue(value || '');
    setShowClearButton((value || '').length > 0);
  }, [value]);

  const wrapperClass = [
    'search-input-wrapper',
    disabled && 'search-input-wrapper--disabled',
    className
  ].filter(Boolean).join(' ');

  const inputClass = [
    'search-input',
    isFocused && 'search-input--focused',
    showClearButton && 'search-input--has-clear',
    disabled && 'search-input--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={wrapperClass}>
      {/* 搜索图标 */}
      {icon && <div className="search-icon">{<SearchIcon />}</div>}

      {/* 输入框 */}
      <input
        ref={inputRef}
        type="text"
        className={inputClass}
        placeholder={placeholder}
        value={internalValue}
        onChange={(e) => debouncedOnChange(e.target.value)}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        autoComplete="off"
      />

      {/* 清除按钮 */}
      {showClearButton && !disabled && (
        <button
          type="button"
          className="clear-button"
          onClick={handleClear}
          aria-label="清除搜索"
        >
          ×
        </button>
      )}

      {/* 快捷键提示 */}
      {!isFocused && !disabled && (
        <div className="shortcut-hint">
          <span>⌘K</span>
        </div>
      )}
    </div>
  );
}

export default SearchInput;
