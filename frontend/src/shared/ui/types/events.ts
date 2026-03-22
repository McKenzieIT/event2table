import type { MouseEvent, KeyboardEvent, ChangeEvent, FormEvent } from "react";

/** 点击事件处理器 */
export type ClickHandler = (event: MouseEvent) => void;

/** 键盘事件处理器 */
export type KeyboardHandler = (event: KeyboardEvent) => void;

/** 变更事件处理器 */
export type ChangeHandler&lt;T = HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement&gt; = (
  event: ChangeEvent&lt;T&gt;
) => void;

/** 表单提交处理器 */
export type SubmitHandler = (event: FormEvent) => void;

/** 异步点击处理器 */
export type AsyncClickHandler = (event: MouseEvent) => Promise&lt;void&gt;;

/** 异步提交处理器 */
export type AsyncSubmitHandler = (event: FormEvent) => Promise&lt;void&gt;;
