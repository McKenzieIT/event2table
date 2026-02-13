# Component Performance Optimizations

本文档记录了基于 [Vercel React Best Practices](https://github.com/vercel/next.js/tree/canary/packages/react-best-practices) 对组件库应用的性能优化。

## 优化概览

| 组件 | 优化规则 | 性能提升 |
|------|---------|---------|
| Button | `rerender-memo`, `rerender-simple-expression-in-memo` | 避免不必要的重渲染 |
| Card | `rerender-memo`, `rendering-hoist-jsx` | 子组件 memoized |
| Input | `rerender-memo`, `rerender-functional-setstate` | 自定义比较函数 |
| Table | `rerender-memo`, `rerender-functional-setstate`, `js-combine-iterations` | 排序逻辑优化 |
| Modal | `advanced-event-handler-refs`, `rerender-move-effect-to-event` | 事件处理器稳定 |
| Badge | `rerender-memo` | 简单组件 memoized |

## 1. Re-render Optimization (MEDIUM)

### Button.jsx

**优化**: 使用 `React.memo` + 自定义比较函数

```jsx
// 优化前 - 每次父组件更新都重渲染
const Button = ({ children, variant, ... }) => {
  return <button>...</button>;
};

// 优化后 - 只在关键 props 变化时重渲染
const MemoizedButton = React.memo(Button, (prevProps, nextProps) => {
  return (
    prevProps.variant === nextProps.variant &&
    prevProps.size === nextProps.size &&
    // ...其他关键 props
  );
});
```

**效果**: 避免父组件状态变化导致的无效重渲染

**规则**: `rerender-memo`, `rerender-simple-expression-in-memo`

---

### Card.jsx

**优化**: Memoized 子组件 (Header, Body, Footer, Title)

```jsx
// 优化后
Card.Header = React.memo(function CardHeader({ children, className, ...props }) {
  return <div className={[...].filter(Boolean).join(' ')} {...props}>
    {children}
  </div>;
});
```

**效果**: 静态卡片内容不会因为兄弟组件更新而重渲染

**规则**: `rerender-memo`

---

### Input.jsx

**优化**: 自定义比较函数（包含 value 和 onChange）

```jsx
const MemoizedInput = React.memo(Input, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.onChange === nextProps.onChange &&
    // ...其他 props
  );
});
```

**效果**: Input 组件只在值或处理函数真正变化时更新

**规则**: `rerender-memo`

---

### Table.jsx

**优化**: 功能性 setState 模式 + `useCallback`

```jsx
// 优化前 - 每次渲染创建新函数
const handleClick = () => {
  const nextSort = sorted === 'asc' ? 'desc' : sorted === 'desc' ? null : 'asc';
  onSort(nextSort);
};

// 优化后 - 稳定的回调函数
const handleClick = React.useCallback(() => {
  if (sortable && onSort) {
    // Functional setState pattern
    onSort((prevSort) => {
      if (prevSort === 'asc') return 'desc';
      if (prevSort === 'desc') return null;
      return 'asc';
    });
  }
}, [sortable, onSort]);
```

**效果**: 表头组件不会因为父组件重新渲染而重新创建事件处理器

**规则**: `rerender-functional-setstate`, `rerender-move-effect-to-event`

---

## 2. Advanced Patterns (LOW)

### Modal.jsx

**优化**: Advanced Event Handler Refs 模式

```jsx
// 优化前 - onClose 变化会导致所有 useEffect 重新执行
useEffect(() => {
  const handleEscape = (e) => {
    if (e.key === 'Escape' && onClose) {  // onClose 依赖不稳定
      onClose();
    }
  };
  document.addEventListener('keydown', handleEscape);
  return () => document.removeEventListener('keydown', handleEscape);
}, [isOpen, closeOnEscape, onClose]);  // onClose 导致频繁重新绑定

// 优化后 - 使用 ref 稳定依赖
const onCloseRef = useRef(onClose);

useEffect(() => {
  onCloseRef.current = onClose;
}, [onClose]);

useEffect(() => {
  const handleEscape = (e) => {
    if (e.key === 'Escape' && onCloseRef.current) {  // ref 稳定
      onCloseRef.current();
    }
  };
  document.addEventListener('keydown', handleEscape);
  return () => document.removeEventListener('keydown', handleEscape);
}, [isOpen, closeOnEscape]);  // 不依赖 onClose
```

**效果**: Modal 的事件监听器不会因为 onClose 函数重新创建而重新绑定

**规则**: `advanced-event-handler-refs`

---

## 3. JavaScript Performance (LOW-MEDIUM)

### 所有组件

**优化**: 数组 join 替代字符串模板拼接

```jsx
// 优化前 - 每次创建多个临时字符串
const className = `
  cyber-button
  cyber-button--${variant}
  cyber-button--${size}
  ${disabled ? 'cyber-button--disabled' : ''}
`.trim();  // 创建 3+ 个字符串

// 优化后 - 单次数组操作
const className = [
  'cyber-button',
  `cyber-button--${variant}`,
  `cyber-button--${size}`,
  disabled && 'cyber-button--disabled'
].filter(Boolean).join(' ');
```

**效果**: 减少临时字符串分配，提高 GC 效率

**规则**: `js-batch-dom-css`, `js-combine-iterations`

---

## 4. Rendering Performance (MEDIUM)

### Table.jsx

**优化**: 条件渲染使用三元运算符

```jsx
// 优化前 - 使用 && 可能导致 0 渲染
{sortable && (
  <span className="cyber-table__sort-indicator">
    {sorted === 'asc' && '↑'}
    {sorted === 'desc' && '↓'}
    {!sorted && '↕'}
  </span>
)}

// 优化后 - 更明确的条件
{sortable ? (
  <span className="cyber-table__sort-indicator">
    {sorted === 'asc' ? '↑' : sorted === 'desc' ? '↓' : '↕'}
  </span>
) : null}
```

**效果**: 避免意外渲染 falsy 值

**规则**: `rendering-conditional-render`

---

## 5. Bundle Size Optimization (CRITICAL)

### index.ts

**当前**: 使用 barrel exports

```ts
export { default as Button } from './Button/Button';
export { default as Card } from './Card/Card';
// ...
```

**潜在优化**: Direct imports（未实施 - 维护性优先）

```ts
// 如果 bundle size 成为问题，可以考虑：
// import Button from '@shared/ui/Button/Button';
// 而不是
// import { Button } from '@shared/ui';
```

**规则**: `bundle-barrel-imports`

**决策**: 当前保持 barrel exports 以提高可维护性。如果 bundle size 成为问题，可以切换到直接导入。

---

## 性能监控

### 开发环境检测

使用 React DevTools Profiler 检测不必要的重渲染：

```jsx
// 在开发环境添加 profiler
import { Profiler } from 'react';

<Profiler id="Button" onRender={(id, phase, actualDuration) => {
  if (actualDuration > 16) {  // 超过一帧 (16ms)
    console.warn(`${id} ${phase} took ${actualDuration}ms`);
  }
}}>
  <Button>Click me</Button>
</Profiler>
```

### 生产环境监控

考虑添加性能标记：

```jsx
const Button = React.forwardRef((props, ref) => {
  React.useEffect(() => {
    performance.mark('button-mount');
    return () => performance.mark('button-unmount');
  }, []);

  return <button ref={ref} {...props} />;
});
```

---

## 未实施的优化

### 1. Table 虚拟滚动
**规则**: `rendering-content-visibility`
**原因**: 当前数据量小，不需要虚拟化
**何时实施**: 当表格行数超过 100 时

### 2. Modal 懒加载
**规则**: `bundle-dynamic-imports`
**原因**: Modal 是核心交互组件
**何时实施**: 如果 Modal 包含复杂子组件（如图表编辑器）

### 3. Icon 组件库
**规则**: `bundle-dynamic-imports`
**原因**: 当前使用 props 传递 icon
**何时实施**: 当引入大量图标时

---

## 最佳实践总结

1. **React.memo**: 用于 props 不频繁变化的组件
2. **useCallback**: 用于传递给子组件的事件处理器
3. **useRef**: 用于稳定事件处理器引用（advanced pattern）
4. **数组 join**: 替代模板字符串拼接 className
5. **自定义比较函数**: 当默认浅比较不足时
6. **Memo 子组件**: Card.Header, Table.Row 等静态组件

---

**版本**: 1.0.0
**基于**: Vercel React Best Practices
**最后更新**: 2025-02-11
