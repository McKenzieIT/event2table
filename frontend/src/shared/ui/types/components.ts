import type { ReactNode } from "react";
import type { BaseComponentProps, Size, Variant, Id } from "./common";

/** 按钮属性 */
export interface ButtonProps extends BaseComponentProps {
  variant?: Variant;
  size?: Size;
  disabled?: boolean;
  loading?: boolean;
  type?: "button" | "submit" | "reset";
  onClick?: (event: React.MouseEvent) => void;
}

/** 输入框属性 */
export interface InputProps extends BaseComponentProps {
  value?: string;
  defaultValue?: string;
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  error?: string;
  type?: "text" | "password" | "email" | "number" | "tel" | "url";
  onChange?: (event: React.ChangeEvent&lt;HTMLInputElement&gt;) => void;
  onFocus?: (event: React.FocusEvent&lt;HTMLInputElement&gt;) => void;
  onBlur?: (event: React.FocusEvent&lt;HTMLInputElement&gt;) => void;
}

/** 选择框属性 */
export interface SelectProps&lt;T = unknown&gt; extends BaseComponentProps {
  value?: T;
  defaultValue?: T;
  options: Array&lt;{ value: T; label: string; disabled?: boolean }&gt;;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  onChange?: (value: T) => void;
}

/** 模态框属性 */
export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: "small" | "medium" | "large" | "fullscreen";
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
}

/** 表格列定义 */
export interface ColumnDef&lt;T = unknown&gt; {
  key: keyof T | string;
  title: string;
  width?: number | string;
  align?: "left" | "center" | "right";
  render?: (value: unknown, row: T, index: number) => ReactNode;
  sortable?: boolean;
}

/** 表格属性 */
export interface TableProps&lt;T extends { id: Id }&gt; extends BaseComponentProps {
  data: T[];
  columns: ColumnDef&lt;T&gt;[];
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
}

/** 表单字段定义 */
export interface FieldDef&lt;T = unknown&gt; {
  name: string;
  label: string;
  type: "text" | "password" | "email" | "number" | "select" | "textarea" | "checkbox";
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
  defaultValue?: T;
  options?: Array&lt;{ value: T; label: string }&gt;;
  validate?: (value: T) => string | undefined;
}

/** 表单属性 */
export interface FormProps extends BaseComponentProps {
  fields: FieldDef[];
  initialValues?: Record&lt;string, unknown&gt;;
  onSubmit: (values: Record&lt;string, unknown&gt;) => void | Promise&lt;void&gt;;
  submitLabel?: string;
}
