# Event2Table 组件开发指南

本指南提供创建、测试和文档化 Event2Table 组件的标准流程和最佳实践。

## 目录

- [如何创建新组件](#如何创建新组件)
- [组件测试规范](#组件测试规范)
- [组件文档规范](#组件文档规范)
- [组件开发最佳实践](#组件开发最佳实践)

---

## 如何创建新组件

### 1. 组件规划

在开始编写代码之前，先明确组件的用途和功能：

- **组件类型**: 基础组件、业务组件、布局组件、状态组件或特殊组件
- **功能需求**: 组件需要实现哪些功能
- **Props 设计**: 需要哪些属性，哪些是必需的，哪些是可选的
- **样式需求**: 需要哪些变体和尺寸

### 2. 创建组件文件

按照标准文件结构创建组件：

```bash
frontend/src/shared/ui/
└── ComponentName/
    ├── ComponentName.tsx       # 组件实现
    ├── ComponentName.css       # 组件样式
    ├── ComponentName.test.tsx  # 单元测试
    └── ComponentName.type-test.tsx  # 类型测试（可选）
```

### 3. 组件实现模板

使用以下模板作为新组件的基础：

```typescript
/**
 * ComponentName Component - "Cyberpunk Lab" Theme
 *
 * 组件功能描述
 *
 * @example
 * // 基础用法
 * <ComponentName variant="primary">
 *   Content
 * </ComponentName>
 *
 * @example
 * // 带回调
 * <ComponentName onChange={handleChange} />
 */

import React from 'react';
import type {
  Variant,
  Size,
  BaseComponentProps,
  MouseEventHandler,
} from '@/types/common';
import './ComponentName.css';

/**
 * ComponentName 组件 Props
 */
export interface ComponentNameProps extends BaseComponentProps {
  /** 组件变体 */
  variant?: Variant;
  /** 组件尺寸 */
  size?: Size;
  /** 点击回调 */
  onClick?: MouseEventHandler;
  /** 是否禁用 */
  disabled?: boolean;
  /** 加载状态 */
  loading?: boolean;
}

/**
 * ComponentName 组件
 */
const ComponentName = React.forwardRef<HTMLDivElement, ComponentNameProps>(({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  className = '',
  ...props
}, ref) => {
  const componentClass = [
    'cyber-component',
    `cyber-component--${variant}`,
    `cyber-component--${size}`,
    disabled && 'cyber-component--disabled',
    loading && 'cyber-component--loading',
    className
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={ref}
      className={componentClass}
      onClick={disabled ? undefined : onClick}
      {...props}
    >
      {loading && <span className="cyber-component__spinner" />}
      {children}
    </div>
  );
});

ComponentName.displayName = 'ComponentName';

// 性能优化：使用 React.memo
const MemoizedComponentName = React.memo(ComponentName);

MemoizedComponentName.displayName = 'MemoizedComponentName';

export { MemoizedComponentName as ComponentName };
export default MemoizedComponentName;
```

### 4. 样式实现模板

```css
/* ComponentName.css */

/* 基础样式 */
.cyber-component {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-base);
  cursor: pointer;
  user-select: none;
}

/* 变体样式 */
.cyber-component--primary {
  background: var(--color-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

.cyber-component--secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
}

.cyber-component--ghost {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid transparent;
}

/* 尺寸样式 */
.cyber-component--sm {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
}

.cyber-component--md {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
}

.cyber-component--lg {
  padding: var(--space-4) var(--space-6);
  font-size: var(--text-base);
}

/* 状态样式 */
.cyber-component--disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.cyber-component--loading {
  opacity: 0.8;
  cursor: wait;
}

/* 悬停效果 */
.cyber-component:not(.cyber-component--disabled):hover {
  box-shadow: 0 0 12px var(--color-primary-light);
  transform: translateY(-1px);
}

/* 子元素 */
.cyber-component__spinner {
  width: 16px;
  height: 16px;
  margin-right: var(--space-2);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### 5. 更新组件库索引

在 `frontend/src/shared/ui/index.ts` 中添加新组件的导出：

```typescript
// 根据组件类型添加到相应分类
export { default as ComponentName } from './ComponentName/ComponentName';
export type { ComponentNameProps } from './ComponentName/ComponentName';
```

### 6. 更新组件库文档

在 `frontend/src/shared/ui/README.md` 中添加组件的文档说明：

```markdown
### ComponentName

组件功能描述

**Variants**: `primary`, `secondary`, `ghost`
**Sizes**: `sm`, `md`, `lg`

```jsx
<ComponentName variant="primary" onClick={handleClick}>
  Click me
</ComponentName>
```

**Features**:
- Feature 1
- Feature 2
- Feature 3
```

---

## 组件测试规范

### 1. 测试文件结构

每个组件都应该有对应的测试文件：

```typescript
// ComponentName.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ComponentName } from './ComponentName';

describe('ComponentName', () => {
  // 测试用例
});
```

### 2. 测试覆盖范围

确保测试覆盖以下方面：

#### 基础渲染测试

```typescript
it('应该正确渲染', () => {
  render(<ComponentName>Test</ComponentName>);
  expect(screen.getByText('Test')).toBeInTheDocument();
});
```

#### Props 测试

```typescript
it('应该正确应用 variant prop', () => {
  const { container } = render(
    <ComponentName variant="primary">Test</ComponentName>
  );
  expect(container.firstChild).toHaveClass('cyber-component--primary');
});

it('应该正确应用 size prop', () => {
  const { container } = render(
    <ComponentName size="lg">Test</ComponentName>
  );
  expect(container.firstChild).toHaveClass('cyber-component--lg');
});
```

#### 事件处理测试

```typescript
it('应该在点击时调用 onClick', () => {
  const handleClick = vi.fn();
  render(<ComponentName onClick={handleClick}>Test</ComponentName>);
  
  fireEvent.click(screen.getByText('Test'));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

#### 状态测试

```typescript
it('应该在 disabled 状态下禁用点击', () => {
  const handleClick = vi.fn();
  render(
    <ComponentName disabled onClick={handleClick}>
      Test
    </ComponentName>
  );
  
  fireEvent.click(screen.getByText('Test'));
  expect(handleClick).not.toHaveBeenCalled();
});

it('应该在 loading 状态下显示加载指示器', () => {
  const { container } = render(
    <ComponentName loading>Test</ComponentName>
  );
  expect(container.querySelector('.cyber-component__spinner')).toBeInTheDocument();
});
```

#### 可访问性测试

```typescript
it('应该在 disabled 时设置正确的 ARIA 属性', () => {
  render(<ComponentName disabled>Test</ComponentName>);
  expect(screen.getByText('Test')).toHaveAttribute('disabled');
});
```

### 3. 测试最佳实践

- **使用描述性的测试名称**: 测试名称应该清楚地说明测试的内容
- **测试用户行为**: 测试用户如何与组件交互，而不是实现细节
- **使用快照测试**: 对于复杂的组件，使用快照测试确保 UI 一致性
- **保持测试独立**: 每个测试应该独立运行，不依赖于其他测试
- **使用 beforeEach**: 如果需要设置，使用 beforeEach 来准备测试环境

```typescript
describe('ComponentName', () => {
  beforeEach(() => {
    // 测试前的准备工作
  });

  afterEach(() => {
    // 测试后的清理工作
  });
});
```

---

## 组件文档规范

### 1. 组件级文档

每个组件都应该有完整的 JSDoc 注释：

```typescript
/**
 * ComponentName Component - "Cyberpunk Lab" Theme
 *
 * 组件的详细功能描述，说明组件的用途和使用场景。
 * 可以包含多行描述，详细说明组件的行为和特性。
 *
 * @example
 * // 基础用法
 * <ComponentName variant="primary">
 *   Content
 * </ComponentName>
 *
 * @example
 * // 带回调的用法
 * const handleClick = () => {
 *   console.log('Clicked!');
 * };
 * <ComponentName onClick={handleClick}>
 *   Click me
 * </ComponentName>
 *
 * @example
 * // 禁用状态
 * <ComponentName disabled>
 *   Disabled
 * </ComponentName>
 */
```

### 2. Props 文档

每个 Props 属性都应该有清晰的 JSDoc 注释：

```typescript
/**
 * ComponentName 组件 Props
 */
export interface ComponentNameProps extends BaseComponentProps {
  /** 组件变体，决定组件的视觉风格 */
  variant?: Variant;
  /** 组件尺寸，影响组件的大小 */
  size?: Size;
  /** 点击事件处理器 */
  onClick?: MouseEventHandler;
  /** 是否禁用组件，禁用后不可交互 */
  disabled?: boolean;
  /** 加载状态，显示加载指示器 */
  loading?: boolean;
  /** 子元素，组件的内容 */
  children?: React.ReactNode;
}
```

### 3. README 文档

在组件的 README 中提供详细的使用说明：

```markdown
### ComponentName

组件的简短描述，说明组件的主要用途。

#### 使用场景

- 场景 1
- 场景 2
- 场景 3

#### 基础用法

```jsx
<ComponentName variant="primary">
  Content
</ComponentName>
```

#### 高级用法

```jsx
<ComponentName
  variant="primary"
  size="lg"
  onClick={handleClick}
  loading={isLoading}
>
  Click me
</ComponentName>
```

#### API

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| variant | `Variant` | `'primary'` | 组件变体 |
| size | `Size` | `'md'` | 组件尺寸 |
| onClick | `MouseEventHandler` | - | 点击回调 |
| disabled | `boolean` | `false` | 是否禁用 |
| loading | `boolean` | `false` | 加载状态 |
| children | `ReactNode` | - | 子元素 |

#### 注意事项

- 注意事项 1
- 注意事项 2
```

---

## 组件开发最佳实践

### 1. 性能优化

#### 使用 React.memo

对于频繁渲染的组件，使用 `React.memo` 进行优化：

```typescript
const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
  // 自定义比较函数
  return prevProps.value === nextProps.value &&
         prevProps.loading === nextProps.loading;
});
```

#### 使用 useCallback 和 useMemo

在父组件中，使用 `useCallback` 和 `useMemo` 避免不必要的重渲染：

```typescript
const handleClick = useCallback(() => {
  // 处理逻辑
}, [dependencies]);

const memoizedValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);
```

#### 避免内联函数

避免在 JSX 中使用内联函数：

```typescript
// ❌ 避免
<ComponentName onClick={() => handleClick()} />

// ✅ 推荐
const handleClick = useCallback(() => {
  // 处理逻辑
}, [dependencies]);

<ComponentName onClick={handleClick} />
```

### 2. 可访问性

#### 语义化 HTML

使用语义化的 HTML 标签：

```typescript
// ✅ 推荐
<button onClick={handleClick}>Click</button>

// ❌ 避免
<div onClick={handleClick}>Click</div>
```

#### ARIA 属性

为交互元素添加适当的 ARIA 属性：

```typescript
<button
  aria-label="关闭"
  aria-pressed={isActive}
  onClick={handleClick}
>
  <Icon />
</button>
```

#### 键盘导航

确保组件支持键盘导航：

```typescript
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    handleClick();
  }
};

<div
  role="button"
  tabIndex={0}
  onKeyDown={handleKeyDown}
  onClick={handleClick}
>
  Content
</div>
```

### 3. 类型安全

#### 避免使用 any

避免使用 `any` 类型，使用具体的类型定义：

```typescript
// ❌ 避免
const handleClick = (event: any) => {
  // 处理逻辑
};

// ✅ 推荐
const handleClick = (event: MouseEvent) => {
  // 处理逻辑
};
```

#### 使用泛型

对于可复用的组件，使用泛型提高类型灵活性：

```typescript
interface GenericComponentProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function GenericComponent<T>({ items, renderItem }: GenericComponentProps<T>) {
  return (
    <div>
      {items.map((item, index) => (
        <div key={index}>{renderItem(item)}</div>
      ))}
    </div>
  );
}
```

#### 导出类型

始终导出组件使用的类型：

```typescript
export interface ComponentNameProps extends BaseComponentProps {
  // Props 定义
}

export type { ComponentNameProps };
```

### 4. 代码组织

#### 单一职责

每个组件应该只负责一个功能：

```typescript
// ✅ 推荐：每个组件职责单一
function Button({ onClick, children }) {
  return <button onClick={onClick}>{children}</button>;
}

function IconButton({ icon, onClick }) {
  return <Button onClick={onClick}>{icon}</Button>;
}

// ❌ 避免：一个组件承担多个职责
function ButtonOrIconButton({ isIcon, icon, children, onClick }) {
  if (isIcon) {
    return <button onClick={onClick}>{icon}</button>;
  }
  return <button onClick={onClick}>{children}</button>;
}
```

#### 组件组合

使用组件组合而不是 props 传递：

```typescript
// ✅ 推荐：使用组件组合
<Card>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Body>Content</Card.Body>
</Card>

// ❌ 避免：使用 props 传递
<Card
  header={<div>Title</div>}
  body={<div>Content</div>}
/>
```

### 5. 样式管理

#### 使用 CSS 类名

使用 CSS 类名而不是内联样式：

```typescript
// ✅ 推荐
<div className="cyber-card">
  Content
</div>

// ❌ 避免
<div style={{ padding: '16px', borderRadius: '8px' }}>
  Content
</div>
```

#### 使用 Tailwind 工具类

对于布局和间距，优先使用 Tailwind 工具类：

```typescript
// ✅ 推荐
<div className="flex items-center gap-4 p-4">
  Content
</div>

// ❌ 避免
<div className="custom-container">
  Content
</div>
```

#### 自定义 CSS 用于组件特定样式

对于组件特定的样式和动画，使用自定义 CSS：

```css
/* ComponentName.css */
.cyber-component {
  /* 组件特定样式 */
}

.cyber-component:hover {
  /* 悬停效果 */
}
```

---

## 总结

遵循本指南可以确保：

1. **一致性**: 所有组件遵循相同的标准和规范
2. **可维护性**: 代码易于理解和维护
3. **可测试性**: 组件易于测试和验证
4. **可访问性**: 组件对所有用户友好
5. **性能**: 组件性能优化良好
6. **类型安全**: TypeScript 类型定义完整准确

---

**版本**: 1.0.0
**最后更新**: 2026-03-20
**维护者**: Event2Table Team
