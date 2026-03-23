# 组件库现代化第二阶段设计文档

## 概述

本文档描述了Event2Table组件库现代化的第二阶段设计，包括迁移统一、性能优化、功能增强、组件扩展和工具完善等四个阶段的详细规划。

**设计日期**：2026-03-20  
**设计者**：Aone Copilot  
**项目周期**：约10周

---

## 项目背景

### 当前状态

在第一阶段中，我们完成了：
- Modal组件现代化（支持多种尺寸、动画、无障碍性）
- Form组件现代化（React Hook Form + Zod验证）
- Table组件现代化（虚拟滚动、列固定、可编辑单元格）
- 迁移工具开发（AST转换工具）

### 发现的问题

1. **双轨运行问题**：
   - Modal：`BaseModal` 与新 `Modal` 同时存在
   - Table：旧 `Table` 与新 `Table` 同时存在
   - Select：未迁移到新架构

2. **性能优化空间**：
   - Table虚拟滚动需要进一步优化
   - Modal动画延迟较高（300ms）
   - Form验证性能可以提升

3. **功能缺失**：
   - Modal不支持拖拽
   - Form缺少DatePicker、Upload、RichText字段
   - Table不支持列分组

---

## 设计风格

### Cyberpunk Lab Theme（赛博朋克实验室主题）

项目采用独特的设计风格，具有以下特点：

#### 视觉特征
- **毛玻璃效果（Glassmorphism）**：半透明背景 + backdrop-filter blur
- **霓虹边框**：cyan色调的发光边框效果
- **深色主题**：rgba(15, 23, 42, 0.95) 背景色
- **平滑动画**：cubic-bezier(0.4, 0, 0.2, 1) 缓动函数

#### CSS变量系统
```css
:root {
  --modal-bg-primary: rgba(15, 23, 42, 0.95);
  --modal-border-color: rgba(6, 182, 212, 0.2);
  --modal-text-primary: #F1F5F9;
  --modal-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  --modal-radius: 12px;
}
```

#### 组件设计原则
1. **性能优先**：React.memo + useCallback + useMemo
2. **无障碍性**：WCAG 2.1 AA标准
3. **类型安全**：完整TypeScript支持
4. **可定制性**：支持className覆盖和样式变量

---

## 实施方案：四阶段并行开发

