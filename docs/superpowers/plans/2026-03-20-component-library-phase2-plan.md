# 组件库现代化第二阶段实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成Event2Table组件库的迁移统一、性能优化、功能增强和组件扩展

**Architecture:** 四阶段并行开发，每阶段3个subagent并行执行，保持Cyberpunk Lab Theme设计风格

**Tech Stack:** React 18, TypeScript, TanStack Table, TanStack Virtual, React Hook Form, Zod, Vitest, Playwright

**Spec Document:** `docs/superpowers/specs/2026-03-20-component-library-phase2-design.md`

---

## 文件结构

### 新增文件
```
frontend/src/shared/ui/components/
├── Select/
│   ├── Select.tsx
│   ├── Select.types.ts
│   ├── Select.css
│   ├── Select.test.tsx
│   └── index.ts
├── DatePicker/
│   ├── DatePicker.tsx
│   ├── DatePicker.types.ts
│   ├── DatePicker.css
│   ├── DatePicker.test.tsx
│   └── index.ts
├── Form/
│   ├── FormDatePicker.tsx
│   ├── FormUpload.tsx
│   ├── FormRichText.tsx
│   └── *.test.tsx
└── Modal/
    └── Modal.css (修改)

frontend/src/shared/hooks/
├── useDraggable.ts
├── usePerformanceMonitor.ts
└── useDebouncedValidation.ts

frontend/src/shared/utils/
└── validationCache.ts

scripts/
├── migrate-modal.ts
├── migrate-table.ts
├── batch-transform.ts
└── migration-tool/

.github/workflows/
└── component-tests.yml
```

### 修改文件
```
frontend/src/shared/ui/index.ts
frontend/src/shared/ui/components/Modal/Modal.tsx
frontend/src/shared/ui/components/Modal/Modal.css
frontend/src/shared/ui/components/Table/Table.tsx
frontend/src/shared/ui/components/Form/Form.tsx
frontend/src/shared/ui/BaseModal/ (废弃)
frontend/src/shared/ui/Table/ (废弃)
frontend/src/shared/ui/Select/ (迁移)
```

---

## 阶段1：迁移与统一 (2周)

### 任务1.1：Modal迁移

**Files:**
- Modify: `frontend/src/shared/ui/index.ts`
- Modify: `frontend/src/shared/ui/BaseModal/BaseModal.tsx`
- Create: `scripts/migrate-modal.ts`
- Test: `frontend/src/shared/ui/components/Modal/Modal.migration.test.tsx`

#### 步骤1.1.1：分析BaseModal使用情况

- [ ] **Step 1: 搜索所有使用BaseModal的文件**

Run: `grep -r "from.*BaseModal" frontend/src --include="*.tsx" --include="*.ts" | cat`

Expected: 列出所有使用BaseModal的文件

- [ ] **Step 2: 搜索所有使用Modal的文件**

Run: `grep -r "from.*Modal" frontend/src --include="*.tsx" --include="*.ts" | grep -v "BaseModal" | cat`

Expected: 列出所有使用新Modal的文件

#### 步骤1.1.2：更新导出文件

- [ ] **Step 3: 读取当前index.ts内容**

Run: `read_file frontend/src/shared/ui/index.ts`

- [ ] **Step 4: 更新index.ts添加兼容导出**

在index.ts中添加：

```typescript
// Modal exports
export { Modal } from './components/Modal/Modal';
export type { ModalProps, ModalSize, ModalAnimation, ModalVariant } from './components/Modal/Modal.types';

// Backward compatibility - BaseModal alias
/**
 * @deprecated Use Modal instead. Will be removed in v3.0.0
 */
export { Modal as BaseModal } from './components/Modal/Modal';
```

- [ ] **Step 5: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

#### 步骤1.1.3：标记旧组件为废弃

- [ ] **Step 6: 读取BaseModal.tsx**

Run: `read_file frontend/src/shared/ui/BaseModal/BaseModal.tsx`

- [ ] **Step 7: 添加废弃注释**

在BaseModal.tsx文件顶部添加：

```typescript
/**
 * @deprecated This component is deprecated. Use Modal from '@/shared/ui/components/Modal' instead.
 * Will be removed in v3.0.0
 * Migration guide: Replace 'BaseModal' with 'Modal' in imports.
 * @see Modal
 */
```

- [ ] **Step 8: 提交更改**

```bash
git add frontend/src/shared/ui/index.ts frontend/src/shared/ui/BaseModal/BaseModal.tsx
git commit -m "feat(modal): add deprecation notice and compatibility export for BaseModal"
```

