# Input Component

## 概述

Input 组件是一个赛博朋克主题风格的输入框组件，支持多种输入类型、标签、错误状态、帮助文本、图标和无障碍功能。使用 CSS Grid 布局实现最佳对齐效果。

## Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `type` | `InputType` | `'text'` | 输入框类型 |
| `label` | `string` | `undefined` | 输入框标签 |
| `placeholder` | `string` | `undefined` | 占位符文本 |
| `value` | `string \| number` | `undefined` | 输入值（受控组件） |
| `error` | `string` | `undefined` | 错误信息 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `required` | `boolean` | `false` | 是否必填 |
| `icon` | `IconComponent` | `undefined` | 图标组件 |
| `helperText` | `string` | `undefined` | 帮助文本 |
| `onChange` | `ChangeEventHandler` | `undefined` | 变更事件处理器 |
| `onBlur` | `FocusEventHandler` | `undefined` | 失焦事件处理器 |
| `onFocus` | `FocusEventHandler` | `undefined` | 聚焦事件处理器 |
| `id` | `string` | `undefined` | 自定义 ID（自动生成如未提供） |
| `name` | `string` | `undefined` | 名称属性 |
| `readOnly` | `boolean` | `false` | 是否只读 |
| `autoFocus` | `boolean` | `false` | 是否自动聚焦 |
| `maxLength` | `number` | `undefined` | 最大长度 |
| `minLength` | `number` | `undefined` | 最小长度 |
| `className` | `string` | `''` | 自定义 CSS 类名 |

### 类型定义

```typescript
type InputType =
  | 'text'
  | 'password'
  | 'email'
  | 'number'
  | 'tel'
  | 'url'
  | 'search'
  | 'date'
  | 'time'
  | 'datetime-local'
  | 'month'
  | 'week'
  | 'file'
  | 'color'
  | 'range';

type IconComponent = React.ComponentType<{ className?: string }>;

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange' | 'onBlur' | 'onFocus' | 'value'>, LabeledComponentProps {
  type?: InputType;
  placeholder?: string;
  icon?: IconComponent;
  value?: string | number;
  onChange?: ChangeEventHandler<HTMLInputElement>;
  onBlur?: FocusEventHandler<HTMLInputElement>;
  onFocus?: FocusEventHandler<HTMLInputElement>;
  id?: string;
  name?: string;
  readOnly?: boolean;
  autoFocus?: boolean;
  maxLength?: number;
  minLength?: number;
}
```

## 使用示例

### 基础用法

```tsx
import { Input } from '@shared/ui';

function MyForm() {
  return (
    <div>
      <Input
        type="text"
        label="用户名"
        placeholder="请输入用户名"
      />
      <Input
        type="password"
        label="密码"
        placeholder="请输入密码"
      />
    </div>
  );
}
```

### 带错误状态

```tsx
import { Input } from '@shared/ui';
import { useState } from 'react';

function FormWithError() {
  const [error, setError] = useState('');

  const validateEmail = (email: string) => {
    if (!email.includes('@')) {
      setError('请输入有效的邮箱地址');
    } else {
      setError('');
    }
  };

  return (
    <Input
      type="email"
      label="邮箱"
      placeholder="example@email.com"
      error={error}
      onChange={(e) => validateEmail(e.target.value)}
    />
  );
}
```

### 带图标

```tsx
import { Input } from '@shared/ui';
import { IconSearch } from '@shared/icons';

function SearchInput() {
  return (
    <Input
      type="search"
      placeholder="搜索..."
      icon={IconSearch}
    />
  );
}
```

### 受控组件

```tsx
import { Input } from '@shared/ui';
import { useState } from 'react';

function ControlledInput() {
  const [value, setValue] = useState('');

  return (
    <Input
      type="text"
      label="搜索"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder="输入搜索关键词"
    />
  );
}
```

### 带帮助文本

```tsx
<Input
  type="password"
  label="密码"
  placeholder="请输入密码"
  helperText="密码至少包含8个字符"
  minLength={8}
  required
/>
```

### 禁用和只读状态

```tsx
<div>
  <Input
    type="text"
    label="用户名"
    value="john_doe"
    disabled
  />
  <Input
    type="text"
    label="邮箱"
    value="john@example.com"
    readOnly
  />
</div>
```

### 完整表单示例

```tsx
import { Input } from '@shared/ui';
import { useState } from 'react';

function UserForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    phone: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
    // 清除错误
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = () => {
    // 验证逻辑
    if (!formData.username) {
      setErrors(prev => ({ ...prev, username: '用户名不能为空' }));
    }
    // ... 其他验证
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
      <Input
        type="text"
        label="用户名"
        placeholder="请输入用户名"
        value={formData.username}
        onChange={handleChange('username')}
        error={errors.username}
        required
      />
      <Input
        type="email"
        label="邮箱"
        placeholder="example@email.com"
        value={formData.email}
        onChange={handleChange('email')}
        error={errors.email}
        required
      />
      <Input
        type="password"
        label="密码"
        placeholder="请输入密码"
        value={formData.password}
        onChange={handleChange('password')}
        error={errors.password}
        helperText="密码至少8个字符"
        minLength={8}
        required
      />
      <Input
        type="tel"
        label="手机号"
        placeholder="请输入手机号"
        value={formData.phone}
        onChange={handleChange('phone')}
        error={errors.phone}
      />
    </form>
  );
}
```

## 注意事项

1. **自动 ID 生成**: 如果未提供 `id` 属性，组件会自动生成唯一 ID 用于标签关联
2. **无障碍性**: 组件完整支持 ARIA 属性，包括 `aria-invalid`、`aria-required`、`aria-describedby`
3. **性能优化**: 使用 `React.memo` 进行优化，具有自定义比较函数
4. **布局**: 使用 CSS Grid 布局，通过 `.cyber-field` 类名实现最佳对齐
5. **错误处理**: 错误信息通过 `error` 属性传递，会自动显示并设置无效状态样式
6. **图标支持**: 图标显示在输入框内部左侧，使用 `.cyber-field__icon` 类名
7. **必填标记**: 当 `required` 为 `true` 时，标签后会自动显示红色星号标记
8. **类型安全**: 所有属性都有完整的 TypeScript 类型定义

## 相关组件

- [`Button`](./Button.md) - 按钮组件
- [`Select`](./Select.md) - 下拉选择组件
- [`Form`](./Form.md) - 表单组件