```
┌─────────────────────────────────────────────────────────────────┐
│                    阶段1：迁移与统一 (2周)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Modal迁移   │  │ Table迁移   │  │ Select迁移  │             │
│  │ (Subagent1) │  │ (Subagent2) │  │ (Subagent3) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    阶段2：性能优化 (2周)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Table虚拟   │  │ Modal动画   │  │ Form验证    │             │
│  │ 滚动优化    │  │ 优化        │  │ 性能优化    │             │
│  │ (Subagent1) │  │ (Subagent2) │  │ (Subagent3) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    阶段3：功能增强 (3周)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Modal拖拽   │  │ Form字段    │  │ Table列     │             │
│  │ 功能        │  │ 类型扩展    │  │ 分组功能    │             │
│  │ (Subagent1) │  │ (Subagent2) │  │ (Subagent3) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 阶段4：组件扩展与工具完善 (3周)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ DatePicker  │  │ AST工具     │  │ 可视化迁移  │             │
│  │ Upload组件  │  │ 增强        │  │ 工具        │             │
│  │ (Subagent1) │  │ (Subagent2) │  │ (Subagent3) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 阶段1：迁移与统一

### 任务1.1：Modal迁移

**目标**：将所有使用 `BaseModal` 的代码迁移到新的 `Modal` 组件

**当前状态分析**：

| 组件 | 位置 | TypeScript | 功能 | 状态 |
|-----|------|-----------|------|------|
| BaseModal (旧) | `frontend/src/shared/ui/BaseModal/` | `@ts-nocheck` | 基础功能 | 待废弃 |
| Modal (新) | `frontend/src/shared/ui/components/Modal/` | 完整类型 | 完整功能 | 保留 |

**API对比**：

| 属性 | BaseModal | Modal | 兼容性 |
|-----|-----------|-------|--------|
| isOpen | ✅ | ✅ | 兼容 |
| onClose | ✅ | ✅ | 兼容 |
| title | ✅ | ✅ | 兼容 |
| children | ✅ | ✅ | 兼容 |
| size | ✅ | ✅ | 兼容 |
| animation | ✅ | ✅ | 兼容 |
| glassmorphism | ✅ | ✅ | 兼容 |
| variant | ✅ | ✅ | 兼容 |
| showHeader | ✅ | ✅ | 兼容 |
| showCloseButton | ✅ | ✅ | 兼容 |
| onBeforeClose | ✅ | ✅ | 兼容 |
| confirmConfig | ✅ | ✅ | 兼容 |
| showFooter | ❌ | ✅ | 新增 |
| footer | ❌ | ✅ | 新增 |
| onAfterOpen | ❌ | ✅ | 新增 |
| onAfterClose | ✅ | ✅ | 兼容 |
| ariaDescribedby | ❌ | ✅ | 新增 |
| ariaLabelledby | ❌ | ✅ | 新增 |

**迁移步骤**：

1. **分析依赖关系**
   ```bash
   # 搜索所有使用BaseModal的文件
   grep -r "from.*BaseModal" frontend/src
   ```

2. **更新导出**
   ```typescript
   // frontend/src/shared/ui/index.ts
   // 将 BaseModal 导出改为 Modal 的别名
   export { Modal as BaseModal } from './components/Modal/Modal';
   // 同时导出新的 Modal
   export { Modal } from './components/Modal/Modal';
   ```

3. **批量替换导入**
   ```typescript
   // 使用AST工具批量替换
   // scripts/migrate-modal.ts
   ```

4. **添加迁移测试**
   - 验证所有使用Modal的页面功能正常
   - 验证无障碍性功能
   - 验证动画效果

5. **废弃旧组件**
   - 标记 `BaseModal` 为 `@deprecated`
   - 添加迁移指南
   - 最终删除旧组件

**文件变更清单**：
- `frontend/src/shared/ui/index.ts` - 更新导出
- `frontend/src/shared/ui/BaseModal/` - 标记废弃
- 所有使用Modal的页面 - 更新导入

---

### 任务1.2：Table迁移

**目标**：统一Table组件，整合VirtualTable功能

**当前状态分析**：

| 组件 | 位置 | 功能 | 状态 |
|-----|------|------|------|
| Table (旧) | `frontend/src/shared/ui/Table/` | 基础表格 | 待废弃 |
| Table (新) | `frontend/src/shared/ui/components/Table/` | 虚拟滚动、分页、编辑 | 保留 |
| VirtualTable | `frontend/src/shared/components/VirtualList/` | 虚拟滚动 | 整合到新Table |

**功能对比**：

| 功能 | 旧Table | 新Table | VirtualTable |
|-----|---------|---------|--------------|
| 基础渲染 | ✅ | ✅ | ✅ |
| 斑马纹 | ✅ | ✅ | ❌ |
| 悬停效果 | ✅ | ✅ | ✅ |
| 排序 | ✅ | ✅ | ❌ |
| 虚拟滚动 | ❌ | ✅ | ✅ |
| 分页 | ❌ | ✅ | ❌ |
| 列固定 | ❌ | ✅ | ❌ |
| 可编辑单元格 | ❌ | ✅ | ❌ |
| TanStack Table | ❌ | ✅ | ❌ |

**迁移策略**：

1. **整合VirtualTable到新Table**
   ```typescript
   // 新Table已支持虚拟滚动
   <Table
     data={data}
     columns={columns}
     virtual={true}
     rowHeight={50}
     maxHeight={600}
   />
   ```

2. **更新页面引用**
   - `EventsList.tsx` - 替换 OptimizedVirtualList
   - `CommonParamsList.tsx` - 替换 OptimizedVirtualList
   - 其他使用Table的页面

3. **废弃旧组件**
   - 标记旧Table为 `@deprecated`
   - 删除VirtualTable独立组件

---

### 任务1.3：Select迁移

**目标**：将Select组件迁移到新架构

**当前状态**：
- 位置：`frontend/src/shared/ui/Select/Select.tsx`
- 状态：独立存在，未迁移到新架构

**迁移方案**：

1. **创建新的Select组件目录**
   ```
   frontend/src/shared/ui/components/Select/
   ├── Select.tsx
   ├── Select.types.ts
   ├── Select.css
   ├── Select.test.tsx
   └── index.ts
   ```

2. **更新组件以符合新架构规范**
   - 添加React Hook Form集成
   - 完善TypeScript类型
   - 添加性能优化（React.memo）

3. **更新所有引用**
   - 更新 `frontend/src/shared/ui/index.ts`
   - 更新所有使用Select的页面

---

## 阶段2：性能优化

### 任务2.1：Table虚拟滚动优化

**目标**：支持50,000+行数据流畅渲染

**现状分析**：
- 新Table组件已集成 `@tanstack/react-virtual`
- 需要进一步优化性能参数

**优化方案**：

```typescript
// 优化虚拟滚动参数
const rowVirtualizer = useVirtualizer({
  count: rows.length,
  getScrollElement: () => tableContainerRef.current,
  estimateSize: () => rowHeight,
  overscan: 10, // 预渲染10行
  measureElement: (element) => element.getBoundingClientRect().height,
});