#### 步骤1.1.4：创建迁移测试

- [ ] **Step 9: 编写迁移验证测试**

创建文件 `frontend/src/shared/ui/components/Modal/Modal.migration.test.tsx`：

```typescript
import { render, screen } from '@testing-library/react';
import { Modal } from '../Modal';
import { BaseModal } from '@/shared/ui';

describe('Modal Migration', () => {
  it('BaseModal should be an alias for Modal', () => {
    expect(BaseModal).toBe(Modal);
  });

  it('Modal should render with all BaseModal props', () => {
    render(
      <Modal
        isOpen={true}
        onClose={() => {}}
        title="Test Modal"
        size="medium"
        animation="slideUp"
      >
        Content
      </Modal>
    );
    
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
});
```

- [ ] **Step 10: 运行测试**

Run: `cd frontend && npm test -- Modal.migration.test.tsx`

Expected: 所有测试通过

- [ ] **Step 11: 提交测试**

```bash
git add frontend/src/shared/ui/components/Modal/Modal.migration.test.tsx
git commit -m "test(modal): add migration verification tests"
```

---

### 任务1.2：Table迁移

**Files:**
- Modify: `frontend/src/shared/ui/index.ts`
- Modify: `frontend/src/shared/ui/Table/Table.tsx`
- Modify: `frontend/src/shared/ui/components/Table/Table.tsx`
- Test: `frontend/src/shared/ui/components/Table/Table.migration.test.tsx`

#### 步骤1.2.1：分析Table使用情况

- [ ] **Step 1: 搜索所有使用旧Table的文件**

Run: `grep -r "from.*ui/Table" frontend/src --include="*.tsx" --include="*.ts" | cat`

Expected: 列出所有使用旧Table的文件

- [ ] **Step 2: 搜索所有使用VirtualList的文件**

Run: `grep -r "from.*VirtualList" frontend/src --include="*.tsx" --include="*.ts" | cat`

Expected: 列出所有使用VirtualList的文件

#### 步骤1.2.2：更新Table组件支持虚拟滚动

- [ ] **Step 3: 读取新Table组件**

Run: `read_file frontend/src/shared/ui/components/Table/Table.tsx`

- [ ] **Step 4: 确认虚拟滚动功能**

检查Table组件是否已支持 `virtual` prop，如果没有则添加：

```typescript
interface TableProps<TData> {
  // ... existing props
  virtual?: boolean;
  rowHeight?: number;
  maxHeight?: number;
}
```

- [ ] **Step 5: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

#### 步骤1.2.3：更新导出文件

- [ ] **Step 6: 更新index.ts**

在index.ts中添加：

```typescript
// Table exports
export { Table } from './components/Table/Table';
export type { TableProps, TableColumn } from './components/Table/Table.types';

// Backward compatibility - Old Table alias
/**
 * @deprecated Use Table from '@/shared/ui/components/Table' instead.
 * Will be removed in v3.0.0
 */
export { Table as LegacyTable } from './Table/Table';
```

- [ ] **Step 7: 标记旧Table为废弃**

在旧Table.tsx文件顶部添加：

```typescript
/**
 * @deprecated Use Table from '@/shared/ui/components/Table' instead.
 * Will be removed in v3.0.0
 */
```

- [ ] **Step 8: 提交更改**

```bash
git add frontend/src/shared/ui/index.ts frontend/src/shared/ui/Table/Table.tsx
git commit -m "feat(table): add deprecation notice and compatibility export for legacy Table"
```

#### 步骤1.2.4：创建迁移测试

- [ ] **Step 9: 编写迁移验证测试**

创建文件 `frontend/src/shared/ui/components/Table/Table.migration.test.tsx`：

```typescript
import { render, screen } from '@testing-library/react';
import { Table } from '../Table';

describe('Table Migration', () => {
  const mockData = [
    { id: 1, name: 'Test 1' },
    { id: 2, name: 'Test 2' },
  ];

  const mockColumns = [
    { id: 'id', header: 'ID', accessorKey: 'id' },
    { id: 'name', header: 'Name', accessorKey: 'name' },
  ];

  it('new Table should render data correctly', () => {
    render(<Table data={mockData} columns={mockColumns} />);
    expect(screen.getByText('Test 1')).toBeInTheDocument();
    expect(screen.getByText('Test 2')).toBeInTheDocument();
  });

  it('new Table should support virtual scrolling', () => {
    const largeData = Array.from({ length: 1000 }, (_, i) => ({
      id: i + 1,
      name: `Test ${i + 1}`,
    }));
    
    const { container } = render(
      <Table data={largeData} columns={mockColumns} virtual maxHeight={500} />
    );
    
    expect(container.querySelector('[data-virtualizer]')).toBeInTheDocument();
  });
});
```

