# Component Migration Rules

本文档详细说明了从旧组件 API 到新组件库的转换规则。

## 目录

- [Modal 组件](#modal-组件)
- [Form 组件](#form-组件)
- [Table 组件](#table-组件)
- [通用转换规则](#通用转换规则)

---

## Modal 组件

### 导入路径变更

#### 旧 API
```typescript
import { Modal } from '@/components/Modal';
```

#### 新 API
```typescript
import { BaseModal } from '@shared/ui/BaseModal/BaseModal';
```

### 组件名称变更

| 旧组件名 | 新组件名 |
|---------|---------|
| `Modal` | `BaseModal` |

### Props 变更

#### 属性重命名

| 旧属性 | 新属性 | 说明 |
|-------|-------|------|
| `visible` | `isOpen` | 控制模态框显示状态 |
| `onRequestClose` | `onClose` | 关闭回调函数 |

#### 新增属性

| 属性名 | 类型 | 说明 |
|-------|------|------|
| `animation` | `'fadeIn' \| 'slideUp' \| 'scale'` | 动画类型 |
| `glassmorphism` | `boolean` | 是否启用毛玻璃效果 |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl' \| 'full'` | 模态框尺寸 |
| `variant` | `'default' \| 'danger' \| 'warning' \| 'success'` | 变体类型 |
| `enableEscClose` | `boolean` | 是否支持 ESC 键关闭 |

#### 保持不变的属性

- `title` - 模态框标题
- `children` - 模态框内容
- `className` - 自定义类名

### 转换示例

#### 旧代码
```typescript
import { Modal } from '@/components/Modal';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <Modal
      visible={isOpen}
      onRequestClose={() => setIsOpen(false)}
      title="Example Modal"
    >
      <p>Modal content</p>
    </Modal>
  );
}
```

#### 新代码
```typescript
import { BaseModal } from '@shared/ui/BaseModal/BaseModal';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <BaseModal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="Example Modal"
      animation="fadeIn"
      glassmorphism
    >
      <p>Modal content</p>
    </BaseModal>
  );
}
```

---

## Form 组件

### 导入路径变更

#### 旧 API
```typescript
import { Form } from '@/components/Form';
import { Input } from '@/components/Input';
```

#### 新 API
```typescript
import { Form } from '@shared/ui/components/Form';
import { FormInput } from '@shared/ui/components/Form';
```

### 组件名称变更

| 旧组件名 | 新组件名 |
|---------|---------|
| `Input` | `FormInput` |
| `Select` | `FormSelect` |
| `Checkbox` | `FormCheckbox` |
| `Radio` | `FormRadio` |

### Props 变更

#### Form 组件

| 旧属性 | 新属性 | 说明 |
|-------|-------|------|
| `initialValues` | `defaultValues` | 表单初始值 |

#### 表单字段组件

所有表单字段组件现在需要配合 `Form` 组件和 `react-hook-form` 使用：

```typescript
import { Form, FormInput } from '@shared/ui/components/Form';
import { useForm } from 'react-hook-form';

function MyForm() {
  const { control } = useForm({
    defaultValues: {
      email: '',
      password: ''
    }
  });
  
  return (
    <Form control={control}>
      <FormInput name="email" label="Email" type="email" />
      <FormInput name="password" label="Password" type="password" />
    </Form>
  );
}
```

### 转换示例

#### 旧代码
```typescript
import { Form, Input } from '@/components/Form';

function MyForm() {
  const handleSubmit = (values) => {
    console.log(values);
  };
  
  return (
    <Form onSubmit={handleSubmit} initialValues={{ email: '' }}>
      <Input name="email" label="Email" />
    </Form>
  );
}
```

#### 新代码
```typescript
import { Form, FormInput } from '@shared/ui/components/Form';
import { useForm } from 'react-hook-form';

function MyForm() {
  const { control, handleSubmit } = useForm({
    defaultValues: { email: '' }
  });
  
  const onSubmit = (data) => {
    console.log(data);
  };
  
  return (
    <Form control={control} onSubmit={handleSubmit(onSubmit)}>
      <FormInput name="email" label="Email" type="email" />
    </Form>
  );
}
```

---

## Table 组件

### 导入路径变更

#### 旧 API
```typescript
import { Table } from '@/components/Table';
import { Column } from '@/components/Table';
```

#### 新 API
```typescript
import Table from '@shared/ui/Table';
```

### 组件结构变更

旧 API 使用 `Column` 组件定义列，新 API 使用组合式子组件：

#### 旧 API 结构
```typescript
<Table dataSource={data}>
  <Column title="Name" dataIndex="name" />
  <Column title="Age" dataIndex="age" />
</Table>
```

#### 新 API 结构
```typescript
<Table>
  <Table.Header>
    <Table.Row>
      <Table.Head>Name</Table.Head>
      <Table.Head>Age</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {data.map(item => (
      <Table.Row key={item.id}>
        <Table.Cell>{item.name}</Table.Cell>
        <Table.Cell>{item.age}</Table.Cell>
      </Table.Row>
    ))}
  </Table.Body>
</Table>
```

### Props 变更

#### Table 组件

| 旧属性 | 新属性 | 说明 |
|-------|-------|------|
| `dataSource` | - | 数据源改为直接渲染 |
| `columns` | - | 列定义改为子组件 |
| `loading` | - | 加载状态需要手动处理 |

#### 新增属性

| 属性名 | 类型 | 说明 |
|-------|------|------|
| `variant` | `'default' \| 'bordered' \| 'compact'` | 表格变体 |
| `striped` | `boolean` | 是否显示斑马纹 |
| `hoverable` | `boolean` | 是否启用悬停效果 |
| `size` | `'sm' \| 'md' \| 'lg'` | 表格尺寸 |

### 转换示例

#### 旧代码
```typescript
import { Table, Column } from '@/components/Table';

interface User {
  id: number;
  name: string;
  email: string;
}

function UserTable({ users }: { users: User[] }) {
  const columns = [
    { title: 'Name', dataIndex: 'name' },
    { title: 'Email', dataIndex: 'email' }
  ];
  
  return (
    <Table dataSource={users} columns={columns} />
  );
}
```

#### 新代码
```typescript
import Table from '@shared/ui/Table';

interface User {
  id: number;
  name: string;
  email: string;
}

function UserTable({ users }: { users: User[] }) {
  return (
    <Table striped hoverable>
      <Table.Header>
        <Table.Row>
          <Table.Head>Name</Table.Head>
          <Table.Head>Email</Table.Head>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {users.map(user => (
          <Table.Row key={user.id}>
            <Table.Cell>{user.name}</Table.Cell>
            <Table.Cell>{user.email}</Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  );
}
```

---

## 通用转换规则

### 1. 导入语句

所有组件导入都需要更新为新的路径：

```typescript
// 旧路径
import { Modal } from '@/components/Modal';
import { Form } from '@/components/Form';
import { Table } from '@/components/Table';

// 新路径
import { BaseModal } from '@shared/ui/BaseModal/BaseModal';
import { Form } from '@shared/ui/components/Form';
import Table from '@shared/ui/Table';
```

### 2. TypeScript 类型

确保更新相关的类型导入：

```typescript
// 旧类型
import type { ModalProps } from '@/components/Modal';

// 新类型
import type { ModalProps } from '@shared/ui/components/Modal';
```

### 3. 样式文件

如果使用了组件的默认样式，需要更新导入路径：

```typescript
// 旧样式
import '@/components/Modal/Modal.css';

// 新样式
import '@shared/ui/BaseModal/BaseModal.css';
```

### 4. 测试文件

更新测试文件中的导入和组件使用：

```typescript
// 旧测试
import { render, screen } from '@testing-library/react';
import { Modal } from '@/components/Modal';

// 新测试
import { render, screen } from '@testing-library/react';
import { BaseModal } from '@shared/ui/BaseModal/BaseModal';
```

---

## 自动化转换

迁移工具会自动处理以下转换：

✅ **自动转换**
- 导入路径更新
- 组件名称重命名
- Props 重命名（如 `visible` → `isOpen`）
- 基本的 AST 结构转换

⚠️ **需要手动检查**
- 复杂的嵌套组件结构
- 自定义样式和主题
- 业务逻辑相关的代码
- 类型定义和接口

❌ **不支持自动转换**
- 第三方集成代码
- 自定义包装组件
- 特定的业务逻辑

---

## 最佳实践

### 1. 渐进式迁移

建议按以下顺序进行迁移：

1. **第一阶段**: 迁移简单的 Modal 组件
2. **第二阶段**: 迁移 Form 组件
3. **第三阶段**: 迁移 Table 组件
4. **第四阶段**: 处理复杂的业务组件

### 2. 测试策略

- 在迁移前确保有充分的测试覆盖
- 使用 `--dry-run` 模式预览变更
- 迁移后运行完整的测试套件
- 进行手动验证和回归测试

### 3. 回滚准备

- 始终使用 `--backup` 选项创建备份
- 保留回滚脚本
- 在非生产环境先进行验证

### 4. 代码审查

- 审查所有自动转换的代码
- 特别关注类型安全和业务逻辑
- 确保没有遗漏的边缘情况

---

## 常见问题

### Q1: 转换后类型错误怎么办？

A: 运行验证工具检查类型问题，然后手动修复无法自动转换的类型定义。

### Q2: 自定义样式丢失了？

A: 新组件库可能使用不同的 CSS 类名，需要手动更新样式文件。

### Q3: 某些 props 不支持了？

A: 查阅新组件库文档，找到替代方案或使用自定义实现。

### Q4: 如何处理复杂的嵌套组件？

A: 对于复杂场景，建议手动重构以充分利用新组件库的功能。

---

## 获取帮助

如果在迁移过程中遇到问题：

1. 查看新组件库文档
2. 运行验证工具获取详细错误信息
3. 检查迁移日志文件
4. 联系技术支持团队
