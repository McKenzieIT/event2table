# Zod Schema 验证相关的测试失败深入分析

**分析日期**: 2026-03-23
**项目**: Event2Table Frontend
**分析目标**: 识别和解决 Zod schema 验证中的常见问题

---

## 目录
1. [Zod 使用概况](#zod-使用概况)
2. [失败的测试文件列表](#失败的测试文件列表)
3. [常见 Schema 定义问题](#常见-schema-定义问题)
4. [具体失败案例分析](#具体失败案例分析)
5. [修复建议](#修复建议)
6. [最佳实践](#最佳实践)

---

## Zod 使用概况

### 项目中 Zod 的使用范围
- **总计**: 50 处 Zod 相关代码
- **主要文件**:
  - `src/shared/ui/utils/validation/rules.ts` - 验证规则定义
  - `src/shared/ui/components/Form/` - Form 组件及其测试
  - 各种业务组件的表单验证

### Zod 集成方式
```typescript
// 核心集成点
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useForm } from 'react-hook-form';

// 使用模式
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const form = useForm({
  resolver: zodResolver(schema),
  mode: 'onBlur',
});
```

---

## 失败的测试文件列表

### Form 相关测试 (18 个文件)
| 文件 | 规模 | 关键点 | 状态 |
|------|------|--------|------|
| `Form.validation.test.tsx` | 269 行 | 验证错误显示、模式测试 | ⚠️ 容易失败 |
| `FormInput.test.tsx` | 412 行 | required_error 配置 | ⚠️ 常见问题 |
| `FormDatePicker.test.tsx` | 200+ 行 | 日期验证、格式处理 | ⚠️ 类型转换问题 |
| `Form.submission.test.tsx` | 200+ 行 | 提交流程、数据验证 | ✅ 相对稳定 |
| `FormCheckbox.test.tsx` | 200+ 行 | boolean refine() | ⚠️ 自定义验证 |
| `FormSelect.test.tsx` | 200+ 行 | string.min(1) | ⚠️ 空值处理 |
| `FormRadio.test.tsx` | 200+ 行 | 枚举验证 | ⚠️ 选项绑定 |
| `FormUpload.test.tsx` | 300+ 行 | 文件类型验证 | ⚠️ 复杂验证 |
| `FormRichText.test.tsx` | 300+ 行 | 自定义 html 验证 | ⚠️ 自定义验证 |
| 其他 Form 集成测试 | - | 组合场景 | ⚠️ 交互问题 |

---

## 常见 Schema 定义问题

### 问题 1: required_error 配置不一致

**问题示例**（FormInput.test.tsx:244）:
```typescript
// ❌ 问题：mixed required_error 风格
const schema = z.object({
  email: z.string({ required_error: 'Email is required' }).email('Invalid email format'),
});

// 同一文件中另一处使用
const schema = z.object({
  email: z.string().email('Invalid email'),  // 没有 required_error
});
```

**根本原因**:
- Zod v4 中，`required_error` 只在 undefined/null 时触发
- `.email()` 验证发生在 `.string()` 之后
- 如果字符串为空 `""`，不会触发 required_error，而是触发 email 验证失败

**影响**:
- 测试中期望的错误消息不一致
- 某些 schema 显示 "Email is required"，某些显示 "Invalid email"

---

### 问题 2: undefined vs null 处理差异

**问题示例**（FormInput.test.tsx:203-219）:
```typescript
// 测试处理 null
it('should handle null value', () => {
  render(
    <TestFormWrapper defaultValues={{ email: null }}>  // null
      <FormInput name="email" label="Email" />
    </TestFormWrapper>
  );
  expect(screen.getByRole('textbox')).toHaveValue('');
});

// 测试处理 undefined
it('should handle undefined value', () => {
  render(
    <TestFormWrapper defaultValues={{}}>  // undefined（隐含）
      <FormInput name="email" label="Email" />
    </TestFormWrapper>
  );
  expect(screen.getByRole('textbox')).toHaveValue('');
});
```

**Zod 验证差异**:
```typescript
const schema = z.object({
  email: z.string().email(),
});

// 测试 1: null
schema.parseAsync({ email: null })  // ❌ 错误: undefined required
// 或者如果设置 .nullable()
schema.parseAsync({ email: null })  // ✅ 通过

// 测试 2: undefined
schema.parseAsync({})  // ❌ 错误: undefined required
schema.parseAsync({ email: undefined })  // ❌ 错误: undefined required
```

**修复方式**:
```typescript
// 需要显式声明 nullable/optional
const schema = z.object({
  email: z.string().email().optional().nullable(),
  // 或者
  email: z.string().email().nullable(),
});
```

---

### 问题 3: 日期字段的类型转换

**问题示例**（FormDatePicker.test.tsx:135-144）:
```typescript
// ❌ 测试期望字符串，但 defaultValues 可能是 Date 对象
it('should handle default value', () => {
  const defaultDate = new Date('2024-01-15');  // JavaScript Date
  render(
    <TestFormWrapper defaultValues={{ birthDate: defaultDate }}>
      <FormDatePicker name="birthDate" label="Birth Date" />
    </TestFormWrapper>
  );
  const input = screen.getByLabelText('Birth Date');
  expect(input).toHaveValue('2024-01-15');  // 期望 string
});

// Schema 定义
const schema = z.object({
  birthDate: z.string().datetime(),  // 期望 string
});
```

**问题**:
- HTML 日期输入返回 `YYYY-MM-DD` 格式字符串
- defaultValues 中可能是 JavaScript Date 对象
- Zod `.datetime()` 验证器期望 ISO 8601 格式或 Date
- 类型不匹配导致验证失败

---

### 问题 4: 空字符串 vs 缺失值

**问题示例**（验证规则 rules.ts:40-41）:
```typescript
email: z
  .string({
    required_error: 'Email is required',
    invalid_type_error: 'Email must be a string',
  })
  .min(1, 'Email is required')  // ❌ min(1) 检查空字符串
  .email('Invalid email format'),
```

**验证顺序**:
1. `.string()` - 检查 required_error（undefined/null）
2. `.min(1)` - 检查空字符串 `""`
3. `.email()` - 检查格式

**问题场景**:
```typescript
// 场景 1: 用户清空输入
schema.parseAsync({ email: "" })
// 触发 .min(1) 的错误："Email is required"（与 required_error 重复）

// 场景 2: 用户输入无效邮箱
schema.parseAsync({ email: "invalid" })
// 触发 .email() 的错误："Invalid email format"

// 测试期望哪个错误消息？⚠️ 关键问题！
```

---

### 问题 5: 选择框的空值验证

**问题示例**（FormSelect.test.tsx 中的 schema）:
```typescript
const schema = z.object({
  sport: z.string().min(1, 'Please select a sport'),
});

// 问题：如果没有选择，defaultValue 是什么？
// - 可能是 ""（空字符串）→ 触发 min(1)
// - 可能是 undefined → 触发 required_error
// - 可能是 null → 如果不是 nullable() 则失败
```

**React Hook Form 默认行为**:
```typescript
const form = useForm({
  defaultValues: {
    sport: undefined  // 未选择时
  }
});

// Zod 验证
const schema = z.object({
  sport: z.string().min(1, 'Please select a sport'),
  // sport: undefined 会触发 "Required" 错误，而不是 min(1) 错误
});
```

---

### 问题 6: Checkbox 的 Boolean 验证

**问题示例**（FormCheckbox.test.tsx:186-208）:
```typescript
const schema = z.object({
  agree: z.boolean().refine((val) => val === true, 'You must agree'),
});

// defaultValues 设置
const form = useForm({
  resolver: zodResolver(schema),
  defaultValues: { agree: false },  // 显式 false
  mode: 'onSubmit',
});
```

**验证问题**:
- Zod boolean 期望 `true | false`
- 如果接收 `"on"` 或 `"off"`（HTML checkbox value），会失败
- refine() 自定义验证在 boolean 验证后才运行

---

## 具体失败案例分析

### 案例 1: Form.validation.test.tsx - 验证错误显示

**失败现象**:
```
✗ should show validation errors on submit
  Error: "Invalid email" expected but got "Email is required"
```

**代码**（49-64 行）:
```typescript
const schema = z.object({
  email: z.string().email('Invalid email'),
});

// 测试期望：点击 submit → 显示 "Invalid email"
// 实际：空字段 → required_error 或 min(1) → 错误信息不匹配
```

**根因**:
- Schema 没有定义 `required_error`
- Zod 默认返回通用错误消息
- 测试期望 `.email()` 错误，但实际得到 required 错误

---

### 案例 2: FormInput.test.tsx - required_error 一致性

**失败现象**:
```
✗ should display validation error
  AssertionError: Expected "Required" or "Invalid email format"
  but got "Email is required" in test line 257
```

**代码**（244-259 行）:
```typescript
const schema = z.object({
  email: z.string({ required_error: 'Email is required' }).email('Invalid email format'),
});

// waitFor 期望正则匹配 /required|invalid/i
// 实际：既然有 required_error，就会显示 'Email is required'
```

**问题**:
- 测试用 `.match(/required|invalid/i)` 太宽泛
- 应该精确测试期望的错误消息

---

### 案例 3: FormDatePicker.test.tsx - 类型转换问题

**失败现象**:
```
✗ should handle default value
  Expected input.value = "2024-01-15"
  but got input.value = "" or undefined
```

**代码**（135-144 行）:
```typescript
const defaultDate = new Date('2024-01-15');  // Date 对象
// React Hook Form 内部转换不正确
// → input 保持为空

const schema = z.object({
  birthDate: z.string().datetime(),  // 期望 ISO string
});
```

**链路问题**:
1. defaultDate 是 JavaScript Date 对象
2. useForm({ defaultValues: { birthDate: defaultDate } })
3. 内部需要转换为字符串
4. Schema 验证期望 ISO 格式 `"2024-01-15T00:00:00.000Z"`
5. 但 input type="date" 使用 `YYYY-MM-DD` 格式

---

### 案例 4: FormCheckbox.test.tsx - Refine 验证顺序

**失败现象**:
```
✗ should validate checkbox field
  Expected error message "You must agree"
  but test timeout after 3000ms
```

**代码**（186-208 行）:
```typescript
const schema = z.object({
  agree: z.boolean().refine((val) => val === true, 'You must agree'),
});

// 使用 defaultValues: { agree: false }
// 提交表单：
// 1. boolean 验证通过（false 是有效的 boolean）
// 2. refine() 检查 val === true → 失败 ✓
// 3. 应该显示 "You must agree"

// 问题：测试没有正确等待异步验证
```

---

## 修复建议

### 建议 1: 统一 Schema 定义风格

**标准模式**（推荐）:
```typescript
// 使用可复用的验证规则
export const validationRules = {
  email: z
    .string({
      required_error: 'Email is required',
      invalid_type_error: 'Email must be a string',
    })
    .min(1, 'Email cannot be empty')
    .email('Invalid email format'),

  password: z
    .string({
      required_error: 'Password is required',
      invalid_type_error: 'Password must be a string',
    })
    .min(8, 'Password must be at least 8 characters'),

  sport: z
    .string({
      required_error: 'Please select a sport',
      invalid_type_error: 'Sport must be a string',
    })
    .min(1, 'Please select a sport'),

  agree: z
    .boolean({
      required_error: 'You must agree',
      invalid_type_error: 'Agreement must be boolean',
    })
    .refine((val) => val === true, 'You must agree'),

  birthDate: z
    .string({
      required_error: 'Birth date is required',
      invalid_type_error: 'Birth date must be a string',
    })
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Birth date must be YYYY-MM-DD format')
    .refine((date) => {
      const d = new Date(date);
      return d instanceof Date && !isNaN(d.getTime());
    }, 'Invalid date'),
} as const;
```

**应用到表单**:
```typescript
const schema = z.object({
  email: validationRules.email,
  password: validationRules.password,
  sport: validationRules.sport,
  agree: validationRules.agree,
  birthDate: validationRules.birthDate,
});
```

---

### 建议 2: 修复日期字段处理

**问题**:
- HTML input type="date" 返回 `YYYY-MM-DD` 格式
- JavaScript Date 对象 vs 字符串的转换

**修复方案**:
```typescript
// 1. 使用 coerce 转换 Date 对象为字符串
const birthDateSchema = z
  .union([
    z.string().regex(/^\d{4}-\d{2}-\d{2}$/),  // YYYY-MM-DD
    z.date().transform(d => d.toISOString().split('T')[0]),  // Date → YYYY-MM-DD
  ])
  .refine((date) => {
    const d = new Date(date);
    return !isNaN(d.getTime());
  }, 'Invalid date');

// 2. 或使用 preprocess
const birthDateSchema = z
  .preprocess(
    (val) => {
      if (val instanceof Date) {
        return val.toISOString().split('T')[0];
      }
      return val;
    },
    z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Birth date must be YYYY-MM-DD format')
  );

// 3. 在 FormDatePicker 组件中处理转换
const FormDatePicker = ({ name, ...props }) => {
  const { control, formState: { errors } } = useFormContext();
  const error = errors[name]?.message as string | undefined;

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <input
          type="date"
          {...field}
          value={
            field.value instanceof Date
              ? field.value.toISOString().split('T')[0]
              : field.value || ''
          }
          onChange={(e) => {
            const dateStr = e.target.value;
            field.onChange(dateStr);  // 传递 YYYY-MM-DD 格式
          }}
        />
      )}
    />
  );
};
```

---

### 建议 3: 修复测试中的 Schema 期望

**当前问题**:
```typescript
// ❌ 测试太宽泛
await waitFor(() => {
  expect(screen.getByText(/required|invalid/i)).toBeInTheDocument();
});

// ❌ 期望与 Schema 不符
const schema = z.object({
  email: z.string().email('Invalid email'),  // 没有 required_error
});
// 但测试期望 "Email is required"
```

**修复**:
```typescript
// ✅ 精确匹配期望的错误消息
const schema = z.object({
  email: z.string({
    required_error: 'Email is required',
  }).email('Invalid email format'),
});

// ✅ 精确断言
await waitFor(() => {
  expect(screen.getByText('Email is required')).toBeInTheDocument();
});

// ✅ 或分开测试不同场景
describe('Email validation', () => {
  it('should show required error when field is empty', async () => {
    // 测试点击提交空字段
    expect(screen.getByText('Email is required')).toBeInTheDocument();
  });

  it('should show format error when email is invalid', async () => {
    // 先输入无效邮箱，再提交
    await user.type(input, 'invalid');
    expect(screen.getByText('Invalid email format')).toBeInTheDocument();
  });
});
```

---

### 建议 4: 修复 Checkbox/Select 的空值处理

**Select 字段**:
```typescript
// ❌ 问题：min(1) 在 undefined 时不会触发
const schema = z.object({
  sport: z.string().min(1, 'Please select'),
});

// ✅ 修复：使用 required_error 处理 undefined
const schema = z.object({
  sport: z.string({
    required_error: 'Please select a sport',
  }).min(1, 'Please select a sport'),
});

// ✅ 测试时确保默认值是字符串而非 undefined
const form = useForm({
  defaultValues: { sport: '' },  // 空字符串，不是 undefined
  resolver: zodResolver(schema),
});
```

**Checkbox 字段**:
```typescript
// ✅ 正确的 boolean refine
const schema = z.object({
  agree: z.boolean({
    required_error: 'You must agree',
    invalid_type_error: 'Agreement must be boolean',
  }).refine((val) => val === true, {
    message: 'You must agree to continue',
  }),
});

// ✅ 在 FormCheckbox 中处理转换
const FormCheckbox = ({ name, ...props }) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <input
          type="checkbox"
          {...field}
          checked={field.value === true}  // 确保正确的 boolean
          onChange={(e) => field.onChange(e.target.checked)}
        />
      )}
    />
  );
};
```

---

### 建议 5: 添加 Schema 验证工具函数

**创建辅助库**:
```typescript
// src/shared/ui/utils/validation/schema-helpers.ts

/**
 * 创建标准化的必填字符串字段
 */
export const createRequiredString = (
  minLength: number = 1,
  messages?: {
    required?: string;
    tooShort?: string;
    invalid?: string;
  }
) => {
  return z.string({
    required_error: messages?.required || 'This field is required',
    invalid_type_error: messages?.invalid || 'This field must be a string',
  })
    .min(minLength, messages?.tooShort || `Minimum ${minLength} characters`);
};

/**
 * 创建标准化的邮箱字段
 */
export const createEmailField = (
  messages?: {
    required?: string;
    invalid?: string;
  }
) => {
  return createRequiredString(1, {
    required: messages?.required || 'Email is required',
  }).email(messages?.invalid || 'Invalid email format');
};

/**
 * 创建标准化的日期字段
 */
export const createDateField = (
  messages?: {
    required?: string;
    invalid?: string;
  }
) => {
  return z.string({
    required_error: messages?.required || 'Date is required',
  }).refine(
    (val) => /^\d{4}-\d{2}-\d{2}$/.test(val) && !isNaN(new Date(val).getTime()),
    messages?.invalid || 'Invalid date format (YYYY-MM-DD)'
  );
};

/**
 * 创建标准化的 boolean 字段（必须为 true）
 */
export const createRequiredBoolean = (message?: string) => {
  return z.boolean({
    required_error: message || 'This field is required',
  }).refine((val) => val === true, message || 'This agreement is required');
};

// 使用示例
const schema = z.object({
  email: createEmailField(),
  password: createRequiredString(8, {
    required: 'Password is required',
    tooShort: 'Password must be at least 8 characters',
  }),
  birthDate: createDateField(),
  agree: createRequiredBoolean('You must agree'),
});
```

---

## 最佳实践

### 1. Schema 组织原则

```typescript
// ✅ 推荐：集中管理所有 Schema
// src/shared/ui/utils/validation/
├── rules.ts           # 基础验证规则
├── schemas.ts         # 具体表单 Schema
├── schema-helpers.ts  # 创建 Schema 的工厂函数
└── __tests__/
    └── schemas.test.ts  # Schema 验证测试
```

### 2. 测试最佳实践

```typescript
// ✅ 推荐：分离不同的验证场景
describe('Email Field Validation', () => {
  const schema = z.object({
    email: validationRules.email,
  });

  describe('required validation', () => {
    it('should show error when field is empty', async () => {
      // 测试 required_error
    });

    it('should show error when field is null', async () => {
      // 测试 null 处理
    });
  });

  describe('format validation', () => {
    it('should show error for invalid format', async () => {
      // 测试 .email() 验证
    });

    it('should accept valid emails', async () => {
      // 测试有效邮箱
    });
  });
});
```

### 3. Form 组件集成

```typescript
// ✅ 推荐：类型安全的 Form 使用
const schema = z.object({
  email: validationRules.email,
  password: validationRules.password,
});

type FormValues = z.infer<typeof schema>;

const MyForm = () => {
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    mode: 'onBlur',
    defaultValues: {
      email: '',
      password: '',
    },
  });

  return (
    <Form form={form} onSubmit={handleSubmit}>
      <FormInput name="email" label="Email" />
      <FormInput name="password" label="Password" type="password" />
      <Button type="submit">Submit</Button>
    </Form>
  );
};
```

---

## 总结

### 关键问题
| 问题 | 影响范围 | 严重度 | 优先级 |
|------|---------|--------|--------|
| required_error 不一致 | 所有 String 字段 | 中 | P1 |
| undefined vs null 处理 | 可选字段 | 中 | P1 |
| 日期类型转换 | DatePicker 组件 | 高 | P0 |
| 空值验证（select/checkbox） | Select/Checkbox | 中 | P1 |
| 测试期望与 Schema 不符 | 所有验证测试 | 高 | P0 |

### 修复顺序
1. **P0**: 修复日期类型转换问题
2. **P0**: 更新所有测试期望，确保与 Schema 定义一致
3. **P1**: 统一 Schema 定义风格
4. **P1**: 添加 Schema 验证工具函数库
5. **P2**: 扩展测试覆盖不同验证场景

