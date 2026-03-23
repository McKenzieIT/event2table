# Modal Component

## 概述

Modal 组件是一个功能完整的模态框组件，支持多种尺寸、动画效果和变体。遵循 React 最佳实践和 WCAG 2.1 AA 无障碍标准，具有 ESC 键关闭、点击遮罩层关闭、焦点陷阱、焦点恢复、键盘导航支持和完整的 ARIA 属性。

## Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `isOpen` | `boolean` | - | 是否打开模态框 |
| `onClose` | `() => void` | - | 关闭回调 |
| `title` | `string` | `undefined` | 模态框标题 |
| `children` | `ReactNode` | - | 模态框内容 |
| `size` | `ModalSize` | `'md'` | 模态框尺寸 |
| `fullScreen` | `boolean` | `false` | 是否全屏显示 |
| `animation` | `ModalAnimation` | `'slideUp'` | 动画效果 |
| `glassmorphism` | `boolean` | `false` | 是否启用毛玻璃效果 |
| `variant` | `ModalVariant` | `'default'` | 模态框变体 |
| `overlayClassName` | `string` | `''` | 遮罩层自定义类名 |
| `className` | `string` | `''` | 内容自定义类名 |
| `style` | `CSSProperties` | `undefined` | 自定义样式 |
| `zIndex` | `number` | `1000` | z-index 层级 |
| `enableEscClose` | `boolean` | `true` | 是否启用 ESC 键关闭 |
| `closeOnBackdropClick` | `boolean` | `true` | 是否点击遮罩层关闭 |
| `onBeforeClose` | `() => Promise<boolean>` | `undefined` | 关闭前确认回调 |
| `confirmConfig` | `ModalConfirmConfig` | `{}` | 确认对话框配置 |
| `showHeader` | `boolean` | `true` | 是否显示头部 |
| `showCloseButton` | `boolean` | `true` | 是否显示关闭按钮 |
| `showFooter` | `boolean` | `false` | 是否显示底部 |
| `footer` | `ReactNode` | `undefined` | 底部内容 |
| `onAfterOpen` | `() => void` | `undefined` | 打开后回调 |
| `onAfterClose` | `() => void` | `undefined` | 关闭后回调 |
| `ariaDescribedby` | `string` | `undefined` | ARIA 描述 ID |
| `ariaLabelledby` | `string` | `undefined` | ARIA 标签 ID |
| `draggable` | `boolean \| ModalDragConfig` | `false` | 是否可拖拽 |

### 类型定义

```typescript
type ModalSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full';

type ModalAnimation = 'none' | 'fadeIn' | 'slideUp' | 'slideDown' | 'scaleIn';

type ModalVariant = 'default' | 'danger' | 'success' | 'info';

interface ModalConfirmConfig {
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
}

interface ModalDragConfig {
  enabled?: boolean;
  bounds?: 'window' | 'parent' | { top?: number; right?: number; bottom?: number; left?: number };
  grid?: [number, number];
}

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children?: ReactNode;
  size?: ModalSize;
  fullScreen?: boolean;
  animation?: ModalAnimation;
  glassmorphism?: boolean;
  variant?: ModalVariant;
  overlayClassName?: string;
  className?: string;
  style?: CSSProperties;
  zIndex?: number;
  enableEscClose?: boolean;
  closeOnBackdropClick?: boolean;
  onBeforeClose?: () => Promise<boolean>;
  confirmConfig?: ModalConfirmConfig;
  showHeader?: boolean;
  showCloseButton?: boolean;
  showFooter?: boolean;
  footer?: ReactNode;
  onAfterOpen?: () => void;
  onAfterClose?: () => void;
  ariaDescribedby?: string;
  ariaLabelledby?: string;
  draggable?: boolean | ModalDragConfig;
}
```

## 使用示例

### 基础用法

```tsx
import { Modal } from '@shared/ui';
import { useState } from 'react';

function BasicModal() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>打开模态框</button>
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="基本信息"
      >
        <p>这是模态框的内容</p>
      </Modal>
    </div>
  );
}
```