// 添加性能监控
const { measureRender } = usePerformanceMonitor('Table');

// 添加缓存机制
const cachedRows = useMemo(() => {
  return virtualRows.map(virtualRow => ({
    ...virtualRow,
    data: rows[virtualRow.index],
  }));
}, [virtualRows, rows]);
```

**性能目标**：
- 50,000行数据渲染时间 < 100ms
- 滚动帧率 ≥ 60fps
- 内存占用 < 100MB

**测试方案**：
```typescript
// 性能测试
describe('Table Performance', () => {
  it('should render 50,000 rows in under 100ms', async () => {
    const data = generateMockData(50000);
    const start = performance.now();
    render(<Table data={data} columns={columns} virtual />);
    const end = performance.now();
    expect(end - start).toBeLessThan(100);
  });
});
```

---

### 任务2.2：Modal动画优化

**目标**：减少动画延迟，提升用户体验

**现状分析**：
- 当前动画延迟：`MODAL_ANIMATION_DELAY` (300ms)
- 目标：降至150ms

**优化方案**：

1. **减少CSS动画时长**
   ```css
   /* 优化前 */
   .modal-content--slideUp {
     animation: modal-slide-up 0.3s cubic-bezier(0.4, 0, 0.2, 1);
   }

   /* 优化后 */
   .modal-content--slideUp {
     animation: modal-slide-up 0.15s cubic-bezier(0.4, 0, 0.2, 1);
     will-change: transform, opacity;
   }

   @keyframes modal-slide-up {
     from {
       opacity: 0;
       transform: translateY(20px);
     }
     to {
       opacity: 1;
       transform: translateY(0);
     }
   }
   ```

2. **使用transform替代opacity**
   - transform动画更高效
   - 避免重绘和重排

3. **添加will-change提示**
   - 提前告知浏览器优化
   - 减少渲染延迟

**性能目标**：
- 动画延迟从300ms降至150ms
- 动画帧率 ≥ 60fps
- 无视觉卡顿

---

### 任务2.3：Form验证性能优化

**目标**：优化表单验证性能，支持批量验证

**现状分析**：
- 使用 React Hook Form + Zod
- 验证模式：`onBlur`、`onChange`

**优化方案**：

1. **实现批量验证（debounce）**
   ```typescript
   import { debounce } from 'lodash-es';

   // 批量验证优化
   const debouncedValidate = useMemo(
     () => debounce((values) => form.trigger(), 300),
     [form]
   );
   ```

2. **添加验证缓存**
   ```typescript
   // 缓存验证结果
   const validationCache = useRef<Map<string, boolean>>(new Map());

   const validateWithCache = useCallback((name: string, value: unknown) => {
     const cacheKey = `${name}:${JSON.stringify(value)}`;
     if (validationCache.current.has(cacheKey)) {
       return validationCache.current.get(cacheKey);
     }
     const result = form.trigger(name);
     validationCache.current.set(cacheKey, result);
     return result;
   }, [form]);
   ```

3. **优化Zod schema解析**
   ```typescript
   // 使用z.lazy延迟解析复杂schema
   const schema = z.object({
     user: z.lazy(() => userSchema),
   });
   ```

**性能目标**：
- 表单验证时间减少50%
- 支持大表单（100+字段）流畅验证
- 减少不必要的重复验证

---

## 阶段3：功能增强

### 任务3.1：Modal拖拽功能

**目标**：支持拖拽标题栏移动Modal

**设计方案**：

```typescript
// 新增拖拽相关props
interface ModalDragConfig {
  enabled: boolean;
  handle?: string; // 拖拽把手选择器，默认为'.modal-header'
  bounds?: 'parent' | 'window' | HTMLElement; // 拖拽边界
  grid?: [number, number]; // 网格对齐
}

