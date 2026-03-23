import { FieldValues, FieldPath } from 'react-hook-form';

import type { Size } from '@/shared/ui/types/common';

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

/** Select mode - default for local filtering, autocomplete for remote search */
export type SelectMode = 'default' | 'autocomplete';

export interface SelectProps<TFieldValues extends FieldValues = FieldValues> {
  name: FieldPath<TFieldValues>;
  label?: string;
  options: SelectOption[];
  value?: string | number | (string | number)[];
  onChange?: (value: string | number | (string | number)[]) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  searchable?: boolean;
  multiple?: boolean;
  error?: string;
  helperText?: string;
  className?: string;
  size?: Size;
  control?: unknown;
  rules?: unknown;
  /** Select mode - 'default' for local filtering, 'autocomplete' for remote search */
  mode?: SelectMode;
  /** Allow creating new options (only for single select) */
  allowCreate?: boolean;
  /** Callback when searching (for autocomplete mode) */
  onSearch?: (searchTerm: string) => void;
  /** Callback when creating a new option */
  onCreate?: (label: string) => void;
  /** Loading state (for autocomplete mode) */
  loading?: boolean;
  /** Debounce delay for search in milliseconds (default: 300) */
  searchDebounce?: number;
  /** Custom message when no options match */
  noOptionsMessage?: string;
}