### 不同尺寸

```tsx
function ModalSizes() {
  const [isOpen, setIsOpen] = useState(false);
  const [size, setSize] = useState<ModalSize>('md');

  return (
    <div>
      <div className="flex gap-2">
        <button onClick={() => { setSize('xs'); setIsOpen(true); }}>XS</button>
        <button onClick={() => { setSize('sm'); setIsOpen(true); }}>SM</button>
        <button onClick={() => { setSize('md'); setIsOpen(true); }}>MD</button>
        <button onClick={() => { setSize('lg'); setIsOpen(true); }}>LG</button>
        <button onClick={() => { setSize('xl'); setIsOpen(true); }}>XL</button>
        <button onClick={() => { setSize('full'); setIsOpen(true); }}>Full</button>
      </div>
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="尺寸示例"
        size={size}
      >
        <p>当前尺寸: {size}</p>
      </Modal>
    </div>
  );
}
```

### 带底部操作

```tsx
function ModalWithFooter() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="确认操作"
      showFooter
      footer={
        <div className="flex justify-end gap-2">
          <button onClick={() => setIsOpen(false)}>取消</button>
          <button onClick={() => setIsOpen(false)}>确认</button>
        </div>
      }
    >
      <p>确定要执行此操作吗？</p>
    </Modal>
  );
}
```

### 关闭前确认

```tsx
function ModalWithConfirm() {
  const [isOpen, setIsOpen] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="编辑表单"
      onBeforeClose={async () => {
        if (hasUnsavedChanges) {
          // 返回 false 会显示确认对话框
          return false;
        }
        return true;
      }}
      confirmConfig={{
        title: '未保存的更改',
        message: '您有未保存的更改，确定要关闭吗？',
        confirmText: '放弃更改',
        cancelText: '继续编辑',
      }}
    >
      <form>
        <input
          type="text"
          placeholder="输入内容..."
          onChange={() => setHasUnsavedChanges(true)}
        />
      </form>
    </Modal>
  );
}
```

### 毛玻璃效果

```tsx
function GlassmorphismModal() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="毛玻璃效果"
      glassmorphism
      animation="fadeIn"
    >
      <p>这是一个带有毛玻璃效果的模态框</p>
    </Modal>
  );
}
```

### 可拖拽模态框

```tsx
function DraggableModal() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="可拖拽模态框"
      draggable
    >
      <p>拖拽标题栏可以移动这个模态框</p>
    </Modal>
  );
}
```

### 自定义拖拽配置

```tsx
function CustomDraggableModal() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="自定义拖拽"
      draggable={{
        enabled: true,
        bounds: 'parent',
        grid: [10, 10],
      }}
    >
      <p>拖拽时按 10px 网格对齐</p>
    </Modal>
  );
}
```

### 不同变体

```tsx
function ModalVariants() {
  const [isOpen, setIsOpen] = useState(false);
  const [variant, setVariant] = useState<ModalVariant>('default');

  return (
    <div>
      <div className="flex gap-2">
        <button onClick={() => { setVariant('default'); setIsOpen(true); }}>默认</button>
        <button onClick={() => { setVariant('danger'); setIsOpen(true); }}>危险</button>
        <button onClick={() => { setVariant('success'); setIsOpen(true); }}>成功</button>
        <button onClick={() => { setVariant('info'); setIsOpen(true); }}>信息</button>
      </div>
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="变体示例"
        variant={variant}
      >
        <p>当前变体: {variant}</p>
      </Modal>
    </div>
  );
}
```

### 不同动画