interface ModalProps {
  // ... 现有props
  draggable?: boolean | ModalDragConfig;
}
```

**实现方案**：

```typescript
// 使用自定义Hook实现拖拽
import { useDraggable } from '@shared/hooks/useDraggable';

const ModalWithDrag = ({ draggable, ...props }) => {
  const dragConfig = typeof draggable === 'boolean' 
    ? { enabled: draggable } 
    : draggable;

  const { position, isDragging, handleDragStart } = useDraggable(dragConfig);

  return (
    <div
      className={cn('modal-content', isDragging && 'modal-content--dragging')}
      style={{ transform: `translate(${position.x}px, ${position.y}px)` }}
    >
      <div 
        className="modal-header" 
        onMouseDown={dragConfig?.enabled ? handleDragStart : undefined}
        style={{ cursor: dragConfig?.enabled ? 'grab' : undefined }}
      >
        {/* 标题内容 */}
      </div>
      {/* Modal内容 */}
    </div>
  );
};
```

**UI设计要点**：
- 拖拽把手样式：标题栏cursor变为`grab`/`grabbing`
- 拖拽时添加阴影增强效果
- 边界限制：防止Modal拖出可视区域
- 保持Cyberpunk Lab Theme风格

---

### 任务3.2：Form新增字段类型

**目标**：添加DatePicker、Upload、RichText字段组件

#### 3.2.1 FormDatePicker

```typescript
interface FormDatePickerProps<TFieldValues extends FieldValues> {
  name: FieldPath<TFieldValues>;
  label?: string;
  format?: string; // 日期格式，默认 'YYYY-MM-DD'
  placeholder?: string;
  minDate?: Date;
  maxDate?: Date;
  disabled?: boolean;
  required?: boolean;
  showTime?: boolean; // 显示时间选择
  locale?: string; // 语言设置
  error?: string;
  helperText?: string;
  className?: string;
}
```

**实现要点**：
- 使用 `react-datepicker` 或自定义实现
- 样式与Cyberpunk Lab Theme保持一致
- 支持键盘导航
- 支持ARIA属性

#### 3.2.2 FormUpload

```typescript
interface FormUploadProps<TFieldValues extends FieldValues> {
  name: FieldPath<TFieldValues>;
  label?: string;
  accept?: string; // 文件类型，如 '.jpg,.png'
  multiple?: boolean;
  maxFileSize?: number; // 最大文件大小（字节）
  maxFiles?: number; // 最大文件数
  onUpload?: (files: File[]) => Promise<void>;
  preview?: boolean; // 是否显示预览
  dragAndDrop?: boolean; // 支持拖拽上传
  error?: string;
  helperText?: string;
  className?: string;
}
```

**实现要点**：
- 支持拖拽上传
- 显示上传进度
- 文件预览功能
- 文件类型验证
- 文件大小验证

#### 3.2.3 FormRichText

```typescript
interface FormRichTextProps<TFieldValues extends FieldValues> {
  name: FieldPath<TFieldValues>;
  label?: string;
  placeholder?: string;
  toolbar?: ToolbarConfig | boolean;
  maxLength?: number;
  minHeight?: number;
  maxHeight?: number;
  error?: string;
  helperText?: string;
  className?: string;
}