- [ ] **Step 10: 运行测试**

Run: `cd frontend && npm test -- Table.migration.test.tsx`

Expected: 所有测试通过

- [ ] **Step 11: 提交测试**

```bash
git add frontend/src/shared/ui/components/Table/Table.migration.test.tsx
git commit -m "test(table): add migration verification tests"
```

---

### 任务1.3：Select迁移

**Files:**
- Create: `frontend/src/shared/ui/components/Select/Select.tsx`
- Create: `frontend/src/shared/ui/components/Select/Select.types.ts`
- Create: `frontend/src/shared/ui/components/Select/Select.css`
- Create: `frontend/src/shared/ui/components/Select/Select.test.tsx`
- Create: `frontend/src/shared/ui/components/Select/index.ts`
- Modify: `frontend/src/shared/ui/index.ts`

#### 步骤1.3.1：读取现有Select组件

- [ ] **Step 1: 读取现有Select组件**

Run: `read_file frontend/src/shared/ui/Select/Select.tsx`

- [ ] **Step 2: 分析Select组件功能**

记录现有Select组件的所有功能和props

#### 步骤1.3.2：创建新的Select组件目录

- [ ] **Step 3: 创建Select.types.ts**

创建文件 `frontend/src/shared/ui/components/Select/Select.types.ts`：

```typescript
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
  value?: string | number;
  onChange?: (value: string | number) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  searchable?: boolean;
  multiple?: boolean;
  error?: string;
  helperText?: string;
  className?: string;
  size?: 'small' | 'medium' | 'large';
  control?: any;
  rules?: any;
}
```

- [ ] **Step 4: 创建Select.tsx**

创建文件 `frontend/src/shared/ui/components/Select/Select.tsx`，实现完整的Select组件，支持：
- 单选/多选
- 搜索过滤
- 键盘导航
- ARIA属性
- Cyberpunk Lab Theme样式

- [ ] **Step 5: 创建Select.css**

创建文件 `frontend/src/shared/ui/components/Select/Select.css`，包含：
- 毛玻璃效果背景
- 霓虹边框高亮
- 平滑动画过渡
- 尺寸变体

- [ ] **Step 6: 创建index.ts**

```typescript
export { Select } from './Select';
export type { SelectProps, SelectOption } from './Select.types';
```

- [ ] **Step 7: 创建Select.test.tsx**

创建完整的测试文件，覆盖：
- 渲染测试
- 选择功能测试
- 搜索功能测试
- 键盘导航测试
- 错误状态测试

- [ ] **Step 8: 运行测试**

Run: `cd frontend && npm test -- Select.test.tsx`

Expected: 所有测试通过

- [ ] **Step 9: 更新index.ts导出**

在 `frontend/src/shared/ui/index.ts` 中添加：

```typescript
// Select exports
export { Select } from './components/Select/Select';
export type { SelectProps, SelectOption } from './components/Select/Select.types';
```

- [ ] **Step 10: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

- [ ] **Step 11: 提交更改**

```bash
git add frontend/src/shared/ui/components/Select frontend/src/shared/ui/index.ts
git commit -m "feat(select): migrate Select component to new architecture"
```

---

## 阶段2：性能优化 (2周)

### 任务2.1：Table虚拟滚动优化

**Files:**
- Modify: `frontend/src/shared/ui/components/Table/Table.tsx`
- Modify: `frontend/src/shared/ui/components/Table/Table.css`
- Create: `frontend/src/shared/hooks/usePerformanceMonitor.ts`
- Test: `frontend/src/shared/ui/components/Table/Table.performance.test.tsx`

#### 步骤2.1.1：创建性能监控Hook

- [ ] **Step 1: 创建usePerformanceMonitor.ts**

创建文件 `frontend/src/shared/hooks/usePerformanceMonitor.ts`：

```typescript
import { useRef, useCallback } from 'react';

export function usePerformanceMonitor(componentName: string) {
  const startTimeRef = useRef<number>(0);

  const measureRender = useCallback(() => {
    startTimeRef.current = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTimeRef.current;
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`[${componentName}] Render time: ${renderTime.toFixed(2)}ms`);
      }
      
      return { renderTime };
    };
  }, [componentName]);

  return { measureRender };
}
```