```tsx
function ModalAnimations() {
  const [isOpen, setIsOpen] = useState(false);
  const [animation, setAnimation] = useState<ModalAnimation>('slideUp');

  return (
    <div>
      <div className="flex gap-2">
        <button onClick={() => { setAnimation('fadeIn'); setIsOpen(true); }}>淡入</button>
        <button onClick={() => { setAnimation('slideUp'); setIsOpen(true); }}>上滑</button>
        <button onClick={() => { setAnimation('slideDown'); setIsOpen(true); }}>下滑</button>
        <button onClick={() => { setAnimation('scaleIn'); setIsOpen(true); }}>缩放</button>
        <button onClick={() => { setAnimation('none'); setIsOpen(true); }}>无动画</button>
      </div>
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="动画示例"
        animation={animation}
      >
        <p>当前动画: {animation}</p>
      </Modal>
    </div>
  );
}
```

### 生命周期回调

```tsx
function ModalWithLifecycle() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="生命周期"
      onAfterOpen={() => console.log('Modal opened')}
      onAfterClose={() => console.log('Modal closed')}
    >
      <p>查看控制台查看生命周期回调</p>
    </Modal>
  );
}
```

### 禁用 ESC 键和遮罩点击

```tsx
function ModalNoClose() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="不可关闭的模态框"
      enableEscClose={false}
      closeOnBackdropClick={false}
      showCloseButton={false}
    >
      <p>只能通过程序调用 onClose() 关闭</p>
      <button onClick={() => setIsOpen(false)}>关闭</button>
    </Modal>
  );
}
```

### 表单编辑模态框

```tsx
function EditFormModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '' });
  const [hasChanges, setHasChanges] = useState(false);

  const handleSave = () => {
    // 保存逻辑
    console.log('Saving:', formData);
    setIsOpen(false);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="编辑用户"
      size="lg"
      showFooter
      footer={
        <div className="flex justify-end gap-2">
          <button onClick={() => setIsOpen(false)}>取消</button>
          <button onClick={handleSave}>保存</button>
        </div>
      }
      onBeforeClose={async () => {
        return !hasChanges;
      }}
      confirmConfig={{
        title: '未保存的更改',
        message: '您有未保存的更改，确定要关闭吗？',
        confirmText: '放弃更改',
        cancelText: '继续编辑',
      }}
    >
      <form>
        <Input
          label="姓名"
          value={formData.name}
          onChange={(e) => {
            setFormData({ ...formData, name: e.target.value });
            setHasChanges(true);
          }}
        />
        <Input
          label="邮箱"
          type="email"
          value={formData.email}
          onChange={(e) => {
            setFormData({ ...formData, email: e.target.value });
            setHasChanges(true);
          }}
        />
      </form>
    </Modal>
  );
}
```

## 注意事项

1. **无障碍性**:
   - 完整支持 WCAG 2.1 AA 标准
   - 自动实现焦点陷阱和焦点恢复
   - 支持 Tab 键导航
   - 完整的 ARIA 属性

2. **键盘操作**:
   - `ESC`: 关闭模态框（可配置）
   - `Tab`: 在可聚焦元素间导航
   - `Shift + Tab`: 反向导航

3. **滚动锁定**:
   - 打开模态框时自动锁定 body 滚动
   - 关闭时自动恢复滚动
   - 自动处理滚动条占位

4. **性能优化**:
   - 使用 `useCallback` 和 `useMemo` 优化
   - 使用 `React.memo` 防止不必要渲染
   - 动画完成后才卸载 DOM

5. **拖拽功能**:
   - 仅在头部区域可拖拽
   - 支持边界限制
   - 支持网格对齐
   - 关闭时自动重置位置

6. **动画效果**:
   - 所有动画都使用 CSS transitions
   - 动画时长: 200ms
   - 可通过 CSS 自定义动画

7. **z-index 管理**:
   - 默认: 1000
   - 确认对话框: 1001
   - 可通过 `zIndex` 属性自定义

8. **确认对话框**:
   - 仅在 `onBeforeClose` 返回 false 时显示
   - 可自定义标题、消息和按钮文本
   - 独立于主模态框的 z-index

## 相关组件

- [`Button`](./Button.md) - 按钮组件
- [`Input`](./Input.md) - 输入框组件
- [`Form`](./Form.md) - 表单组件
- [`ErrorBoundary`](./ErrorBoundary.md) - 错误边界组件
