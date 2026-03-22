# 组件代码质量改进实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 系统性解决Event2Table前端组件库的技术债务，建立自动化质量保障体系

**Architecture:** 采用分层渐进式重构方案，按优先级分6个阶段执行：类型安全 → 错误处理 → 性能优化 → 代码质量 → 工程化 → 文档。每阶段3个subagent并行工作。

**Tech Stack:** TypeScript, React, Vitest, ESLint, Prettier, Husky, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-03-22-component-quality-improvement-design.md`

---

## 阶段 1：类型安全基础

**目标:** 消除107处any类型，建立完整类型定义体系

**预计时间:** 1.5-2小时

### Task 1.1: 基础组件类型强化

**Files:**
- Modify: `frontend/src/shared/ui/Button/Button.tsx`
- Modify: `frontend/src/shared/ui/Input/Input.tsx`
- Modify: `frontend/src/shared/ui/TextArea/TextArea.tsx`
- Modify: `frontend/src/shared/ui/Checkbox/Checkbox.tsx`
- Modify: `frontend/src/shared/ui/Radio/Radio.tsx`
- Modify: `frontend/src/shared/ui/Switch/Switch.tsx`
- Modify: `frontend/src/shared/ui/components/Select/Select.tsx`

- [ ] **Step 1: 统计当前any类型数量**

Run: `grep -r ": any" frontend/src/shared/ui --include="*.tsx" --include="*.ts" | wc -l`
Expected: 显示当前any类型数量（约107处）

- [ ] **Step 2: 消除Button组件any类型**

检查Button.tsx中的any类型，替换为具体类型：

```typescript
// 示例：Button Props类型定义
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}
```

- [ ] **Step 3: 消除Input组件any类型**

检查Input.tsx中的any类型，替换为具体类型：

```typescript
// 示例：Input Props类型定义
interface InputProps {
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  type?: 'text' | 'password' | 'email' | 'number';
  className?: string;
}
```

- [ ] **Step 4: 消除TextArea组件any类型**

检查TextArea.tsx中的any类型，替换为具体类型

- [ ] **Step 5: 消除Checkbox组件any类型**

检查Checkbox.tsx中的any类型，替换为具体类型

- [ ] **Step 6: 消除Radio组件any类型**

检查Radio.tsx中的any类型，替换为具体类型

- [ ] **Step 7: 消除Switch组件any类型**

检查Switch.tsx中的any类型，替换为具体类型

- [ ] **Step 8: 消除Select组件any类型**

检查Select.tsx中的any类型，替换为具体类型：

```typescript
// 示例：Select Props类型定义
interface SelectProps<T = string> {
  value: T;
  onChange: (value: T) => void;
  options: Array<{ label: string; value: T }>;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  multiple?: boolean;
  className?: string;
}
```

- [ ] **Step 10: 运行TypeScript编译检查**

Run: `cd frontend && npm run type-check`
Expected: 无类型错误

- [ ] **Step 11: 运行测试确保功能正常**

Run: `cd frontend && npm test -- --run`
Expected: 所有测试通过

- [ ] **Step 12: 提交更改**

```bash
git add frontend/src/shared/ui/Button frontend/src/shared/ui/Input frontend/src/shared/ui/TextArea frontend/src/shared/ui/Checkbox frontend/src/shared/ui/Radio frontend/src/shared/ui/Switch frontend/src/shared/ui/components/Select
git commit -m "feat(ui): eliminate any types in basic components (Button, Input, TextArea, Checkbox, Radio, Switch, Select)"
```

---

### Task 1.2: 业务组件类型强化

**Files:**
- Modify: `frontend/src/shared/ui/components/Modal/Modal.tsx`
- Modify: `frontend/src/shared/ui/Card/Card.tsx`
- Modify: `frontend/src/shared/ui/Pagination/Pagination.tsx`
- Modify: `frontend/src/shared/ui/components/Table/Table.tsx`
- Modify: `frontend/src/shared/ui/components/Form/Form.tsx`

- [ ] **Step 1: 消除Modal组件any类型**

检查Modal.tsx中的any类型，完善Props接口：

```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
  closeOnOverlayClick?: boolean;
  closeOnEsc?: boolean;
  className?: string;
}
```

- [ ] **Step 2: 消除Card组件any类型**

检查Card.tsx中的any类型，完善Props接口

- [ ] **Step 3: 消除Pagination组件any类型**

检查Pagination.tsx中的any类型，完善Props接口：

```typescript
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  siblingCount?: number;
  showFirstLast?: boolean;
  className?: string;
}
```

- [ ] **Step 4: 消除Table组件any类型**

检查Table.tsx中的any类型，添加泛型支持：

```typescript
interface TableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  onRowClick?: (row: T) => void;
  sortable?: boolean;
  pagination?: PaginationConfig;
  className?: string;
}
```

- [ ] **Step 5: 消除Form组件any类型**

检查Form.tsx中的any类型，完善表单类型定义

- [ ] **Step 6: 添加联合类型和类型守卫**

为复杂组件添加联合类型和类型守卫函数：

```typescript
// 示例：类型守卫
function isButtonProps(props: ButtonProps | LinkButtonProps): props is ButtonProps {
  return !('to' in props);
}
```

- [ ] **Step 7: 运行TypeScript编译检查**

Run: `cd frontend && npm run type-check`
Expected: 无类型错误

- [ ] **Step 8: 运行测试确保功能正常**

Run: `cd frontend && npm test -- --run`
Expected: 所有测试通过

- [ ] **Step 9: 提交更改**

```bash
git add frontend/src/shared/ui/components/Modal frontend/src/shared/ui/Card frontend/src/shared/ui/Pagination frontend/src/shared/ui/components/Table frontend/src/shared/ui/components/Form
git commit -m "feat(ui): eliminate any types in business components (Modal, Card, Pagination, Table, Form)"
```

---

### Task 1.3: 工具类型和类型定义文件

**Files:**
- Create: `frontend/src/shared/ui/types/common.ts`
- Create: `frontend/src/shared/ui/types/components.ts`
- Create: `frontend/src/shared/ui/types/utils.ts`
- Create: `frontend/src/shared/ui/types/index.ts`

- [ ] **Step 1: 创建types目录**

Run: `mkdir -p frontend/src/shared/ui/types`
Expected: 目录创建成功

- [ ] **Step 1.1: 检查当前any类型分布**

Run: `grep -r ": any" frontend/src/shared/ui --include="*.tsx" --include="*.ts" -l | head -20`
Expected: 列出包含any类型的文件，了解分布情况

- [ ] **Step 2: 创建common.ts - 通用类型定义**

```typescript
// frontend/src/shared/ui/types/common.ts

