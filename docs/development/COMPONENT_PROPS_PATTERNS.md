# React组件Props类型设计模式指南

> **版本**: 1.0.0 | **最后更新**: 2026-03-01
>
> **📚 本文档**: Event2Table项目中React组件Props设计的最佳实践总结

---

## 目录

1. [基础模式](#1-基础组件props模式)
2. [可组合模式](#2-可组合props模式)
3. [事件处理模式](#3-事件处理props模式)
4. [渲染Props模式](#4-渲染props模式)
5. [多态组件模式](#5-多态组件props模式)
6. [扩展性模式](#6-扩展性props模式)
7. [验证模式](#7-props验证模式)
8. [实际案例](#8-实际案例)
9. [最佳实践清单](#9-最佳实践检查清单)

---

## 1. 基础组件Props模式

### 1.1 最小基础Props

所有组件都应该包含的基础属性：

```typescript
/**
 * 基础组件Props - 包含通用属性
 */
export interface BaseComponentProps {
  /** CSS类名 */
  className?: string;
  /** 子元素 */
  children?: ReactNode;
  /** 是否禁用 */
  disabled?: boolean;
  /** 加载状态 */
  loading?: boolean;
  /** 测试ID（用于测试） */
  'data-testid'?: string;
}
```

**使用示例**：

```typescript
import { BaseComponentProps } from '@/types/common';

interface MyComponentProps extends BaseComponentProps {
  // 组件特定属性
  title?: string;
}
```

**优点**：
- ✅ 提供统一的组件接口
- ✅ 支持测试自动化
- ✅ 便于样式定制

---

## 2. 可组合Props模式

### 2.1 标签组件Props

适用于Input、Select等带标签的表单组件：

```typescript
/**
 * 带标签的组件Props
 * 从 @/types/common 导入
 */
export interface LabeledComponentProps extends BaseComponentProps {
  /** 标签文本 */
  label?: string;
  /** 是否必填 */
  required?: boolean;
  /** 提示文本 */
  helperText?: string;
  /** 错误信息 */
  error?: string;
}
```

**实际应用 - Input组件**：

```typescript
export interface InputProps extends
  Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'>,
  LabeledComponentProps {

  type?: InputType;
  placeholder?: string;
  value?: string | number;
  onChange?: ChangeEventHandler<HTMLInputElement>;
}
```

### 2.2 可选择组件Props

适用于需要值选择的组件（Input、Select、Checkbox等）：

```typescript
/**
 * 可选择组件Props
 * 从 @/types/common 导入
 */
export interface SelectableComponentProps<T = string | number>
  extends BaseComponentProps {
  /** 当前值 */
  value?: T;
  /** 值变更回调 */
  onChange?: ValueChangeCallback<T>;
  /** 占位文本 */
  placeholder?: string;
  /** 选项列表 */
  options?: SelectOption<T>[];
}
```

### 2.3 组合多个模式

**实际应用 - Select组件**：

```typescript
export interface SelectProps extends
  Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange' | 'value'>,
  LabeledComponentProps {  // 组合标签模式

  options?: SelectOption[];
  value?: string | number;
  onChange?: ValueChangeCallback<string | number>;
  placeholder?: string;
  searchable?: boolean;
}
```

**优点**：
- ✅ 代码复用性强
- ✅ 类型安全
- ✅ 易于维护

---

## 3. 事件处理Props模式

### 3.1 通用事件处理器类型

```typescript
/**
 * 事件处理器类型 - 泛型版本
 * 从 @/types/common 导入
 */
export type EventHandler<TEvent = Event, TReturn = void> =
  (event: TEvent) => TReturn;

/**
 * 鼠标事件处理器
 */
export type MouseEventHandler = EventHandler<MouseEvent>;

/**
 * 变更事件处理器
 */
export type ChangeEventHandler<T = Element> =
  EventHandler<ChangeEvent<T>>;

/**
 * 焦点事件处理器
 */
export type FocusEventHandler = EventHandler<FocusEvent>;

/**
 * 点击回调函数类型
 */
export type ClickCallback = (event: MouseEvent) => void | Promise<void>;

/**
 * 值变更回调函数类型
 */
export type ValueChangeCallback<T = string | number> = (value: T) => void;
```

### 3.2 实际应用 - Button组件

```typescript
export interface ButtonProps extends
  Omit<React.ComponentPropsWithoutRef<'button'>, 'size' | 'onClick'>,
  BaseComponentProps {

  variant?: ButtonVariant;
  size?: Size;
  icon?: IconComponent;
  onClick?: MouseEventHandler;  // 使用通用事件处理器类型
}
```

### 3.3 异步事件处理

```typescript
/**
 * 异步函数类型
 * 从 @/types/common 导入
 */
export type AsyncFunction<T = void, P extends unknown[] = []> =
  (...args: P) => Promise<T>;

// 应用示例
interface FormProps {
  /** 异步提交处理 */
  onSubmit: AsyncFunction<void, [FormData]>;
  /** 提交成功回调 */
  onSuccess?: (data: ApiResponse) => void;
  /** 提交失败回调 */
  onError?: (error: Error) => void;
}
```

**优点**：
- ✅ 类型安全的事件处理
- ✅ 支持异步操作
- ✅ 统一的事件接口

---

## 4. 渲染Props模式

### 4.1 基础渲染Props

```typescript
interface RenderPropsComponentProps<T> {
  data: T[];
  renderItem: (item: T, index: number) => ReactNode;
  renderEmpty?: () => ReactNode;
  renderLoading?: () => ReactNode;
  renderError?: (error: Error) => ReactNode;
}
```

### 4.2 实际应用 - 列表组件

```typescript
interface ListProps<T> {
  /** 数据源 */
  data: T[];
  /** 渲染单项 */
  renderItem: (item: T, index: number) => ReactNode;
  /** 空状态渲染 */
  renderEmpty?: () => ReactNode;
  /** 加载状态渲染 */
  renderLoading?: () => ReactNode;
  /** 错误状态渲染 */
  renderError?: (error: Error) => ReactNode;
  /** 提取key的函数 */
  keyExtractor: (item: T, index: number) => string | number;
}

function List<T>({ data, renderItem, renderEmpty, keyExtractor }: ListProps<T>) {
  if (data.length === 0 && renderEmpty) {
    return renderEmpty();
  }

  return (
    <ul>
      {data.map((item, index) => (
        <li key={keyExtractor(item, index)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  );
}
```

**使用示例**：

```typescript
<List
  data={users}
  keyExtractor={(user) => user.id}
  renderItem={(user) => (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  )}
  renderEmpty={() => <div>No users found</div>}
/>
```

**优点**：
- ✅ 灵活的渲染逻辑
- ✅ 组件复用性强
- ✅ 关注点分离

---

## 5. 多态组件Props模式

### 5.1 基础多态组件

允许组件渲染为不同的HTML元素：

```typescript
interface PolymorphicComponentProps<E extends React.ElementType> {
  /** 渲染为的元素类型 */
  as?: E;
  /** 子元素 */
  children?: ReactNode;
}

type Props<E extends React.ElementType> =
  PolymorphicComponentProps<E> &
  Omit<React.ComponentPropsWithoutRef<E>, 'as'>;
```

### 5.2 实际应用 - 多态Button

```typescript
type ButtonAsProp<E extends React.ElementType> = {
  as?: E;
} & Omit<React.ComponentPropsWithoutRef<E>, 'as'>;

type ButtonProps<E extends React.ElementType> = ButtonAsProp<E> & {
  variant?: 'primary' | 'secondary';
};

function Button<E extends React.ElementType = 'button'>({
  as,
  variant = 'primary',
  ...props
}: ButtonProps<E>) {
  const Component = as || 'button';
  return <Component className={`btn btn-${variant}`} {...props} />;
}

// 使用示例
<Button>Click me</Button>                    // 渲染为 <button>
<Button as="a" href="/home">Home</Button>    // 渲染为 <a>
<Button as={Link} to="/about">About</Button> // 渲染为 React Router Link
```

**优点**：
- ✅ 灵活的组件行为
- ✅ 减少重复代码
- ✅ 更好的类型推断

---

## 6. 扩展性Props模式

### 6.1 使用...rest允许扩展

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  /** 允许传递任意其他属性 */
  [key: string]: unknown;
}
```

### 6.2 使用Omit排除冲突属性

```typescript
// 从 Input 组件的实际实现
export interface InputProps extends
  Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange' | 'onBlur' | 'onFocus' | 'value'>,
  LabeledComponentProps {

  type?: InputType;
  value?: string | number;
  onChange?: ChangeEventHandler<HTMLInputElement>;
  onBlur?: FocusEventHandler;
  onFocus?: FocusEventHandler;
}
```

**为什么需要Omit？**
- `React.InputHTMLAttributes` 已经包含 `type`、`onChange` 等属性
- 我们想要自定义这些属性的类型（更严格的类型）
- 使用 `Omit` 排除原始属性，避免类型冲突

### 6.3 使用泛型增强扩展性

```typescript
/**
 * 提取类型 - 仅保留指定属性
 * 从 @/types/common 导入
 */
export type ExtractType<T, K extends keyof T> = Pick<T, K>;

/**
 * 排除类型 - 排除指定属性
 */
export type ExcludeType<T, K extends keyof T> = Omit<T, K>;

/**
 * 可选类型 - 指定属性变为可选
 */
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * 必需类型 - 指定属性变为必需
 */
export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

/**
 * 只读类型 - 指定属性变为只读
 */
export type ReadonlyBy<T, K extends keyof T> = Omit<T, K> & Readonly<Pick<T, K>>;
```

**应用示例**：

```typescript
// 让某些属性可选
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

type UserUpdateProps = PartialBy<User, 'name' | 'email'>;
// 等价于：
// interface UserUpdateProps {
//   id: number;
//   name?: string;
//   email?: string;
//   age: number;
// }

// 让某些属性必需
type UserCreateProps = RequiredBy<User, 'name' | 'email'>;
// 所有属性都必需
```

**优点**：
- ✅ 灵活的类型组合
- ✅ 避免属性冲突
- ✅ 更好的类型推断

---

## 7. Props验证模式

### 7.1 运行时验证

```typescript
interface Props {
  name: string;
  age: number;
}

function Component({ name, age }: Props) {
  useEffect(() => {
    if (!name || name.length === 0) {
      console.warn('[Component] name should not be empty');
    }
    if (age < 0 || age > 150) {
      console.warn('[Component] age should be between 0 and 150');
    }
  }, [name, age]);

  return <div>{name}: {age}</div>;
}
```

### 7.2 使用TypeScript类型守卫

```typescript
/**
 * 检查值是否为GameContext
 * 从 @/types/common 导入
 */
export function isGameContext(value: unknown): value is GameContext {
  return (
    typeof value === 'object' &&
    value !== null &&
    'gid' in value &&
    'name' in value &&
    'ods_db' in value
  );
}

// 使用示例
function GameSelector({ game }: { game: unknown }) {
  if (!isGameContext(game)) {
    return <div>Invalid game context</div>;
  }

  return <div>{game.name}</div>; // TypeScript知道这是GameContext
}
```

### 7.3 Props默认值模式

```typescript
interface ComponentProps {
  title?: string;
  count?: number;
  disabled?: boolean;
}

function Component({
  title = 'Default Title',
  count = 0,
  disabled = false
}: ComponentProps) {
  return (
    <div>
      <h1>{title}</h1>
      <p>Count: {count}</p>
      {disabled && <p>Disabled</p>}
    </div>
  );
}
```

**优点**：
- ✅ 早期发现错误
- ✅ 更好的开发体验
- ✅ 生产环境健壮性

---

## 8. 实际案例

### 案例1: Button组件（完整实现）

**文件**: `/frontend/src/shared/ui/Button/Button.tsx`

```typescript
export interface ButtonProps extends
  Omit<React.ComponentPropsWithoutRef<'button'>, 'size' | 'onClick'>,
  BaseComponentProps {

  /** Button variant */
  variant?: ButtonVariant;
  /** Button size */
  size?: Size;
  /** Icon component */
  icon?: IconComponent;
  /** Click handler */
  onClick?: MouseEventHandler;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon: Icon,
  onClick,
  className = '',
  ...props
}, ref) => {
  // ... 实现代码
});
```

**关键点**：
- ✅ 使用 `React.forwardRef` 支持ref转发
- ✅ 使用 `Omit` 排除冲突的 `size` 和 `onClick` 属性
- ✅ 提供 `loading` 状态
- ✅ 支持图标
- ✅ 使用 `React.memo` 优化性能

### 案例2: Input组件（完整实现）

**文件**: `/frontend/src/shared/ui/Input/Input.tsx`

```typescript
export interface InputProps extends
  Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange' | 'onBlur' | 'onFocus' | 'value'>,
  LabeledComponentProps {

  type?: InputType;
  placeholder?: string;
  icon?: IconComponent;
  value?: string | number;
  onChange?: ChangeEventHandler<HTMLInputElement>;
  onBlur?: FocusEventHandler;
  onFocus?: FocusEventHandler;
  id?: string;
  name?: string;
  readOnly?: boolean;
  autoFocus?: boolean;
  maxLength?: number;
  minLength?: number;
}

const Input = forwardRef<HTMLInputElement, InputProps>(({
  type = 'text' as InputType,
  label,
  placeholder,
  error,
  disabled = false,
  required = false,
  icon: Icon,
  helperText,
  className = '',
  value,
  onChange,
  onBlur,
  onFocus,
  id: customId,
  name,
  readOnly = false,
  autoFocus = false,
  maxLength,
  minLength,
  ...props
}, ref) => {
  // ... 实现代码
});
```

**关键点**：
- ✅ 继承 `LabeledComponentProps`（标签、错误、必填等）
- ✅ 使用 `Omit` 排除原生input属性，使用自定义类型
- ✅ 使用 `forwardRef` 支持ref转发
- ✅ 自动生成ID（用于label关联）
- ✅ 完整的可访问性支持（ARIA属性）

### 案例3: Select组件（完整实现）

**文件**: `/frontend/src/shared/ui/Select/Select.tsx`

```typescript
export interface SelectProps extends
  Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange' | 'value'>,
  LabeledComponentProps {

  options?: SelectOption[];
  value?: string | number;
  onChange?: ValueChangeCallback<string | number>;
  placeholder?: string;
  searchable?: boolean;
}

const Select = forwardRef<HTMLDivElement, SelectProps>(({
  label,
  options = [],
  value,
  onChange,
  placeholder = 'Select...',
  searchable = false,
  disabled = false,
  required = false,
  error,
  helperText,
  className = '',
  ...props
}, ref) => {
  // ... 实现代码（包含搜索、键盘导航、智能定位等功能）
});
```

**关键点**：
- ✅ 继承 `LabeledComponentProps`
- ✅ 使用 `ValueChangeCallback` 类型（而非直接的函数类型）
- ✅ 支持搜索功能
- ✅ 键盘导航支持
- ✅ 智能下拉定位（根据viewport空间自动向上或向下）
- ✅ 完整的可访问性支持

### 案例4: ConfirmDialog组件（完整实现）

**文件**: `/frontend/src/shared/ui/ConfirmDialog/ConfirmDialog.tsx`

```typescript
interface ConfirmDialogProps {
  /** 对话框是否打开 */
  open: boolean;
  /** 对话框标题 */
  title: string;
  /** 对话框消息内容 */
  message: string;
  /** 确认按钮文本，默认为"确认" */
  confirmText?: string;
  /** 取消按钮文本，默认为"取消" */
  cancelText?: string;
  /** 对话框变体类型，默认为"primary" */
  variant?: 'danger' | 'warning' | 'info' | 'primary';
  /** 确认按钮回调函数 */
  onConfirm: () => void;
  /** 取消按钮回调函数 */
  onCancel: () => void;
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmText = '确认',
  cancelText = '取消',
  variant = 'primary',
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  // ... 实现代码（包含ESC键支持、点击遮罩关闭等）
}
```

**关键点**：
- ✅ 简洁的Props接口
- ✅ 提供默认值
- ✅ 支持多种变体
- ✅ 生命周期管理（锁定body滚动）
- ✅ 键盘交互支持（ESC关闭）

---

## 9. 最佳实践检查清单

### 9.1 Props设计检查清单

**基础规范**：
- [ ] 所有Props都有明确的JSDoc注释
- [ ] 使用 `interface` 而非 `type` 定义Props（除非需要联合类型）
- [ ] 必需属性放在前面，可选属性放在后面
- [ ] 相关属性分组在一起

**类型安全**：
- [ ] 避免使用 `any`，使用泛型或具体类型
- [ ] 使用 `Omit` 排除原生HTML元素的冲突属性
- [ ] 使用 `Pick` 和 `Partial` 组合现有类型
- [ ] 为回调函数提供明确的类型签名

**可复用性**：
- [ ] 继承 `BaseComponentProps` 获取通用属性
- [ ] 继承 `LabeledComponentProps` 支持标签
- [ ] 继承 `SelectableComponentProps` 支持值选择
- [ ] 提取可复用的类型到 `@/types/common`

**扩展性**：
- [ ] 使用 `...props` 传递未知属性到DOM元素
- [ ] 使用 `React.forwardRef` 支持ref转发
- [ ] 避免过度使用索引签名（`[key: string]: unknown`）
- [ ] 提供合理的默认值

**可访问性**：
- [ ] 支持所有标准ARIA属性
- [ ] 提供 `data-testid` 用于测试
- [ ] 支持键盘导航
- [ ] 提供有意义的错误消息

### 9.2 命名规范

**Props命名**：
- ✅ 使用 `camelCase` 命名（`onChange` 而非 `on_change`）
- ✅ 事件处理器以 `on` 开头（`onClick`、`onSubmit`）
- ✅ 布尔值使用 `is`、`has`、`should` 前缀（`isLoading`、`hasError`）
- ✅ 回调函数使用 `Handle` 后缀（`onClickHandle`）或直接使用动词（`onChange`）

**类型命名**：
- ✅ Props接口以 `Props` 结尾（`ButtonProps`、`InputProps`）
- ✅ 回调类型以 `Callback` 或 `Handler` 结尾（`ClickCallback`、`MouseEventHandler`）
- ✅ 联合类型使用描述性名称（`ButtonVariant`、`Size`）

### 9.3 性能优化

**使用React.memo**：
```typescript
const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
  // 自定义比较函数
  return prevProps.value === nextProps.value &&
         prevProps.onChange === nextProps.onChange;
});
```

**使用useCallback包装回调**：
```typescript
const handleClick = useCallback((event: MouseEvent) => {
  // 处理点击
}, [/* 依赖项 */]);
```

**避免在Props中传递新对象**：
```typescript
// ❌ 错误：每次渲染都创建新对象
<Component style={{ color: 'red' }} />

// ✅ 正确：使用useMemo或常量
const style = { color: 'red' };
<Component style={style} />
```

### 9.4 文档规范

**JSDoc注释模板**：

```typescript
/**
 * ComponentName - 简短描述
 *
 * 详细描述组件的用途、特性和使用场景。
 * 可以包含多行说明。
 *
 * @example
 * // 简单示例
 * <ComponentName prop="value" />
 *
 * @example
 * // 复杂示例
 * <ComponentName
 *   prop1="value1"
 *   prop2={false}
 *   onEvent={() => console.log('event')}
 * />
 */
export interface ComponentNameProps {
  /** 属性描述 */
  propName?: string;
  /** 另一个属性描述 */
  anotherProp?: number;
}
```

---

## 10. 常见陷阱和解决方案

### 陷阱1: 过度使用索引签名

**问题**：
```typescript
// ❌ 错误：失去类型安全
interface Props {
  [key: string]: unknown;
  name: string; // 这个声明会被索引签名覆盖
}
```

**解决方案**：
```typescript
// ✅ 正确：使用精确的类型
interface Props {
  name: string;
  className?: string;
  // 只在真正需要时添加索引签名
  [key: string]: unknown;
}
```

### 陷阱2: 忘记排除原生属性

**问题**：
```typescript
// ❌ 错误：类型冲突
interface ButtonProps extends React.ComponentPropsWithoutRef<'button'> {
  size?: 'sm' | 'md' | 'lg'; // 与原生button的size属性冲突
}
```

**解决方案**：
```typescript
// ✅ 正确：排除冲突属性
interface ButtonProps extends
  Omit<React.ComponentPropsWithoutRef<'button'>, 'size'> {
  size?: 'sm' | 'md' | 'lg';
}
```

### 陷阱3: 不支持ref转发

**问题**：
```typescript
// ❌ 错误：无法使用ref
function Button({ children, onClick }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>;
}

// 使用时ref无法工作
const ref = useRef<HTMLButtonElement>();
<Button ref={ref} /> // TypeScript错误！
```

**解决方案**：
```typescript
// ✅ 正确：使用forwardRef
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  children,
  onClick
}, ref) => {
  return <button ref={ref} onClick={onClick}>{children}</button>;
});
```

### 陷阱4: 不提供默认值

**问题**：
```typescript
// ❌ 错误：使用时需要显式传递所有可选属性
<Button size={undefined} variant={undefined} />
```

**解决方案**：
```typescript
// ✅ 正确：在组件内部提供默认值
const Button = ({
  size = 'md',
  variant = 'primary',
  ...props
}: ButtonProps) => {
  // ...
};
```

---

## 11. 工具和资源

### 11.1 类型工具库

项目已包含的实用类型（`@/types/common`）：

```typescript
// 部分类型
import type {
  BaseComponentProps,
  LabeledComponentProps,
  SelectableComponentProps,
  ValueChangeCallback,
  EventHandler,
  AsyncFunction,
  // ... 更多类型
} from '@/types/common';
```

### 11.2 推荐工具

- **TypeScript**: 类型检查
- **ESLint**: 代码规范检查
- **Prettier**: 代码格式化
- **@typescript-eslint**: TypeScript特定规则

### 11.3 相关文档

- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Event2Table前端开发规范](/Users/mckenzie/Documents/event2table/docs/development/frontend-development.md)

---

## 12. 总结

### 核心原则

1. **类型安全优先**: 使用TypeScript的完整类型系统
2. **可组合性**: 通过继承和组合复用Props类型
3. **扩展性**: 设计易于扩展的Props接口
4. **可访问性**: 支持ARIA和键盘导航
5. **性能优化**: 使用React.memo和useCallback优化性能

### 快速参考

| 模式 | 适用场景 | 导入来源 |
|------|----------|----------|
| `BaseComponentProps` | 所有组件 | `@/types/common` |
| `LabeledComponentProps` | 表单组件（Input、Select） | `@/types/common` |
| `SelectableComponentProps` | 需要值选择的组件 | `@/types/common` |
| `ValueChangeCallback<T>` | 值变更回调 | `@/types/common` |
| `EventHandler<T>` | 事件处理器 | `@/types/common` |
| `Omit<Props, 'key'>` | 排除冲突属性 | TypeScript内置 |
| `Partial<Props>` | 所有属性可选 | TypeScript内置 |

### 实际案例统计

本文档包含 **4个完整案例**：
1. ✅ Button组件 - 基础组件模式
2. ✅ Input组件 - 标签组件模式
3. ✅ Select组件 - 可选择组件模式
4. ✅ ConfirmDialog组件 - 简洁Props模式

---

**文档维护**: 本文档应随着项目组件库的发展持续更新。

**反馈**: 如果发现任何问题或有改进建议，请更新本文档或联系开发团队。

**最后更新**: 2026-03-01
**版本**: 1.0.0
