/**
 * 工具类型定义
 * 提供类型操作和转换的工具类型
 */

/** 提取组件Props类型 */
export type PropsOf<T> = T extends React.ComponentType<infer P> ? P : never;

/** 使Props部分可选 */
export type PartialProps<T> = Partial<T>;

/** 使Props全部必选 */
export type RequiredProps<T> = Required<T>;

/** 提取特定属性 */
export type PickProps<T, K extends keyof T> = Pick<T, K>;

/** 排除特定属性 */
export type OmitProps<T, K extends keyof T> = Omit<T, K>;

/** 条件类型 */
export type If<T, Condition, True, False> = T extends Condition ? True : False;

/** 事件处理器类型 */
export type EventHandler<E = Event> = (event: E) => void;

/** 提取数组元素类型 */
export type ArrayElement<T> = T extends readonly (infer E)[] ? E : never;

/** 提取Promise返回类型 */
export type Awaited<T> = T extends Promise<infer U> ? U : T;

/** 提取函数返回类型 */
export type ReturnType<T extends (...args: unknown[]) => unknown> = T extends (
  ...args: unknown[]
) => infer R
  ? R
  : never;

/** 提取函数参数类型 */
export type Parameters<T extends (...args: unknown[]) => unknown> = T extends (
  ...args: infer P
) => unknown
  ? P
  : never;

/** 非空类型 */
export type NonNullable<T> = T extends null | undefined ? never : T;

/** 只读属性 */
export type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

/** 可变属性 */
export type Mutable<T> = {
  -readonly [P in keyof T]: T[P];
};

/** 提取对象键类型 */
export type ObjectKeys<T extends object> = keyof T;

/** 提取对象值类型 */
export type ObjectValues<T extends object> = T[keyof T];

/** 合并类型 */
export type Merge<M, N> = Omit<M, keyof N> & N;

/** 忽略类型（用于忽略未使用变量警告） */
export type Ignore = never;
