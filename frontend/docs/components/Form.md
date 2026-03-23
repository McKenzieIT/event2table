# Form Components

## 概述

Form 系列组件是一套基于 React Hook Form 的表单组件集合，提供了完整的表单字段类型、验证、错误处理和无障碍支持。包括 FormInput、FormSelect、FormDatePicker、FormCheckbox、FormRadio、FormUpload 等组件。

## Form 容器组件

### Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `form` | `UseFormReturn` | - | React Hook Form 实例 |
| `onSubmit` | `(data: TFieldValues) => void \| Promise<void>` | - | 提交回调 |
| `validationMode` | `FormValidationMode` | `'onBlur'` | 验证模式 |
| `reValidateMode` | `FormValidationMode` | `'onChange'` | 重新验证模式 |
| `resetAfterSubmit` | `boolean` | `false` | 提交后是否重置表单 |
| `children` | `ReactNode` | - | 子组件 |
| `className` | `string` | `''` | 自定义 CSS 类名 |
| `id` | `string` | `undefined` | 表单 ID |

### 使用示例

```tsx
import { Form } from '@shared/ui/components/Form';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  username: z.string().min(3, '用户名至少3个字符'),
  email: z.string().email('请输入有效的邮箱'),
  password: z.string().min(8, '密码至少8个字符'),
});

type FormData = z.infer<typeof schema>;

function MyForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: FormData) => {
    console.log('Form data:', data);
    // 提交逻辑
  };

  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormInput name="username" label="用户名" required />
      <FormInput name="email" label="邮箱" type="email" required />
      <FormInput name="password" label="密码" type="password" required />
      <button type="submit">提交</button>
    </Form>
  );
}
```

## FormInput

### Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `name` | `FieldPath<TFieldValues>` | - | 字段名称 |
| `label` | `string` | `undefined` | 标签 |
| `type` | `'text' \| 'email' \| 'password' \| 'number' \| 'tel' \| 'url' \| 'search'` | `'text'` | 输入类型 |
| `placeholder` | `string` | `undefined` | 占位符 |
| `helperText` | `string` | `undefined` | 帮助文本 |
| `required` | `boolean` | `false` | 是否必填 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `autoComplete` | `string` | `undefined` | 自动完成 |
| `className` | `string` | `''` | 自定义 CSS 类名 |

### 使用示例

```tsx
import { FormInput } from '@shared/ui/components/Form';

function MyForm() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormInput
        name="username"
        label="用户名"
        placeholder="请输入用户名"
        required
        helperText="用户名至少3个字符"
      />
      <FormInput
        name="email"
        label="邮箱"
        type="email"
        placeholder="example@email.com"
        required
      />
      <FormInput
        name="phone"
        label="手机号"
        type="tel"
        placeholder="请输入手机号"
      />
    </Form>
  );
}
```

## FormSelect

### Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `name` | `FieldPath<TFieldValues>` | - | 字段名称 |
| `label` | `string` | `undefined` | 标签 |
| `options` | `SelectOption[]` | - | 选项列表 |
| `placeholder` | `string` | `'Select...'` | 占位符 |
| `searchable` | `boolean` | `false` | 是否可搜索 |
| `helperText` | `string` | `undefined` | 帮助文本 |
| `required` | `boolean` | `false` | 是否必填 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `className` | `string` | `''` | 自定义 CSS 类名 |

### 使用示例

```tsx
import { FormSelect } from '@shared/ui/components/Form';

function MyForm() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormSelect
        name="role"
        label="角色"
        options={[
          { value: 'admin', label: '管理员' },
          { value: 'user', label: '普通用户' },
          { value: 'guest', label: '访客' },
        ]}
        required
      />
      <FormSelect
        name="city"
        label="城市"
        options={cityOptions}
        searchable
        placeholder="搜索城市..."
      />
    </Form>
  );
}
```

## FormDatePicker

### Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `name` | `FieldPath<TFieldValues>` | - | 字段名称 |
| `label` | `string` | `undefined` | 标签 |
| `format` | `string` | `'YYYY-MM-DD'` | 日期格式 |
| `showTime` | `boolean` | `false` | 是否显示时间 |
| `timeFormat` | `string` | `'HH:mm'` | 时间格式 |
| `minDate` | `Date` | `undefined` | 最小日期 |
| `maxDate` | `Date` | `undefined` | 最大日期 |
| `placeholder` | `string` | `'Select date...'` | 占位符 |
| `helperText` | `string` | `undefined` | 帮助文本 |
| `required` | `boolean` | `false` | 是否必填 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `className` | `string` | `''` | 自定义 CSS 类名 |

### 使用示例

```tsx
import { FormDatePicker } from '@shared/ui/components/Form';

function MyForm() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormDatePicker
        name="birthDate"
        label="出生日期"
        maxDate={new Date()}
        required
      />
      <FormDatePicker
        name="appointmentDate"
        label="预约时间"
        showTime
        placeholder="选择日期和时间"
      />
      <FormDatePicker
        name="startDate"
        label="开始日期"
        minDate={new Date()}
        helperText="只能选择今天之后的日期"
      />
    </Form>
  );
}
```

