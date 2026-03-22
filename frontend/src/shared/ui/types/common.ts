/** 基础组件属性 */
export interface BaseComponentProps {
  className?: string;
  id?: string;
  "data-testid"?: string;
  children?: React.ReactNode;
}

/** 尺寸类型 */
export type Size = "small" | "medium" | "large";

/** 变体类型 */
export type Variant = "primary" | "secondary" | "outline" | "ghost" | "danger";

/** 状态类型 */
export type Status = "idle" | "loading" | "success" | "error";

/** 通用响应类型 */
export interface ApiResponse&lt;T&gt; {
  data: T;
  message: string;
  success: boolean;
}

/** 分页参数 */
export interface PaginationParams {
  page: number;
  pageSize: number;
  total?: number;
}

/** 排序参数 */
export interface SortParams {
  field: string;
  order: "asc" | "desc";
}

/** 通用ID类型 */
export type Id = string | number;

/** 可选ID类型 */
export type OptionalId = Id | undefined | null;

/** 选项类型 */
export interface Option<T = unknown> {
  value: T;
  label: string;
  disabled?: boolean;
}
