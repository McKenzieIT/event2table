# @shared/ui - Event2Table 组件库

生产级 React 组件库，采用 Cyberpunk Lab 主题设计。

## 组件命名规范

### 文件命名

- **组件文件**: 使用 PascalCase，如 `Button.tsx`
- **样式文件**: 与组件同名，如 `Button.css`
- **类型文件**: 组件名 + `.type-test.tsx`，如 `Button.type-test.tsx`
- **测试文件**: 组件名 + `.test.tsx`，如 `Button.test.tsx`

### 组件命名

- **基础组件**: 使用单一名词，如 `Button`, `Card`, `Input`
- **复合组件**: 使用名词短语，如 `SearchInput`, `SelectGamePrompt`
- **子组件**: 使用父组件名 + 子功能，如 `Card.Header`, `Card.Body`

### 变量和函数命名

- **Props 接口**: 组件名 + `Props`，如 `ButtonProps`
- **类型导出**: 使用 `export type`，如 `export type { ButtonProps }`
- **事件处理器**: `on` + 动作，如 `onClick`, `onChange`, `onFocus`

## Props 接口设计原则

### 基础 Props 继承

所有组件应继承基础 Props 接口：

```typescript
import type { BaseComponentProps } from '@/types/common';

export interface ComponentProps extends BaseComponentProps {
  // 组件特定属性
}
```

### Props 类型定义

1. **必需属性**: 明确标注必需属性
2. **可选属性**: 提供合理的默认值
3. **回调函数**: 使用已定义的事件处理器类型
4. **枚举类型**: 使用联合类型而非字符串

```typescript
// ✅ 好的做法
export interface ButtonProps extends BaseComponentProps {
  variant?: ButtonVariant;
  size?: Size;
  onClick?: MouseEventHandler;
}

// ❌ 避免
export interface ButtonProps {
  variant: string; // 应使用联合类型
  size?: 'small' | 'medium' | 'large'; // 应使用已定义的 Size 类型
}
```

### Props 文档注释

每个属性都应有 JSDoc 注释：

```typescript
export interface ButtonProps extends BaseComponentProps {
  /** 按钮变体 */
  variant?: ButtonVariant;
  /** 按钮尺寸 */
  size?: Size;
  /** 是否禁用 */
  disabled?: boolean;
  /** 加载状态 */
  loading?: boolean;
}
```

## 样式规范

### CSS 类命名

使用 BEM 风格的命名规范：

```css
/* 组件类 */
.cyber-button { }

/* 修饰符 */
.cyber-button--primary { }
.cyber-button--disabled { }
.cyber-button--loading { }

/* 子元素 */
.cyber-button__icon { }
.cyber-button__spinner { }
```

### Tailwind CSS 使用

1. **优先使用 Tailwind 工具类**进行布局和间距
2. **自定义 CSS**用于组件特定样式和动画
3. **避免内联样式**，使用类名控制样式

```jsx
// ✅ 好的做法
<div className="flex items-center gap-4 p-4 cyber-card">
  <Card.Body>Content</Card.Body>
</div>

// ❌ 避免
<div style={{ display: 'flex', padding: '16px' }}>
  Content
</div>
```

### 样式组织

```css
/* 1. 组件基础样式 */
.cyber-button {
  /* ... */
}

/* 2. 变体样式 */
.cyber-button--primary { }
.cyber-button--secondary { }

/* 3. 尺寸样式 */
.cyber-button--sm { }
.cyber-button--md { }

/* 4. 状态样式 */
.cyber-button--disabled { }
.cyber-button--loading { }

/* 5. 子元素样式 */
.cyber-button__icon { }
```

## 组件分类

### 基础组件

通用 UI 组件，可在任何场景使用：