- [ ] **Step 2: 提交性能监控Hook**

```bash
git add frontend/src/shared/hooks/usePerformanceMonitor.ts
git commit -m "feat(performance): add performance monitoring hook"
```

#### 步骤2.1.2：优化Table虚拟滚动

- [ ] **Step 3: 读取Table.tsx**

Run: `read_file frontend/src/shared/ui/components/Table/Table.tsx`

- [ ] **Step 4: 添加虚拟滚动优化**

在Table组件中添加：
- 性能监控
- 缓存机制
- will-change CSS优化

- [ ] **Step 5: 添加CSS优化**

在Table.css中添加：

```css
.table-container--virtual {
  will-change: transform;
  contain: strict;
}

.table-row--virtual {
  position: absolute;
  will-change: transform;
  contain: layout style;
}
```

- [ ] **Step 6: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

- [ ] **Step 7: 提交优化**

```bash
git add frontend/src/shared/ui/components/Table/Table.tsx frontend/src/shared/ui/components/Table/Table.css
git commit -m "perf(table): optimize virtual scrolling with caching and will-change"
```

#### 步骤2.1.3：创建性能测试

- [ ] **Step 8: 编写性能测试**

创建文件 `frontend/src/shared/ui/components/Table/Table.performance.test.tsx`：

```typescript
import { render } from '@testing-library/react';
import { Table } from './Table';

describe('Table Performance', () => {
  const generateMockData = (count: number) =>
    Array.from({ length: count }, (_, i) => ({
      id: i + 1,
      name: `User ${i + 1}`,
      email: `user${i + 1}@example.com`,
    }));

  const columns = [
    { id: 'id', header: 'ID', accessorKey: 'id' },
    { id: 'name', header: 'Name', accessorKey: 'name' },
    { id: 'email', header: 'Email', accessorKey: 'email' },
  ];

  it('should render 1000 rows in under 100ms', () => {
    const data = generateMockData(1000);
    const start = performance.now();
    
    render(<Table data={data} columns={columns} virtual />);
    
    const end = performance.now();
    expect(end - start).toBeLessThan(100);
  });

  it('should render 10000 rows in under 200ms', () => {
    const data = generateMockData(10000);
    const start = performance.now();
    
    render(<Table data={data} columns={columns} virtual />);
    
    const end = performance.now();
    expect(end - start).toBeLessThan(200);
  });
});
```

- [ ] **Step 9: 运行性能测试**

Run: `cd frontend && npm test -- Table.performance.test.tsx`

Expected: 所有测试通过

- [ ] **Step 10: 提交测试**

```bash
git add frontend/src/shared/ui/components/Table/Table.performance.test.tsx
git commit -m "test(table): add performance tests for virtual scrolling"
```

---

### 任务2.2：Modal动画优化

**Files:**
- Modify: `frontend/src/shared/ui/components/Modal/Modal.tsx`
- Modify: `frontend/src/shared/ui/components/Modal/Modal.css`

#### 步骤2.2.1：优化CSS动画

- [ ] **Step 1: 读取Modal.css**

Run: `read_file frontend/src/shared/ui/components/Modal/Modal.css`

- [ ] **Step 2: 更新动画时长**

将动画时长从0.3s减少到0.15s，添加will-change和GPU加速：

```css
.modal-content--slideUp {
  animation: modal-slide-up 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, opacity;
}

.modal-content {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}
```

- [ ] **Step 3: 更新Modal.tsx中的延迟常量**

将 `MODAL_ANIMATION_DELAY` 从300改为150

- [ ] **Step 4: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

- [ ] **Step 5: 提交优化**

```bash
git add frontend/src/shared/ui/components/Modal/Modal.tsx frontend/src/shared/ui/components/Modal/Modal.css
git commit -m "perf(modal): reduce animation delay from 300ms to 150ms with GPU acceleration"
```

---

### 任务2.3：Form验证性能优化

**Files:**
- Modify: `frontend/src/shared/ui/components/Form/Form.tsx`
- Create: `frontend/src/shared/utils/validationCache.ts`
- Create: `frontend/src/shared/hooks/useDebouncedValidation.ts`
- Test: `frontend/src/shared/ui/components/Form/Form.performance.test.tsx`

#### 步骤2.3.1：创建验证缓存工具

- [ ] **Step 1: 创建validationCache.ts**

创建文件 `frontend/src/shared/utils/validationCache.ts`：