interface ToolbarConfig {
  heading?: boolean;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  strike?: boolean;
  link?: boolean;
  image?: boolean;
  list?: boolean;
  code?: boolean;
}
```

**实现要点**：
- 使用 `@tiptap/react` 或 `react-quill`
- 自定义工具栏配置
- 样式与整体设计一致
- 支持字符计数

---

### 任务3.3：Table列分组功能

**目标**：支持多级表头

**设计方案**：

```typescript
interface TableColumnGroup<TData> {
  id: string;
  header: string;
  columns: TableColumn<TData>[];
  align?: 'left' | 'center' | 'right';
  className?: string;
}

// 使用示例
const columns: TableColumnGroup<User>[] = [
  {
    id: 'personal',
    header: '个人信息',
    columns: [
      { id: 'name', header: '姓名', accessorKey: 'name' },
      { id: 'age', header: '年龄', accessorKey: 'age' },
    ],
  },
  {
    id: 'contact',
    header: '联系方式',
    columns: [
      { id: 'email', header: '邮箱', accessorKey: 'email' },
      { id: 'phone', header: '电话', accessorKey: 'phone' },
    ],
  },
];
```

**实现方案**：

```typescript
// 使用TanStack Table的column grouping功能
const table = useReactTable({
  data,
  columns,
  // ... 其他配置
});

