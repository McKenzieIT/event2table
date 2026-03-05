# TypeScript 迁移检查清单

> **基于 Event2Table 项目 150+ 组件迁移经验总结**
> **版本**: 1.0 | **更新时间**: 2026-03-01

本文档提供系统化的 TypeScript 迁移流程，帮助开发者高效、安全地将 React 组件从 JavaScript 迁移到 TypeScript。

---

## 📋 快速导航

- [阶段1: 准备工作](#阶段1-准备工作) - 5分钟
- [阶段2: 文件分析](#阶段2-文件分析) - 10分钟
- [阶段3: 类型定义](#阶段3-类型定义) - 15-30分钟
- [阶段4: 组件迁移](#阶段4-组件迁移) - 30-60分钟
- [阶段5: Hook迁移](#阶段5-hook迁移) - 15-30分钟
- [阶段6: 测试迁移](#阶段6-测试迁移) - 15分钟
- [阶段7: 验证](#阶段7-验证) - 10分钟
- [阶段8: 清理](#阶段8-清理) - 5分钟
- [常见问题快速参考](#常见问题快速参考)
- [工具推荐](#工具推荐)

---

## 阶段1: 准备工作

> **预估时间**: 5分钟 | **优先级**: 🔴 必须完成

### 环境检查

- [ ] **备份当前代码分支**
  ```bash
  git checkout -b typescript-migration-<component-name>
  git push origin typescript-migration-<component-name>
  ```

- [ ] **检查 tsconfig.json 配置**
  ```bash
  # 确认以下配置存在
  - jsx: "react-jsx"
  - moduleResolution: "node"
  - strict: true
  - esModuleInterop: true
  - skipLibCheck: true
  ```

- [ ] **确认项目构建成功**
  ```bash
  cd frontend
  npm run build
  # 确保构建成功无错误
  ```

- [ ] **运行现有测试确保通过**
  ```bash
  npm run test:unit
  npm run test:e2e
  # 确保所有测试通过
  ```

### 依赖检查

- [ ] **确认 TypeScript 版本**
  ```bash
  npm list typescript
  # 推荐: >= 5.0.0
  ```

- [ ] **确认类型定义包**
  ```bash
  npm list @types/react @types/react-dom
  # 确保已安装
  ```

---

## 阶段2: 文件分析

> **预估时间**: 10分钟 | **优先级**: 🔴 必须完成

### 依赖关系分析

- [ ] **识别需要迁移的 .js/.jsx 文件**
  ```bash
  # 查找所有 JS 文件
  find src -name "*.jsx" -o -name "*.js"
  ```

- [ ] **分析文件依赖关系**
  ```bash
  # 使用 madge 查看依赖图
  npx madge --image dep-graph.png src/components/YourComponent.jsx
  ```

- [ ] **确定迁移优先级**
  - ✅ **优先**: 无依赖的工具函数
  - ✅ **其次**: 基础 UI 组件（Button, Input 等）
  - ✅ **然后**: 业务组件
  - ⏳ **最后**: 复杂的容器组件

- [ ] **列出潜在的风险点**
  - [ ] 使用了 `any` 类型的 props
  - [ ] 复杂的泛型使用
  - [ ] 动态属性访问（`obj[key]`）
  - [ ] 第三方库集成（缺少类型定义）

---

## 阶段3: 类型定义

> **预估时间**: 15-30分钟 | **优先级**: 🔴 必须完成

### Props 接口定义

- [ ] **定义 Props 接口**
  ```typescript
  // ✅ 正确: 使用 interface 定义组件 Props
  interface ButtonProps {
    label: string;
    onClick: () => void;
    disabled?: boolean;
    variant?: 'primary' | 'secondary' | 'danger';
  }

  // ✅ 或使用 type（更灵活）
  type ButtonProps = {
    label: string;
    onClick: () => void;
  } & (HTMLAttributes<HTMLButtonElement>);
  ```

- [ ] **为 children 添加类型**
  ```typescript
  import type { ReactNode } from 'react';

  interface CardProps {
    children: ReactNode;
    header?: string;
  }
  ```

- [ ] **为事件处理器添加类型**
  ```typescript
  import type { ChangeEvent, MouseEvent, FormEvent } from 'react';

  interface InputProps {
    onChange: (e: ChangeEvent<HTMLInputElement>) => void;
    onClick?: (e: MouseEvent<HTMLButtonElement>) => void;
    onSubmit?: (e: FormEvent<HTMLFormElement>) => void;
  }
  ```

### 状态类型定义

- [ ] **定义 useState 类型**
  ```typescript
  // ✅ 简单类型：自动推断
  const [count, setCount] = useState(0);

  // ✅ 复杂类型：显式注解
  interface User {
    id: number;
    name: string;
    email: string;
  }
  const [user, setUser] = useState<User | null>(null);

  // ✅ 联合类型
  type Status = 'idle' | 'loading' | 'success' | 'error';
  const [status, setStatus] = useState<Status>('idle');
  ```

- [ ] **定义 useReducer 类型**
  ```typescript
  interface State {
    count: number;
    status: string;
  }

  type Action =
    | { type: 'INCREMENT' }
    | { type: 'DECREMENT' }
    | { type: 'SET_COUNT'; payload: number };

  const [state, dispatch] = useReducer<State, Action>(reducer, initialState);
  ```

### Context 类型定义

- [ ] **定义 Context 类型**
  ```typescript
  interface ThemeContextValue {
    theme: 'light' | 'dark';
    toggleTheme: () => void;
  }

  const ThemeContext = createContext<ThemeContextValue | null>(null);

  // ✅ 使用自定义 Hook
  function useTheme(): ThemeContextValue {
    const context = useContext(ThemeContext);
    if (!context) {
      throw new Error('useTheme must be used within ThemeProvider');
    }
    return context;
  }
  ```

### API 响应类型定义

- [ ] **定义 API 响应类型**
  ```typescript
  // ✅ API 响应结构
  interface ApiResponse<T> {
    success: boolean;
    data: T;
    message?: string;
    error?: string;
  }

  // ✅ 具体数据类型
  interface Game {
    id: number;
    gid: string;
    name: string;
    ods_db: string;
  }

  // ✅ 使用泛型
  async function fetchGames(): Promise<ApiResponse<Game[]>> {
    const response = await fetch('/api/games');
    return response.json();
  }
  ```

---

## 阶段4: 组件迁移

> **预估时间**: 30-60分钟 | **优先级**: 🔴 必须完成

### 函数组件类型注解

- [ ] **添加函数组件类型注解**
  ```typescript
  // ✅ 方式1: 使用 React.FC（不推荐）
  const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
    return <button onClick={onClick}>{label}</button>;
  };

  // ✅ 方式2: 直接函数声明（推荐）
  function Button({ label, onClick }: ButtonProps) {
    return <button onClick={onClick}>{label}</button>;
  }

  // ✅ 方式3: 箭头函数（推荐）
  const Button = ({ label, onClick }: ButtonProps) => {
    return <button onClick={onClick}>{label}</button>;
  };
  ```

- [ ] **为泛型组件添加类型**
  ```typescript
  interface ListProps<T> {
    items: T[];
    renderItem: (item: T) => ReactNode;
    keyExtractor: (item: T) => string;
  }

  function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
    return (
      <ul>
        {items.map((item) => (
          <li key={keyExtractor(item)}>{renderItem(item)}</li>
        ))}
      </ul>
    );
  }

  // 使用
  <List
    items={users}
    renderItem={(user) => <span>{user.name}</span>}
    keyExtractor={(user) => user.id}
  />
  ```

### React Hook 类型注解

- [ ] **为 useState 添加类型**
  ```typescript
  // ✅ 简单类型
  const [count, setCount] = useState<number>(0);

  // ✅ 对象类型
  const [form, setForm] = useState<{
    username: string;
    password: string;
  }>({ username: '', password: '' });

  // ✅ 使用 interface
  interface FormData {
    username: string;
    password: string;
  }
  const [form, setForm] = useState<FormData>({ username: '', password: '' });
  ```

- [ ] **为 useRef 添加类型**
  ```typescript
  // ✅ DOM 元素引用
  const inputRef = useRef<HTMLInputElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // ✅ 普通值引用
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const dataRef = useRef<UserData | undefined>();
  ```

- [ ] **为 useCallback 添加类型**
  ```typescript
  // ✅ 简单回调
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  // ✅ 带参数的回调
  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
  }, []);

  // ✅ 显式返回类型
  const memoizedValue = useCallback<string>(() => {
    return computeExpensiveValue();
  }, [dependency]);
  ```

- [ ] **为 useMemo 添加类型**
  ```typescript
  // ✅ 自动推断（推荐）
  const filteredList = useMemo(() => {
    return items.filter(item => item.active);
  }, [items]);

  // ✅ 显式类型（复杂场景）
  const sortedList = useMemo<Item[]>(() => {
    return items.sort((a, b) => a.id - b.id);
  }, [items]);
  ```

- [ ] **为自定义 Hook 添加类型**
  ```typescript
  // ✅ 自定义 Hook 定义
  function useLocalStorage<T>(
    key: string,
    initialValue: T
  ): [T, (value: T) => void] {
    const [storedValue, setStoredValue] = useState<T>(initialValue);

    const setValue = useCallback((value: T) => {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    }, [key]);

    return [storedValue, setValue];
  }

  // 使用
  const [name, setName] = useLocalStorage<string>('name', '');
  ```

---

## 阶段5: Hook 迁移

> **预估时间**: 15-30分钟 | **优先级**: 🟡 重要

### 自定义 Hook 类型

- [ ] **自定义 Hook 参数类型**
  ```typescript
  // ✅ 基础参数类型
  function useGame(gameGid: number) {
    // ...
  }

  // ✅ 可选参数
  interface UseGameOptions {
    enabled?: boolean;
    refetchInterval?: number;
  }

  function useGame(gameGid: number, options?: UseGameOptions) {
    // ...
  }

  // ✅ 参数对象（推荐）
  interface UseFetchParams {
    url: string;
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
    headers?: Record<string, string>;
    body?: any;
  }

  function useFetch<T>({ url, method = 'GET', headers, body }: UseFetchParams) {
    // ...
  }
  ```

- [ ] **自定义 Hook 返回类型**
  ```typescript
  // ✅ 返回元组类型（类似 useState）
  function useToggle(initialValue: boolean): [boolean, () => void] {
    const [value, setValue] = useState(initialValue);
    const toggle = useCallback(() => setValue(v => !v), []);
    return [value, toggle];
  }

  // ✅ 返回对象类型
  interface UseFetchResult<T> {
    data: T | null;
    loading: boolean;
    error: Error | null;
    refetch: () => void;
  }

  function useFetch<T>(params: UseFetchParams): UseFetchResult<T> {
    // ...
  }

  // ✅ 使用
  const { data, loading, error, refetch } = useFetch<User>({
    url: '/api/user'
  });
  ```

- [ ] **泛型 Hook 定义**
  ```typescript
  // ✅ 泛型 Hook
  function useArray<T>(initialArray: T[]) {
    const [array, setArray] = useState<T[]>(initialArray);

    const push = useCallback((element: T) => {
      setArray(prev => [...prev, element]);
    }, []);

    const filter = useCallback((callback: (item: T) => boolean) => {
      return array.filter(callback);
    }, [array]);

    return { array, push, filter };
  }

  // 使用
  const { array, push, filter } = useArray<number>([1, 2, 3]);
  const { array: users, push: addUser } = useArray<User>([]);
  ```

---

## 阶段6: 测试迁移

> **预估时间**: 15分钟 | **优先级**: 🟡 重要

### 测试文件迁移

- [ ] **更新测试文件扩展名**
  ```bash
  # 重命名测试文件
  mv Button.test.jsx Button.test.tsx
  mv Button.spec.jsx Button.spec.tsx
  ```

- [ ] **添加测试框架类型导入**
  ```typescript
  // Vitest / Jest
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/react';

  // React Testing Library
  import type { RenderResult } from '@testing-library/react';
  ```

- [ ] **修复 Mock 函数类型**
  ```typescript
  // ✅ Mock 函数
  const mockOnClick = vi.fn();
  const mockHandleChange = vi.fn((e: ChangeEvent<HTMLInputElement>) => {
    // ...
  });

  // ✅ Mock 组件
  vi.mock('../api/games', () => ({
    fetchGames: vi.fn(() => Promise.resolve([])),
  }));

  // ✅ Mock 返回类型
  const mockUseGame = vi.fn(() => ({
    data: mockGameData,
    loading: false,
    error: null,
  }));
  ```

- [ ] **验证所有测试通过**
  ```bash
  # 运行迁移的组件测试
  npm run test -- Button.test.tsx

  # 运行所有测试
  npm run test:unit
  npm run test:e2e
  ```

---

## 阶段7: 验证

> **预估时间**: 10分钟 | **优先级**: 🔴 必须完成

### 类型检查

- [ ] **运行 TypeScript 编译器检查**
  ```bash
  # 检查类型错误（不生成文件）
  npx tsc --noEmit

  # 检查特定文件
  npx tsc --noEmit src/components/Button.tsx
  ```

- [ ] **运行开发服务器**
  ```bash
  npm run dev
  # 确认没有类型错误
  ```

- [ ] **运行生产构建**
  ```bash
  npm run build
  # 确认构建成功
  ```

### 运行测试

- [ ] **运行单元测试**
  ```bash
  npm run test:unit
  # 确保所有测试通过
  ```

- [ ] **运行 E2E 测试**
  ```bash
  npm run test:e2e
  # 确保端到端测试通过
  ```

- [ ] **手动测试迁移的组件**
  - [ ] 组件渲染正常
  - [ ] 交互功能正常
  - [ ] 控制台无错误
  - [ ] 样式无变化

### 性能检查

- [ ] **检查 bundle 大小**
  ```bash
  # 构建后检查
  npm run build

  # 查看输出大小
  ls -lh dist/assets/

  # 使用 bundle analyzer
  npm run build:analyze
  ```

- [ ] **验证性能无退化**
  - [ ] 组件加载速度
  - [ ] 交互响应时间
  - [ ] 内存使用

---

## 阶段8: 清理

> **预估时间**: 5分钟 | **优先级**: 🟢 建议

### 文件清理

- [ ] **删除原始 .js/.jsx 文件**
  ```bash
  # 确认迁移成功后删除
  rm src/components/Button.jsx
  rm src/components/Button.js
  ```

- [ ] **更新导入语句**
  ```typescript
  // ❌ 旧的导入
  import { Button } from './Button.jsx';

  // ✅ 新的导入（省略扩展名）
  import { Button } from './Button';

  // ✅ 或显式包含 .tsx
  import { Button } from './Button.tsx';
  ```

- [ ] **更新相关文件的导入**
  ```typescript
  // 搜索所有导入该组件的文件
  grep -r "from './Button.jsx'" src/

  # 批量替换
  find src -name "*.tsx" -o -name "*.ts" | xargs sed -i '' "s|from './Button.jsx'|from './Button'|g"
  ```

### 提交代码

- [ ] **审查变更**
  ```bash
  git diff
  # 检查所有变更
  ```

- [ ] **提交代码**
  ```bash
  git add .
  git commit -m "feat: migrate Button component to TypeScript

  - Add ButtonProps interface
  - Add type annotations for all hooks
  - Update tests to TypeScript
  - All tests passing

  BREAKING CHANGE: Button component now requires TypeScript"
  ```

- [ ] **推送分支**
  ```bash
  git push origin typescript-migration-button
  ```

- [ ] **创建 Pull Request**
  - [ ] 填写 PR 描述
  - [ ] 关联相关 Issue
  - [ ] 请求代码审查

### 更新文档

- [ ] **更新组件文档**
  ```markdown
  ## Button

  **TypeScript Component**: ✅

  ### Props

  | Prop | Type | Required | Default | Description |
  |------|------|----------|---------|-------------|
  | label | `string` | Yes | - | Button label |
  | onClick | `() => void` | Yes | - | Click handler |
  | disabled | `boolean` | No | `false` | Disabled state |
  | variant | `'primary' \| 'secondary' \| 'danger'` | No | `'primary'` | Button variant |
  ```

- [ ] **更新迁移日志**
  ```markdown
  # TypeScript Migration Progress

  - [x] Button
  - [x] Input
  - [ ] Card
  - [ ] Modal
  ```

---

## 常见问题快速参考

### 问题1: 类型导入错误

**错误信息**:
```
TS2307: Cannot find module './Button' or its corresponding type declarations.
```

**解决方案**:
```typescript
// ❌ 错误：混合导入
import { Button } from './Button';
import type { ButtonProps } from './Button.tsx';

// ✅ 正确：统一导入
import { Button } from './Button';
import type { ButtonProps } from './Button';

// ✅ 或使用 type-only import
import type { ButtonProps } from './Button';
```

---

### 问题2: React 事件类型

**错误信息**:
```
TS2345: Argument of type 'Event' is not assignable to parameter of type 'MouseEvent<Element, MouseEvent>'
```

**解决方案**:
```typescript
// ❌ 错误：使用通用 Event
onClick={(e: Event) => {
  console.log(e.target); // 类型错误
}}

// ✅ 正确：使用具体的 React 事件类型
import type { MouseEvent, ChangeEvent, FormEvent, KeyboardEvent } from 'react';

onClick={(e: MouseEvent<HTMLButtonElement>) => {
  console.log(e.currentTarget); // 正确
}}

onChange={(e: ChangeEvent<HTMLInputElement>) => {
  console.log(e.target.value); // 正确
}}

onSubmit={(e: FormEvent<HTMLFormElement>) => {
  e.preventDefault();
}}

onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter') {
    // ...
  }
}}
```

---

### 问题3: 泛型组件

**错误信息**:
```
TS7231: Cannot instantiate generic type without type arguments
```

**解决方案**:
```typescript
// ❌ 错误：缺少泛型参数
function List({ items, renderItem }) {
  return <ul>{items.map(renderItem)}</ul>;
}

// ✅ 正确：添加泛型参数
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => ReactNode;
  keyExtractor: (item: T) => string | number;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item) => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// 使用
<List
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
  keyExtractor={(user) => user.id}
/>
```

---

### 问题4: children 类型

**错误信息**:
```
TS2769: No overload matches this call
```

**解决方案**:
```typescript
import type { ReactNode } from 'react';

// ✅ 正确：children 类型
interface CardProps {
  children: ReactNode;
  header?: string;
}

function Card({ children, header }: CardProps) {
  return (
    <div className="card">
      {header && <div className="card-header">{header}</div>}
      <div className="card-body">{children}</div>
    </div>
  );
}

// ✅ 更精确的类型
interface ButtonProps {
  children: React.ReactNode; // 任何可渲染内容
}

interface LinkProps {
  children: string; // 仅文本
}
```

---

### 问题5: useState 初始类型

**错误信息**:
```
TS2345: Argument of type 'null' is not assignable to parameter of type 'User'
```

**解决方案**:
```typescript
// ❌ 错误：null 不能赋值给 User
const [user, setUser] = useState<User>(null);

// ✅ 正确：使用联合类型
const [user, setUser] = useState<User | null>(null);

// ✅ 或使用类型断言
const [user, setUser] = useState<User | null>(null as User | null);

// ✅ 或提供初始值
const [user, setUser] = useState<User>({
  id: 0,
  name: '',
  email: ''
});
```

---

### 问题6: useRef 类型

**错误信息**:
```
TS2322: Type 'HTMLElement | null' is not assignable to type 'HTMLInputElement'
```

**解决方案**:
```typescript
// ❌ 错误：过于宽泛
const inputRef = useRef<HTMLElement>(null);

// ✅ 正确：使用具体的 DOM 元素类型
const inputRef = useRef<HTMLInputElement>(null);
const buttonRef = useRef<HTMLButtonElement>(null);
const divRef = useRef<HTMLDivElement>(null);
const formRef = useRef<HTMLFormElement>(null);

// 使用
<input ref={inputRef} />
<button ref={buttonRef}>Click</button>
<div ref={divRef}>Content</div>
```

---

### 问题7: 第三方库类型缺失

**错误信息**:
```
TS7016: Could not find a declaration file for module 'some-library'
```

**解决方案**:
```bash
# 1. 检查是否有官方类型定义
npm install @types/some-library

# 2. 如果没有，创建自定义类型定义
# 创建 src/types/some-library.d.ts
declare module 'some-library' {
  export interface SomeInterface {
    property: string;
    method(): void;
  }
}

# 3. 在 tsconfig.json 中包含
{
  "include": ["src/types/**/*.d.ts"]
}
```

---

### 问题8: 动态属性访问

**错误信息**:
```
TS7053: Element implicitly has an 'any' type because expression of type 'string' can't be used to index type 'User'
```

**解决方案**:
```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

// ❌ 错误：动态属性访问不安全
function getUserProperty(user: User, key: string) {
  return user[key]; // 类型错误
}

// ✅ 方案1：使用 keyof
function getUserProperty(user: User, key: keyof User) {
  return user[key];
}

// ✅ 方案2：使用类型断言
function getUserProperty(user: User, key: string) {
  return user[key as keyof User];
}

// ✅ 方案3：泛型约束
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// 使用
const userName = getProperty(user, 'name'); // 类型正确
```

---

### 问题9: React.forwardRef 类型

**错误信息**:
```
TS2740: Type '{}' is missing properties from type 'ForwardRefRenderFunction'
```

**解决方案**:
```typescript
import type { forwardRef as ForwardRef } from 'react';

// ✅ 正确：forwardRef 类型注解
interface ButtonProps {
  label: string;
  onClick: () => void;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ label, onClick }, ref) => {
    return (
      <button ref={ref} onClick={onClick}>
        {label}
      </button>
    );
  }
);

// ✅ 或显式类型
const Button: ForwardRefRenderFunction<HTMLButtonElement, ButtonProps> = (
  { label, onClick },
  ref
) => {
  return (
    <button ref={ref} onClick={onClick}>
      {label}
    </button>
  );
};

export default forwardRef(Button);
```

---

### 问题10: CSS Modules 类型

**错误信息**:
```
TS2339: Property 'className' does not exist on type 'typeof import("*.module.css")'
```

**解决方案**:
```typescript
// ✅ 方案1：创建类型定义文件
# 创建 src/types/css-modules.d.ts
declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.module.scss' {
  const classes: { [key: string]: string };
  export default classes;
}

// ✅ 方案2：使用 require
import styles = require('./Button.module.css');

// ✅ 方案3：使用类型断言
const styles = require('./Button.module.css') as Record<string, string>;

// 使用
<button className={styles.button}>Click</button>
```

---

## 工具推荐

### VSCode 插件

1. **TypeScript Importer** - 自动导入类型
   ```bash
   ext install pmneo.tsimporter
   ```

2. **TypeScript Hero** - 快速类型定义和重构
   ```bash
   ext install rbbit.typescript-hero
   ```

3. **Error Lens** - 内联显示错误信息
   ```bash
   ext install usernamehw.errorlens
   ```

4. **TypeScript VSCode** - 增强 TypeScript 支持
   ```bash
   ext install ms-vscode.vscode-typescript-next
   ```

### 命令行工具

1. **TypeScript Compiler (tsc)**
   ```bash
   # 检查类型错误
   npx tsc --noEmit

   # 增量编译
   npx tsc --watch

   # 生成声明文件
   npx tsc --declaration
   ```

2. **TypeDoc** - 生成 API 文档
   ```bash
   npm install -g typedoc
   typedoc --out docs src
   ```

3. **ts-migrate** - 自动迁移工具
   ```bash
   npx ts-migrate migrate src/components/Button.jsx
   ```

### 代码格式化

1. **ESLint + TypeScript**
   ```bash
   npm install -D @typescript-eslint/parser @typescript-eslint/eslint-plugin

   # .eslintrc.js
   module.exports = {
     parser: '@typescript-eslint/parser',
     plugins: ['@typescript-eslint'],
     extends: [
       'plugin:@typescript-eslint/recommended'
     ]
   };
   ```

2. **Prettier + TypeScript**
   ```bash
   npm install -D prettier

   # .prettierrc
   {
     "semi": true,
     "singleQuote": true,
     "trailingComma": "es5"
   }
   ```

---

## 时间估算

基于 Event2Table 项目 150+ 组件迁移经验：

| 组件类型 | 预估时间 | 难度 | 示例 |
|---------|---------|------|------|
| **简单组件** | 15-30 分钟 | ⭐ | Button, Input, Label |
| **中等组件** | 30-60 分钟 | ⭐⭐ | Card, Modal, Form |
| **复杂组件** | 1-2 小时 | ⭐⭐⭐ | DataTable, Canvas, FlowBuilder |
| **自定义 Hook** | 15-30 分钟 | ⭐⭐ | useLocalStorage, useFetch |
| **工具函数** | 10-15 分钟 | ⭐ | formatDate, debounce |

### 影响时间的因素

- ✅ **加速因素**:
  - 已有类似的类型定义
  - 组件结构简单清晰
  - 使用了 React Hooks（而非 Class 组件）
  - 已有完整的单元测试

- ⏳ **延缓因素**:
  - 复杂的泛型使用
  - 第三方库缺少类型定义
  - 动态属性访问
  - 复杂的状态管理逻辑

---

## 最佳实践

### 1. 类型定义原则

```typescript
// ✅ 优先使用 interface（可扩展）
interface User {
  id: number;
  name: string;
}

interface AdminUser extends User {
  permissions: string[];
}

// ✅ 使用 type（联合类型、交叉类型）
type Status = 'idle' | 'loading' | 'success' | 'error';
type ButtonProps = BaseProps & { onClick: () => void };

// ✅ 使用 type（元组类型）
type Coordinate = [number, number];

// ❌ 避免：过度使用 any
const data: any = fetchData(); // 不安全

// ✅ 推荐：使用 unknown
const data: unknown = fetchData();
if (typeof data === 'string') {
  console.log(data); // 安全
}
```

### 2. 类型导出

```typescript
// ✅ 导出 Props 类型（便于复用和测试）
export interface ButtonProps {
  label: string;
  onClick: () => void;
}

export function Button({ label, onClick }: ButtonProps) {
  return <button onClick={onClick}>{label}</button>;
}

// ✅ 在测试文件中导入
import type { ButtonProps } from './Button';
```

### 3. 类型辅助工具

```typescript
// ✅ Partial - 所有属性可选
type UserUpdate = Partial<User>;

// ✅ Required - 所有属性必填
type RequiredUser = Required<Partial<User>>;

// ✅ Readonly - 所有属性只读
type ReadonlyUser = Readonly<User>;

// ✅ Pick - 选择部分属性
type UserPreview = Pick<User, 'id' | 'name'>;

// ✅ Omit - 排除部分属性
type CreateUserInput = Omit<User, 'id'>;

// ✅ Record - 构建对象类型
type UserRoleMap = Record<string, 'admin' | 'user'>;

// ✅ ReturnType - 获取函数返回类型
type FetchResult = ReturnType<typeof fetchUser>;
```

### 4. 类型守卫

```typescript
// ✅ typeof 类型守卫
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

// ✅ instanceof 类型守卫
function isDate(value: unknown): value is Date {
  return value instanceof Date;
}

// ✅ in 操作符类型守卫
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value
  );
}

// 使用
function processValue(value: unknown) {
  if (isUser(value)) {
    console.log(value.name); // 类型安全
  }
}
```

### 5. 避免类型断言

```typescript
// ❌ 避免：过度使用 as
const user = data as User; // 不安全

// ✅ 推荐：类型守卫
if (isUser(data)) {
  console.log(data.name); // 安全
}

// ✅ 推荐：类型窄化
if (data && typeof data === 'object' && 'name' in data) {
  console.log(data.name);
}
```

---

## 参考资料

### 官方文档

- [TypeScript 官方文档](https://www.typescriptlang.org/docs/)
- [React TypeScript 文档](https://react-typescript-cheatsheet.netlify.app/)
- [React + TypeScript 入门](https://react.dev/learn/typescript)

### 社区资源

- [TypeScript 教程](https://www.typescripttutorial.net/)
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

### Event2Table 项目资源

- [React最佳实践](../lessons-learned/react-best-practices.md)
- [架构设计文档](./architecture.md)
- [贡献指南](./contributing.md)

---

## 总结

本检查清单基于 Event2Table 项目 150+ 组件的实际迁移经验总结，涵盖了从准备到清理的完整流程。按照此清单操作，可以：

✅ **系统化迁移** - 不遗漏任何步骤
✅ **减少错误** - 提前发现潜在问题
✅ **提高效率** - 明确的时间估算
✅ **保证质量** - 完整的验证流程

### 快速回顾

**迁移流程**: 8个阶段，总计约 2-3 小时（中等复杂度组件）
**核心原则**: 类型安全优先，逐步迁移，充分测试
**关键工具**: TypeScript Compiler, VSCode, ESLint, Prettier
**常见陷阱**: React 事件类型、泛型组件、动态属性访问

### 下一步

- [ ] 开始迁移第一个组件
- [ ] 建立组件迁移日志
- [ ] 定期同步团队经验
- [ ] 持续优化类型定义

---

**文档版本**: 1.0
**最后更新**: 2026-03-01
**维护者**: Event2Table Development Team