- **Button** - 按钮组件
- **Input** - 输入框组件
- **TextArea** - 多行文本输入
- **Select** - 下拉选择器
- **Checkbox** - 复选框
- **Radio** - 单选按钮
- **Switch** - 开关切换
- **Badge** - 徽章标签
- **Spinner** - 加载指示器
- **Table** - 数据表格

### 业务组件

与业务逻辑相关的组件：

- **SelectGamePrompt** - 游戏选择提示
- **ConfirmDialog** - 确认对话框
- **SearchInput** - 搜索输入框
- **BulkOperationsToolbar** - 批量操作工具栏

### 布局组件

用于页面布局的组件：

- **Card** - 卡片容器
- **Modal** - 模态框
- **PageLoader** - 页面加载器
- **Pagination** - 分页组件
- **Breadcrumb** - 面包屑导航

### 状态组件

显示各种状态的组件：

- **EmptyState** - 空状态
- **ErrorState** - 错误状态
- **Skeleton** - 骨架屏
- **Toast** - 消息提示
- **Loading** - 加载状态

### 特殊组件

特殊用途的组件：

- **ErrorBoundary** - 错误边界
- **CanvasErrorBoundary** - 画布错误边界
- **PerformanceMonitor** - 性能监控
- **CodeBlock** - 代码块

## 类型定义

所有组件应使用 `@/types/common` 中定义的通用类型：

```typescript
import type {
  Size,           // 'sm' | 'md' | 'lg'
  Variant,        // 'primary' | 'secondary' | 'ghost' | 'danger' ...
  Priority,       // 'high' | 'medium' | 'low'
  Status,         // 'idle' | 'loading' | 'success' | 'error'
  IconComponent,  // 图标组件类型
  SelectOption,   // 选项类型
  BaseComponentProps,
  MouseEventHandler,
  ValueChangeCallback,
} from '@/types/common';
```

## Design Philosophy

**Theme**: "Refined Cyberpunk Lab" - 保守、专业的科技美学，带有微妙的赛博朋克元素

### Core Design Principles

1. **传统网格布局**: 12列网格系统，非对称
2. **微妙动画**: 向上滑动淡入（不使用全息效果，以避免性能风险）
3. **悬停优先交互**: 悬停时才出现发光效果（不使用持续脉冲）
4. **专业美学**: 精炼的科技外观，适合数据工具
5. **暗模式优化**: 优化的黑色背景，带有青色点缀

### Color Palette

| Role | Color | Usage |
|------|-------|-------|
| Primary (Cyan) | `#06B6D4` | CTA, active states, links |
| Background | `#000000` | Main background (OLED-optimized) |
| Surface | `rgba(15, 23, 42, 0.6)` | Cards, modals |
| Text Primary | `#F1F5F9` | Headlines, important text |
| Text Secondary | `#94A3B8` | Labels, descriptions |
| Text Tertiary | `#64748B` | Disabled states |
| Success | `#22C55E` | Success states |
| Warning | `#F59E0B` | Warning states |
| Danger | `#EF4444` | Error states |

## Installation

```bash
# Components are already included in the project
# Import from @shared/ui
```

## Usage

```javascript
import { Button, Card, Input, Table, Modal, Badge } from '@shared/ui';

function MyPage() {
  return (
    <Card>
      <Card.Header>
        <Card.Title>Data Generator</Card.Title>
      </Card.Header>
      <Card.Body>
        <Input label="Game Name" placeholder="Enter name..." />
        <Button variant="primary">Generate</Button>
      </Card.Body>
    </Card>
  );
}
```

## Components

### Button

主要行动按钮，具有悬停发光效果。

**Variants**: `primary`, `secondary`, `ghost`, `danger`
**Sizes**: `sm`, `md`, `lg`

```jsx
<Button variant="primary" onClick={handleClick}>
  Generate HQL
</Button>

<Button variant="danger" loading={isLoading}>
  Delete
</Button>

<Button size="lg" icon={Icon}>
  With Icon
</Button>
```

