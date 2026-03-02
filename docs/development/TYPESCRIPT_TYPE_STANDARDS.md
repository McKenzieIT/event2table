# TypeScript 类型规范文档

> **版本**: 1.0.0
> **最后更新**: 2026-03-01
> **适用范围**: Event2Table 前端项目

---

## 目录

1. [类型定义基础规范](#1-类型定义基础规范)
2. [组件Props定义规范](#2-组件props定义规范)
3. [API类型定义规范](#3-api类型定义规范)
4. [类型复用规范](#4-类型复用规范)
5. [泛型使用指南](#5-泛型使用指南)
6. [类型安全最佳实践](#6-类型安全最佳实践)
7. [常见模式与反模式](#7-常见模式与反模式)
8. [迁移指南](#8-迁移指南)
9. [检查清单](#9-检查清单)

---

## 1. 类型定义基础规范

### 1.1 命名约定

#### Interface vs Type 的使用原则

**✅ 使用 `interface` 的场景**：
- 定义对象结构（组件Props、API响应、数据模型）
- 需要扩展（extends）其他类型
- 需要实现（implements）某个契约

**✅ 使用 `type` 的场景**：
- 定义联合类型（Union Types）
- 定义交叉类型（Intersection Types）
- 定义工具类型（Utility Types）
- 定义原始类型别名（Primitive Aliases）

#### 示例对比

```typescript
// ✅ 正确：使用 interface 定义对象结构
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  onClick?: (event: MouseEvent) => void;
  children?: ReactNode;
}

// ✅ 正确：使用 type 定义联合类型
type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';
type Status = 'idle' | 'loading' | 'success' | 'error';

// ✅ 正确：使用 type 定义工具类型
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// ✅ 正确：interface 可以扩展
interface ButtonProps extends BaseComponentProps {
  variant?: Variant;
  onClick?: MouseEventHandler;
}

// ✅ 正确：type 也可以交叉
type ButtonPropsWithRef = ButtonProps & { ref?: Ref<HTMLButtonElement> };

// ❌ 错误：使用 type 定义可扩展的对象结构
type ButtonProps = {
  variant?: string;
  onClick?: (event: MouseEvent) => void;
};
// 原因：失去扩展能力和声明合并能力
```

#### 命名规范

```typescript
// ✅ Interface: PascalCase
interface ButtonProps {}
interface GameContext {}
interface ApiResponse {}

// ✅ Type: PascalCase
type Variant = 'primary' | 'secondary';
type Status = 'idle' | 'loading';

// ✅ 泛型参数: T (Type), K (Key), P (Props), E (Element)
interface ApiResponse<T> {}
type PartialBy<T, K> = Omit<T, K>;

// ✅ 回调函数类型: EventHandler 后缀
type MouseEventHandler = (event: MouseEvent) => void;
type ChangeEventHandler = (event: ChangeEvent) => void;

// ✅ 组件Props: Props 后缀
interface ButtonProps {}
interface InputProps {}

// ❌ 错误：不一致的命名
interface button_Props {}
type variant = 'primary' | 'secondary';
```

### 1.2 导入/导出规范

#### 类型导入（Type-only Imports）

**✅ 推荐模式**：

```typescript
// ✅ 正确：使用 type 关键字导入类型
import type { ReactNode, MouseEvent } from 'react';
import type { ButtonProps } from './Button';
import type { GameContext } from '@/types/common';

// ✅ 正确：混合导入（类型和值）
import { React, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { Button } from './Button';
import type { ButtonProps } from './Button';

// ❌ 错误：不区分类型和值导入
import { ReactNode, MouseEvent } from 'react';
// 原因：ReactNode 是类型，不能在运行时使用
```

#### 导出规范

```typescript
// ✅ 正确：直接导出类型定义
export interface ButtonProps {}
export type Variant = 'primary' | 'secondary';

// ✅ 正确：先定义后导出（便于文档注释）
interface ButtonProps {
  /** Button variant */
  variant?: Variant;
}
export { ButtonProps };

// ✅ 正确：导出类型别名
export type { ButtonProps };
export type { Variant, Size };

// ❌ 错误：default export 类型
// types.ts
export default interface ButtonProps {}  // 不推荐

// Button.tsx
import ButtonProps from './types';  // 不清晰
```

### 1.3 类型文件组织

```
frontend/src/
├── types/
│   ├── common.ts           # 共享类型定义（30+类型）
│   ├── api.ts              # API相关类型
│   ├── components.ts       # 组件通用类型
│   └── utils.ts            # 工具类型
├── shared/
│   ├── ui/
│   │   ├── Button/
│   │   │   ├── Button.tsx          # 组件实现
│   │   │   ├── Button.test.tsx     # 组件测试
│   │   │   └── Button.types.ts     # 组件特定类型（可选）
│   │   └── Input/
│   │       ├── Input.tsx
│   │       ├── Input.type-test.tsx  # 类型测试
│   │       └── Input.css
│   └── api/
│       ├── client.ts
│       └── types.ts          # API类型定义
```

**类型定义放置原则**：
- ✅ **通用类型** → `src/types/common.ts`
- ✅ **组件特定类型** → 组件文件内或组件文件夹的 `types.ts`
- ✅ **API类型** → `src/shared/api/types.ts`
- ✅ **业务领域类型** → `src/types/{domain}.ts`

---

## 2. 组件Props定义规范

### 2.1 基础Props模式

#### 标准组件Props结构

```typescript
/**
 * Button组件Props
 *
 * @example
 * ```tsx
 * <Button variant="primary" onClick={handleClick}>
 *   Click Me
 * </Button>
 * ```
 */
export interface ButtonProps
  extends Omit<React.ComponentPropsWithoutRef<'button'>, 'size' | 'onClick'>,
    BaseComponentProps {
  /** Button variant */
  variant?: Variant;
  /** Button size */
  size?: Size;
  /** Click handler */
  onClick?: MouseEventHandler;
  /** Button content */
  children?: ReactNode;
}
```

#### Props继承层次

```
React.ComponentPropsWithoutRef<'button'>  (原生HTML属性)
    ↓
BaseComponentProps                         (基础组件属性)
    ↓
ButtonProps                                (组件特定属性)
```

**关键要点**：
1. **继承原生属性**：使用 `React.ComponentPropsWithoutRef` 或 `React.ComponentProps`
2. **排除冲突属性**：使用 `Omit<T, 'prop1' | 'prop2'>`
3. **复用基础Props**：继承 `BaseComponentProps`, `LabeledComponentProps`
4. **添加特定属性**：在扩展后添加组件特有属性

### 2.2 组件Props示例

#### Input组件（完整示例）

```typescript
import type {
  LabeledComponentProps,
  ChangeEventHandler,
  FocusEventHandler,
} from '@/types/common';

export interface InputProps
  extends Omit<React.ComponentPropsWithoutRef<'input'>, 'size' | 'onChange'>,
    LabeledComponentProps {
  /** Input type */
  type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url' | 'search' | 'date' | 'time';
  /** Current value */
  value?: string | number;
  /** Change handler */
  onChange?: ChangeEventHandler<HTMLInputElement>;
  /** Blur handler */
  onBlur?: FocusEventHandler;
  /** Focus handler */
  onFocus?: FocusEventHandler;
  /** Icon component */
  icon?: React.ComponentType<{ className?: string }>;
  /** Helper text */
  helperText?: string;
  /** Error message */
  error?: string;
}
```

#### Select组件（完整示例）

```typescript
import type {
  SelectOption,
  LabeledComponentProps,
  ValueChangeCallback,
} from '@/types/common';

export interface SelectProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange' | 'value'>,
    LabeledComponentProps {
  /** Options array */
  options?: SelectOption[];
  /** Current value */
  value?: string | number;
  /** Value change callback */
  onChange?: ValueChangeCallback<string | number>;
  /** Placeholder text */
  placeholder?: string;
  /** Enable search */
  searchable?: boolean;
  /** Disable select */
  disabled?: boolean;
}
```

#### Modal组件（完整示例）

```typescript
export interface ModalProps extends BaseComponentProps {
  /** Modal title */
  title?: string;
  /** Is modal open */
  isOpen: boolean;
  /** Close handler */
  onClose: () => void;
  /** Modal size */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Show close button */
  showCloseButton?: boolean;
  /** Close on overlay click */
  closeOnOverlayClick?: boolean;
  /** Close on ESC key */
  closeOnEsc?: boolean;
  /** Modal content */
  children: ReactNode;
}
```

### 2.3 Props文档注释规范

```typescript
/**
 * Button组件Props
 *
 * @description
 * 支持多种变体的按钮组件，具有cyberpunk风格的视觉效果。
 *
 * @example
 * ```tsx
 * // Primary button
 * <Button variant="primary">Click Me</Button>
 *
 * // Disabled button
 * <Button disabled>Processing...</Button>
 *
 * // With icon
 * <Button icon={SearchIcon}>Search</Button>
 * ```
 */
export interface ButtonProps extends BaseComponentProps {
  /**
   * Button variant
   * @default 'primary'
   */
  variant?: Variant;

  /**
   * Button size
   * @default 'md'
   */
  size?: Size;

  /**
   * Click event handler
   */
  onClick?: MouseEventHandler;

  /**
   * Button content (text or other components)
   */
  children?: ReactNode;

  /**
   * Icon component to display
   */
  icon?: IconComponent;

  /**
   * Loading state (shows spinner and disables button)
   * @default false
   */
  loading?: boolean;
}
```

### 2.4 Props扩展模式

#### 使用泛型创建可复用Props

```typescript
// ✅ 正确：泛型组件Props
interface SelectProps<T = string | number> {
  value?: T;
  options?: SelectOption<T>[];
  onChange?: (value: T) => void;
}

// 使用
const StringSelect: React.FC<SelectProps<string>> = (props) => { /* ... */ };
const NumberSelect: React.FC<SelectProps<number>> = (props) => { /* ... */ };

// ✅ 正确：多泛型组件Props
interface TableProps<TData, TFilters> {
  data: TData[];
  filters?: TFilters;
  onFilterChange?: (filters: TFilters) => void;
}

// 使用
interface User { id: number; name: string; }
interface UserFilters { name?: string; active?: boolean; }

const UserTable: React.FC<TableProps<User, UserFilters>> = (props) => { /* ... */ };
```

#### 条件类型Props

```typescript
// ✅ 正确：根据variant改变props类型
type ButtonProps = {
  variant: 'primary' | 'secondary';
  children: ReactNode;
} & (
  | { isLoading: true; loadingText?: string }
  | { isLoading?: false; loadingText?: never }
);

// 使用
<Button variant="primary" isLoading loadingText="Processing..." />  // ✅
<Button variant="primary" isLoading={false} loadingText="Error" />  // ❌ Type error
```

---

## 3. API类型定义规范

### 3.1 API响应类型

#### 标准API响应格式

```typescript
/**
 * 标准API响应格式
 * @template T - 响应数据类型
 */
export interface ApiResponse<T = unknown> {
  /** 请求是否成功 */
  success: boolean;
  /** 响应数据 */
  data?: T;
  /** 错误信息 */
  error?: string;
  /** 提示消息 */
  message?: string;
  /** 时间戳 */
  timestamp?: string;
}

/**
 * 成功响应类型（Type Guard友好）
 */
export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  message?: string;
  timestamp: string;
}

/**
 * 错误响应类型
 */
export interface ApiErrorResponse {
  success: false;
  error: string;
  error_type?: string;
  details?: Record<string, string>;
  timestamp: string;
}

/**
 * 联合响应类型
 */
export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;
```

#### 分页响应类型

```typescript
/**
 * 分页响应格式
 * @template T - 列表项类型
 */
export interface PaginatedApiResponse<T = unknown> extends ApiResponse<T[]> {
  /** 分页信息 */
  pagination?: {
    /** 当前页码 */
    page: number;
    /** 每页数量 */
    page_size: number;
    /** 总记录数 */
    total: number;
    /** 总页数 */
    total_pages: number;
    /** 是否有下一页 */
    has_next: boolean;
    /** 是否有上一页 */
    has_prev: boolean;
  };
}

// 使用示例
interface Game {
  gid: number;
  name: string;
  ods_db: string;
}

type GamesListResponse = PaginatedApiResponse<Game>;
```

### 3.2 API请求类型

#### 请求参数类型

```typescript
/**
 * 分页参数
 */
export interface PaginationParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * 筛选参数基类
 */
export interface FilterParams {
  /** 搜索关键词 */
  search?: string;
  /** 状态筛选 */
  status?: string;
  /** 日期范围 */
  date_from?: string;
  date_to?: string;
}

/**
 * 游戏列表请求参数
 */
export interface GamesListParams extends PaginationParams, FilterParams {
  /** ODS数据库筛选 */
  ods_db?: string;
  /** 是否包含事件数量 */
  include_event_count?: boolean;
}
```

#### 请求配置类型

```typescript
/**
 * API请求配置
 */
export interface ApiRequestOptions extends RequestInit {
  /** 自动解析JSON响应 */
  parseJson?: boolean;
  /** 错误时抛出FetchError */
  throwOnError?: boolean;
  /** 请求超时(毫秒) */
  timeout?: number;
  /** 请求唯一标识(用于缓存) */
  cacheKey?: string;
}

/**
 * API客户端配置
 */
export interface ApiClientConfig {
  /** 基础URL */
  baseURL?: string;
  /** 默认请求头 */
  headers?: Record<string, string>;
  /** 默认超时时间(毫秒) */
  timeout?: number;
  /** 调试模式 */
  debug?: boolean;
  /** 请求拦截器 */
  requestInterceptor?: (config: ApiRequestOptions) => ApiRequestOptions;
  /** 响应拦截器 */
  responseInterceptor?: (response: Response) => Response;
}
```

### 3.3 API错误类型

```typescript
/**
 * Fetch错误类
 */
export class FetchError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'FetchError';
  }

  /**
   * 从Response创建FetchError
   */
  static async fromResponse(response: Response): Promise<FetchError> {
    let data: unknown = null;

    try {
      data = await response.json();
    } catch {
      // Response不是JSON或为空
    }

    return new FetchError(
      `HTTP ${response.status}`,
      response.status,
      data
    );
  }

  /** 是否验证错误 (400, 422) */
  isValidation(): boolean {
    return this.status === 400 || this.status === 422;
  }

  /** 是否未找到 (404) */
  isNotFound(): boolean {
    return this.status === 404;
  }

  /** 是否冲突 (409) */
  isConflict(): boolean {
    return this.status === 409;
  }

  /** 是否服务器错误 (5xx) */
  isServerError(): boolean {
    return this.status >= 500;
  }

  /** 是否网络错误 (0) */
  isNetworkError(): boolean {
    return this.status === 0;
  }
}
```

### 3.4 完整API类型示例

```typescript
// types/api/games.ts

/**
 * 游戏实体
 */
export interface Game {
  /** 数据库自增ID */
  id: number;
  /** 游戏业务GID */
  gid: number;
  /** 游戏名称 */
  name: string;
  /** ODS数据库名称 */
  ods_db: string;
  /** 游戏描述 */
  description?: string;
  /** DWD表前缀 */
  dwd_prefix?: string;
  /** 创建时间 */
  created_at: string;
  /** 更新时间 */
  updated_at: string;
  /** 事件数量统计 */
  event_count?: number;
}

/**
 * 创建游戏请求
 */
export interface CreateGameRequest {
  /** 游戏GID (必填) */
  gid: number;
  /** 游戏名称 (必填) */
  name: string;
  /** ODS数据库 (必填) */
  ods_db: 'ieu_ods' | 'overseas_ods';
  /** 游戏描述 */
  description?: string;
  /** DWD表前缀 */
  dwd_prefix?: string;
}

/**
 * 更新游戏请求
 */
export type UpdateGameRequest = PartialBy<CreateGameRequest, 'gid' | 'name' | 'ods_db'>;

/**
 * 游戏列表响应
 */
export type GamesListResponse = ApiResponse<Game[]>;

/**
 * 游戏详情响应
 */
export type GameDetailResponse = ApiResponse<Game>;

/**
 * 创建游戏响应
 */
export type CreateGameResponse = ApiResponse<{ game_id: number }>;

/**
 * API端点映射
 */
export const GameApiEndpoints = {
  list: '/api/games',
  detail: (gid: number) => `/api/games/${gid}`,
  create: '/api/games',
  update: (gid: number) => `/api/games/${gid}`,
  delete: (gid: number) => `/api/games/${gid}`,
} as const;
```

---

## 4. 类型复用规范

### 4.1 共享类型定义

#### 何时定义共享类型

**✅ 定义共享类型的场景**：
- 3个或以上组件使用相同类型
- 跨模块使用的类型（API、组件、工具函数）
- 核心业务领域类型（Game, Event, Parameter）

**❌ 不定义共享类型的场景**：
- 仅1个组件使用的类型
- 特定UI组件的内部类型
- 临时使用的类型

#### 共享类型示例

```typescript
// ✅ 正确：定义在 src/types/common.ts

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
}

/**
 * 带标签的组件Props
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

/**
 * 可选择组件Props
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

// 组件中使用
export interface InputProps extends LabeledComponentProps { /* ... */ }
export interface SelectProps extends LabeledComponentProps { /* ... */ }
export interface CheckboxProps extends LabeledComponentProps { /* ... */ }
```

### 4.2 类型组合模式

#### 使用交叉类型（Intersection Types）

```typescript
// ✅ 正确：组合多个类型
type ButtonWithIcon = ButtonProps & { icon: IconComponent };
type ButtonWithLoading = ButtonProps & { loading: boolean };
type CompleteButton = ButtonWithIcon & ButtonWithLoading;

// ✅ 正确：使用 & 添加必需属性
type RequiredButtonProps = ButtonProps & {
  onClick: MouseEventHandler;  // 必需
  children: ReactNode;         // 必需
};

// 使用
const PrimaryButton: React.FC<RequiredButtonProps> = ({ onClick, children, ...props }) => {
  return <button onClick={onClick} {...props}>{children}</button>;
};
```

#### 使用Omit和Pick

```typescript
// ✅ 正确：排除某些属性
type InputWithoutLabel = Omit<InputProps, 'label' | 'helperText'>;

// ✅ 正确：仅保留某些属性
type InputLabelOnly = Pick<InputProps, 'label' | 'required' | 'error'>;

// ✅ 正确：组合Omit和Pick
type InputWithCustomLabel = Omit<InputProps, 'label'> & Pick<InputProps, 'label'>;

// ✅ 正确：排除后添加新属性
type ButtonWithoutOnClick = Omit<ButtonProps, 'onClick'> & {
  handleClick: () => void;  // 重命名onClick
};
```

#### 使用Partial和Required

```typescript
// ✅ 正确：所有属性变为可选
type PartialGame = Partial<Game>;

// ✅ 正确：指定属性变为可选
type GameUpdate = PartialBy<Game, 'name' | 'description'>;

// ✅ 正确：所有属性变为必需
type RequiredGame = Required<Partial<Game>>;

// ✅ 正确：指定属性变为必需
type GameCreate = RequiredBy<Partial<Game>, 'gid' | 'name' | 'ods_db'>;

// 使用示例
const createGame = (data: GameCreate) => { /* ... */ };
createGame({ gid: 10000147, name: 'STAR001', ods_db: 'ieu_ods' }); // ✅
createGame({ gid: 10000147, name: 'STAR001' }); // ❌ 缺少ods_db
```

### 4.3 类型复用最佳实践

#### 避免重复定义

```typescript
// ❌ 错误：重复定义相同类型
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
}

interface InputProps {
  size?: 'sm' | 'md' | 'lg';  // 重复
  disabled?: boolean;          // 重复
}

// ✅ 正确：复用共享类型
interface ButtonProps extends BaseComponentProps {
  variant?: Variant;
  size?: Size;
}

interface InputProps extends BaseComponentProps {
  type?: string;
  value?: string;
}
```

#### 使用类型推导

```typescript
// ✅ 正确：从数组推导类型
const games = [
  { gid: 10000147, name: 'STAR001', ods_db: 'ieu_ods' },
  { gid: 10000148, name: 'STAR002', ods_db: 'ieu_ods' },
] as const;

type Game = typeof games[number];
// 等价于: type Game = { gid: number; name: string; ods_db: string; }

// ✅ 正确：从对象推导类型
const config = {
  apiUrl: 'http://localhost:5001',
  timeout: 30000,
  retries: 3,
} as const;

type Config = typeof config;
// 等价于: type Config = { readonly apiUrl: string; readonly timeout: number; readonly retries: number; }

// ✅ 正确：从函数返回值推导类型
function fetchGame(gid: number) {
  return fetch(`/api/games/${gid}`).then(r => r.json());
}

type GameResponse = Awaited<ReturnType<typeof fetchGame>>;
```

---

## 5. 泛型使用指南

### 5.1 函数泛型

#### 基础泛型函数

```typescript
// ✅ 正确：简单的泛型函数
function identity<T>(value: T): T {
  return value;
}

// 使用
const num = identity<number>(42);
const str = identity('hello');

// ✅ 正确：类型推导（更简洁）
const num = identity(42);      // T推导为number
const str = identity('hello'); // T推导为string
```

#### 多泛型参数

```typescript
// ✅ 正确：多个泛型参数
function pair<T, U>(first: T, second: U): [T, U] {
  return [first, second];
}

// 使用
const p1 = pair(1, 'hello');           // [number, string]
const p2 = pair('id', { id: 1 });      // [string, { id: number }]
```

#### 泛型约束

```typescript
// ✅ 正确：约束泛型必须有特定属性
function logLength<T extends { length: number }>(value: T): void {
  console.log(value.length);
}

// 使用
logLength('hello');       // ✅ string有length
logLength([1, 2, 3]);     // ✅ array有length
logLength({ length: 5 }); // ✅ 对象有length
logLength(42);            // ❌ number没有length

// ✅ 正确：约束泛型必须是函数类型
type AsyncCallback = (...args: unknown[]) => void;

function setTimeout<T extends AsyncCallback>(callback: T, ms: number): void {
  setTimeout(() => callback(...([] as unknown[])), ms);
}
```

### 5.2 组件泛型

#### 泛型组件Props

```typescript
// ✅ 正确：泛型组件
interface SelectProps<T = string | number> {
  value?: T;
  options?: SelectOption<T>[];
  onChange?: (value: T) => void;
}

function Select<T extends string | number = string>(props: SelectProps<T>) {
  // 组件实现
  return null;
}

// 使用
<Select<string> value="en" options={langOptions} />
<Select<number> value={1} options={numberOptions} />
```

#### 使用as const断言

```typescript
// ✅ 正确：使用as const创建泛型组件工厂
function createTable<T extends Record<string, unknown>>() {
  return function TableComponent(props: { data: T[] }) {
    return <table>{/* 渲染表格 */}</table>;
  };
}

// 使用
type User = { id: number; name: string; };
const UserTable = createTable<User>();

<UserTable data={users} />
```

### 5.3 工具类型使用

#### TypeScript内置工具类型

```typescript
// ✅ Partial - 所有属性变为可选
type PartialGame = Partial<Game>;

// ✅ Required - 所有属性变为必需
type RequiredGame = Required<Partial<Game>>;

// ✅ Readonly - 所有属性变为只读
type ReadonlyGame = Readonly<Game>;

// ✅ Pick - 仅保留指定属性
type GameBasic = Pick<Game, 'gid' | 'name'>;

// ✅ Omit - 排除指定属性
type GameWithoutTimestamps = Omit<Game, 'created_at' | 'updated_at'>;

// ✅ Record - 创建对象类型
type GamesByGid = Record<number, Game>;

// ✅ Exclude - 从联合类型排除
type Variant = 'primary' | 'secondary' | 'ghost';
type NonGhostVariant = Exclude<Variant, 'ghost'>;

// ✅ Extract - 提取联合类型的部分
type StringOrNumber = string | number | boolean;
type StringOrNumberOnly = Extract<StringOrNumber, string | number>;

// ✅ NonNullable - 排除null和undefined
type NonNullableString = NonNullable<string | null | undefined>;

// ✅ ReturnType - 获取函数返回值类型
function fetchGame(): Promise<Game> {
  return Promise.resolve({} as Game);
}
type GamePromise = ReturnType<typeof fetchGame>; // Promise<Game>

// ✅ Parameters - 获取函数参数类型
type FetchGameParams = Parameters<typeof fetchGame>; // []

// ✅ Awaited - 获取Promise的resolve类型
type GameData = Awaited<Promise<Game>>; // Game
```

#### 自定义工具类型

```typescript
// ✅ 指定属性变为可选
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// ✅ 指定属性变为必需
export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

// ✅ 指定属性变为只读
export type ReadonlyBy<T, K extends keyof T> = Omit<T, K> & Readonly<Pick<T, K>>;

// ✅ 指定属性变为可写
export type WritableBy<T, K extends keyof T> = Omit<T, K> & { [P in K]-?: T[P] };

// 使用示例
interface User {
  id: number;
  name: string;
  email: string;
  createdAt: string;
}

type UserUpdate = PartialBy<User, 'name' | 'email'>;
// { id: number; name?: string; email?: string; createdAt: string; }

type UserCreate = RequiredBy<Partial<User>, 'name' | 'email'>;
// { id?: number; name: string; email: string; createdAt?: string; }
```

---

## 6. 类型安全最佳实践

### 6.1 避免any的使用

#### ❌ 错误使用any的场景

```typescript
// ❌ 错误：使用any失去类型检查
function processData(data: any) {
  return data.map((item: any) => item.value);  // 无类型检查
}

// ✅ 正确：使用泛型保留类型信息
function processData<T extends { value: unknown }>(data: T[]): T['value'][] {
  return data.map(item => item.value as T['value']);
}

// ✅ 更好：明确类型定义
interface DataItem {
  id: string;
  value: number;
}

function processData(data: DataItem[]): number[] {
  return data.map(item => item.value);
}
```

#### 使用unknown代替any

```typescript
// ❌ 错误：any不安全
function parseJSON(json: string): any {
  return JSON.parse(json);
}
const result = parseJSON('{"name": "test"}');
result.foo.bar;  // 运行时错误，但编译时不报错

// ✅ 正确：unknown安全
function parseJSON(json: string): unknown {
  return JSON.parse(json);
}
const result = parseJSON('{"name": "test"}');

if (typeof result === 'object' && result !== null && 'name' in result) {
  console.log(result.name);  // ✅ 类型安全
}
```

#### 类型守卫（Type Guards）

```typescript
// ✅ 正确：定义类型守卫
function isGame(value: unknown): value is Game {
  return (
    typeof value === 'object' &&
    value !== null &&
    'gid' in value &&
    'name' in value &&
    'ods_db' in value
  );
}

// 使用
function processGame(data: unknown) {
  if (isGame(data)) {
    console.log(data.name);  // ✅ TypeScript知道data是Game
  } else {
    console.log('Invalid game data');
  }
}

// ✅ 正确：使用类型谓词
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number';
}

function processValue(value: unknown) {
  if (isString(value)) {
    console.log(value.toUpperCase());  // ✅ string方法可用
  } else if (isNumber(value)) {
    console.log(value.toFixed(2));     // ✅ number方法可用
  }
}
```

### 6.2 类型断言 vs 类型守卫

#### 类型断言（Type Assertion）

```typescript
// ⚠️ 谨慎使用：类型断言绕过类型检查
const game = unknownValue as Game;
const game = <Game>unknownValue;

// ✅ 安全场景：API响应已知结构
interface ApiResponse {
  success: boolean;
  data: unknown;
}

const response = await fetch('/api/games');
const json = await response.json() as ApiResponse;
if (json.success && isGame(json.data)) {
  // ...
}
```

#### 类型守卫（推荐）

```typescript
// ✅ 推荐：类型守卫运行时验证
function isGame(value: unknown): value is Game {
  return (
    typeof value === 'object' &&
    value !== null &&
    'gid' in value &&
    'name' in value &&
    'ods_db' in value
  );
}

const value = JSON.parse(jsonString);
if (isGame(value)) {
  console.log(value.name);  // ✅ 类型安全
}
```

#### 断言函数（Assertion Functions）

```typescript
// ✅ 断言函数：不符合条件时抛出错误
function assertIsGame(value: unknown): asserts value is Game {
  if (
    typeof value !== 'object' ||
    value === null ||
    !('gid' in value) ||
    !('name' in value) ||
    !('ods_db' in value)
  ) {
    throw new Error('Value is not a Game');
  }
}

// 使用
function processGame(data: unknown) {
  assertIsGame(data);  // 如果data不是Game，抛出错误
  console.log(data.name);  // ✅ 后续代码知道data是Game
}
```

### 6.3 可选链和空值合并

#### 可选链（Optional Chaining）

```typescript
// ✅ 正确：使用可选链避免运行时错误
const game = games?.find(g => g.gid === 10000147);
const name = game?.name ?? 'Unknown';

// ❌ 错误：不安全的嵌套访问
const name = games.find(g => g.gid === 10000147).name;  // 可能undefined
const db = game.ods_db.toLowerCase();  // 运行时错误

// ✅ 正确：使用可选链
const db = game?.ods_db?.toLowerCase() ?? 'default';

// ✅ 正确：可选方法调用
const result = data?.map?.(item => item.value);

// ✅ 正确：可选数组访问
const first = items?.[0];
```

#### 空值合并（Nullish Coalescing）

```typescript
// ✅ 正确：使用 ?? 处理null/undefined
const name = game?.name ?? 'Unknown';
const count = event?.count ?? 0;

// ❌ 错误：使用 || 处理falsy值
const count = event?.count || 0;  // 如果count是0，会被替换

// ✅ 正确：区分null/undefined和falsy值
const displayCount = count ?? 0;  // 只有null/undefined才替换
const displayEnabled = enabled ?? true;  // 保留false值
```

#### 结合使用

```typescript
// ✅ 正确：可选链 + 空值合并
const displayName = game?.name?.trim() ?? 'Unnamed Game';
const apiEndpoint = config?.apiUrl ?? 'http://localhost:5001';
const timeout = config?.timeout ?? 30000;

// ✅ 正确：复杂嵌套
const dbPath = game?.ods_db?.toLowerCase()?.replace('_', '-') ?? 'default';

// ✅ 正确：函数调用
const result = callback?.(data) ?? defaultResult;
```

### 6.4 严格模式配置

#### 渐进式启用严格模式

```json
// tsconfig.json
{
  "compilerOptions": {
    // 阶段1: 启用noImplicitAny
    "noImplicitAny": true,

    // 阶段2: 启用strictNullChecks
    "strictNullChecks": true,

    // 阶段3: 启用完整strict模式
    "strict": true,

    // 阶段4: 启用额外检查
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
```

---

## 7. 常见模式与反模式

### 7.1 Props定义模式

#### ✅ 正确模式

```typescript
// ✅ 正确：扩展基础Props，排除冲突
export interface ButtonProps
  extends Omit<React.ComponentPropsWithoutRef<'button'>, 'size'>,
    BaseComponentProps {
  variant?: Variant;
  size?: Size;
  onClick?: MouseEventHandler;
  children?: ReactNode;
}

// ✅ 正确：组合多个共享Props
export interface InputProps
  extends LabeledComponentProps,
    SelectableComponentProps<string> {
  type?: string;
  value?: string;
  onChange?: ChangeEventHandler<HTMLInputElement>;
}

// ✅ 正确：泛型Props
export interface SelectProps<T = string | number>
  extends BaseComponentProps {
  value?: T;
  options?: SelectOption<T>[];
  onChange?: ValueChangeCallback<T>;
}

// ✅ 正确：条件类型
type ButtonProps = {
  children: ReactNode;
} & (
  | { variant: 'primary'; onClick: () => void }
  | { variant: 'disabled'; onClick?: never }
);
```

#### ❌ 错误模式

```typescript
// ❌ 错误：不扩展原生属性
export interface ButtonProps {
  variant?: Variant;
  size?: Size;
  onClick?: (event: MouseEvent) => void;
  // 缺少disabled, autoFocus, form等原生属性
}

// ❌ 错误：重复定义已有类型
export interface ButtonProps {
  variant?: 'primary' | 'secondary';  // 应使用Variant类型
  size?: 'sm' | 'md' | 'lg';          // 应使用Size类型
  disabled?: boolean;                 // BaseComponentProps已有
  children?: ReactNode;               // BaseComponentProps已有
}

// ❌ 错误：使用any
export interface SelectProps {
  value: any;
  options: any[];
  onChange: any;
}

// ❌ 错误：不必要的泛型
export interface ButtonProps<T = string> {
  children?: T;  // Button不需要泛型
}
```

### 7.2 类型定义模式

#### ✅ 正确模式

```typescript
// ✅ 正确：使用接口定义对象类型
interface Game {
  gid: number;
  name: string;
  ods_db: string;
}

// ✅ 正确：使用type定义联合类型
type Variant = 'primary' | 'secondary' | 'ghost';
type Status = 'idle' | 'loading' | 'success' | 'error';

// ✅ 正确：使用type定义工具类型
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// ✅ 正确：类型守卫
function isGame(value: unknown): value is Game {
  return (
    typeof value === 'object' &&
    value !== null &&
    'gid' in value &&
    'name' in value
  );
}

// ✅ 正确：使用typeof推导类型
const config = {
  apiUrl: 'http://localhost:5001',
  timeout: 30000,
} as const;

type Config = typeof config;
```

#### ❌ 错误模式

```typescript
// ❌ 错误：使用type定义可扩展对象
type Game = {
  gid: number;
  name: string;
};
// 原因：失去扩展能力

// ❌ 错误：使用any
function processData(data: any) {
  return data.map((item: any) => item.value);
}

// ❌ 错误：不使用类型守卫
function processGame(data: unknown) {
  const game = data as Game;  // 不安全
  console.log(game.name);     // 可能运行时错误
}

// ❌ 错误：重复定义
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost' | 'danger';
}

type InputProps = {
  variant: 'primary' | 'secondary' | 'ghost' | 'danger';
};

// 应该共享Variant类型
```

### 7.3 API类型模式

#### ✅ 正确模式

```typescript
// ✅ 正确：定义标准API响应
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// ✅ 正确：定义成功和错误响应
export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
}

export interface ApiErrorResponse {
  success: false;
  error: string;
}

// ✅ 正确：使用联合类型
export type GameListResponse = ApiResponse<Game[]>;

// ✅ 正确：分页响应
export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    total: number;
    has_next: boolean;
  };
}

// ✅ 正确：请求参数
export interface FetchGamesParams {
  page?: number;
  per_page?: number;
  search?: string;
}
```

#### ❌ 错误模式

```typescript
// ❌ 错误：不定义类型
async function fetchGames() {
  const response = await fetch('/api/games');
  return response.json();  // 返回any
}

// ✅ 正确：定义返回类型
async function fetchGames(): Promise<Game[]> {
  const response = await fetch('/api/games');
  return response.json();
}

// ❌ 错误：重复定义响应结构
interface GameListResponse {
  success: boolean;
  data?: Game[];
  error?: string;
}

interface EventListResponse {
  success: boolean;
  data?: Event[];
  error?: string;
}

// ✅ 正确：使用泛型
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
```

### 7.4 组件类型模式

#### ✅ 正确模式

```typescript
// ✅ 正确：定义完整的Props接口
export interface ButtonProps extends BaseComponentProps {
  variant?: Variant;
  size?: Size;
  onClick?: MouseEventHandler;
  children?: ReactNode;
}

// ✅ 正确：使用forwardRef
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', onClick, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        onClick={onClick}
        {...props}
      >
        {children}
      </button>
    );
  }
);

// ✅ 正确：添加displayName
Button.displayName = 'Button';

// ✅ 正确：导出类型
export type { ButtonProps };
```

#### ❌ 错误模式

```typescript
// ❌ 错误：不定义Props类型
export const Button = ({ variant, onClick, children }) => {
  return <button onClick={onClick}>{children}</button>;
};

// ❌ 错误：不使用forwardRef
export const Button = ({ onClick, children }: ButtonProps) => {
  return <button onClick={onClick}>{children}</button>;
};
// 问题：无法通过ref访问DOM元素

// ❌ 错误：不导出Props类型
export interface ButtonProps { /* ... */ }
export const Button = (props: ButtonProps) => { /* ... */ };
// 问题：外部无法使用ButtonProps类型
```

---

## 8. 迁移指南

### 8.1 JavaScript → TypeScript

#### 步骤1: 文件重命名

```bash
# 重命名文件扩展名
mv Button.jsx Button.tsx
mv Input.jsx Input.tsx
mv utils.js utils.ts
```

#### 步骤2: 添加类型注释

```javascript
// ❌ 原始JavaScript
export function Button({ variant = 'primary', onClick, children }) {
  return <button onClick={onClick}>{children}</button>;
}

// ✅ 添加TypeScript类型
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  onClick?: (event: MouseEvent) => void;
  children?: ReactNode;
}

export function Button({ variant = 'primary', onClick, children }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>;
}
```

#### 步骤3: 使用JSDoc（渐进式迁移）

```javascript
// ✅ 使用JSDoc添加类型注释
/**
 * @param {Object} props
 * @param {'primary' | 'secondary' | 'ghost'} [props.variant='primary']
 * @param {(event: MouseEvent) => void} [props.onClick]
 * @param {ReactNode} [props.children]
 */
export function Button({ variant = 'primary', onClick, children }) {
  return <button onClick={onClick}>{children}</button>;
}
```

### 8.2 PropTypes → TypeScript

#### 迁移对照表

```javascript
// ❌ 原始PropTypes
Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary', 'ghost']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  onClick: PropTypes.func,
  children: PropTypes.node,
};

// ✅ TypeScript类型
interface ButtonProps extends BaseComponentProps {
  variant?: Variant;
  size?: Size;
  disabled?: boolean;
  loading?: boolean;
  onClick?: MouseEventHandler;
  children?: ReactNode;
}
```

#### 常见PropTypes映射

```typescript
// PropTypes.string → string
name?: string;

// PropTypes.number → number
count?: number;

// PropTypes.bool → boolean
disabled?: boolean;

// PropTypes.func → Function类型
onClick?: MouseEventHandler;
onChange?: ChangeEventHandler;

// PropTypes.node → ReactNode
children?: ReactNode;

// PropTypes.element → ReactElement
icon?: ReactElement;

// PropTypes.oneOf(['a', 'b']) → 联合类型
variant?: 'primary' | 'secondary';

// PropTypes.oneOfType([A, B]) → 联合类型
value?: string | number;

// PropTypes.arrayOf(PropTypes.shape({})) → 类型数组
items?: Array<{ id: string; name: string }>;

// PropTypes.shape({}) → 对象类型
user?: { id: number; name: string };

// PropTypes.instanceOf(Class) → 类实例
error?: Error;

// PropTypes.object → Record<string, unknown>
metadata?: Record<string, unknown>;
```

### 8.3 逐步迁移策略

#### 阶段1: 添加JSDoc注释

```javascript
/**
 * @type {import('types').ButtonProps}
 */
const buttonProps = {
  variant: 'primary',
  onClick: handleClick,
};
```

#### 阶段2: 启用checkJs

```json
// tsconfig.json
{
  "compilerOptions": {
    "allowJs": true,
    "checkJs": false  // 逐步启用
  }
}
```

#### 阶段3: 逐文件迁移

1. **低优先级**：工具函数、纯函数
2. **中优先级**：业务组件、Hook
3. **高优先级**：核心组件、API层

#### 阶段4: 启用严格模式

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": false,  // 初始false
    "noImplicitAny": true,  // 阶段1
    "strictNullChecks": true,  // 阶段2
    "strict": true  // 最终阶段
  }
}
```

### 8.4 常见迁移问题

#### 问题1: any类型的滥用

```typescript
// ❌ 问题：所有类型都是any
function processData(data: any): any {
  return data.map((item: any) => item.value);
}

// ✅ 解决：明确类型定义
interface DataItem {
  id: string;
  value: number;
}

function processData(data: DataItem[]): number[] {
  return data.map(item => item.value);
}
```

#### 问题2: 类型断言过度使用

```typescript
// ❌ 问题：过度使用类型断言
const game = data as Game;
const name = (data as Game).name;

// ✅ 解决：使用类型守卫
function isGame(value: unknown): value is Game {
  return (
    typeof value === 'object' &&
    value !== null &&
    'name' in value
  );
}

if (isGame(data)) {
  console.log(data.name);
}
```

#### 问题3: 缺少null检查

```typescript
// ❌ 问题：未处理null/undefined
const name = game.name.toUpperCase();  // 运行时错误

// ✅ 解决：使用可选链和空值合并
const name = game?.name?.toUpperCase() ?? 'Unknown';
```

---

## 9. 检查清单

### 9.1 类型定义检查清单

#### 组件Props定义

- [ ] Props接口是否继承正确的基类（BaseComponentProps, LabeledComponentProps）
- [ ] 是否排除与原生属性冲突的属性（使用Omit）
- [ ] 是否为所有Props添加了JSDoc注释
- [ ] 可选属性是否使用 `?` 标记
- [ ] 是否为props设置了默认值
- [ ] 是否导出了Props类型供外部使用

#### 类型定义

- [ ] Interface vs Type的使用是否正确
- [ ] 是否使用了共享类型而不是重复定义
- [ ] 联合类型是否使用type定义
- [ ] 复杂类型是否拆分为多个小类型
- [ ] 是否使用了类型推导避免重复定义

#### 泛型使用

- [ ] 泛型参数是否使用合理的命名（T, K, P, E）
- [ ] 泛型是否有约束（extends）
- [ ] 是否提供了合理的默认泛型参数
- [ ] 泛型是否真的必要（避免过度设计）

### 9.2 类型安全检查清单

#### 避免any

- [ ] 是否避免了使用any
- [ ] 是否使用unknown代替any
- [ ] 是否为any类型添加了类型守卫

#### 类型守卫

- [ ] 是否为外部数据定义了类型守卫
- [ ] 是否使用了类型谓词（value is Type）
- [ ] 是否使用了断言函数（asserts value is Type）

#### 空值处理

- [ ] 是否使用可选链（?.）避免运行时错误
- [ ] 是否使用空值合并（??）处理null/undefined
- [ ] 是否区分了null/undefined和falsy值

### 9.3 API类型检查清单

#### API响应

- [ ] 是否定义了标准的ApiResponse<T>类型
- [ ] 是否定义了成功和错误响应类型
- [ ] 是否为分页响应定义了专用类型
- [ ] 是否为枚举值定义了字面量类型

#### API请求

- [ ] 是否定义了请求参数类型
- [ ] 是否为查询参数、路径参数、请求体分别定义类型
- [ ] 是否为API端点定义了类型安全的映射

#### 错误处理

- [ ] 是否定义了FetchError类
- [ ] 是否为错误响应定义了详细类型
- [ ] 是否为错误类型定义了判断方法（isValidation, isNotFound等）

### 9.4 代码审查检查清单

#### 组件类型审查

```typescript
// ✅ 检查项
- [ ] Props接口是否完整定义
- [ ] 是否使用了React.forwardRef
- [ ] 是否设置了displayName
- [ ] 是否导出了Props类型
- [ ] 是否有完整的JSDoc注释
- [ ] 是否有使用示例

// 示例：完整的组件类型定义
export interface ButtonProps extends BaseComponentProps {
  /** Button variant */
  variant?: Variant;
  /** Button size */
  size?: Size;
  /** Click handler */
  onClick?: MouseEventHandler;
  /** Button content */
  children?: ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', onClick, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`cyber-button cyber-button--${variant}`}
        onClick={onClick}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
export type { ButtonProps };
```

#### 函数类型审查

```typescript
// ✅ 检查项
- [ ] 参数是否有明确的类型注解
- [ ] 返回值是否有明确的类型注解
- [ ] 泛型参数是否有合理的约束
- [ ] 是否有完整的JSDoc注释

// 示例：完整的函数类型定义
/**
 * 获取游戏列表
 *
 * @param params - 查询参数
 * @returns 游戏列表
 * @throws {FetchError} 当请求失败时
 *
 * @example
 * ```tsx
 * const games = await fetchGames({ page: 1, per_page: 10 });
 * ```
 */
export async function fetchGames(
  params?: GamesListParams
): Promise<Game[]> {
  const response = await fetch('/api/games');
  if (!response.ok) {
    throw await FetchError.fromResponse(response);
  }
  return response.json();
}
```

---

## 10. 参考资源

### 10.1 项目文档

- **[CLAUDE.md](../../CLAUDE.md)** - 项目开发规范
- **[React组件开发指南](./react-component-guide.md)** - 组件开发最佳实践
- **[API开发指南](./api-development.md)** - API开发规范

### 10.2 类型定义文件

- **[frontend/src/types/common.ts](../../frontend/src/types/common.ts)** - 共享类型定义（30+类型）
- **[frontend/src/shared/api/types.ts](../../frontend/src/shared/api/types.ts)** - API类型定义
- **[frontend/tsconfig.json](../../frontend/tsconfig.json)** - TypeScript配置

### 10.3 示例组件

- **[Input.type-test.tsx](../../frontend/src/shared/ui/Input/Input.type-test.tsx)** - Input组件类型测试
- **[Button.tsx](../../frontend/src/shared/ui/Button/Button.tsx)** - Button组件完整类型定义
- **[Select.tsx](../../frontend/src/shared/ui/Select/Select.tsx)** - Select组件完整类型定义

### 10.4 外部资源

- **[TypeScript官方文档](https://www.typescriptlang.org/docs/)**
- **[React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)**
- **[TypeScript Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)**

---

**文档维护**: 本文档应随着项目类型定义的演进持续更新。如有疑问或建议，请联系开发团队。
