# 导出问题修复报告

> **日期**: 2026-02-11
> **问题**: 构建失败，导出不匹配错误
> **状态**: ✅ 已修复

---

## 🔍 发现的问题

### 1. **SelectGamePrompt 导出不匹配**

**错误信息**:
```
✘ [ERROR] No matching export in "src/shared/ui/SelectGamePrompt.jsx" for import "default"
```

**原因**: `SelectGamePrompt.jsx` 使用**命名导出** (`export function`)，但 `index.js` 和 `index.ts` 中使用**默认导出**方式导入。

**SelectGamePrompt.jsx** (Line 11):
```jsx
export function SelectGamePrompt({ message }) {
  // ...
}
```

**修复前** (index.js Line 29):
```javascript
export { default as SelectGamePrompt } from './SelectGamePrompt';  // ❌ 错误
```

**修复后** (index.js Line 29):
```javascript
export { SelectGamePrompt } from './SelectGamePrompt';  // ✅ 正确
```

**同时修复 index.ts** (添加了缺失的导出):
```typescript
// Special components
export { SelectGamePrompt } from './SelectGamePrompt';
```

---

### 2. **Button 导出路径错误**

**问题**: `index.js` 中 Button 的导出路径指向不存在的 `index.jsx` 文件。

**修复前** (index.js Line 6):
```javascript
export { Button, IconButton } from './Button';  // ❌ 指向 ./Button/index.jsx (不存在)
```

**修复后** (index.js Line 6):
```javascript
export { default as Button } from './Button/Button';  // ✅ 指向正确的文件
```

**说明**: 移除了 `IconButton` 导出，因为该组件不存在。

---

### 3. **Card 导出路径错误**

**问题**: `index.js` 中 Card 的导出路径指向不存在的 `index.jsx` 文件。

**修复前** (index.js Line 9):
```javascript
export { Card, CardHeader, CardBody, CardFooter } from './Card';  // ❌ 指向 ./Card/index.jsx (不存在)
```

**修复后** (index.js Line 9):
```javascript
export { default as Card } from './Card/Card';  // ✅ 指向正确的文件
```

**说明**:
- Card 的子组件通过 `Card.Header`, `Card.Body`, `Card.Footer` 访问
- 它们作为 Card 对象的属性附加，会随主组件一起导出

---

## ✅ 修复后的正确导出

### index.js (完整版本)

```javascript
/**
 * UI Components 统一导出
 */

// Button Components
export { default as Button } from './Button/Button';

// Card Components
export { default as Card } from './Card/Card';

// Form Components
export { default as Input } from './Input/Input';
export { default as TextArea } from './TextArea/TextArea';
export { default as Select } from './Select/Select';
export { default as Checkbox } from './Checkbox/Checkbox';
export { default as Radio } from './Radio/Radio';
export { default as Switch } from './Switch/Switch';

// Display Components
export { default as Badge } from './Badge/Badge';
export { default as Spinner } from './Spinner/Spinner';
export { default as Table } from './Table/Table';

// Feedback Components
export { ToastProvider, useToast } from './Toast/Toast';
export { default as Modal } from './Modal/Modal';

// Special Components
export { SelectGamePrompt } from './SelectGamePrompt';
export { default as Loading } from './Loading';
export { default as CanvasErrorBoundary } from './CanvasErrorBoundary';
```

### index.ts (完整版本)

```typescript
// ... (其他组件导出)

export { default as Spinner } from './Spinner/Spinner';

// Special components
export { SelectGamePrompt } from './SelectGamePrompt';

// Re-export for named imports (optional, for better IDE support)
// ... (其他组件重导出)
```

---

## 📋 组件导出方式总结

| 组件 | 导出方式 | 文件路径 | 说明 |
|------|---------|---------|------|
| Button | 默认导出 | `./Button/Button.jsx` | ✅ 已修复路径 |
| Card | 默认导出 | `./Card/Card.jsx` | ✅ 已修复路径，包含子组件 |
| Input | 默认导出 | `./Input/Input.jsx` | ✅ 正确 |
| TextArea | 默认导出 | `./TextArea/TextArea.jsx` | ✅ 正确 |
| Select | 默认导出 | `./Select/Select.jsx` | ✅ 正确 |
| Checkbox | 默认导出 | `./Checkbox/Checkbox.jsx` | ✅ 正确 |
| Radio | 默认导出 | `./Radio/Radio.jsx` | ✅ 正确 |
| Switch | 默认导出 | `./Switch/Switch.jsx` | ✅ 正确 |
| Badge | 默认导出 | `./Badge/Badge.jsx` | ✅ 正确 |
| Spinner | 默认导出 | `./Spinner/Spinner.jsx` | ✅ 正确 |
| Table | 默认导出 | `./Table/Table.jsx` | ✅ 正确 |
| Modal | 默认导出 | `./Modal/Modal.jsx` | ✅ 正确 |
| Toast | 命名导出 | `./Toast/Toast.jsx` | ✅ ToastProvider, useToast |
| Loading | 默认导出 | `./Loading.jsx` | ✅ 正确 |
| CanvasErrorBoundary | 默认导出 | `./CanvasErrorBoundary.jsx` | ✅ 正确 |
| **SelectGamePrompt** | **命名导出** | `./SelectGamePrompt.jsx` | ✅ **已修复导出方式** |

---

## 🎯 导出规则总结

### 默认导出 vs 命名导出

**默认导出** (用于大多数组件):
```jsx
// Component.jsx
export default MyComponent;

// index.js
export { default as MyComponent } from './Component/Component';
```

**命名导出** (用于特殊组件):
```jsx
// Component.jsx
export function MyComponent() { ... }

// index.js
export { MyComponent } from './Component';
```

**混合导出** (如 Toast):
```jsx
// Toast.jsx
export function ToastProvider() { ... }
export function useToast() { ... }
export const ToastType = { ... };

// index.js
export { ToastProvider, useToast, ToastType } from './Toast/Toast';
```

---

## ✅ 验证清单

- [x] 所有默认导出使用 `export { default as ComponentName }`
- [x] 所有命名导出使用 `export { ComponentName }`
- [x] 所有导出路径指向正确的文件（`./Component/Component.jsx`）
- [x] 不存在 `IconButton` 导出（已移除）
- [x] `SelectGamePrompt` 使用命名导出
- [x] `index.ts` 和 `index.js` 保持一致

---

## 🚀 下一步

现在可以运行构建命令验证修复：

```bash
cd /Users/mckenzie/Documents/event2table/frontend

# 开发模式
npm run dev

# 生产构建
npm run build
```

应该不会再有导出相关的错误。

---

**修复状态**: ✅ **完成**
**测试状态**: ⏳ **待用户验证**