/** 通用尺寸类型 */
export type Size = 'small' | 'medium' | 'large';

/** 通用变体类型 */
export type Variant = 'primary' | 'secondary' | 'outline' | 'ghost';

/** 通用状态类型 */
export type Status = 'default' | 'success' | 'warning' | 'error';

/** 通用ID类型 */
export type ID = string | number;

/** 通用回调函数类型 */
export type Callback<T = void> = (args: T) => void;

/** 通用异步状态 */
export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

/** 通用分页配置 */
export interface PaginationConfig {
  page: number;
  pageSize: number;
  total: number;
  onChange: (page: number, pageSize: number) => void;
}
```

- [ ] **Step 3: 创建components.ts - 组件公共类型**

```typescript
// frontend/src/shared/ui/types/components.ts

import type { ReactNode, CSSProperties, HTMLAttributes } from 'react';

/** 基础组件Props */
export interface BaseComponentProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
  id?: string;
  'data-testid'?: string;
}

/** 可禁用组件Props */
export interface DisableableProps {
  disabled?: boolean;
}

/** 可点击组件Props */
export interface ClickableProps {
  onClick?: (event: React.MouseEvent) => void;
}

/** 表单控件Props */
export interface FormControlProps extends BaseComponentProps, DisableableProps {
  name?: string;
  required?: boolean;
  error?: string;
}

/** HTML属性扩展类型 */
export type HTMLProps<T extends HTMLElement> = HTMLAttributes<T> & {
  as?: keyof JSX.IntrinsicElements;
};
```

- [ ] **Step 4: 创建utils.ts - 工具类型**

```typescript
// frontend/src/shared/ui/types/utils.ts

/** 提取Props类型 */
export type PropsOf<T> = T extends React.ComponentType<infer P> ? P : never;

/** 使Props可选 */
export type PartialProps<T> = Partial<T>;

/** 使Props必选 */
export type RequiredProps<T> = Required<T>;

/** 提取特定属性 */
export type PickProps<T, K extends keyof T> = Pick<T, K>;

/** 排除特定属性 */
export type OmitProps<T, K extends keyof T> = Omit<T, K>;

/** 条件类型 */
export type If<T, Condition, True, False> = T extends Condition ? True : False;

/** 事件处理器类型 */
export type EventHandler<E = Event> = (event: E) => void;
```

- [ ] **Step 5: 创建index.ts - 统一导出**

```typescript
// frontend/src/shared/ui/types/index.ts

export * from './common';
export * from './components';
export * from './utils';
```

- [ ] **Step 6: 更新组件导入类型**

在需要使用公共类型的组件中导入：

```typescript
import type { BaseComponentProps, Size, Variant } from '../types';
```

- [ ] **Step 7: 验证any类型数量归零**

Run: `grep -r ": any" frontend/src/shared/ui --include="*.tsx" --include="*.ts" | wc -l`
Expected: 0

- [ ] **Step 8: 运行TypeScript编译检查**

Run: `cd frontend && npm run type-check`
Expected: 无类型错误

- [ ] **Step 9: 提交更改**

```bash
git add frontend/src/shared/ui/types
git commit -m "feat(ui): add shared type definitions (common, components, utils)"
```

---

### 阶段 1 验收

- [ ] **验收 1: 运行完整测试套件**

Run: `cd frontend && npm test -- --run`
Expected: 所有测试通过

- [ ] **验收 2: TypeScript严格模式编译通过**

Run: `cd frontend && npm run type-check`
Expected: 无错误

- [ ] **验收 3: any类型数量为零**

Run: `grep -r ": any" frontend/src/shared/ui --include="*.tsx" --include="*.ts" | wc -l`
Expected: 0

- [ ] **验收 4: 创建阶段tag**

```bash
git tag -a v1.0.0-phase1-types -m "Phase 1: Type Safety Complete"
git push origin v1.0.0-phase1-types
```

---

## 阶段 2：错误处理增强

**目标:** 统一错误处理模式，增强组件健壮性

**预计时间:** 1.5-2小时

### Task 2.1: Error Boundary优化

**Files:**
- Modify: `frontend/src/shared/ui/ErrorBoundary.tsx`
- Modify: `frontend/src/shared/ui/CanvasErrorBoundary.tsx`
- Create: `frontend/src/shared/ui/ErrorBoundary/types.ts`
- Create: `frontend/src/shared/ui/ErrorBoundary/ErrorBoundary.test.tsx`

- [ ] **Step 1: 创建Error Boundary类型定义**

```typescript
// frontend/src/shared/ui/ErrorBoundary/types.ts

