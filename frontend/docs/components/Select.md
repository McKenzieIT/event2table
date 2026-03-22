# Select Component

## 概述

Select 组件是一个功能丰富的赛博朋克主题下拉选择组件，支持单选/多选、搜索过滤、键盘导航、智能下拉定位、点击外部关闭、无障碍属性和 React Hook Form 集成。

## Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `name` | `string` | - | 表单字段名称 |
| `label` | `string` | `undefined` | 选择器标签 |
| `options` | `SelectOption[]` | `[]` | 可选项列表 |
| `value` | `string \| number \| (string \| number)[]` | `undefined` | 选中的值 |
| `onChange` | `(value: string \| number \| (string \| number)[]) => void` | `undefined` | 值变更回调 |
| `placeholder` | `string` | `'Select...'` | 占位符文本 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `required` | `boolean` | `false` | 是否必填 |
| `searchable` | `boolean` | `false` | 是否启用搜索 |
| `multiple` | `boolean` | `false` | 是否支持多选 |
| `error` | `string` | `undefined` | 错误信息 |
| `helperText` | `string` | `undefined` | 帮助文本 |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | 尺寸 |
| `control` | `Control` | `undefined` | React Hook Form control |
| `rules` | `ValidationRules` | `undefined` | 验证规则 |
| `className` | `string` | `''` | 自定义 CSS 类名 |

### 类型定义

```typescript
interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface SelectProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange'> {
  name: string;
  label?: string;
  options: SelectOption[];
  value?: string | number | (string | number)[];
  onChange?: (value: string | number | (string | number)[]) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  searchable?: boolean;
  multiple?: boolean;
  error?: string;
  helperText?: string;
  size?: 'small' | 'medium' | 'large';
  control?: Control<FieldValues, any>;
  rules?: ValidationRules;
  className?: string;
}
```

## 使用示例

### 基础单选

```tsx
import { Select } from '@shared/ui';
import { useState } from 'react';

function BasicSelect() {
  const [value, setValue] = useState<string>('');
  
  const options = [
    { value: 'apple', label: '苹果' },
    { value: 'banana', label: '香蕉' },
    { value: 'orange', label: '橙子' },
  ];

  return (
    <Select
      name="fruit"
      label="选择水果"
      options={options}
      value={value}
      onChange={setValue}
      placeholder="请选择水果"
    />
  );
}
```

### 可搜索选择器

```tsx
import { Select } from '@shared/ui';
import { useState } from 'react';

function SearchableSelect() {
  const [value, setValue] = useState<string>('');
  
  const options = [
    { value: 'beijing', label: '北京' },
    { value: 'shanghai', label: '上海' },
    { value: 'guangzhou', label: '广州' },
    { value: 'shenzhen', label: '深圳' },
    { value: 'hangzhou', label: '杭州' },
  ];

  return (
    <Select
      name="city"
      label="选择城市"
      options={options}
      value={value}
      onChange={setValue}
      placeholder="搜索城市..."
      searchable
    />
  );
}
```

### 多选选择器

```tsx
import { Select } from '@shared/ui';
import { useState } from 'react';

function MultiSelect() {
  const [values, setValues] = useState<(string | number)[]>([]);
  
  const options = [
    { value: 'frontend', label: '前端开发' },
    { value: 'backend', label: '后端开发' },
    { value: 'design', label: 'UI/UX 设计' },
    { value: 'product', label: '产品管理' },
  ];

  return (
    <Select
      name="skills"
      label="技能选择"
      options={options}
      value={values}
      onChange={setValues}
      placeholder="选择技能"
      multiple
    />
  );
}
```

### 带错误状态

```tsx
import { Select } from '@shared/ui';
import { useState } from 'react';

function SelectWithError() {
  const [value, setValue] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleChange = (newValue: string | number | (string | number)[]) => {
    setValue(newValue as string);
    if (!newValue) {
      setError('请选择一个选项');
    } else {
      setError('');
    }
  };

  return (
    <Select
      name="category"
      label="分类"
      options={[
        { value: 'tech', label: '技术' },
        { value: 'art', label: '艺术' },
      ]}
      value={value}
      onChange={handleChange}
      error={error}
      required
    />
  );
}
```

### React Hook Form 集成

```tsx
import { Select } from '@shared/ui';
import { useForm } from 'react-hook-form';

function FormWithSelect() {
  const { control } = useForm({
    defaultValues: {
      role: ''
    }
  });

  return (
    <Select
      name="role"
      label="角色"
      control={control}
      options={[
        { value: 'admin', label: '管理员' },
        { value: 'user', label: '普通用户' },
        { value: 'guest', label: '访客' },
      ]}
      placeholder="选择角色"
      required
    />
  );
}
```

### 带验证规则

```tsx
import { Select } from '@shared/ui';
import { useForm } from 'react-hook-form';

function ValidatedSelect() {
  const { control } = useForm({
    defaultValues: {
      priority: ''
    }
  });

  return (
    <Select
      name="priority"
      label="优先级"
      control={control}
      options={[
        { value: 'low', label: '低' },
        { value: 'medium', label: '中' },
        { value: 'high', label: '高' },
      ]}
      placeholder="选择优先级"
      rules={{
        required: '请选择优先级'
      }}
    />
  );
}
```

### 不同尺寸

```tsx
<div>
  <Select
    name="size-small"
    label="小尺寸"
    options={options}
    value={value}
    onChange={setValue}
    size="small"
  />
  <Select
    name="size-medium"
    label="中尺寸"
    options={options}
    value={value}
    onChange={setValue}
    size="medium"
  />
  <Select
    name="size-large"
    label="大尺寸"
    options={options}
    value={value}
    onChange={setValue}
    size="large"
  />
</div>
```

### 禁用选项

```tsx
import { Select } from '@shared/ui';
import { useState } from 'react';

function SelectWithDisabledOptions() {
  const [value, setValue] = useState<string>('');
  
  const options = [
    { value: 'option1', label: '选项 1' },
    { value: 'option2', label: '选项 2', disabled: true },
    { value: 'option3', label: '选项 3' },
  ];

  return (
    <Select
      name="disabled-options"
      label="选择选项"
      options={options}
      value={value}
      onChange={setValue}
    />
  );
}
```

## 注意事项

1. **键盘导航**: 支持以下键盘操作
   - `Enter` / `Space`: 打开下拉菜单或选中选项
   - `Escape`: 关闭下拉菜单
   - `ArrowUp` / `ArrowDown`: 在选项间导航
   - `Tab`: 关闭下拉菜单并移出焦点

2. **智能定位**: 下拉菜单会根据视口位置自动选择向上或向下展开

3. **React Hook Form**: 当提供 `control` 属性时，组件会自动与 React Hook Form 集成

4. **多选模式**: 在多选模式下，选择一个选项后会自动关闭下拉菜单

5. **搜索功能**: 搜索会过滤选项列表，不区分大小写

6. **无障碍性**: 组件完整支持 ARIA 属性，包括 `aria-describedby`、`aria-required`、`aria-invalid`

7. **点击外部关闭**: 点击下拉菜单外部区域会自动关闭菜单

8. **性能优化**: 使用 `React.memo` 进行优化，避免不必要的重新渲染

## 相关组件

- [`Input`](./Input.md) - 输入框组件
- [`Button`](./Button.md) - 按钮组件
- [`Form`](./Form.md) - 表单组件
