# Button Component

## 概述

Button 组件是一个现代化的、科技风格设计的按钮组件，支持多种变体和尺寸，具有微妙的发光效果和平滑的过渡动画。基于 React.memo 优化，防止不必要的重新渲染。

## Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `variant` | `ButtonVariant` | `'primary'` | 按钮变体类型 |
| `size` | `Size` | `'medium'` | 按钮尺寸 |
| `disabled` | `boolean` | `false` | 是否禁用按钮 |
| `loading` | `boolean` | `false` | 是否显示加载状态 |
| `icon` | `IconComponent` | `undefined` | 图标组件 |
| `onClick` | `MouseEventHandler` | `undefined` | 点击事件处理器 |
| `className` | `string` | `''` | 自定义 CSS 类名 |
| `children` | `ReactNode` | - | 按钮内容 |

### 类型定义

```typescript
type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'ghost'
  | 'danger'
  | 'outline-primary'
  | 'outline-danger'
  | 'outline-secondary'
  | 'success'
  | 'warning'
  | 'info'
  | 'outline-success'
  | 'text';

type Size = 'small' | 'medium' | 'large';

type IconComponent = React.ComponentType<{ className?: string }>;

interface ButtonProps extends Omit<ComponentPropsWithoutRef<'button'>, 'size' | 'onClick'>, BaseComponentProps {
  variant?: ButtonVariant;
  size?: Size;
  icon?: IconComponent;
  loading?: boolean;
  onClick?: MouseEventHandler;
}
```

## 使用示例

### 基础用法

```tsx
import { Button } from '@shared/ui';

function MyComponent() {
  return (
    <div>
      <Button variant="primary">主要按钮</Button>
      <Button variant="secondary">次要按钮</Button>
      <Button variant="ghost">幽灵按钮</Button>
      <Button variant="danger">危险按钮</Button>
    </div>
  );
}
```

### 不同尺寸

```tsx
<Button size="small">小按钮</Button>
<Button size="medium">中等按钮</Button>
<Button size="large">大按钮</Button>
```

### 带图标

```tsx
import { Button } from '@shared/ui';
import { IconDownload } from '@shared/icons';

<Button icon={IconDownload}>下载</Button>
```

### 加载状态

```tsx
<Button loading>提交中...</Button>
```

### 禁用状态

```tsx
<Button disabled>禁用按钮</Button>
```

### 完整示例

```tsx
import { Button } from '@shared/ui';
import { useState } from 'react';

function FormExample() {
  const [loading, setLoading] = useState(false);
  const [disabled, setDisabled] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await submitData();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex gap-2">
      <Button 
        variant="primary" 
        loading={loading}
        onClick={handleSubmit}
      >
        提交
      </Button>
      <Button 
        variant="ghost" 
        disabled={disabled}
        onClick={() => setDisabled(!disabled)}
      >
        切换禁用
      </Button>
      <Button variant="danger" onClick={() => window.location.reload()}>
        刷新
      </Button>
    </div>
  );
}
```

## 注意事项

1. **性能优化**: 组件已使用 `React.memo` 进行优化，具有自定义比较函数，避免不必要的重新渲染
2. **可访问性**: 按钮自动继承原生 `<button>` 元素的所有可访问性属性
3. **样式**: 使用 CSS 类名 `cyber-button` 作为基础类，变体通过 `variant` 属性添加
4. **加载状态**: 当 `loading` 为 `true` 时，按钮会自动禁用并显示旋转加载图标
5. **图标**: 图标会显示在文本左侧，使用 `cyber-button__icon` 类名进行样式控制
6. **类型安全**: 所有属性都有完整的 TypeScript 类型定义

## 相关组件

- [`Input`](./Input.md) - 输入框组件
- [`Select`](./Select.md) - 下拉选择组件
- [`Modal`](./Modal.md) - 模态框组件
