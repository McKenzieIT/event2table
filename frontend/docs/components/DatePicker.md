# DatePicker Component

## 概述

DatePicker 组件是一个基于原生日期输入的日期选择器组件，集成了 React Hook Form，支持日期和时间选择、日期格式、最小/最大日期限制、验证和无障碍功能。

## Props

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

### 类型定义

```typescript
interface DatePickerProps<TFieldValues extends FieldValues = FieldValues>
  extends FormFieldProps<TFieldValues> {
  format?: string;
  showTime?: boolean;
  timeFormat?: string;
  minDate?: Date;
  maxDate?: Date;
  placeholder?: string;
}
```

## 使用示例

### 基础用法（独立使用）

```tsx
import { DatePicker } from '@shared/ui/components/DatePicker';
import { useState } from 'react';

function BasicDatePicker() {
  const [date, setDate] = useState<Date | null>(null);

  return (
    <DatePicker
      value={date}
      onChange={setDate}
      label="选择日期"
      placeholder="请选择日期"
    />
  );
}
```

### React Hook Form 集成

```tsx
import { FormDatePicker } from '@shared/ui/components/Form';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  birthDate: z.date({
    required_error: '请选择出生日期',
    invalid_type_error: '无效的日期',
  }),
  appointmentDate: z.date().optional(),
});

type FormData = z.infer<typeof schema>;

function MyForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      birthDate: undefined,
      appointmentDate: undefined,
    },
  });

  const onSubmit = (data: FormData) => {
    console.log('Form data:', data);
  };

  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormDatePicker
        name="birthDate"
        label="出生日期"
        required
      />
      <FormDatePicker
        name="appointmentDate"
        label="预约时间"
        placeholder="选择预约时间"
      />
      <button type="submit">提交</button>
    </Form>
  );
}
```

### 日期和时间选择

```tsx
import { FormDatePicker } from '@shared/ui/components/Form';

function DateTimePicker() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormDatePicker
        name="eventDate"
        label="活动日期和时间"
        showTime
        placeholder="选择日期和时间"
        helperText="请选择活动的具体时间"
      />
    </Form>
  );
}
```

### 最小/最大日期限制

```tsx
import { FormDatePicker } from '@shared/ui/components/Form';

function DateRangePicker() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormDatePicker
        name="startDate"
        label="开始日期"
        minDate={new Date()}
        helperText="只能选择今天及以后的日期"
      />
      <FormDatePicker
        name="endDate"
        label="结束日期"
        minDate={new Date()}
        maxDate={new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)} // 30天后
        helperText="只能选择未来30天内的日期"
      />
    </Form>
  );
}
```

### 出生日期选择器

```tsx
import { FormDatePicker } from '@shared/ui/components/Form';

function BirthDatePicker() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormDatePicker
        name="birthDate"
        label="出生日期"
        maxDate={new Date()}
        required
        helperText="请选择您的出生日期"
      />
    </Form>
  );
}
```

### 预约时间选择器

```tsx
import { FormDatePicker } from '@shared/ui/components/Form';

function AppointmentPicker() {
  const minDate = new Date();
  minDate.setDate(minDate.getDate() + 1); // 明天

  const maxDate = new Date();
  maxDate.setDate(maxDate.getDate() + 30); // 30天后

  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormDatePicker
        name="appointmentDate"
        label="预约时间"
        showTime
        minDate={minDate}
        maxDate={maxDate}
        required
        helperText="请选择未来1-30天内的预约时间"
      />
    </Form>
  );
}
```

### 禁用状态

```tsx
import { FormDatePicker } from '@shared/ui/components/Form';

function DisabledDatePicker() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormDatePicker
        name="disabledDate"
        label="禁用的日期选择器"
        disabled
        value={new Date()}
      />
    </Form>
  );
}
```

### 自定义格式

```tsx
import { FormDatePicker } from '@shared/ui/components/Form';

function CustomFormatPicker() {
  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormDatePicker
        name="customDate"
        label="自定义格式"
        format="DD/MM/YYYY"
        placeholder="DD/MM/YYYY"
      />
    </Form>
  );
}
```

### 完整表单示例

```tsx
import { Form, FormDatePicker, FormInput } from '@shared/ui/components/Form';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1, '请输入姓名'),
  birthDate: z.date({
    required_error: '请选择出生日期',
  }).refine(
    (date) => date <= new Date(),
    { message: '出生日期不能是未来日期' }
  ),
  appointmentDate: z.date().optional(),
  notes: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

function CompleteForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      birthDate: undefined,
      appointmentDate: undefined,
      notes: '',
    },
  });

  const onSubmit = async (data: FormData) => {
    console.log('Submitting:', data);
    // 提交逻辑
  };

  return (
    <Form form={form} onSubmit={onSubmit}>
      <FormInput
        name="name"
        label="姓名"
        placeholder="请输入姓名"
        required
      />
      
      <FormDatePicker
        name="birthDate"
        label="出生日期"
        maxDate={new Date()}
        required
        helperText="请选择您的出生日期"
      />
      
      <FormDatePicker
        name="appointmentDate"
        label="预约时间"
        showTime
        minDate={new Date()}
        placeholder="选择预约时间"
      />
      
      <FormInput
        name="notes"
        label="备注"
        placeholder="请输入备注信息"
      />
      
      <div className="form-actions">
        <button type="submit">提交</button>
        <button type="button" onClick={() => form.reset()}>
          重置
        </button>
      </div>
    </Form>
  );
}
```

## 注意事项

1. **浏览器兼容性**:
   - 使用原生 `<input type="date">` 和 `<input type="datetime-local">`
   - 现代浏览器支持良好
   - 旧版浏览器可能显示为普通文本输入框

2. **日期格式**:
   - `format` 属性仅用于显示，不影响实际值
   - 实际存储的值始终是 Date 对象
   - 时区处理：使用本地时区

3. **验证**:
   - 与 React Hook Form 完美集成
   - 支持自定义验证规则
   - 自动显示验证错误

4. **无障碍性**:
   - 完整的 ARIA 属性支持
   - 键盘导航支持
   - 屏幕阅读器友好

5. **性能优化**:
   - 使用 React.memo 优化
   - 避免不必要的重新渲染
   - 日期转换函数使用 useCallback

6. **最佳实践**:
   - 为日期选择器提供清晰的标签
   - 合理设置 minDate 和 maxDate
   - 提供帮助文本说明日期范围
   - 处理时区问题（如需要）

7. **已知限制**:
   - 依赖浏览器原生日期选择器
   - 样式定制受限（因使用原生控件）
   - 不支持复杂的日期范围选择

## 相关组件

- [`Form`](./Form.md) - 表单容器组件
- [`Input`](./Input.md) - 输入框组件
- [`Select`](./Select.md) - 下拉选择组件
- [`Button`](./Button.md) - 按钮组件
