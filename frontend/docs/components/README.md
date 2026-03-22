# Event2Table UI Components API Documentation

## 概述

本文档提供了 Event2Table 项目 UI 组件库的完整 API 文档。所有组件都基于 React + TypeScript 开发，遵循赛博朋克实验室主题设计，具有完整的类型定义和无障碍支持。

## 组件列表

### 基础组件

#### [Button](./Button.md)
现代化的按钮组件，支持多种变体和尺寸，具有发光效果和平滑过渡动画。

- **特性**: 13 种变体、3 种尺寸、加载状态、图标支持
- **性能**: 使用 React.memo 优化
- **无障碍**: 完整的 ARIA 属性支持

#### [Input](./Input.md)
赛博朋克主题的输入框组件，支持多种输入类型、标签、错误状态和图标。

- **特性**: 14 种输入类型、自动 ID 生成、图标支持、帮助文本
- **布局**: CSS Grid 布局
- **无障碍**: 完整的 ARIA 属性支持

#### [Select](./Select.md)
功能丰富的下拉选择组件，支持单选/多选、搜索过滤和键盘导航。

- **特性**: 单选/多选、可搜索、键盘导航、智能定位
- **集成**: React Hook Form 支持
- **无障碍**: 完整的 ARIA 属性和键盘导航

### 数据展示

#### [Table](./Table.md)
基于 TanStack Table 的高性能表格组件，支持虚拟滚动、列固定和可编辑单元格。

- **特性**: 虚拟滚动、列固定、行选择、可编辑单元格
- **性能**: TanStack Table 引擎，支持大数据集
- **功能**: 排序、过滤、分页、自定义渲染

### 布局组件

#### [Modal](./Modal.md)
功能完整的模态框组件，支持多种尺寸、动画效果和拖拽功能。

- **特性**: 6 种尺寸、5 种动画、拖拽、毛玻璃效果
- **无障碍**: WCAG 2.1 AA 标准，焦点陷阱
- **交互**: ESC 关闭、点击遮罩关闭、关闭确认

### 状态组件

#### [ErrorBoundary](./ErrorBoundary.md)
增强版错误边界组件，用于捕获错误并显示备用 UI。

- **特性**: 自定义回退 UI、错误回调、自动重置
- **灵活性**: 支持渲染函数、resetKeys
- **集成**: 错误日志服务集成

### 表单组件

#### [Form](./Form.md)
基于 React Hook Form 的表单组件集合，提供完整的表单字段类型。

**包含组件**:
- `FormInput` - 输入框
- `FormSelect` - 下拉选择
- `FormDatePicker` - 日期选择器
- `FormCheckbox` - 复选框
- `FormRadio` - 单选按钮
- `FormUpload` - 文件上传

- **特性**: Zod 验证、类型安全、实时验证
- **集成**: React Hook Form 完美集成
- **无障碍**: 完整的 ARIA 属性支持

#### [DatePicker](./DatePicker.md)
基于原生日期输入的日期选择器组件，支持日期和时间选择。

- **特性**: 日期/时间选择、日期范围限制、格式化
- **集成**: React Hook Form 支持
- **无障碍**: 原生控件，键盘友好

## 快速开始

### 安装

所有组件都通过 `@shared/ui` 包导出：

```tsx
import { Button, Input, Select, Table, Modal, ErrorBoundary } from '@shared/ui';
import { Form, FormInput, FormSelect, FormDatePicker } from '@shared/ui/components/Form';
```

### 基础示例

```tsx
import { Button, Input, Modal } from '@shared/ui';
import { useState } from 'react';

function App() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <ErrorBoundary>
      <div>
        <Input label="用户名" placeholder="请输入用户名" />
        <Button onClick={() => setIsOpen(true)}>打开对话框</Button>
        <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title="示例">
          <p>这是一个模态框</p>
        </Modal>
      </div>
    </ErrorBoundary>
  );
}
```

### 表单示例

```tsx
import { Form, FormInput, FormSelect, FormDatePicker } from '@shared/ui/components/Form';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  username: z.string().min(3),
  role: z.string(),
  birthDate: z.date(),
});

function MyForm() {
  const form = useForm({
    resolver: zodResolver(schema),
  });

  return (
    <Form form={form} onSubmit={console.log}>
      <FormInput name="username" label="用户名" required />
      <FormSelect name="role" label="角色" options={roleOptions} required />
      <FormDatePicker name="birthDate" label="出生日期" required />
      <button type="submit">提交</button>
    </Form>
  );
}
```

## 设计原则

### 1. 类型安全
所有组件都有完整的 TypeScript 类型定义，提供编译时类型检查和智能提示。

### 2. 性能优化
- 使用 `React.memo` 防止不必要的重新渲染
- 自定义比较函数优化 props 比较
- 虚拟滚动支持大数据集

### 3. 无障碍性
- 完整的 ARIA 属性支持
- 键盘导航支持
- 屏幕阅读器友好
- 遵循 WCAG 2.1 AA 标准

### 4. 可定制性
- 支持自定义 CSS 类名
- 支持自定义样式
- 支持自定义渲染函数
- 支持主题切换

### 5. 开发者体验
- 清晰的 API 设计
- 丰富的使用示例
- 完整的文档
- 友好的错误提示

## 浏览器支持

- Chrome/Edge: 最新 2 个版本
- Firefox: 最新 2 个版本
- Safari: 最新 2 个版本
- 移动浏览器: iOS Safari 12+, Chrome Mobile

## 贡献指南

如需添加新组件或修改现有组件，请遵循以下规范：

1. 使用 TypeScript 编写
2. 添加完整的类型定义
3. 编写使用示例
4. 确保无障碍性
5. 添加性能优化
6. 编写文档

## 相关资源

- [项目架构文档](../../architecture.md)
- [开发指南](../../development/getting-started.md)
- [API 文档](../../api/)
- [组件测试](../../../test/)

## 版本历史

- **v1.0.0** - 初始版本，包含所有基础组件
- **v1.1.0** - 添加 Form 系列组件
- **v1.2.0** - 添加 Table 组件，支持虚拟滚动
- **v1.3.0** - 添加 Modal 拖拽功能
- **v1.4.0** - 完善无障碍支持

## 许可证

MIT License