// 渲染多级表头
const renderHeaderGroups = () => {
  return table.getHeaderGroups().map((headerGroup) => (
    <tr key={headerGroup.id}>
      {headerGroup.headers.map((header) => (
        <th
          key={header.id}
          colSpan={header.colSpan}
          className={cn(
            'table-th',
            header.depth > 0 && 'table-th--group'
          )}
        >
          {flexRender(header.column.columnDef.header, header.getContext())}
        </th>
      ))}
    </tr>
  ));
};
```

**UI设计要点**：
- 多级表头样式：使用嵌套的`<th>`元素
- 分组标题样式：与普通表头区分
- 边框和背景：保持整体风格一致
- 支持排序指示器

---

## 阶段4：组件扩展与工具完善

### 任务4.1：DatePicker组件

**目标**：创建符合Cyberpunk Lab Theme的日期选择器

**设计方案**：

```typescript
interface DatePickerProps {
  value?: Date | null;
  onChange?: (date: Date | null) => void;
  format?: string;
  placeholder?: string;
  minDate?: Date;
  maxDate?: Date;
  disabled?: boolean;
  showTime?: boolean;
  locale?: string;
  error?: string;
  helperText?: string;
  className?: string;
}
```

**样式特点**：
- 毛玻璃效果背景
- 霓虹边框高亮
- 平滑动画过渡
- 键盘导航支持

**实现要点**：
- 使用 `@popperjs/core` 定位
- 支持多种日期格式
- 支持时间选择
- 支持国际化

---

### 任务4.2：AST转换工具增强

**目标**：改进AST转换工具，支持更复杂的转换

**增强功能**：

1. **批量文件处理**
   ```typescript
   interface BatchTransformOptions {
     inputPath: string;
     outputPath: string;
     pattern: string; // glob pattern
     rules: TransformRule[];
   }

   async function batchTransform(options: BatchTransformOptions): Promise<TransformResult[]> {
     const files = await glob(options.pattern, { cwd: options.inputPath });
     return Promise.all(files.map(file => transformFile(file, options.rules)));
   }
   ```

2. **转换规则配置**
   ```typescript
   interface TransformRule {
     type: 'import' | 'jsx' | 'props';
     from: string;
     to: string;
     conditions?: Condition[];
   }

   interface Condition {
     type: 'hasProp' | 'hasChild' | 'hasImport';
     value: string;
   }
   ```

3. **转换预览**
   ```typescript
   interface TransformPreview {
     file: string;
     original: string;
     transformed: string;
     diff: DiffResult[];
   }

   async function previewTransform(file: string, rules: TransformRule[]): Promise<TransformPreview> {
     const original = await fs.readFile(file, 'utf-8');
     const transformed = await transform(original, rules);
     return { file, original, transformed, diff: computeDiff(original, transformed) };
   }
   ```

4. **回滚功能**
   ```typescript
   interface TransformBackup {
     timestamp: string;
     files: { path: string; content: string }[];
   }

   async function createBackup(files: string[]): Promise<TransformBackup> {
     const timestamp = new Date().toISOString();
     const backup = await Promise.all(files.map(async (file) => ({
       path: file,
       content: await fs.readFile(file, 'utf-8'),
     })));
     return { timestamp, files: backup };
   }
   ```

---

### 任务4.3：可视化迁移工具

**目标**：提供Web界面的迁移工具

**功能设计**：

1. **文件浏览器**
   - 选择要迁移的文件或目录
   - 显示文件树结构
   - 支持搜索和过滤

2. **差异对比**
   - 显示迁移前后的差异
   - 支持语法高亮
   - 支持并排对比

3. **一键迁移**
   - 点击按钮执行迁移
   - 显示迁移进度
   - 支持批量迁移

4. **进度显示**
   - 实时显示迁移进度
   - 显示成功/失败统计
   - 支持日志查看

**技术方案**：

```
┌─────────────────────────────────────────────────────────────┐
│                    可视化迁移工具架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    WebSocket    ┌─────────────────────┐   │
│  │   Frontend  │ ◄──────────────► │      Backend        │   │
│  │   (React)   │                 │    (Node.js)        │   │
│  │             │                 │                     │   │
│  │ - Monaco    │                 │ - AST Transform     │   │
│  │   Editor    │                 │ - File System       │   │
│  │ - Diff View │                 │ - Progress Tracking │   │
│  │ - File Tree │                 │ - Backup Management │   │
│  └─────────────┘                 └─────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 任务4.4：自动化测试流程

**目标**：CI/CD集成自动化测试

**测试类型**：

1. **单元测试**
   - 组件级别的测试
   - 测试覆盖目标：90%+
   - 使用 Vitest + React Testing Library

2. **集成测试**
   - 组件交互测试
   - 测试覆盖目标：80%+
   - 测试关键用户流程

3. **E2E测试**
   - 用户流程测试
   - 使用 Playwright
   - 测试核心业务流程

4. **视觉回归测试**
   - UI变更检测
   - 使用 Percy 或 Chromatic
   - 确保UI一致性

**CI/CD配置**：

```yaml
# .github/workflows/component-tests.yml
name: Component Library Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Run unit tests
        run: npm run test:unit -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Run integration tests
        run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npm run test:e2e
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/

  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Run visual regression tests
        run: npm run test:visual
```

---

## 测试计划

### 单元测试

| 组件 | 测试覆盖目标 | 关键测试点 |
|-----|-------------|-----------|
| Modal | 95% | 打开/关闭、动画、无障碍性、拖拽 |
| Form | 90% | 验证、提交、字段组件 |
| Table | 90% | 虚拟滚动、排序、分页、编辑 |
| Select | 90% | 选择、搜索、键盘导航 |
| DatePicker | 90% | 日期选择、格式化、边界 |

### 集成测试

| 场景 | 测试目标 |
|-----|---------|
| 表单提交 | 验证 → 提交 → 成功/失败处理 |
| 表格操作 | 排序 → 筛选 → 分页 → 选择 |
| Modal交互 | 打开 → 编辑 → 保存/取消 |

