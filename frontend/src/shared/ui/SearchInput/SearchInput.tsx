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
 * 性能优化：
 * - React.memo防止不必要的重新渲染
 * - useCallback稳定事件处理器
 * - useMemo缓存CSS类名计算
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

import React, { useState, useEffect, useCallback, useRef, useMemo, ReactNode, KeyboardEvent, ChangeEvent } from 'react';
import './SearchInput.css';

/**
 * SearchInput Props Interface
 */
interface SearchInputProps {
  /** 当前输入值 */
  value?: string;
  /** 值变化回调（防抖后触发） */
  onChange?: (value: string) => void;
  /** 占位符文本 */
  placeholder?: string;
  /** 清除按钮回调 */
  onClear?: () => void;
  /** 防抖延迟时间（毫秒），默认300ms */
  debounceMs?: number;
  /** 自定义搜索图标 */
  icon?: ReactNode;
  /** 是否禁用 */
  disabled?: boolean;
  /** 自定义类名 */
  className?: string;
  /** HTML input属性 */
  [key: string]: any;
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
  icon,
  disabled = false,
  className = '',
}: SearchInputProps) {
  const defaultSearchIcon = (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"></circle>
      <path d="m21 21-4.35-4.35"></path>
    </svg>
  );

  // Handle both function components and JSX elements
  const searchIcon = icon !== undefined ? icon : defaultSearchIcon;
  const renderedIcon = typeof searchIcon === 'function' ? React.createElement(searchIcon) : searchIcon;
  const inputRef = useRef<HTMLInputElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [showClearButton, setShowClearButton] = useState(false);
  const [internalValue, setInternalValue] = useState(value);

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // 使用useEffect处理防抖
  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (onChange && internalValue !== value) {
      console.log('[SearchInput] Scheduling onChange with debounce:', internalValue, 'debounceMs:', debounceMs);
      timeoutRef.current = setTimeout(() => {
        console.log('[SearchInput] Triggering onChange with value:', internalValue);
        onChange(internalValue);
      }, debounceMs);
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [internalValue, debounceMs, onChange]);

  // 处理输入变化
  const handleChange = useCallback((newValue: string) => {
    console.log('[SearchInput] handleChange called with newValue:', newValue);
    setInternalValue(newValue);
    setShowClearButton(newValue.length > 0);
  }, []);

  // 处理清除操作
  const handleClear = useCallback(() => {
    setInternalValue('');
    setShowClearButton(false);
    onClear?.();
    onChange?.('');
    inputRef.current?.focus();
  }, [onClear, onChange]);

  // 处理焦点变化
  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  // 处理快捷键
  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLInputElement>) => {
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

  // PERFORMANCE: useMemo to cache CSS class computations
  // Prevents re-creation of class strings on every render
  const wrapperClass = useMemo(() => {
    return [
      'search-input-wrapper',
      disabled && 'search-input-wrapper--disabled',
      className
    ].filter(Boolean).join(' ');
  }, [disabled, className]);

  // PERFORMANCE: useMemo to cache CSS class computations
  // Prevents re-creation of class strings on every render
  const inputClass = useMemo(() => {
    return [
      'search-input',
      isFocused && 'search-input--focused',
      showClearButton && 'search-input--has-clear',
      disabled && 'search-input--disabled'
    ].filter(Boolean).join(' ');
  }, [isFocused, showClearButton, disabled]);

  return (
    <div className={wrapperClass}>
      <div className="search-icon" data-testid="search-icon-wrapper">
        {renderedIcon}
      </div>

      {/* 输入框 */}
      <input
        ref={inputRef}
        type="text"
        className={inputClass}
        placeholder={placeholder}
        value={internalValue}
        onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange(e.target.value)}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        autoComplete="off"
        aria-label={placeholder}
        aria-describedby={!disabled ? "search-shortcut-hint" : undefined}
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
        <div className="shortcut-hint" id="search-shortcut-hint">
          <span>⌘K</span>
        </div>
      )}
    </div>
  );
}

// PERFORMANCE: React.memo with custom comparison
// Prevents re-renders when only irrelevant props change
const MemoizedSearchInput = React.memo(SearchInput, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.onChange === nextProps.onChange &&
    prevProps.onClear === nextProps.onClear &&
    prevProps.placeholder === nextProps.placeholder &&
    prevProps.debounceMs === nextProps.debounceMs &&
    prevProps.className === nextProps.className
  );
});

MemoizedSearchInput.displayName = 'MemoizedSearchInput';

export default MemoizedSearchInput;
