# Table Component

## 概述

Table 组件是一个基于 TanStack Table 的高性能、功能丰富的表格组件，支持虚拟滚动、列固定、可编辑单元格、高级排序和过滤、行选择、响应式设计和主题定制。

## Props

| 属性名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `data` | `TData[]` | `[]` | 表格数据 |
| `columns` | `TableColumn<TData>[]` | `[]` | 列定义 |
| `variant` | `'default' \| 'compact' \| 'bordered'` | `'default'` | 表格变体 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 表格尺寸 |
| `striped` | `boolean` | `true` | 是否显示斑马纹 |
| `hoverable` | `boolean` | `true` | 是否启用悬停效果 |
| `bordered` | `boolean` | `false` | 是否显示边框 |
| `selectable` | `boolean` | `false` | 是否支持行选择 |
| `onSelectionChange` | `(rows: TData[]) => void` | `undefined` | 选择变更回调 |
| `initialSelectedIds` | `(string \| number)[]` | `[]` | 初始选中行 ID |
| `sortable` | `boolean` | `true` | 是否支持排序 |
| `onSortChange` | `(sorting: SortingState) => void` | `undefined` | 排序变更回调 |
| `initialSorting` | `SortingState` | `[]` | 初始排序状态 |
| `filterable` | `boolean` | `true` | 是否支持过滤 |
| `onFilterChange` | `(filters: ColumnFiltersState) => void` | `undefined` | 过滤变更回调 |
| `initialFilters` | `ColumnFiltersState` | `[]` | 初始过滤状态 |
| `pagination` | `boolean` | `true` | 是否启用分页 |
| `pageSize` | `number` | `10` | 每页显示行数 |
| `currentPage` | `number` | `1` | 当前页码 |
| `onPageChange` | `(page: number, pageSize: number) => void` | `undefined` | 分页变更回调 |
| `pageSizeOptions` | `number[]` | `[10, 20, 50, 100]` | 每页行数选项 |
| `virtual` | `boolean` | `false` | 是否启用虚拟滚动 |
| `rowHeight` | `number` | `50` | 行高度（虚拟滚动） |
| `maxHeight` | `number` | `600` | 最大高度（虚拟滚动） |
| `overscan` | `number` | `10` | 预渲染行数（虚拟滚动） |
| `dynamicRowHeight` | `boolean` | `false` | 是否动态计算行高 |
| `onVirtualScrollMetrics` | `(metrics: VirtualScrollMetrics) => void` | `undefined` | 虚拟滚动指标回调 |
| `editable` | `boolean` | `false` | 是否支持单元格编辑 |
| `onEdit` | `(row: TData, columnId: string, value: unknown) => void` | `undefined` | 编辑回调 |
| `onRowClick` | `(row: TData, event: MouseEvent) => void` | `undefined` | 行点击回调 |
| `onRowDoubleClick` | `(row: TData, event: MouseEvent) => void` | `undefined` | 行双击回调 |
| `onCellClick` | `(cell: CellContext, event: MouseEvent) => void` | `undefined` | 单元格点击回调 |
| `loading` | `boolean` | `false` | 是否加载中 |
| `loadingComponent` | `ReactNode` | `undefined` | 自定义加载组件 |
| `empty` | `boolean` | `false` | 是否为空状态 |
| `emptyComponent` | `ReactNode` | `undefined` | 自定义空状态组件 |
| `theme` | `'light' \| 'dark'` | `'light'` | 主题 |
| `className` | `string` | `''` | 自定义 CSS 类名 |
| `style` | `CSSProperties` | `undefined` | 自定义样式 |

### 类型定义

