import type { MouseEvent, KeyboardEvent, ChangeEvent, FormEvent, FocusEvent } from "react";

/** 点击事件处理器 */
export type ClickHandler = (event: MouseEvent) => void;

/** 键盘事件处理器 */
export type KeyboardHandler = (event: KeyboardEvent) => void;

/** 变更事件处理器 */
export type ChangeHandler<T = HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement> = (
  event: ChangeEvent<T>
) => void;

/** 焦点事件处理器 */
export type FocusHandler<T = HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement> = (
  event: FocusEvent<T>
) => void;

/** 表单提交处理器 */
export type SubmitHandler = (event: FormEvent) => void;

/** 异步点击处理器 */
export type AsyncClickHandler = (event: MouseEvent) => Promise<void>;

/** 异步提交处理器 */
export type AsyncSubmitHandler = (event: FormEvent) => Promise<void>;
