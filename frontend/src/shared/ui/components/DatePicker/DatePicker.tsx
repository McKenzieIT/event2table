import React, { useState, useRef, useEffect, useCallback, forwardRef, useMemo } from 'react';
import { DatePickerProps, DatePickerRef } from './DatePicker.types';
import './DatePicker.css';

// Date formatting utilities
const formatDate = (date: Date | null, format: string = 'YYYY-MM-DD'): string => {
  if (!date) return '';
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes);
};

const parseDate = (dateString: string, format: string = 'YYYY-MM-DD'): Date | null => {
  if (!dateString) return null;
  
  try {
    // Simple parsing for YYYY-MM-DD format
    const parts = dateString.split('-');
    if (parts.length === 3) {
      const year = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1;
      const day = parseInt(parts[2], 10);
      return new Date(year, month, day);
    }
    return new Date(dateString);
  } catch {
    return null;
  }
};

const getDaysInMonth = (year: number, month: number): number => {
  return new Date(year, month + 1, 0).getDate();
};

const getFirstDayOfMonth = (year: number, month: number, firstDayOfWeek: number = 0): number => {
  const day = new Date(year, month, 1).getDay();
  return (day - firstDayOfWeek + 7) % 7;
};

const isSameDay = (date1: Date, date2: Date): boolean => {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate();
};

const isDateInRange = (date: Date, minDate?: Date, maxDate?: Date): boolean => {
  if (minDate && date < minDate) return false;
  if (maxDate && date > maxDate) return false;
  return true;
};