```typescript
interface TableColumn<TData extends Record<string, unknown>> {
  id?: string;
  accessorKey?: keyof TData;
  header?: string | ReactNode | ((props: HeaderContext<TData>) => ReactNode);
  cell?: ((props: CellContext<TData>) => ReactNode);
  size?: number | 'auto';
  minWidth?: number;
  maxWidth?: number;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  filterable?: boolean;
  fixed?: 'left' | 'right';
  editable?: boolean;
  editComponent?: (props: EditCellProps<TData>) => ReactNode;
  cellRenderer?: (props: CellRendererProps<TData>) => ReactNode;
  headerRenderer?: (props: HeaderRendererProps<TData>) => ReactNode;
}

interface TableProps<TData extends Record<string, unknown>> {
  data: TData[];
  columns: TableColumn<TData>[];
  variant?: 'default' | 'compact' | 'bordered';
  size?: 'sm' | 'md' | 'lg';
  striped?: boolean;
  hoverable?: boolean;
  bordered?: boolean;
  selectable?: boolean;
  onSelectionChange?: (rows: TData[]) => void;
  initialSelectedIds?: (string | number)[];
  sortable?: boolean;
  onSortChange?: (sorting: SortingState) => void;
  initialSorting?: SortingState;
  filterable?: boolean;
  onFilterChange?: (filters: ColumnFiltersState) => void;
  initialFilters?: ColumnFiltersState;
  pagination?: boolean;
  pageSize?: number;
  currentPage?: number;
  onPageChange?: (page: number, pageSize: number) => void;
  pageSizeOptions?: number[];
  virtual?: boolean;
  rowHeight?: number;
  maxHeight?: number;
  overscan?: number;
  dynamicRowHeight?: boolean;
  onVirtualScrollMetrics?: (metrics: VirtualScrollMetrics) => void;
  editable?: boolean;
  onEdit?: (row: TData, columnId: string, value: unknown) => void;
  onRowClick?: (row: TData, event: MouseEvent) => void;
  onRowDoubleClick?: (row: TData, event: MouseEvent) => void;
  onCellClick?: (cell: CellContext, event: MouseEvent) => void;
  loading?: boolean;
  loadingComponent?: ReactNode;
  empty?: boolean;
  emptyComponent?: ReactNode;
  theme?: 'light' | 'dark';
  className?: string;
  style?: CSSProperties;
}
```

## 使用示例

### 基础表格

```tsx
import { Table } from '@shared/ui';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

function BasicTable() {
  const data: User[] = [
    { id: 1, name: '张三', email: 'zhangsan@example.com', role: '管理员' },
    { id: 2, name: '李四', email: 'lisi@example.com', role: '用户' },
    { id: 3, name: '王五', email: 'wangwu@example.com', role: '用户' },
  ];

  const columns: TableColumn<User>[] = [
    { accessorKey: 'id', header: 'ID', size: 80 },
    { accessorKey: 'name', header: '姓名' },
    { accessorKey: 'email', header: '邮箱' },
    { accessorKey: 'role', header: '角色', align: 'center' },
  ];

  return <Table data={data} columns={columns} />;
}
```

### 可选择表格

```tsx
import { Table } from '@shared/ui';
import { useState } from 'react';

function SelectableTable() {
  const [selectedUsers, setSelectedUsers] = useState<User[]>([]);

  const columns: TableColumn<User>[] = [
    { accessorKey: 'name', header: '姓名' },
    { accessorKey: 'email', header: '邮箱' },
    { accessorKey: 'role', header: '角色' },
  ];

  return (
    <div>
      <Table
        data={data}
        columns={columns}
        selectable
        onSelectionChange={setSelectedUsers}
      />
      <p>已选择 {selectedUsers.length} 个用户</p>
    </div>
  );
}
```

### 可排序和过滤

```tsx
import { Table } from '@shared/ui';

function SortableFilterableTable() {
  const columns: TableColumn<User>[] = [
    { accessorKey: 'name', header: '姓名', sortable: true },
    { accessorKey: 'email', header: '邮箱', sortable: true },
    { accessorKey: 'role', header: '角色', sortable: true },
  ];

  return (
    <Table
      data={data}
      columns={columns}
      sortable
      filterable
    />
  );
}
```

### 分页表格

```tsx
import { Table } from '@shared/ui';
import { useState } from 'react';

function PaginatedTable() {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  return (
    <Table
      data={largeData}
      columns={columns}
      pagination
      currentPage={currentPage}
      pageSize={pageSize}
      onPageChange={(page, size) => {
        setCurrentPage(page);
        setPageSize(size);
      }}
      pageSizeOptions={[10, 20, 50, 100]}
    />
  );
}
```

### 虚拟滚动（大数据集）

```tsx
import { Table } from '@shared/ui';

function VirtualScrollTable() {
  const [metrics, setMetrics] = useState<VirtualScrollMetrics | null>(null);

  return (
    <div>
      <Table
        data={hugeData}
        columns={columns}
        virtual
        rowHeight={50}
        maxHeight={600}
        onVirtualScrollMetrics={setMetrics}
      />
      {metrics && (
        <div className="metrics">
          <p>总行数: {metrics.totalRows}</p>
          <p>可见行数: {metrics.visibleRows}</p>
          <p>渲染时间: {metrics.renderTime?.toFixed(2)}ms</p>
        </div>
      )}
    </div>
  );
}
```

### 可编辑表格