### E2E测试

| 流程 | 测试步骤 |
|-----|---------|
| 用户管理 | 登录 → 用户列表 → 创建用户 → 编辑用户 → 删除用户 |
| 事件管理 | 事件列表 → 创建事件 → 编辑事件 → 验证事件 |

---

## 风险评估

### 技术风险

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 迁移导致功能回退 | 高 | 完整的测试覆盖，逐步迁移 |
| 性能优化效果不佳 | 中 | 性能基准测试，A/B测试 |
| 新功能与现有架构冲突 | 中 | 设计评审，原型验证 |

### 项目风险

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 时间估算不准确 | 中 | 预留缓冲时间，分阶段交付 |
| 依赖升级导致兼容性问题 | 中 | 锁定依赖版本，逐步升级 |
| 团队成员变动 | 中 | 文档完善，知识共享 |

---

## 交付物

### 阶段1交付物
- [ ] Modal迁移完成，旧组件废弃
- [ ] Table迁移完成，VirtualTable整合
- [ ] Select迁移到新架构
- [ ] 迁移测试通过

### 阶段2交付物
- [ ] Table虚拟滚动性能优化
- [ ] Modal动画优化
- [ ] Form验证性能优化
- [ ] 性能测试报告

### 阶段3交付物
- [ ] Modal拖拽功能
- [ ] FormDatePicker组件
- [ ] FormUpload组件
- [ ] FormRichText组件
- [ ] Table列分组功能

### 阶段4交付物
- [ ] DatePicker独立组件
- [ ] AST工具增强版
- [ ] 可视化迁移工具
- [ ] CI/CD自动化测试流程
- [ ] 完整文档

---

## 附录

### A. 文件结构

```
frontend/src/shared/ui/
├── components/
│   ├── Modal/
│   │   ├── Modal.tsx
│   │   ├── Modal.types.ts
│   │   ├── Modal.css
│   │   ├── Modal.test.tsx
│   │   └── index.ts
│   ├── Form/
│   │   ├── Form.tsx
│   │   ├── Form.types.ts
│   │   ├── FormInput.tsx
│   │   ├── FormSelect.tsx
│   │   ├── FormCheckbox.tsx
│   │   ├── FormRadio.tsx
│   │   ├── FormDatePicker.tsx (新增)
│   │   ├── FormUpload.tsx (新增)
│   │   ├── FormRichText.tsx (新增)
│   │   └── index.ts
│   ├── Table/
│   │   ├── Table.tsx
│   │   ├── Table.types.ts
│   │   ├── Table.css
│   │   ├── Table.test.tsx
│   │   └── index.ts
│   ├── Select/
│   │   ├── Select.tsx
│   │   ├── Select.types.ts
│   │   ├── Select.css
│   │   ├── Select.test.tsx
│   │   └── index.ts
│   └── DatePicker/
│       ├── DatePicker.tsx (新增)
│       ├── DatePicker.types.ts (新增)
│       ├── DatePicker.css (新增)
│       ├── DatePicker.test.tsx (新增)
│       └── index.ts (新增)
├── index.ts
└── ...
```

### B. 依赖版本

```json
{
  "dependencies": {
    "@tanstack/react-table": "^8.11.0",
    "@tanstack/react-virtual": "^3.0.0",
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "@tiptap/react": "^2.1.0",
    "react-datepicker": "^4.25.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.1.0",
    "@testing-library/user-event": "^14.5.0",
    "@playwright/test": "^1.40.0",
    "vitest": "^1.0.0"
  }
}
```

### C. 参考资料

- [TanStack Table文档](https://tanstack.com/table/latest)
- [TanStack Virtual文档](https://tanstack.com/virtual/latest)
- [React Hook Form文档](https://react-hook-form.com/)
- [Zod文档](https://zod.dev/)
- [WCAG 2.1 AA标准](https://www.w3.org/TR/WCAG21/)