```typescript
export class ValidationCache {
  private cache: Map<string, { value: unknown; result: boolean | string }>;
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  get(key: string, value: unknown): boolean | string | undefined {
    const cached = this.cache.get(key);
    if (cached && this.isEqual(cached.value, value)) {
      return cached.result;
    }
    return undefined;
  }

  set(key: string, value: unknown, result: boolean | string): void {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey !== undefined) {
        this.cache.delete(firstKey);
      }
    }
    this.cache.set(key, { value, result });
  }

  clear(): void {
    this.cache.clear();
  }

  private isEqual(a: unknown, b: unknown): boolean {
    return JSON.stringify(a) === JSON.stringify(b);
  }
}

export const validationCache = new ValidationCache();
```

- [ ] **Step 2: 创建useDebouncedValidation.ts**

创建文件 `frontend/src/shared/hooks/useDebouncedValidation.ts`：

```typescript
import { useRef, useCallback, useEffect } from 'react';
import { UseFormReturn } from 'react-hook-form';
import { debounce } from 'lodash-es';

export function useDebouncedValidation<TFieldValues extends Record<string, any>>(
  form: UseFormReturn<TFieldValues>,
  delay: number = 300
) {
  const debouncedValidateRef = useRef(
    debounce(async (fields?: string[]) => {
      await form.trigger(fields as any);
    }, delay)
  );

  useEffect(() => {
    return () => {
      debouncedValidateRef.current.cancel();
    };
  }, []);

  const validateField = useCallback((fieldName: string) => {
    debouncedValidateRef.current(fieldName);
  }, []);

  return { validateField };
}
```

- [ ] **Step 3: 提交验证工具**

```bash
git add frontend/src/shared/utils/validationCache.ts frontend/src/shared/hooks/useDebouncedValidation.ts
git commit -m "feat(form): add validation cache and debounced validation hooks"
```

#### 步骤2.3.2：优化Form组件

- [ ] **Step 4: 读取Form.tsx**

Run: `read_file frontend/src/shared/ui/components/Form/Form.tsx`

- [ ] **Step 5: 添加验证优化**

在Form组件中集成验证缓存和debounce

- [ ] **Step 6: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

- [ ] **Step 7: 提交优化**

```bash
git add frontend/src/shared/ui/components/Form/Form.tsx
git commit -m "perf(form): add validation caching and debouncing"
```

#### 步骤2.3.3：创建性能测试

- [ ] **Step 8: 编写性能测试**

创建文件 `frontend/src/shared/ui/components/Form/Form.performance.test.tsx`

- [ ] **Step 9: 运行性能测试**

Run: `cd frontend && npm test -- Form.performance.test.tsx`

Expected: 所有测试通过

- [ ] **Step 10: 提交测试**

```bash
git add frontend/src/shared/ui/components/Form/Form.performance.test.tsx
git commit -m "test(form): add performance tests for validation optimization"
```

---

## 阶段3：功能增强 (3周)

### 任务3.1：Modal拖拽功能

**Files:**
- Create: `frontend/src/shared/hooks/useDraggable.ts`
- Modify: `frontend/src/shared/ui/components/Modal/Modal.tsx`
- Modify: `frontend/src/shared/ui/components/Modal/Modal.types.ts`
- Modify: `frontend/src/shared/ui/components/Modal/Modal.css`
- Test: `frontend/src/shared/ui/components/Modal/Modal.drag.test.tsx`

#### 步骤3.1.1：创建拖拽Hook

- [ ] **Step 1: 创建useDraggable.ts**

创建文件 `frontend/src/shared/hooks/useDraggable.ts`，实现：
- 拖拽位置跟踪
- 边界限制
- 网格对齐
- 重置功能

- [ ] **Step 2: 提交拖拽Hook**

```bash
git add frontend/src/shared/hooks/useDraggable.ts
git commit -m "feat(modal): add useDraggable hook for modal dragging"
```

#### 步骤3.1.2：更新Modal组件

- [ ] **Step 3: 更新Modal.types.ts**

添加拖拽相关类型：

```typescript
export interface ModalDragConfig {
  enabled: boolean;
  handle?: string;
  bounds?: 'parent' | 'window' | HTMLElement;
  grid?: [number, number];
}

export interface ModalProps {
  // ... existing props
  draggable?: boolean | ModalDragConfig;
}
```

- [ ] **Step 4: 更新Modal.tsx**

集成useDraggable hook

- [ ] **Step 5: 更新Modal.css**

