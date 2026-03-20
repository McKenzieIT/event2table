# Form System - 使用指南

统一的表单系统，基于 React Hook Form 和 Zod 构建，提供类型安全、高性能的表单组件。

## 特性

- ✅ **类型安全**：完整的 TypeScript 支持
- ✅ **高性能**：基于 React Hook Form 的非受控组件模式
- ✅ **自动验证**：集成 Zod 进行强大的表单验证
- ✅ **易于使用**：简洁的 API 设计
- ✅ **可扩展**：灵活的验证规则和自定义组件

## 快速开始

### 1. 基本用法

```tsx
import { Form, FormInput, useFormContextValue } from '@/shared/ui/components/Form';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// 定义验证 schema
const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type FormData = z.infer<typeof schema>;

function MyForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const handleSubmit = async (data: FormData) => {
    console.log('Form submitted:', data);
    // 处理提交逻辑
  };

  return (
    <Form form={form} onSubmit={handleSubmit}>
      <FormInput
        name="email"
        label="Email"
        type="email"
        placeholder="Enter your email"
        required
      />
      <FormInput
        name="password"
        label="Password"
        type="password"
        placeholder="Enter your password"
        required
      />
      <button type="submit">Submit</button>
    </Form>
  );
}
```

### 2. 使用预定义的验证规则

```tsx
import { validationRules } from '@/shared/ui/utils/validation/rules';

const schema = z.object({
  email: validationRules.email,
  password: validationRules.strongPassword,
  name: validationRules.name,
  age: validationRules.age,
});
```

### 3. 使用预定义的表单 Schema

```tsx
import { formSchemas, type LoginFormValues } from '@/shared/ui/utils/validation/rules';

function LoginForm() {
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(formSchemas.login),
  });

  // ...
}
```

## 组件 API

### Form

主表单容器组件。

```tsx
<Form
  form={form}                    // React Hook Form 实例
  onSubmit={handleSubmit}         // 提交处理函数
  validationMode="onBlur"        // 验证模式（可选）
  resetAfterSubmit={false}       // 提交后重置表单（可选）
>
  {children}
</Form>
```

### FormInput

输入框组件。

```tsx
<FormInput
  name="fieldName"               // 字段名称
  label="Field Label"            // 标签（可选）
  type="text"                    // 输入类型（可选）
  placeholder="Placeholder"      // 占位符（可选）
  helperText="Helper text"       // 帮助文本（可选）
  required={false}               // 是否必填（可选）
  disabled={false}               // 是否禁用（可选）
/>
```

### FormSelect

下拉选择组件。

```tsx
<FormSelect
  name="fieldName"
  label="Field Label"
  options={[
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
  ]}
  placeholder="Select an option"  // 占位符（可选）
  required={false}
/>
```

### FormCheckbox

复选框组件。

```tsx
<FormCheckbox
  name="fieldName"
  label="Checkbox label"
  required={false}
  indeterminate={false}          // 不确定状态（可选）
/>
```

### FormRadio

单选按钮组组件。

```tsx
<FormRadio
  name="fieldName"
  label="Radio Label"
  options={[
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
  ]}
  direction="column"             // 布局方向（可选）
  required={false}
/>
```

## 验证规则

### 预定义规则

```typescript
import { validationRules } from '@/shared/ui/utils/validation/rules';

// 常用规则
validationRules.email           // 邮箱验证
validationRules.password        // 密码验证（最少8位）
validationRules.strongPassword  // 强密码验证
validationRules.name            // 姓名验证
validationRules.username        // 用户名验证
validationRules.phone           // 电话号码验证
validationRules.url             // URL验证
validationRules.age             // 年龄验证
validationRules.date            // 日期验证
validationRules.requiredString  // 必填字符串
validationRules.requiredNumber  // 必填数字
validationRules.requiredBoolean // 必填布尔值
validationRules.optionalString  // 可选字符串
validationRules.optionalNumber  // 可选数字
validationRules.stringArray     // 字符串数组
validationRules.enum(['a', 'b']) // 枚举验证
```

### 预定义 Schema

```typescript
import { formSchemas } from '@/shared/ui/utils/validation/rules';

// 登录表单
formSchemas.login

// 注册表单
formSchemas.registration

// 个人资料表单
formSchemas.profile

// 联系表单
formSchemas.contact
```

### 自定义验证

```typescript
const customSchema = z.object({
  // 自定义规则
  customField: z.string()
    .min(5, 'Must be at least 5 characters')
    .max(50, 'Must be less than 50 characters')
    .regex(/^[a-z]+$/, 'Only lowercase letters allowed'),
  
  // 条件验证
  confirmPassword: z.string()
    .refine((val, ctx) => {
      if (val !== ctx.parent.password) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Passwords don't match",
        });
      }
      return true;
    }),
});
```

## 性能优化

表单系统已经内置了多种性能优化：

1. **React.memo**：所有组件都已使用 React.memo 进行优化
2. **useMemo**：CSS 类名和计算结果都已缓存
3. **useCallback**：事件处理器都已缓存
4. **非受控组件**：使用 React Hook Form 的非受控组件模式，减少重新渲染

## 类型推断

```typescript
import { z } from 'zod';

const schema = z.object({
  email: z.string(),
  password: z.string(),
});

// 自动推断表单数据类型
type FormData = z.infer<typeof schema>;

// 类型安全的表单处理
const handleSubmit = (data: FormData) => {
  // data.email 和 data.password 都有正确的类型
};
```

## 最佳实践

1. **使用 TypeScript**：充分利用类型系统，避免运行时错误
2. **定义清晰的 Schema**：使用 Zod 定义清晰的验证规则
3. **合理使用验证模式**：根据场景选择合适的验证模式
4. **提供友好的错误信息**：为每个验证规则提供清晰的错误消息
5. **复用验证规则**：使用预定义的验证规则，避免重复代码

## 迁移指南

### 从现有组件迁移

如果你已经有使用现有 Input、Select、Checkbox、Radio 组件的表单，可以这样迁移：

```tsx
// 之前
<Input
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={error}
/>

// 之后
<FormInput
  name="email"
  label="Email"
/>
```

## 示例

### 完整的登录表单

```tsx
import { Form, FormInput } from '@/shared/ui/components/Form';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { formSchemas, type LoginFormValues } from '@/shared/ui/utils/validation/rules';

function LoginForm() {
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(formSchemas.login),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const handleSubmit = async (data: LoginFormValues) => {
    try {
      // 提交逻辑
      await login(data);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <Form form={form} onSubmit={handleSubmit}>
      <FormInput
        name="email"
        label="Email"
        type="email"
        placeholder="Enter your email"
        required
      />
      <FormInput
        name="password"
        label="Password"
        type="password"
        placeholder="Enter your password"
        required
      />
      <button type="submit">Login</button>
    </Form>
  );
}
```

## 故障排除

### 常见问题

1. **表单不提交**：检查是否有验证错误，确保所有必填字段都已填写
2. **类型错误**：确保 schema 的类型与表单字段的类型匹配
3. **验证不工作**：检查 resolver 是否正确配置

## 更多资源

- [React Hook Form 文档](https://react-hook-form.com/)
- [Zod 文档](https://zod.dev/)
- [@hookform/resolvers 文档](https://hookform.resolvers.dev/)