export interface ErrorInfo {
  componentStack: string;
  errorBoundary?: string;
}

export interface FallbackProps {
  error: Error;
  errorInfo: ErrorInfo;
  resetErrorBoundary: () => void;
}

export interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode | ((props: FallbackProps) => React.ReactNode);
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  onReset?: () => void;
  resetKeys?: unknown[];
}
```

- [ ] **Step 2: 优化ErrorBoundary组件**

更新ErrorBoundary.tsx，添加错误日志记录和恢复机制：

```typescript
// frontend/src/shared/ui/ErrorBoundary.tsx

import React from 'react';
import type { ErrorBoundaryProps, FallbackProps } from './types';

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, State> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // 记录错误日志
    console.error('ErrorBoundary caught:', error, errorInfo);
    
    // 调用外部错误处理器
    this.props.onError?.(error, { componentStack: errorInfo.componentStack });
    
    this.setState({ errorInfo });
  }

  handleReset = (): void => {
    this.props.onReset?.();
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render(): React.ReactNode {
    if (this.state.hasError) {
      const { fallback } = this.props;
      
      if (typeof fallback === 'function') {
        return fallback({
          error: this.state.error!,
          errorInfo: { componentStack: this.state.errorInfo?.componentStack || '' },
          resetErrorBoundary: this.handleReset,
        });
      }
      
      return fallback || (
        <div className="error-boundary-fallback">
          <h2>Something went wrong</h2>
          <button onClick={this.handleReset}>Try again</button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

- [ ] **Step 3: 优化CanvasErrorBoundary组件**

类似方式优化CanvasErrorBoundary.tsx

- [ ] **Step 4: 添加Error Boundary测试**

创建或更新测试文件

- [ ] **Step 5: 运行测试**

Run: `cd frontend && npm test -- --run ErrorBoundary`
Expected: 所有测试通过

- [ ] **Step 6: 提交更改**

```bash
git add frontend/src/shared/ui/ErrorBoundary frontend/src/shared/ui/CanvasErrorBoundary.tsx
git commit -m "feat(ui): enhance ErrorBoundary with logging and recovery"
```

---

### Task 2.2: 表单验证错误处理

**Files:**
- Modify: `frontend/src/shared/ui/components/Form/Form.tsx`
- Modify: `frontend/src/shared/ui/components/Form/FormInput.tsx`
- Modify: `frontend/src/shared/ui/components/Form/FormSelect.tsx`
- Create: `frontend/src/shared/ui/components/Form/validation.ts`

- [ ] **Step 1: 创建统一验证错误格式**

```typescript
// frontend/src/shared/ui/components/Form/validation.ts

export interface ValidationError {
  field: string;
  message: string;
  type: 'required' | 'format' | 'range' | 'custom';
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

export type Validator = (value: unknown, fieldName: string) => ValidationError | null;

export const required: Validator = (value, fieldName) => {
  if (value === undefined || value === null || value === '') {
    return { field: fieldName, message: `${fieldName} is required`, type: 'required' };
  }
  return null;
};

export const email: Validator = (value, fieldName) => {
  if (typeof value === 'string' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    return { field: fieldName, message: 'Invalid email format', type: 'format' };
  }
  return null;
};

export const minLength = (min: number): Validator => (value, fieldName) => {
  if (typeof value === 'string' && value.length < min) {
    return { field: fieldName, message: `${fieldName} must be at least ${min} characters`, type: 'range' };
  }
  return null;
};

export function validate(value: unknown, validators: Validator[], fieldName: string): ValidationError[] {
  return validators
    .map(validator => validator(value, fieldName))
    .filter((error): error is ValidationError => error !== null);
}
```

- [ ] **Step 2: 更新Form组件支持新验证**

更新Form.tsx使用新的验证系统

- [ ] **Step 3: 更新FormInput组件**

更新FormInput.tsx使用新的验证错误显示

- [ ] **Step 4: 更新FormSelect组件**

更新FormSelect.tsx使用新的验证错误显示

- [ ] **Step 5: 运行测试**

Run: `cd frontend && npm test -- --run Form`
Expected: 所有测试通过

- [ ] **Step 6: 提交更改**

```bash
git add frontend/src/shared/ui/components/Form
git commit -m "feat(ui): add unified form validation error handling"
```

---

### Task 2.3: 异步操作错误处理

**Files:**
- Create: `frontend/src/shared/hooks/useErrorHandler.ts`
- Create: `frontend/src/shared/hooks/useAsyncAction.ts`
- Create: `frontend/src/shared/hooks/index.ts`
- Modify: `frontend/src/shared/ui/Toast/Toast.tsx`

- [ ] **Step 1: 创建useErrorHandler Hook**

```typescript
// frontend/src/shared/hooks/useErrorHandler.ts

import { useCallback, useState } from 'react';

export interface ErrorHandlerOptions {
  onRetry?: () => void;
  maxRetries?: number;
  showToast?: boolean;
}

export interface ErrorHandlerState {
  error: Error | null;
  retryCount: number;
}

export function useErrorHandler(options: ErrorHandlerOptions = {}) {
  const { onRetry, maxRetries = 3, showToast = true } = options;
  const [state, setState] = useState<ErrorHandlerState>({
    error: null,
    retryCount: 0,
  });

  const handleError = useCallback((error: Error) => {
    console.error('Error caught:', error);
    setState(prev => ({ ...prev, error }));
    
    if (showToast) {
      // 显示Toast错误提示
      // toast.error(error.message);
    }
  }, [showToast]);

  const retry = useCallback(() => {
    if (state.retryCount < maxRetries && onRetry) {
      setState(prev => ({ ...prev, retryCount: prev.retryCount + 1 }));
      onRetry();
    }
  }, [state.retryCount, maxRetries, onRetry]);

  const reset = useCallback(() => {
    setState({ error: null, retryCount: 0 });
  }, []);

  return {
    error: state.error,
    retryCount: state.retryCount,
    canRetry: state.retryCount < maxRetries,
    handleError,
    retry,
    reset,
  };
}
```

- [ ] **Step 2: 创建useAsyncAction Hook**

```typescript
// frontend/src/shared/hooks/useAsyncAction.ts

import { useCallback, useState } from 'react';

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useAsyncAction<T>(
  asyncFn: () => Promise<T>,
  options: { onSuccess?: (data: T) => void; onError?: (error: Error) => void } = {}
) {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await asyncFn();
      setState({ data, loading: false, error: null });
      options.onSuccess?.(data);
      return data;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      setState(prev => ({ ...prev, loading: false, error: err }));
      options.onError?.(err);
      throw err;
    }
  }, [asyncFn, options]);

  return { ...state, execute };
}
```

- [ ] **Step 3: 更新Toast组件支持错误类型**

更新Toast.tsx添加错误类型支持

- [ ] **Step 4: 运行测试**

Run: `cd frontend && npm test -- --run hooks`
Expected: 所有测试通过

- [ ] **Step 5: 提交更改**

```bash
git add frontend/src/shared/hooks frontend/src/shared/ui/Toast
git commit -m "feat(hooks): add useErrorHandler and useAsyncAction hooks"
```

---

### 阶段 2 验收

- [ ] **验收 1: 运行完整测试套件**

Run: `cd frontend && npm test -- --run`
Expected: 所有测试通过

- [ ] **验收 2: TypeScript编译通过**

Run: `cd frontend && npm run type-check`
Expected: 无错误

- [ ] **验收 3: 创建阶段tag**

```bash
git tag -a v1.0.0-phase2-error-handling -m "Phase 2: Error Handling Complete"
git push origin v1.0.0-phase2-error-handling
```

---

## 阶段 3：性能优化

**目标:** 优化渲染性能，减少不必要的重渲染

**预计时间:** 2-2.5小时

### Task 3.1: React性能优化

**Files:**
- Modify: 所有组件文件（按需）

- [ ] **Step 1: 分析当前性能基准**

Run: `cd frontend && npm run build && npm run analyze`
Expected: 生成Bundle分析报告

- [ ] **Step 2: 检查React.memo使用情况**

Run: `grep -r "React.memo" frontend/src/shared/ui --include="*.tsx" | wc -l`
Expected: 了解当前使用情况

- [ ] **Step 3: 为频繁渲染的组件添加React.memo**

识别需要优化的组件，添加React.memo：

```typescript
// 示例：使用React.memo优化
const MyComponent = React.memo(function MyComponent(props: MyComponentProps) {
  // 组件实现
}, (prevProps, nextProps) => {
  // 自定义比较函数（可选）
  return prevProps.value === nextProps.value;
});
```

- [ ] **Step 4: 优化useMemo和useCallback使用**

检查并添加useMemo/useCallback：

```typescript
// 示例：使用useMemo优化计算
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// 示例：使用useCallback优化回调
const handleClick = useCallback((id: string) => {
  onItemClick(id);
}, [onItemClick]);
```

- [ ] **Step 5: 优化Context使用**

检查并优化Context，避免不必要的重渲染：

```typescript
// 示例：分离Context值和dispatch
const DataContext = createContext<Data | null>(null);
const DataDispatchContext = createContext<DataDispatch | null>(null);
```

- [ ] **Step 6: 运行性能测试**

Run: `cd frontend && npm run test:perf`
Expected: 性能指标满足要求

- [ ] **Step 7: 提交更改**

```bash
git add frontend/src/shared/ui
git commit -m "perf(ui): optimize React performance with memo, useMemo, useCallback"
```

---

### Task 3.2: 列表和表格性能

**Files:**
- Modify: `frontend/src/shared/ui/components/Table/Table.tsx`
- Modify: `frontend/src/shared/ui/Pagination/Pagination.tsx`
- Create: `frontend/src/shared/ui/components/Table/VirtualTable.tsx`

- [ ] **Step 1: 创建虚拟滚动Table组件**

```typescript
// frontend/src/shared/ui/components/Table/VirtualTable.tsx

import React, { useMemo, useCallback } from 'react';
import type { TableProps } from './types';

interface VirtualTableProps<T> extends Omit<TableProps<T>, 'virtualScroll'> {
  rowHeight: number;
  visibleRows: number;
}

export function VirtualTable<T extends { id: string | number }>({
  data,
  columns,
  rowHeight,
  visibleRows,
  ...props
}: VirtualTableProps<T>) {
  const [scrollTop, setScrollTop] = React.useState(0);
  
  const startIndex = Math.floor(scrollTop / rowHeight);
  const endIndex = Math.min(startIndex + visibleRows, data.length);
  
  const visibleData = useMemo(
    () => data.slice(startIndex, endIndex),
    [data, startIndex, endIndex]
  );
  
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);
  
  return (
    <div
      className="virtual-table-container"
      style={{ height: visibleRows * rowHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: data.length * rowHeight, position: 'relative' }}>
        <table style={{ position: 'absolute', top: startIndex * rowHeight }}>
          <tbody>
            {visibleData.map((row) => (
              <tr key={row.id} style={{ height: rowHeight }}>
                {columns.map((col) => (
                  <td key={String(col.key)}>{col.render?.(row) ?? String(row[col.key as keyof T])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 为Table组件添加虚拟滚动选项**

更新Table.tsx添加虚拟滚动支持

- [ ] **Step 3: 优化Pagination组件**

添加防抖和虚拟渲染优化

- [ ] **Step 4: 创建性能基准测试**

```typescript
// frontend/src/shared/ui/components/Table/__tests__/Table.perf.test.ts

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Table } from '../Table';

describe('Table Performance', () => {
  it('should render 1000 rows in less than 100ms', () => {
    const data = Array.from({ length: 1000 }, (_, i) => ({ id: i, name: `Item ${i}` }));
    const columns = [{ key: 'name', title: 'Name' }];
    
    const start = performance.now();
    render(<Table data={data} columns={columns} />);
    const end = performance.now();
    
    expect(end - start).toBeLessThan(100);
  });
});
```

- [ ] **Step 5: 运行性能测试**

Run: `cd frontend && npm test -- --run Table.perf`
Expected: 性能测试通过

- [ ] **Step 6: 提交更改**

```bash
git add frontend/src/shared/ui/components/Table frontend/src/shared/ui/Pagination
git commit -m "perf(ui): add virtual scrolling for large tables"
```

---

### Task 3.3: Bundle优化

**Files:**
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/package.json`

- [ ] **Step 1: 分析当前Bundle大小**

Run: `cd frontend && npm run build && ls -la dist/assets`
Expected: 查看当前构建产物大小

- [ ] **Step 2: 配置Vite代码分割**

```typescript
// frontend/vite.config.ts

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: [
            // 组件库相关依赖
          ],
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
});
```

- [ ] **Step 3: 优化Tree Shaking**

确保所有导出使用ESM格式，避免副作用

- [ ] **Step 4: 配置依赖预构建**

优化Vite的依赖预构建配置

- [ ] **Step 5: 重新构建并验证**

Run: `cd frontend && npm run build && npm run analyze`
Expected: Bundle大小减少>20%

- [ ] **Step 6: 提交更改**

```bash
git add frontend/vite.config.ts frontend/package.json
git commit -m "perf(build): optimize bundle size with code splitting"
```

---

### 阶段 3 验收

- [ ] **验收 1: 运行完整测试套件**

Run: `cd frontend && npm test -- --run`
Expected: 所有测试通过

- [ ] **验收 2: TypeScript编译通过**

Run: `cd frontend && npm run type-check`
Expected: 无错误

- [ ] **验收 3: Bundle大小减少验证**

Run: `cd frontend && npm run build && du -sh dist`
Expected: Bundle大小减少>20%

- [ ] **验收 4: 创建阶段tag**

```bash
git tag -a v1.0.0-phase3-performance -m "Phase 3: Performance Optimization Complete"
git push origin v1.0.0-phase3-performance
```

---

## 阶段 4：代码质量提升

**目标:** 消除重复代码，降低复杂度

**预计时间:** 1.5-2小时

### Task 4.1: 重复代码消除

**Files:**
- Modify: `frontend/src/shared/hooks/`（公共hooks）
- Modify: `frontend/src/shared/utils/`（公共工具）

- [ ] **Step 1: 运行重复代码检测**

Run: `npx jscpd frontend/src/shared/ui --min-lines 10 --reporters console`
Expected: 识别重复代码块

- [ ] **Step 2: 提取公共Hooks**

创建可复用的自定义Hooks：

```typescript
// frontend/src/shared/hooks/useToggle.ts

import { useCallback, useState } from 'react';

export function useToggle(initialValue = false): [boolean, () => void, (value: boolean) => void] {
  const [value, setValue] = useState(initialValue);
  
  const toggle = useCallback(() => setValue(v => !v), []);
  const set = useCallback((newValue: boolean) => setValue(newValue), []);
  
  return [value, toggle, set];
}
```

```typescript
// frontend/src/shared/hooks/useDebounce.ts

import { useEffect, useState } from 'react';

export function useDebounce<T>(value: T, delay = 300): T {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  
  return debouncedValue;
}
```

- [ ] **Step 3: 提取公共工具函数**

```typescript
// frontend/src/shared/utils/classNames.ts

export function classNames(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
```

```typescript
// frontend/src/shared/utils/format.ts

export function formatDate(date: Date | string, format = 'YYYY-MM-DD'): string {
  // 格式化实现
}

export function formatNumber(num: number, options?: Intl.NumberFormatOptions): string {
  return new Intl.NumberFormat('zh-CN', options).format(num);
}
```

- [ ] **Step 4: 运行重复代码检测验证**

Run: `npx jscpd frontend/src/shared/ui --min-lines 10 --reporters console`
Expected: 代码重复率<5%

- [ ] **Step 5: 提交更改**

```bash
git add frontend/src/shared/hooks frontend/src/shared/utils
git commit -m "refactor(ui): extract common hooks and utils to reduce code duplication"
```

---

### Task 4.2: 复杂度降低

**Files:**
- Modify: `frontend/src/shared/ui/components/Table/Table.tsx`
- Modify: `frontend/src/shared/ui/components/Form/Form.tsx`
- Modify: `frontend/src/shared/ui/components/Modal/Modal.tsx`

- [ ] **Step 1: 检查当前圈复杂度**

Run: `npx eslint frontend/src/shared/ui --rule 'complexity: error' --format json | jq '.[].messages | length'`
Expected: 了解当前复杂度情况

- [ ] **Step 2: 拆分Table组件**

将Table组件拆分为更小的子组件：

**Files:**
- Create: `frontend/src/shared/ui/components/Table/TableHeader.tsx`
- Create: `frontend/src/shared/ui/components/Table/TableBody.tsx`
- Create: `frontend/src/shared/ui/components/Table/TableRow.tsx`
- Create: `frontend/src/shared/ui/components/Table/TableFooter.tsx`
- Modify: `frontend/src/shared/ui/components/Table/Table.tsx`

```typescript
// frontend/src/shared/ui/components/Table/TableHeader.tsx
export function TableHeader<T>({ columns }: { columns: ColumnDef<T>[] }) {
  return (
    <thead>
      <tr>
        {columns.map((col) => (
          <th key={String(col.key)}>{col.title}</th>
        ))}
      </tr>
    </thead>
  );
}

// frontend/src/shared/ui/components/Table/TableBody.tsx
export function TableBody<T extends { id: string | number }>({
  data,
  columns,
  onRowClick,
}: {
  data: T[];
  columns: ColumnDef<T>[];
  onRowClick?: (row: T) => void;
}) {
  return (
    <tbody>
      {data.map((row) => (
        <TableRow key={row.id} row={row} columns={columns} onRowClick={onRowClick} />
      ))}
    </tbody>
  );
}
```

- [ ] **Step 3: 拆分Form组件**

将Form组件拆分为更小的子组件

- [ ] **Step 4: 拆分Modal组件**

将Modal组件拆分为更小的子组件

- [ ] **Step 5: 运行ESLint检查**

Run: `cd frontend && npm run lint`
Expected: 无复杂度警告

- [ ] **Step 6: 提交更改**

```bash
git add frontend/src/shared/ui/components/Table frontend/src/shared/ui/components/Form frontend/src/shared/ui/components/Modal
git commit -m "refactor(ui): reduce complexity by splitting large components"
```

---

### Task 4.3: 代码规范统一

**Files:**
- Modify: 所有组件文件（按需）

- [ ] **Step 1: 统一命名规范**

确保所有组件遵循命名规范：
- 组件文件：PascalCase.tsx
- Hook文件：camelCase.ts
- 工具文件：camelCase.ts
- 类型文件：camelCase.ts

- [ ] **Step 2: 统一文件结构**

确保所有组件遵循统一结构：
```
ComponentName/
├── ComponentName.tsx
├── ComponentName.module.css
├── index.ts
├── types.ts
└── __tests__/
    └── ComponentName.test.tsx
```

- [ ] **Step 3: 统一Props定义**

确保所有组件Props遵循统一模式：

```typescript
interface ComponentNameProps extends BaseComponentProps {
  // 必需属性
  requiredProp: string;
  
  // 可选属性（带默认值）
  optionalProp?: boolean;
  
  // 回调函数
  onCallback?: (value: string) => void;
}
```

- [ ] **Step 4: 添加JSDoc注释**

为所有公共API添加JSDoc：

```typescript
/**
 * Button组件 - 通用按钮组件
 * 
 * @example
 * ```tsx
 * <Button variant="primary" onClick={handleClick}>
 *   Click me
 * </Button>
 * ```
 */
export function Button(props: ButtonProps): JSX.Element {
  // ...
}
```

- [ ] **Step 5: 提交更改**

```bash
git add frontend/src/shared/ui
git commit -m "style(ui): unify code style and add JSDoc comments"
```

---

### 阶段 4 验收

- [ ] **验收 1: 运行完整测试套件**

Run: `cd frontend && npm test -- --run`
Expected: 所有测试通过

- [ ] **验收 2: 代码重复率检测**

Run: `npx jscpd frontend/src/shared/ui --min-lines 10 --reporters console`
Expected: 代码重复率<5%

- [ ] **验收 3: 圈复杂度检测**

Run: `cd frontend && npm run lint`
Expected: 无复杂度警告

- [ ] **验收 4: 创建阶段tag**

```bash
git tag -a v1.0.0-phase4-quality -m "Phase 4: Code Quality Complete"
git push origin v1.0.0-phase4-quality
```

---

## 阶段 5：工程化建设

**目标:** 建立自动化质量保障体系

**预计时间:** 2-2.5小时

### Task 5.1: ESLint和Prettier配置优化

**Files:**
- Modify: `config/.eslintrc.yml`
- Modify: `config/.prettierrc`
- Modify: `frontend/.prettierrc`
- Create: `.husky/pre-commit`

- [ ] **Step 1: 检查当前ESLint错误数量**

Run: `cd frontend && npm run lint 2>&1 | grep -E "error|warning" | tail -5`
Expected: 了解当前错误数量（2654个错误，1438个警告）

- [ ] **Step 2: 修复ESLint错误（批量）**

Run: `cd frontend && npm run lint -- --fix`
Expected: 自动修复可修复的错误

- [ ] **Step 3: 修复剩余ESLint错误（手动）**

针对无法自动修复的错误，逐个组件手动修复

- [ ] **Step 4: 统一Prettier配置**

合并config和frontend的Prettier配置：

```json
// config/.prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always"
}
```

- [ ] **Step 5: 安装并配置Husky**

```bash
npm install husky --save-dev
npx husky init
echo "npm run lint" > .husky/pre-commit
chmod +x .husky/pre-commit
```

- [ ] **Step 6: 验证pre-commit hook**

Run: `ls .husky/ && cat .husky/pre-commit`
Expected: 文件存在且内容正确

- [ ] **Step 7: 提交更改**

```bash
git add config/.eslintrc.yml config/.prettierrc frontend/.prettierrc .husky
git commit -m "chore: fix ESLint errors, unify Prettier config, add Husky pre-commit hooks"
```

---

### Task 5.2: 测试覆��率提升

**Files:**
- Modify: 所有`__tests__`目录下的测试文件

- [ ] **Step 1: 检查当前测试覆盖率**

Run: `cd frontend && npm run test:coverage`
Expected: 了解当前覆盖率（约80%）

- [ ] **Step 2: 识别未覆盖的代码**

查看覆盖率报告，识别覆盖率低于阈值的模块

- [ ] **Step 3: 补充单元测试**

为未覆盖的代码补充单元测试

- [ ] **Step 4: 添加集成测试**

添加跨组件的集成测试

- [ ] **Step 5: 添加边界测试**

添加边界情况和异常情况的测试

- [ ] **Step 6: 验证覆盖率达标**

Run: `cd frontend && npm run test:coverage`
Expected: 覆盖率>90%

- [ ] **Step 7: 提交更改**

```bash
git add frontend/src/shared/ui
git commit -m "test(ui): increase test coverage to >90%"
```

---

### Task 5.3: CI/CD集成优化

**Files:**
- Modify: `.github/workflows/ci-cd.yml`
- Modify: `.github/workflows/frontend-ci.yml`
- Create: `.github/workflows/quality-check.yml`

- [ ] **Step 1: 分析现有workflow文件**

Run: `ls .github/workflows/`
Expected: 查看现有workflow文件列表

- [ ] **Step 2: 创建质量门禁workflow**

```yaml
# .github/workflows/quality-check.yml

name: Quality Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  quality:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Type check
        working-directory: ./frontend
        run: npm run type-check
      
      - name: Lint
        working-directory: ./frontend
        run: npm run lint
      
      - name: Test with coverage
        working-directory: ./frontend
        run: npm run test:coverage
      
      - name: Check coverage threshold
        working-directory: ./frontend
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 90" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 90% threshold"
            exit 1
          fi
          echo "Coverage $COVERAGE% meets threshold"
      
      - name: Build
        working-directory: ./frontend
        run: npm run build
      
      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: frontend/coverage/
```

- [ ] **Step 3: 优化现有frontend-ci.yml**

添加质量门禁依赖

- [ ] **Step 4: 提交更改**

```bash
git add .github/workflows
git commit -m "ci: add quality gate workflow with coverage threshold"
```

---

### 阶段 5 验收

- [ ] **验收 1: ESLint零错误零警告**

Run: `cd frontend && npm run lint`
Expected: 无错误无警告

- [ ] **验收 2: 测试覆盖率达标**

Run: `cd frontend && npm run test:coverage`
Expected: 覆盖率>90%

- [ ] **验收 3: pre-commit hook正常工作**

```bash
echo "test" >> README.md
git add README.md
git commit -m "test: trigger pre-commit"
# 应该触发npm run lint
git reset --hard HEAD~1
```
Expected: pre-commit hook触发lint检查

- [ ] **验收 4: 创建阶段tag**

```bash
git tag -a v1.0.0-phase5-engineering -m "Phase 5: Engineering Complete"
git push origin v1.0.0-phase5-engineering
```

---

## 阶段 6：文档完善

**目标:** 完善所有文档，建立知识库

**预计时间:** 1.5-2小时

### Task 6.1: API文档

**Files:**
- Modify: `frontend/src/shared/ui/README.md`
- Create: `frontend/src/shared/ui/docs/`
- Create: `frontend/src/shared/ui/docs/api/`

- [ ] **Step 1: 创建文档目录结构**

Run: `mkdir -p frontend/src/shared/ui/docs/api`
Expected: 目录创建成功

- [ ] **Step 2: 为每个组件生成API文档**

为每个组件创建独立的API文档：

```markdown
<!-- frontend/src/shared/ui/docs/api/Button.md -->

# Button

按钮组件，用于触发操作。

## Props

| 属性 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| variant | 'primary' \| 'secondary' \| 'outline' \| 'ghost' | 否 | 'primary' | 按钮变体 |
| size | 'small' \| 'medium' \| 'large' | 否 | 'medium' | 按钮尺寸 |
| disabled | boolean | 否 | false | 是否禁用 |
| loading | boolean | 否 | false | 是否显示加载状态 |
| onClick | (event: MouseEvent) => void | 否 | - | 点击回调 |

## 示例

### 基础用法

\`\`\`tsx
<Button variant="primary" onClick={handleClick}>
  点击我
</Button>
\`\`\`

### 加载状态

\`\`\`tsx
<Button loading>提交中...</Button>
\`\`\`
```

- [ ] **Step 3: 更新组件库README**

更新README.md作为文档索引

- [ ] **Step 4: 创建API索引**

创建所有组件的API索引页面

- [ ] **Step 5: 提交更改**

```bash
git add frontend/src/shared/ui/docs frontend/src/shared/ui/README.md
git commit -m "docs(ui): add comprehensive API documentation for all components"
```

---

### Task 6.2: 开发规范文档

**Files:**
- Create: `docs/frontend/CONTRIBUTING.md`
- Create: `docs/frontend/CODING_STANDARDS.md`
- Create: `docs/frontend/TESTING_GUIDE.md`

- [ ] **Step 1: 创建docs/frontend目录**

Run: `mkdir -p docs/frontend`
Expected: 目录创建成功

- [ ] **Step 2: 编写CONTRIBUTING.md**

```markdown
<!-- docs/frontend/CONTRIBUTING.md -->

# 贡献指南

## 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 提交规范

使用 Conventional Commits 格式：

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式化
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 代码审查

所有 PR 必须通过：
- ESLint 检查
- 类型检查
- 单元测试
- 覆盖率检查 (>90%)
```

- [ ] **Step 3: 编写CODING_STANDARDS.md**

```markdown
<!-- docs/frontend/CODING_STANDARDS.md -->

# 编码规范

## TypeScript

- 启用严格模式
- 禁止使用 any 类型
- 所有公共 API 必须有类型定义
- 使用 interface 定义 Props
- 使用 type 定义联合类型

## 组件开发

### 命名规范

- 组件文件：PascalCase.tsx
- Hook 文件：camelCase.ts
- 工具文件：camelCase.ts

### 文件结构

\`\`\`
ComponentName/
├── ComponentName.tsx
├── ComponentName.module.css
├── index.ts
├── types.ts
└── __tests__/
    └── ComponentName.test.tsx
\`\`\`

### Props 定义

\`\`\`typescript
interface ComponentProps extends BaseComponentProps {
  // 必需属性在前
  requiredProp: string;
  
  // 可选属性在后
  optionalProp?: boolean;
  
  // 回调函数最后
  onCallback?: (value: string) => void;
}
\`\`\`
```

- [ ] **Step 4: 编写TESTING_GUIDE.md**

```markdown
<!-- docs/frontend/TESTING_GUIDE.md -->

# 测试指南

## 测试框架

使用 Vitest + React Testing Library

## 测试结构

\`\`\`typescript
describe('ComponentName', () => {
  describe('rendering', () => {
    it('should render correctly', () => {
      // 测试基本渲染
    });
  });
  
  describe('interaction', () => {
    it('should handle click', () => {
      // 测试交互
    });
  });
  
  describe('accessibility', () => {
    it('should be accessible', () => {
      // 测试可访问性
    });
  });
});
\`\`\`

## 覆盖率要求

- 语句覆盖率：>90%
- 分支覆盖率：>80%
- 函数覆盖率：>90%
- 行覆盖率：>90%
```

- [ ] **Step 5: 提交更改**

```bash
git add docs/frontend
git commit -m "docs: add contributing guide, coding standards, and testing guide"
```

---

### Task 6.3: 示例和Demo

**Files:**
- Modify: `frontend/src/shared/ui/__showcase__/`

- [ ] **Step 1: 检查现有showcase目录**

Run: `ls frontend/src/shared/ui/__showcase__/`
Expected: 了解现有示例

- [ ] **Step 2: 为每个组件创建示例**

创建或更新每个组件的示例文件

- [ ] **Step 3: 创建使用案例文档**

创建常见使用案例的示例

- [ ] **Step 4: 创建常见问题解答**

```markdown
<!-- frontend/src/shared/ui/docs/FAQ.md -->

# 常见问题

## 如何自定义样式？

使用 className 属性或 CSS Modules...

## 如何处理表单验证？

使用 Form 组件的验证功能...
```

- [ ] **Step 5: 创建故障排查指南**

```markdown
<!-- frontend/src/shared/ui/docs/TROUBLESHOOTING.md -->

# 故障排查

## 组件不渲染

检查以下几点：
1. Props 是否正确传递
2. 是否有条件渲染阻止了显示
3. 控制台是否有错误

## 样式不生效

检查以下几点：
1. CSS 文件是否正确导入
2. className 是否正确
3. 是否有样式冲突
```

- [ ] **Step 6: 提交更改**

```bash
git add frontend/src/shared/ui/__showcase__ frontend/src/shared/ui/docs
git commit -m "docs(ui): add examples, FAQ, and troubleshooting guide"
```

---

### 阶段 6 验收

- [ ] **验收 1: 所有组件有API文档**

Run: `ls frontend/src/shared/ui/docs/api/ | wc -l`
Expected: 文档数量与组件数量匹配

- [ ] **验收 2: 开发规范文档完整**

Run: `ls docs/frontend/`
Expected: CONTRIBUTING.md, CODING_STANDARDS.md, TESTING_GUIDE.md 存在

- [ ] **验收 3: 示例覆盖完整**

Run: `ls frontend/src/shared/ui/__showcase__/`
Expected: 每个组件都有示例

- [ ] **验收 4: 创建最终版本tag**

```bash
git tag -a v1.0.0 -m "Component Quality Improvement Complete"
git push origin v1.0.0
```

---

## 最终验收

### 代码质量指标

- [ ] **验收 1: TypeScript严格模式通过**

Run: `cd frontend && npm run type-check`
Expected: 无错误

- [ ] **验收 2: any类型数量为零**

Run: `grep -r ": any" frontend/src/shared/ui --include="*.tsx" --include="*.ts" | wc -l`
Expected: 0

- [ ] **验收 3: ESLint零错误零警告**

Run: `cd frontend && npm run lint`
Expected: 无错误无警告

- [ ] **验收 4: 测试覆盖率>90%**

Run: `cd frontend && npm run test:coverage`
Expected: 覆盖率>90%

### 工程化指标

- [ ] **验收 5: pre-commit hooks配置完成**

Run: `ls .husky/`
Expected: pre-commit 文件存在

- [ ] **验收 6: CI/CD质量门禁配置完成**

Run: `cat .github/workflows/quality-check.yml`
Expected: workflow 文件存在且配置正确

### 文档完整性

- [ ] **验收 7: API文档覆盖100%**

Run: `ls frontend/src/shared/ui/docs/api/ | wc -l`
Expected: 所有组件都有文档

- [ ] **验收 8: 开发规范文档完善**

Run: `ls docs/frontend/`
Expected: 所有规范文档存在

---

## 参考资源

- [Spec Document](../specs/2026-03-22-component-quality-improvement-design.md)
- [TypeScript官方文档](https://www.typescriptlang.org/docs/)
- [React官方文档](https://react.dev/)
- [Vitest文档](https://vitest.dev/)
- [ESLint文档](https://eslint.org/)