添加拖拽相关样式

- [ ] **Step 6: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

- [ ] **Step 7: 提交更改**

```bash
git add frontend/src/shared/ui/components/Modal/Modal.tsx frontend/src/shared/ui/components/Modal/Modal.types.ts frontend/src/shared/ui/components/Modal/Modal.css
git commit -m "feat(modal): add drag functionality to Modal component"
```

#### 步骤3.1.3：创建拖拽测试

- [ ] **Step 8: 编写拖拽测试**

创建文件 `frontend/src/shared/ui/components/Modal/Modal.drag.test.tsx`

- [ ] **Step 9: 运行测试**

Run: `cd frontend && npm test -- Modal.drag.test.tsx`

Expected: 所有测试通过

- [ ] **Step 10: 提交测试**

```bash
git add frontend/src/shared/ui/components/Modal/Modal.drag.test.tsx
git commit -m "test(modal): add tests for drag functionality"
```

---

### 任务3.2：Form新增字段类型

**Files:**
- Create: `frontend/src/shared/ui/components/Form/FormDatePicker.tsx`
- Create: `frontend/src/shared/ui/components/Form/FormUpload.tsx`
- Create: `frontend/src/shared/ui/components/Form/FormRichText.tsx`
- Test: 对应的测试文件

#### 步骤3.2.1：创建FormDatePicker

- [ ] **Step 1: 创建FormDatePicker.tsx**

实现日期选择器组件，支持：
- 日期格式化
- 时间选择
- 日期范围限制
- Cyberpunk Lab Theme样式

- [ ] **Step 2: 创建FormDatePicker.test.tsx**

- [ ] **Step 3: 运行测试**

Run: `cd frontend && npm test -- FormDatePicker.test.tsx`

Expected: 所有测试通过

- [ ] **Step 4: 提交FormDatePicker**

```bash
git add frontend/src/shared/ui/components/Form/FormDatePicker.tsx frontend/src/shared/ui/components/Form/FormDatePicker.test.tsx
git commit -m "feat(form): add FormDatePicker component"
```

#### 步骤3.2.2：创建FormUpload

- [ ] **Step 5: 创建FormUpload.tsx**

实现文件上传组件，支持：
- 拖拽上传
- 多文件上传
- 文件预览
- 文件类型/大小验证
- 上传进度

- [ ] **Step 6: 创建FormUpload.test.tsx**

- [ ] **Step 7: 运行测试**

Run: `cd frontend && npm test -- FormUpload.test.tsx`

Expected: 所有测试通过

- [ ] **Step 8: 提交FormUpload**

```bash
git add frontend/src/shared/ui/components/Form/FormUpload.tsx frontend/src/shared/ui/components/Form/FormUpload.test.tsx
git commit -m "feat(form): add FormUpload component with drag and drop support"
```

#### 步骤3.2.3：创建FormRichText

- [ ] **Step 9: 创建FormRichText.tsx**

实现富文本编辑器组件，支持：
- 工具栏配置
- 字符计数
- 最大长度限制
- Cyberpunk Lab Theme样式

- [ ] **Step 10: 创建FormRichText.test.tsx**

- [ ] **Step 11: 运行测试**

Run: `cd frontend && npm test -- FormRichText.test.tsx`

Expected: 所有测试通过

- [ ] **Step 12: 提交FormRichText**

```bash
git add frontend/src/shared/ui/components/Form/FormRichText.tsx frontend/src/shared/ui/components/Form/FormRichText.test.tsx
git commit -m "feat(form): add FormRichText component with customizable toolbar"
```

---

### 任务3.3：Table列分组功能

**Files:**
- Modify: `frontend/src/shared/ui/components/Table/Table.tsx`
- Modify: `frontend/src/shared/ui/components/Table/Table.types.ts`
- Modify: `frontend/src/shared/ui/components/Table/Table.css`
- Test: `frontend/src/shared/ui/components/Table/Table.grouping.test.tsx`

#### 步骤3.3.1：更新Table类型

- [ ] **Step 1: 读取Table.types.ts**

Run: `read_file frontend/src/shared/ui/components/Table/Table.types.ts`

- [ ] **Step 2: 添加列分组类型**

```typescript
export interface TableColumnGroup<TData> {
  id: string;
  header: string;
  columns: TableColumn<TData>[];
  align?: 'left' | 'center' | 'right';
  className?: string;
}
```

#### 步骤3.3.2：更新Table组件

- [ ] **Step 3: 读取Table.tsx**