**Features**:
- 悬停发光效果（主色调为青色，危险色调为红色）
- 加载旋转器
- 图标支持
- 禁用状态

### Card

具有玻璃质感的卡片，带有微妙的边框和阴影。

**Variants**: `default`, `outlined`, `elevated`
**Padding**: `sm`, `md`, `lg`, `none`

```jsx
<Card hoverable glowing>
  <Card.Header>
    <Card.Title>Card Title</Card.Title>
  </Card.Header>
  <Card.Body>
    Card content goes here
  </Card.Body>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>
```

**Features**:
- 玻璃质感效果（backdrop-filter blur）
- 悬停提升效果
- 可选连续发光
- 子组件：Header, Body, Footer, Title

### Input

表单输入框，具有聚焦光晕和验证状态。

**Types**: `text`, `password`, `number`, `email`

```jsx
<Input
  label="Game Name"
  placeholder="Enter game name..."
  value={value}
  onChange={(e) => setValue(e.target.value)}
  helperText="This field is required"
  required
/>

<Input
  label="Password"
  type="password"
  error="Password must be at least 8 characters"
/>
```

**Features**:
- 聚焦光晕效果（青色）
- 验证状态（错误、成功）
- 辅助文本
- 图标支持
- 必填指示器

### Table

数据表格，带有微妙的行悬停效果。

**Variants**: `default`, `bordered`, `compact`
**Sizes**: `sm`, `md`, `lg`

```jsx
<Table striped hoverable>
  <Table.Header>
    <Table.Row>
      <Table.Head sortable>Game Name</Table.Head>
      <Table.Head align="center">Events</Table.Head>
      <Table.Head align="right">Last Update</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {games.map((game) => (
      <Table.Row key={game.id}>
        <Table.Cell>{game.name}</Table.Cell>
        <Table.Cell align="center">{game.events}</Table.Cell>
        <Table.Cell align="right">{game.updatedAt}</Table.Cell>
      </Table.Row>
    ))}
  </Table.Body>
</Table>
```

**Features**:
- 条纹条纹（可选）
- 行悬停（背景颜色变化，不完全高亮）
- 可排序列带有指示器
- 响应式溢出
- 点击行

### Modal

带有背景模糊和向上滑动动画的对话框模态框。

**Sizes**: `sm`, `md`, `lg`, `xl`, `full`
**Variants**: `default`, `danger`, `warning`

```jsx
const [isOpen, setIsOpen] = useState(false);

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Delete"
  variant="danger"
  showFooter
  footerActions={
    <>
      <Button variant="ghost" onClick={() => setIsOpen(false)}>Cancel</Button>
      <Button variant="danger" onClick={handleDelete}>Delete</Button>
    </>
  }
>
  <p>Are you sure you want to delete this game?</p>
  <p>This action cannot be undone.</p>
</Modal>
```

**Features**:
- 背景模糊效果
- 向上滑动入场动画
- 聚焦陷阱
- ESC键关闭
- 自定义底部动作
- 移动设备响应式（底部抽屉）

### Badge

带有发光装饰的状态徽章。

**Variants**: `default`, `primary`, `success`, `warning`, `danger`, `info`

```jsx
<Badge variant="success" dot>Active</Badge>
<Badge variant="warning">Draft</Badge>
<Badge variant="primary" pill>New</Badge>
```

**Features**:
- 色彩点指示器
- 圆角形状（可选）
- 悬停发光效果
- 状态颜色

## Component Showcase

在交互展示中查看所有组件：

```bash
# 访问: /component-showcase
import ComponentShowcase from '@shared/ui/__showcase__/ComponentShowcase';
```

展示演示：
- 所有组件变体
- 交互状态
- 动画时间
- 使用示例

## Theming

### CSS 自定义属性

在应用程序中覆盖主题标记：