```tsx
import { Table } from '@shared/ui';

function EditableTable() {
  const [data, setData] = useState<User[]>(initialData);

  const handleEdit = (row: User, columnId: string, value: unknown) => {
    setData(prevData =>
      prevData.map(item =>
        item.id === row.id ? { ...item, [columnId]: value } : item
      )
    );
  };

  const columns: TableColumn<User>[] = [
    { accessorKey: 'name', header: '姓名', editable: true },
    { accessorKey: 'email', header: '邮箱', editable: true },
    { accessorKey: 'role', header: '角色', editable: true },
  ];

  return (
    <Table
      data={data}
      columns={columns}
      editable
      onEdit={handleEdit}
    />
  );
}
```

### 自定义单元格渲染

```tsx
import { Table } from '@shared/ui';

function CustomCellTable() {
  const columns: TableColumn<User>[] = [
    { accessorKey: 'name', header: '姓名' },
    { accessorKey: 'email', header: '邮箱' },
    {
      accessorKey: 'role',
      header: '角色',
      cellRenderer: ({ value }) => (
        <span className={`badge badge-${value === '管理员' ? 'primary' : 'secondary'}`}>
          {value}
        </span>
      ),
    },
    {
      accessorKey: 'status',
      header: '状态',
      cellRenderer: ({ value }) => (
        <span className={`status status-${value.toLowerCase()}`}>
          {value}
        </span>
      ),
    },
  ];

  return <Table data={data} columns={columns} />;
}
```

### 固定列

```tsx
import { Table } from '@shared/ui';

function FixedColumnTable() {
  const columns: TableColumn<User>[] = [
    { accessorKey: 'id', header: 'ID', fixed: 'left', size: 80 },
    { accessorKey: 'name', header: '姓名', fixed: 'left', size: 150 },
    { accessorKey: 'email', header: '邮箱' },
    { accessorKey: 'role', header: '角色' },
    { accessorKey: 'actions', header: '操作', fixed: 'right', size: 120 },
  ];

  return <Table data={data} columns={columns} />;
}
```

### 行点击事件

```tsx
import { Table } from '@shared/ui';

function RowClickTable() {
  const handleRowClick = (row: User, event: MouseEvent) => {
    console.log('Clicked row:', row);
  };

  const handleRowDoubleClick = (row: User, event: MouseEvent) => {
    console.log('Double clicked row:', row);
    // 打开详情页或编辑对话框
  };

  return (
    <Table
      data={data}
      columns={columns}
      onRowClick={handleRowClick}
      onRowDoubleClick={handleRowDoubleClick}
      hoverable
    />
  );
}
```

### 加载和空状态

```tsx
import { Table } from '@shared/ui';
import { Spinner } from '@shared/ui';

function LoadingAndEmptyTable() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<User[]>([]);

  useEffect(() => {
    fetchData().then(result => {
      setData(result);
      setLoading(false);
    });
  }, []);

  return (
    <Table
      data={data}
      columns={columns}
      loading={loading}
      loadingComponent={<Spinner />}
      empty={data.length === 0 && !loading}
      emptyComponent={
        <div className="empty-state">
          <p>暂无数据</p>
          <button onClick={fetchData}>刷新</button>
        </div>
      }
    />
  );
}
```

## 注意事项

1. **性能优化**: 
   - 使用 TanStack Table 提供最佳性能
   - 虚拟滚动适用于大数据集（1000+ 行）
   - 组件已使用 `React.memo` 优化

2. **列固定**: 
   - 使用 `fixed: 'left'` 或 `fixed: 'right'` 固定列
   - 固定列会自动添加阴影效果

3. **虚拟滚动**: 
   - 启用虚拟滚动时，建议设置固定的 `rowHeight`
   - `dynamicRowHeight` 会降低性能，仅在必要时使用
   - `overscan` 控制预渲染行数，影响滚动性能

4. **可编辑单元格**: 
   - 双击单元格进入编辑模式
   - 按 Enter 保存，按 Escape 取消
   - 可通过 `editComponent` 自定义编辑组件

5. **无障碍性**: 
   - 支持键盘导航
   - 完整的 ARIA 属性支持

6. **主题支持**: 
   - 通过 `theme` 属性切换明暗主题
   - 使用 CSS 变量实现主题定制

7. **响应式**: 
   - 表格容器会自动适应父容器宽度
   - 列宽可以设置为固定值或 'auto'

## 相关组件

- [`Button`](./Button.md) - 按钮组件
- [`Input`](./Input.md) - 输入框组件
- [`Select`](./Select.md) - 下拉选择组件
- [`Modal`](./Modal.md) - 模态框组件