Run: `read_file frontend/src/shared/ui/components/Table/Table.tsx`

- [ ] **Step 4: 添加列分组支持**

使用TanStack Table的column grouping功能

- [ ] **Step 5: 更新Table.css**

添加多级表头样式

- [ ] **Step 6: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

- [ ] **Step 7: 提交更改**

```bash
git add frontend/src/shared/ui/components/Table/Table.tsx frontend/src/shared/ui/components/Table/Table.types.ts frontend/src/shared/ui/components/Table/Table.css
git commit -m "feat(table): add column grouping support"
```

#### 步骤3.3.3：创建列分组测试

- [ ] **Step 8: 编写列分组测试**

创建文件 `frontend/src/shared/ui/components/Table/Table.grouping.test.tsx`

- [ ] **Step 9: 运行测试**

Run: `cd frontend && npm test -- Table.grouping.test.tsx`

Expected: 所有测试通过

- [ ] **Step 10: 提交测试**

```bash
git add frontend/src/shared/ui/components/Table/Table.grouping.test.tsx
git commit -m "test(table): add tests for column grouping"
```

---

## 阶段4：组件扩展与工具完善 (3周)

### 任务4.1：DatePicker组件

**Files:**
- Create: `frontend/src/shared/ui/components/DatePicker/DatePicker.tsx`
- Create: `frontend/src/shared/ui/components/DatePicker/DatePicker.types.ts`
- Create: `frontend/src/shared/ui/components/DatePicker/DatePicker.css`
- Create: `frontend/src/shared/ui/components/DatePicker/DatePicker.test.tsx`
- Create: `frontend/src/shared/ui/components/DatePicker/index.ts`

#### 步骤4.1.1：创建DatePicker类型

- [ ] **Step 1: 创建DatePicker.types.ts**

```typescript
export interface DatePickerProps {
  value?: Date | null;
  onChange?: (date: Date | null) => void;
  format?: string;
  placeholder?: string;
  minDate?: Date;
  maxDate?: Date;
  disabled?: boolean;
  showTime?: boolean;
  locale?: string;
  error?: string;
  helperText?: string;
  className?: string;
}
```

#### 步骤4.1.2：创建DatePicker组件

- [ ] **Step 2: 创建DatePicker.tsx**

实现完整的日期选择器，支持：
- 日历视图
- 月份/年份选择
- 时间选择
- 键盘导航
- Cyberpunk Lab Theme样式

- [ ] **Step 3: 创建DatePicker.css**

- [ ] **Step 4: 创建index.ts**

- [ ] **Step 5: 创建DatePicker.test.tsx**

- [ ] **Step 6: 运行测试**

Run: `cd frontend && npm test -- DatePicker.test.tsx`

Expected: 所有测试通过

- [ ] **Step 7: 更新index.ts导出**

- [ ] **Step 8: 运行类型检查**

Run: `cd frontend && npm run type-check`

Expected: 无类型错误

- [ ] **Step 9: 提交DatePicker**

```bash
git add frontend/src/shared/ui/components/DatePicker frontend/src/shared/ui/index.ts
git commit -m "feat(datepicker): add DatePicker component with Cyberpunk Lab Theme"
```

---

### 任务4.2：AST转换工具增强

**Files:**
- Create: `scripts/batch-transform.ts`
- Modify: `scripts/migrate-modal.ts`
- Modify: `scripts/migrate-table.ts`

#### 步骤4.2.1：创建批量转换工具

- [ ] **Step 1: 创建batch-transform.ts**

实现：
- 批量文件处理
- 转换规则配置
- 转换预览
- 回滚功能

- [ ] **Step 2: 提交批量转换工具**

```bash
git add scripts/batch-transform.ts
git commit -m "feat(ast): add batch transform tool with preview and rollback"
```

#### 步骤4.2.2：增强现有迁移脚本

- [ ] **Step 3: 读取migrate-modal.ts**

Run: `read_file scripts/migrate-modal.ts`

- [ ] **Step 4: 增强migrate-modal.ts**

添加批量处理和预览功能

- [ ] **Step 5: 读取migrate-table.ts**

Run: `read_file scripts/migrate-table.ts`

- [ ] **Step 6: 增强migrate-table.ts**

添加批量处理和预览功能

- [ ] **Step 7: 提交增强**

```bash
git add scripts/migrate-modal.ts scripts/migrate-table.ts
git commit -m "feat(ast): enhance migration scripts with batch processing"
```

---

### 任务4.3：可视化迁移工具

