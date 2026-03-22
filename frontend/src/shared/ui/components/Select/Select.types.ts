import { FieldValues, FieldPath } from 'react-hook-form';

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

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
  size?: 'small' | 'medium' | 'large';
  control?: unknown;
  rules?: unknown;
}