## FormCheckbox

### Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `name` | `FieldPath<TFieldValues>` | - | 字段名称 |
| `label` | `string` | `undefined` | 标签 |
| `indeterminate` | `boolean` | `false` | 半选状态 |
| `helperText` | `string` | `undefined` | 帮助文本 |
| `required` | `boolean` | `false` | 是否必填 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `className` | `string` | `''` | 自定义 CSS 类名 |

### 使用示例

```tsx
import { FormCheckbox } from '@shared/ui/components/Form';

function MyForm() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormCheckbox
        name="agree"
        label="我同意服务条款和隐私政策"
        required
      />
      <FormCheckbox
        name="newsletter"
        label="订阅新闻通讯"
        helperText="我们会定期发送最新动态"
      />
    </Form>
  );
}
```

## FormRadio

### Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `name` | `FieldPath<TFieldValues>` | - | 字段名称 |
| `label` | `string` | `undefined` | 标签 |
| `options` | `RadioOption[]` | - | 选项列表 |
| `direction` | `'row' \| 'column'` | `'column'` | 布局方向 |
| `helperText` | `string` | `undefined` | 帮助文本 |
| `required` | `boolean` | `false` | 是否必填 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `className` | `string` | `''` | 自定义 CSS 类名 |

### 使用示例

```tsx
import { FormRadio } from '@shared/ui/components/Form';

function MyForm() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormRadio
        name="gender"
        label="性别"
        options={[
          { value: 'male', label: '男' },
          { value: 'female', label: '女' },
          { value: 'other', label: '其他' },
        ]}
        required
      />
      <FormRadio
        name="plan"
        label="订阅计划"
        direction="row"
        options={[
          { value: 'free', label: '免费版' },
          { value: 'pro', label: '专业版' },
          { value: 'enterprise', label: '企业版' },
        ]}
      />
    </Form>
  );
}
```

## FormUpload

### Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `name` | `FieldPath<TFieldValues>` | - | 字段名称 |
| `label` | `string` | `undefined` | 标签 |
| `accept` | `string` | `undefined` | 接受的文件类型 |
| `multiple` | `boolean` | `false` | 是否多选 |
| `maxSize` | `number` | `5242880` | 最大文件大小（字节） |
| `maxFiles` | `number` | `10` | 最大文件数量 |
| `enableDragDrop` | `boolean` | `true` | 是否启用拖拽 |
| `onUpload` | `(files: File[]) => Promise<UploadFile[]>` | `undefined` | 上传处理器 |
| `buttonText` | `string` | `'上传文件'` | 按钮文本 |
| `showPreview` | `boolean` | `true` | 是否显示预览 |
| `helperText` | `string` | `undefined` | 帮助文本 |
| `required` | `boolean` | `false` | 是否必填 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `className` | `string` | `''` | 自定义 CSS 类名 |

### 使用示例

```tsx
import { FormUpload } from '@shared/ui/components/Form';

function MyForm() {
  const handleUpload = async (files: File[]) => {
    // 上传文件到服务器
    const uploadedFiles = await Promise.all(
      files.map(async (file) => {
        const result = await uploadFile(file);
        return {
          id: result.id,
          file,
          progress: 100,
          status: 'success' as const,
        };
      })
    );
    return uploadedFiles;
  };

  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormUpload
        name="avatar"
        label="头像"
        accept="image/*"
        maxSize={2 * 1024 * 1024} // 2MB
        onUpload={handleUpload}
        buttonText="选择图片"
        helperText="支持 JPG、PNG 格式，最大 2MB"
      />
      <FormUpload
        name="documents"
        label="文档"
        accept=".pdf,.doc,.docx"
        multiple
        maxFiles={5}
        onUpload={handleUpload}
        enableDragDrop
      />
    </Form>
  );
}
```

## 注意事项

1. **表单验证**:
   - 使用 Zod 进行类型安全的验证
   - 支持自定义验证规则
   - 实时验证和提交时验证

2. **错误处理**:
   - 自动显示字段级错误
   - 支持自定义错误消息
   - 错误状态样式自动应用

3. **无障碍性**:
   - 完整的 ARIA 属性支持
   - 标签和输入正确关联
   - 键盘导航支持

4. **性能优化**:
   - 使用 React Hook Form 的优化
   - 减少不必要的重新渲染
   - 表单状态管理高效

5. **类型安全**:
   - 完整的 TypeScript 类型支持
   - 类型推断自动完成
   - 编译时类型检查

6. **最佳实践**:
   - 使用 Zod schema 定义验证规则
   - 为所有字段提供标签和帮助文本
   - 合理设置验证模式
   - 处理异步提交

## 相关组件

- [`Input`](./Input.md) - 独立输入框组件
- [`Select`](./Select.md) - 独立选择器组件
- [`DatePicker`](./DatePicker.md) - 独立日期选择器组件
- [`Button`](./Button.md) - 按钮组件