```css
:root {
  /* 颜色 */
  --color-primary: #06B6D4;
  --color-primary-light: #22D3EE;

  /* 背景 */
  --bg-primary: #000000;
  --bg-secondary: rgba(15, 23, 42, 0.6);
  --bg-tertiary: rgba(15, 23, 42, 0.8);

  /* 文本 */
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-tertiary: #64748B;

  /* 边框 */
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-default: rgba(6, 182, 212, 0.2);
}
```

### 深色模式

所有组件默认支持深色模式。要支持浅色模式：

```css
[data-theme="light"] {
  --bg-primary: #FFFFFF;
  --text-primary: #0F172A;
  /* ... 覆盖其他标记 */
}
```

## Best Practices

### 1. 组件组合

使用子组件以保持代码整洁：

```jsx
// 好的
<Card>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Body>Content</Card.Body>
</Card>

// 不好的
<Card className="custom-header">...</Card>
```

### 2. 变体选择

- **主要**: 主要CTA（每页一个）
- **次要**: 替代性操作
- **幽灵**: 低优先级操作
- **危险**: 析构性操作

### 3. 加载状态

始终为异步操作提供反馈：

```jsx
const [loading, setLoading] = useState(false);

const handleClick = async () => {
  setLoading(true);
  try {
    await apiCall();
  } finally {
    setLoading(false);
  }
};

<Button loading={loading} onClick={handleClick}>
  Submit
</Button>
```

### 4. 可访问性

所有组件支持：
- 键盘导航
- ARIA属性
- 聚焦管理
- 屏幕阅读器支持

### 5. 性能

- 动画使用CSS变换（GPU加速）
- 不使用连续动画（仅悬停）
- 模态的懒加载
- 大表格的虚拟滚动

## Migration Guide

### 从现有组件迁移

1. **识别组件类型**（按钮、卡片等）
2. **从@shared/ui导入**
3. **更新props**以匹配新API
4. **验证样式和交互**

示例迁移：

```jsx
// 迁移前
<button className="btn btn-primary" onClick={action}>
  Click
</button>

// 迁移后
import { Button } from '@shared/ui';

<Button variant="primary" onClick={action}>
  Click
</Button>
```

## File Structure

```
@shared/ui/
├── Button/
│   ├── Button.jsx
│   └── Button.css
├── Card/
│   ├── Card.jsx
│   └── Card.css
├── Input/
│   ├── Input.jsx
│   └── Input.css
├── Table/
│   ├── Table.jsx
│   └── Table.css
├── Modal/
│   ├── Modal.jsx
│   └── Modal.css
├── Badge/
│   ├── Badge.jsx
│   └── Badge.css
├── __showcase__/
│   ├── ComponentShowcase.jsx
│   └── ComponentShowcase.css
├── index.ts
└── README.md
```

## Contributing

### 添加新组件

1. 创建组件目录：`ComponentName/`
2. 创建 `ComponentName.jsx` 和 `ComponentName.css`
3. 按照现有模式（变体、大小、forwardRef）编写代码
4. 添加到 `index.ts` 导出
5. 添加展示示例
6. 更新此README

### 组件模板

```jsx
import React from 'react';
import './ComponentName.css';

const ComponentName = React.forwardRef(({
  // props
}, ref) => {
  return (
    <div ref={ref} className="cyber-component">
      {/* 实现 */}
    </div>
  );
});

export default ComponentName;
```

## Performance Notes

- **动画性能**: 所有动画使用 `transform` 和 `opacity`（GPU加速）
- **打包大小**: 组件库是tree-shakeable
- **懒加载**: 模态使用React Portal以实现最佳渲染
- **CSS-in-JS**: 使用vanilla CSS以提高运行时性能

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT

## Credits

设计系统基于"Cyberpunk Lab"主题 - 精炼、专业的科技美学，带有微妙的赛博朋克元素。

---

**版本**: 1.0.0
**最后更新日期**: 2025-02-11
**维护者**: DWD生成器团队