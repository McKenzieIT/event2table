import { ReactNode } from 'react';

export type DatePickerVariant = 'default' | 'outlined' | 'filled';
export type DatePickerSize = 'sm' | 'md' | 'lg';
export type DatePickerTheme = 'light' | 'dark' | 'auto';

export interface DatePickerProps {
  /** Selected date value */
  value?: Date | null;
  /** Callback when date changes */
  onChange?: (date: Date | null) => void;
  /** Date format string (e.g., 'YYYY-MM-DD') */
  format?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Minimum selectable date */
  minDate?: Date;
  /** Maximum selectable date */
  maxDate?: Date;
  /** Whether the picker is disabled */
  disabled?: boolean;
  /** Whether to show time selection */
  showTime?: boolean;
  /** Time format string (e.g., 'HH:mm') */
  timeFormat?: string;
  /** Locale for date formatting */
  locale?: string;
  /** Error message */
  error?: string;
  /** Helper text below the input */
  helperText?: string;
  /** Additional CSS class name */
  className?: string;
  /** DatePicker variant style */
  variant?: DatePickerVariant;
  /** DatePicker size */
  size?: DatePickerSize;
  /** DatePicker theme */
  theme?: DatePickerTheme;
  /** Custom input icon */
  icon?: ReactNode;
  /** Whether to show week numbers */
  showWeekNumbers?: boolean;
  /** First day of week (0 = Sunday, 1 = Monday, etc.) */
  firstDayOfWeek?: number;
  /** Custom date renderer */
  renderDate?: (date: Date, isSelected: boolean) => ReactNode;
  /** Custom header renderer */
  renderHeader?: (date: Date) => ReactNode;
  /** Disable specific dates */
  disableDate?: (date: Date) => boolean;
  /** Whether to close on select */
  closeOnSelect?: boolean;
  /** Whether the picker is clearable */
  clearable?: boolean;
  /** Input ID */
  id?: string;
  /** Input name */
  name?: string;
  /** Required field */
  required?: boolean;
  /** Auto focus */
  autoFocus?: boolean;
  /** Tab index */
  tabIndex?: number;
  /** Aria label */
  ariaLabel?: string;
  /** Test ID for testing */
  testId?: string;
}

export interface DatePickerRef {
  /** Open the date picker */
  open: () => void;
  /** Close the date picker */
  close: () => void;
  /** Clear the selected date */
  clear: () => void;
  /** Focus the input */
  focus: () => void;
  /** Blur the input */
  blur: () => void;
}

export interface DatePickerCalendarProps {
  /** Current view date */
  viewDate: Date;
  /** Selected date */
  selectedDate: Date | null;
  /** Callback when date is selected */
  onSelect: (date: Date) => void;
  /** Callback when view date changes */
  onViewDateChange: (date: Date) => void;
  /** Minimum selectable date */
  minDate?: Date;
  /** Maximum selectable date */
  maxDate?: Date;
  /** Whether to show week numbers */
  showWeekNumbers?: boolean;
  /** First day of week */
  firstDayOfWeek?: number;
  /** Disable specific dates */
  disableDate?: (date: Date) => boolean;
  /** Custom date renderer */
  renderDate?: (date: Date, isSelected: boolean) => ReactNode;
  /** Custom header renderer */
  renderHeader?: (date: Date) => ReactNode;
  /** DatePicker theme */
  theme?: DatePickerTheme;
}

export interface DatePickerTimeProps {
  /** Selected time */
  value: Date | null;
  /** Callback when time changes */
  onChange: (date: Date) => void;
  /** Time format string */
  format?: string;
  /** Whether time picker is disabled */
  disabled?: boolean;
  /** DatePicker theme */
  theme?: DatePickerTheme;
}

export interface DatePickerMonthYearProps {
  /** Current view date */
  viewDate: Date;
  /** Callback when month/year changes */
  onChange: (date: Date) => void;
  /** Minimum selectable date */
  minDate?: Date;
  /** Maximum selectable date */
  maxDate?: Date;
  /** DatePicker theme */
  theme?: DatePickerTheme;
}