export const DatePicker = forwardRef<DatePickerRef, DatePickerProps>(
  (
    {
      value,
      onChange,
      format = 'YYYY-MM-DD',
      placeholder = 'Select date',
      minDate,
      maxDate,
      disabled = false,
      showTime = false,
      timeFormat = 'HH:mm',
      locale = 'en-US',
      error,
      helperText,
      className = '',
      variant = 'default',
      size = 'md',
      theme = 'light',
      icon,
      showWeekNumbers = false,
      firstDayOfWeek = 0,
      renderDate,
      renderHeader,
      disableDate,
      closeOnSelect = true,
      clearable = false,
      id,
      name,
      required = false,
      autoFocus = false,
      tabIndex,
      ariaLabel = 'Date picker',
      testId = 'date-picker',
    },
    ref
  ) => {
    // State
    const [isOpen, setIsOpen] = useState(false);
    const [inputValue, setInputValue] = useState(formatDate(value, format));
    const [viewDate, setViewDate] = useState(value || new Date());
    const [currentView, setCurrentView] = useState<'days' | 'months' | 'years'>('days');
    
    // Refs
    const containerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    
    // Update input value when value prop changes
    useEffect(() => {
      setInputValue(formatDate(value, format));
    }, [value, format]);
    
    // Handle click outside
    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
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
    
    // Handle keyboard navigation
    const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
      if (disabled) return;
      
      switch (event.key) {
        case 'Enter':
        case ' ':
          event.preventDefault();
          setIsOpen(!isOpen);
          break;
        case 'Escape':
          setIsOpen(false);
          break;
        case 'ArrowUp':
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
          } else {
            setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1));
          }
          break;
        case 'ArrowDown':
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
          } else {
            setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1));
          }
          break;
        case 'ArrowLeft':
          if (isOpen) {
            event.preventDefault();
            setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1));
          }
          break;
        case 'ArrowRight':
          if (isOpen) {
            event.preventDefault();
            setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1));
          }
          break;
      }
    }, [disabled, isOpen, viewDate]);
    
    // Handle date selection
    const handleDateSelect = useCallback((date: Date) => {
      if (disableDate && disableDate(date)) return;
      if (!isDateInRange(date, minDate, maxDate)) return;
      
      onChange?.(date);
      setInputValue(formatDate(date, format));
      
      if (closeOnSelect && !showTime) {
        setIsOpen(false);
      }
    }, [onChange, format, disableDate, minDate, maxDate, closeOnSelect, showTime]);
    
    // Handle input change
    const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.value;
      setInputValue(newValue);
      
      const parsedDate = parseDate(newValue, format);
      if (parsedDate && isDateInRange(parsedDate, minDate, maxDate)) {
        onChange?.(parsedDate);
        setViewDate(parsedDate);
      }
    }, [format, minDate, maxDate, onChange]);
    
    // Handle clear
    const handleClear = useCallback(() => {
      onChange?.(null);
      setInputValue('');
      setIsOpen(false);
    }, [onChange]);
    
    // Expose ref methods
    React.useImperativeHandle(ref, () => ({
      open: () => setIsOpen(true),
      close: () => setIsOpen(false),
      clear: handleClear,
      focus: () => inputRef.current?.focus(),
      blur: () => inputRef.current?.blur(),
    }), [handleClear]);
    
    // Generate calendar days
    const calendarDays = useMemo(() => {
      const year = viewDate.getFullYear();
      const month = viewDate.getMonth();
      const daysInMonth = getDaysInMonth(year, month);
      const firstDay = getFirstDayOfMonth(year, month, firstDayOfWeek);
      
      const days: Array<{ date: Date; isCurrentMonth: boolean; isToday: boolean; isSelected: boolean; isDisabled: boolean }> = [];
      
      // Previous month days
      const prevMonth = month === 0 ? 11 : month - 1;
      const prevYear = month === 0 ? year - 1 : year;
      const daysInPrevMonth = getDaysInMonth(prevYear, prevMonth);
      
      for (let i = firstDay - 1; i >= 0; i--) {
        const date = new Date(prevYear, prevMonth, daysInPrevMonth - i);
        days.push({
          date,
          isCurrentMonth: false,
          isToday: isSameDay(date, new Date()),
          isSelected: value ? isSameDay(date, value) : false,
          isDisabled: !isDateInRange(date, minDate, maxDate) || (disableDate ? disableDate(date) : false),
        });
      }
      
      // Current month days
      for (let i = 1; i <= daysInMonth; i++) {
        const date = new Date(year, month, i);
        days.push({
          date,
          isCurrentMonth: true,
          isToday: isSameDay(date, new Date()),
          isSelected: value ? isSameDay(date, value) : false,
          isDisabled: !isDateInRange(date, minDate, maxDate) || (disableDate ? disableDate(date) : false),
        });
      }
      
      // Next month days
      const nextMonth = month === 11 ? 0 : month + 1;
      const nextYear = month === 11 ? year + 1 : year;
      const remainingDays = 42 - days.length; // 6 rows × 7 days = 42
      
      for (let i = 1; i <= remainingDays; i++) {
        const date = new Date(nextYear, nextMonth, i);
        days.push({
          date,
          isCurrentMonth: false,
          isToday: isSameDay(date, new Date()),
          isSelected: value ? isSameDay(date, value) : false,
          isDisabled: !isDateInRange(date, minDate, maxDate) || (disableDate ? disableDate(date) : false),
        });
      }
      
      return days;
    }, [viewDate, firstDayOfWeek, value, minDate, maxDate, disableDate]);
    
    // Week day names
    const weekDayNames = useMemo(() => {
      const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      return Array.from({ length: 7 }, (_, i) => days[(i + firstDayOfWeek) % 7]);
    }, [firstDayOfWeek]);
    
    // Month names
    const monthNames = useMemo(() => [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ], []);
    
    // Generate years for year selection
    const years = useMemo(() => {
      const currentYear = new Date().getFullYear();
      return Array.from({ length: 100 }, (_, i) => currentYear - 50 + i);
    }, []);
    
    // Classes
    const containerClasses = [
      'date-picker',
      `date-picker--${variant}`,
      `date-picker--${size}`,
      `date-picker--${theme}`,
      disabled && 'date-picker--disabled',
      error && 'date-picker--error',
      isOpen && 'date-picker--open',
      className,
    ].filter(Boolean).join(' ');
    
    return (
      <div
        ref={containerRef}
        className={containerClasses}
        data-testid={testId}
      >
        <div className="date-picker__input-wrapper">
          {icon && <span className="date-picker__icon">{icon}</span>}
          
          <input
            ref={inputRef}
            id={id}
            name={name}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onFocus={() => !disabled && setIsOpen(true)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            required={required}
            autoFocus={autoFocus}
            tabIndex={tabIndex}
            aria-label={ariaLabel}
            className="date-picker__input"
          />
          
          {clearable && value && !disabled && (
            <button
              type="button"
              className="date-picker__clear-button"
              onClick={handleClear}
              aria-label="Clear date"
            >
              ×
            </button>
          )}
          
          <button
            type="button"
            className="date-picker__calendar-button"
            onClick={() => !disabled && setIsOpen(!isOpen)}
            disabled={disabled}
            aria-label="Toggle calendar"
          >
            📅
          </button>
        </div>
        
        {error && <span className="date-picker__error">{error}</span>}
        {helperText && !error && <span className="date-picker__helper-text">{helperText}</span>}
        
        {isOpen && (
          <div className="date-picker__dropdown">
            <div className="date-picker__header">
              {currentView === 'days' && (
                <>
                  <button
                    type="button"
                    className="date-picker__nav-button"
                    onClick={() => setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1))}
                  >
                    ‹
                  </button>
                  <button
                    type="button"
                    className="date-picker__month-year-button"
                    onClick={() => setCurrentView('months')}
                  >
                    {monthNames[viewDate.getMonth()]} {viewDate.getFullYear()}
                  </button>
                  <button
                    type="button"
                    className="date-picker__nav-button"
                    onClick={() => setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1))}
                  >
                    ›
                  </button>
                </>
              )}
              
              {currentView === 'months' && (
                <>
                  <button
                    type="button"
                    className="date-picker__nav-button"
                    onClick={() => setViewDate(new Date(viewDate.getFullYear() - 1, viewDate.getMonth(), 1))}
                  >
                    ‹
                  </button>
                  <button
                    type="button"
                    className="date-picker__month-year-button"
                    onClick={() => setCurrentView('years')}
                  >
                    {viewDate.getFullYear()}
                  </button>
                  <button
                    type="button"
                    className="date-picker__nav-button"
                    onClick={() => setViewDate(new Date(viewDate.getFullYear() + 1, viewDate.getMonth(), 1))}
                  >
                    ›
                  </button>
                </>
              )}
              
              {currentView === 'years' && (
                <button
                  type="button"
                  className="date-picker__month-year-button"
                  onClick={() => setCurrentView('days')}
                >
                  {years[0]} - {years[years.length - 1]}
                </button>
              )}
            </div>
            
            {currentView === 'days' && (
              <>
                <div className="date-picker__weekdays">
                  {showWeekNumbers && <div className="date-picker__weekday date-picker__weekday--week-number">W</div>}
                  {weekDayNames.map((day) => (
                    <div key={day} className="date-picker__weekday">
                      {day}
                    </div>
                  ))}
                </div>
                
                <div className="date-picker__days">
                  {calendarDays.map((day, index) => {
                    const content = renderDate 
                      ? renderDate(day.date, day.isSelected)
                      : day.date.getDate();
                    
                    return (
                      <div
                        key={index}
                        className={[
                          'date-picker__day',
                          !day.isCurrentMonth && 'date-picker__day--other-month',
                          day.isToday && 'date-picker__day--today',
                          day.isSelected && 'date-picker__day--selected',
                          day.isDisabled && 'date-picker__day--disabled',
                        ].filter(Boolean).join(' ')}
                        onClick={() => !day.isDisabled && handleDateSelect(day.date)}
                      >
                        {content}
                      </div>
                    );
                  })}
                </div>
              </>
            )}
            
            {currentView === 'months' && (
              <div className="date-picker__months">
                {monthNames.map((month, index) => (
                  <div
                    key={month}
                    className={[
                      'date-picker__month',
                      viewDate.getMonth() === index && 'date-picker__month--selected',
                    ].filter(Boolean).join(' ')}
                    onClick={() => {
                      setViewDate(new Date(viewDate.getFullYear(), index, 1));
                      setCurrentView('days');
                    }}
                  >
                    {month}
                  </div>
                ))}
              </div>
            )}
            
            {currentView === 'years' && (
              <div className="date-picker__years">
                {years.map((year) => (
                  <div
                    key={year}
                    className={[
                      'date-picker__year',
                      viewDate.getFullYear() === year && 'date-picker__year--selected',
                    ].filter(Boolean).join(' ')}
                    onClick={() => {
                      setViewDate(new Date(year, viewDate.getMonth(), 1));
                      setCurrentView('months');
                    }}
                  >
                    {year}
                  </div>
                ))}
              </div>
            )}
            
            {showTime && value && (
              <div className="date-picker__time">
                <input
                  type="time"
                  value={formatDate(value, timeFormat)}
                  onChange={(e) => {
                    const [hours, minutes] = e.target.value.split(':').map(Number);
                    const newDate = new Date(value);
                    newDate.setHours(hours, minutes);
                    onChange?.(newDate);
                  }}
                  className="date-picker__time-input"
                />
              </div>
            )}
          </div>
        )}
      </div>
    );
  }
);

DatePicker.displayName = 'DatePicker';