**Files:**
- Create: `scripts/migration-tool/server.ts`
- Create: `scripts/migration-tool/client/index.html`
- Create: `scripts/migration-tool/client/app.tsx`
- Create: `scripts/migration-tool/websocket.ts`

#### 步骤4.3.1：创建后端服务

- [ ] **Step 1: 创建server.ts**

实现：
- WebSocket服务器
- AST转换服务
- 文件系统操作
- 进度跟踪

- [ ] **Step 2: 创建websocket.ts**

实现WebSocket通信协议

#### 步骤4.3.2：创建前端界面

- [ ] **Step 3: 创建index.html**

- [ ] **Step 4: 创建app.tsx**

实现：
- 文件浏览器
- 差异对比（使用Monaco Editor）
- 一键迁移
- 进度显示

- [ ] **Step 5: 提交可视化迁移工具**

```bash
git add scripts/migration-tool/
git commit -m "feat(tools): add visual migration tool with Monaco Editor diff view"
```

---

### 任务4.4：自动化测试流程

**Files:**
- Create: `.github/workflows/component-tests.yml`

#### 步骤4.4.1：创建CI/CD配置

- [ ] **Step 1: 创建component-tests.yml**

创建完整的GitHub Actions工作流，包含：
- 单元测试
- 集成测试
- E2E测试
- 视觉回归测试
- 覆盖率报告

- [ ] **Step 2: 提交CI/CD配置**

```bash
git add .github/workflows/component-tests.yml
git commit -m "ci: add comprehensive component testing workflow"
```

#### 步骤4.4.2：验证CI/CD流程

- [ ] **Step 3: 推送到远程仓库**

Run: `git push origin main`

- [ ] **Step 4: 检查GitHub Actions运行状态**

在GitHub上检查工作流是否正常运行

---

## 测试计划

### 单元测试覆盖目标

| 组件 | 目标覆盖率 | 关键测试点 |
|-----|-----------|-----------|
| Modal | 95% | 打开/关闭、动画、拖拽、无障碍性 |
| Table | 90% | 虚拟滚动、排序、分页、列分组 |
| Form | 90% | 验证、提交、字段组件 |
| Select | 90% | 选择、搜索、键盘导航 |
| DatePicker | 90% | 日期选择、格式化、边界 |

### 集成测试场景

| 场景 | 测试目标 |
|-----|---------|
| 表单提交 | 验证 → 提交 → 成功/失败处理 |
| 表格操作 | 排序 → 筛选 → 分页 → 选择 |
| Modal交互 | 打开 → 编辑 → 保存/取消 |

### E2E测试流程

| 流程 | 测试步骤 |
|-----|---------|
| 用户管理 | 登录 → 用户列表 → 创建用户 → 编辑用户 → 删除用户 |
| 事件管理 | 事件列表 → 创建事件 → 编辑事件 → 验证事件 |

---

## 风险评估

### 技术风险

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 迁移导致功能回退 | 高 | 完整的测试覆盖，逐步迁移 |
| 性能优化效果不佳 | 中 | 性能基准测试，A/B测试 |
| 新功能与现有架构冲突 | 中 | 设计评审，原型验证 |

### 项目风险

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 时间估算不准确 | 中 | 预留缓冲时间，分阶段交付 |
| 依赖升级导致兼容性问题 | 中 | 锁定依赖版本，逐步升级 |

---

## 交付物清单

### 阶段1交付物
- [ ] Modal迁移完成，旧组件废弃
- [ ] Table迁移完成，VirtualTable整合
- [ ] Select迁移到新架构
- [ ] 迁移测试通过

### 阶段2交付物
- [ ] Table虚拟滚动性能优化
- [ ] Modal动画优化
- [ ] Form验证性能优化
- [ ] 性能测试报告

### 阶段3交付物
- [ ] Modal拖拽功能
- [ ] FormDatePicker组件
- [ ] FormUpload组件
- [ ] FormRichText组件
- [ ] Table列分组功能

### 阶段4交付物
- [ ] DatePicker独立组件
- [ ] AST工具增强版
- [ ] 可视化迁移工具
- [ ] CI/CD自动化测试流程
- [ ] 完整文档

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-03-20-component-library-phase2-plan.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** - 使用 superpowers:subagent-driven-development，每个任务派遣一个fresh subagent，任务间有review checkpoint，快速迭代

**2. Inline Execution** - 使用 superpowers:executing-plans，在当前会话中批量执行，有checkpoint供review

**Which approach?**
