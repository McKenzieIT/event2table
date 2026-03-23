# 组件库优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 优化 Event2Table 组件库，删除废弃组件，优化大文件，提升性能和测试覆盖率

**Architecture:** 四阶段渐进式优化方案，每轮使用 3 个 subagent 并行处理，遵循 TDD 和分组测试原则

**Tech Stack:** React, TypeScript, Jest, React Testing Library, React.memo, useCallback, useMemo

---

## 实施约束条件

### ⚠️ 强制约束（不可偏离）

1. **并行处理约束**：
   - ✅ 每一轮必须使用 3 个 subagent 并行处理任务
   - ❌ 不得因 token 或时间限制减少 subagent 数量
   - ❌ 不得因 token 或时间限制改为串行执行
   - ✅ 仅当方案本身错误时才可调整（需向用户确认）

2. **分组测试约束**：
   - ✅ 所有测试必须使用分组测试方案
   - ✅ 推荐参数：`--testPathPattern="xxx" --maxWorkers=1`
   - ❌ 不得直接运行 `npm test`（会触发 60s 超时）

3. **实施完成文档约束**：
   - ✅ 完成后必须创建 `docs/implementation-reports/YYYY-MM-DD-component-library-optimization-completed.md`
   - ✅ 必须提交到 Git 并推送到 GitHub 远程仓库

---

## 阶段 1：低风险清理（删除废弃组件）

### 轮次 1.1：删除 BaseModal 组件（3 个 subagent 并行）

**Subagent 1 任务：查找并记录所有 BaseModal 的使用位置**

- [ ] **Step 1: 查找所有 BaseModal 的导入**

```bash
grep -r "from.*BaseModal" frontend/src --include="*.tsx" --include="*.ts" > /tmp/basemodal-imports.txt
cat /tmp/basemodal-imports.txt
```

Expected: 找到所有使用 BaseModal 的文件

- [ ] **Step 2: 记录所有使用位置**

创建文件：`docs/migration-records/basemodal-migration.md`

```markdown
# BaseModal 迁移记录

## 使用位置清单

| 文件路径 | 行号 | 当前导入 | 目标导入 |
|---------|------|---------|---------|
| ... | ... | ... | ... |

## 总计
- 总使用次数：xx 处
- 需要迁移：xx 个文件
```

- [ ] **Step 3: 提交记录**

```bash
git add docs/migration-records/basemodal-migration.md
git commit -m "docs: 记录 BaseModal 迁移清单"
```

**Subagent 2 任务：更新所有 BaseModal 的导入路径**

- [ ] **Step 1: 批量更新导入路径**

对每个使用 BaseModal 的文件：

```typescript
// 旧导入
import { BaseModal } from '@/shared/ui/BaseModal';
import { BaseModal } from '@/shared/ui/BaseModal/BaseModal';

// 新导入
import { Modal } from '@/shared/ui/components/Modal';
```

- [ ] **Step 2: 更新组件使用**

```typescript
// 旧使用
<BaseModal isOpen={isOpen} onClose={onClose}>
  {children}
</BaseModal>

// 新使用（确保 API 兼容）
<Modal isOpen={isOpen} onClose={onClose}>
  {children}
</Modal>
```

- [ ] **Step 3: 提交更新**

```bash
git add .
git commit -m "refactor: 迁移 BaseModal 到 Modal 组件"
```

**Subagent 3 任务：删除 BaseModal 组件文件和目录**

- [ ] **Step 1: 创建备份分支**

```bash
git checkout -b backup/basemodal-deletion-backup
git push origin backup/basemodal-deletion-backup
git checkout main
```

- [ ] **Step 2: 删除 BaseModal 目录**

```bash
rm -rf frontend/src/shared/ui/BaseModal
git add -A
git commit -m "refactor: 删除废弃的 BaseModal 组件"
```

- [ ] **Step 3: 验证删除**

```bash
# 验证文件已删除
ls frontend/src/shared/ui/BaseModal
# Expected: No such file or directory

# 验证没有残留引用
grep -r "BaseModal" frontend/src --include="*.tsx" --include="*.ts"
# Expected: 无结果
```

---

### 轮次 1.2：验证 BaseModal 删除（分组测试）

- [ ] **Step 1: 运行 Modal 组件测试**

```bash
npm test -- --testPathPattern="Modal" --maxWorkers=1
```

Expected: 所有 Modal 相关测试通过

- [ ] **Step 2: 运行 TypeScript 类型检查**

```bash
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 3: 运行 ESLint 检查**

```bash
npm run lint
```

Expected: 无 ESLint 错误

- [ ] **Step 4: 提交验证结果**

```bash
git add .
git commit -m "test: 验证 BaseModal 删除后的功能完整性"
```

---

### 轮次 1.3：删除 Select（旧）组件（3 个 subagent 并行）

**Subagent 1 任务：查找并记录所有 Select（旧）的使用位置**

- [ ] **Step 1: 查找所有 Select（旧）的导入**

```bash
# 查找旧版 Select 的导入（排除 components/Select）
grep -r "from.*Select" frontend/src --include="*.tsx" --include="*.ts" | grep -v "components/Select" > /tmp/select-old-imports.txt
cat /tmp/select-old-imports.txt
```

Expected: 找到所有使用旧版 Select 的文件

- [ ] **Step 2: 记录所有使用位置**

创建文件：`docs/migration-records/select-old-migration.md`

```markdown
# Select（旧）迁移记录

## 使用位置清单

| 文件路径 | 行号 | 当前导入 | 目标导入 |
|---------|------|---------|---------|
| ... | ... | ... | ... |

## 总计
- 总使用次数：xx 处
- 需要迁移：xx 个文件
```

- [ ] **Step 3: 提交记录**

```bash
git add docs/migration-records/select-old-migration.md
git commit -m "docs: 记录 Select（旧）迁移清单"
```

**Subagent 2 任务：更新所有 Select（旧）的导入路径**

- [ ] **Step 1: 批量更新导入路径**

对每个使用旧版 Select 的文件：

```typescript
// 旧导入
import { Select } from '@/shared/ui/Select';

// 新导入
import { Select } from '@/shared/ui/components/Select';
```

- [ ] **Step 2: 验证 API 兼容性**

检查新版 Select 的 API 是否与旧版兼容，如有差异需要调整使用方式

- [ ] **Step 3: 提交更新**

```bash
git add .
git commit -m "refactor: 迁移 Select（旧）到新版 Select 组件"
```

**Subagent 3 任务：删除 Select（旧）组件文件和目录**

- [ ] **Step 1: 删除 Select（旧）目录**

```bash
rm -rf frontend/src/shared/ui/Select
git add -A
git commit -m "refactor: 删除废弃的 Select（旧）组件"
```

- [ ] **Step 2: 验证删除**

```bash
# 验证文件已删除
ls frontend/src/shared/ui/Select
# Expected: No such file or directory

# 验证没有残留引用
grep -r "from.*@/shared/ui/Select['\"]" frontend/src --include="*.tsx" --include="*.ts"
# Expected: 无结果
```

- [ ] **Step 3: 提交验证**

```bash
git add .
git commit -m "test: 验证 Select（旧）删除后的功能完整性"
```

---

### 轮次 1.4：删除 Table（旧）组件（3 个 subagent 并行）

**Subagent 1 任务：查找并记录所有 Table（旧）的使用位置**

- [ ] **Step 1: 查找所有 Table（旧）的导入**

```bash
# 查找旧版 Table 的导入（排除 components/Table）
grep -r "from.*Table" frontend/src --include="*.tsx" --include="*.ts" | grep -v "components/Table" > /tmp/table-old-imports.txt
cat /tmp/table-old-imports.txt
```

Expected: 找到所有使用旧版 Table 的文件

- [ ] **Step 2: 记录所有使用位置**

创建文件：`docs/migration-records/table-old-migration.md`

```markdown
# Table（旧）迁移记录

## 使用位置清单

| 文件路径 | 行号 | 当前导入 | 目标导入 |
|---------|------|---------|---------|
| ... | ... | ... | ... |

## 总计
- 总使用次数：xx 处
- 需要迁移：xx 个文件
```

- [ ] **Step 3: 提交记录**

```bash
git add docs/migration-records/table-old-migration.md
git commit -m "docs: 记录 Table（旧）迁移清单"
```

**Subagent 2 任务：更新所有 Table（旧）的导入路径**

- [ ] **Step 1: 批量更新导入路径**

对每个使用旧版 Table 的文件：

```typescript
// 旧导入
import { Table } from '@/shared/ui/Table';

// 新导入
import { Table } from '@/shared/ui/components/Table';
```

- [ ] **Step 2: 验证 API 兼容性**

检查新版 Table 的 API 是否与旧版兼容，如有差异需要调整使用方式

- [ ] **Step 3: 提交更新**

```bash
git add .
git commit -m "refactor: 迁移 Table（旧）到新版 Table 组件"
```

**Subagent 3 任务：删除 Table（旧）组件文件和目录**

- [ ] **Step 1: 删除 Table（旧）目录**

```bash
rm -rf frontend/src/shared/ui/Table
git add -A
git commit -m "refactor: 删除废弃的 Table（旧）组件"
```

- [ ] **Step 2: 验证删除**

```bash
# 验证文件已删除
ls frontend/src/shared/ui/Table
# Expected: No such file or directory

# 验证没有残留引用
grep -r "from.*@/shared/ui/Table['\"]" frontend/src --include="*.tsx" --include="*.ts"
# Expected: 无结果
```

- [ ] **Step 3: 提交验证**

```bash
git add .
git commit -m "test: 验证 Table（旧）删除后的功能完整性"
```

---

### 轮次 1.5：阶段 1 最终验证（分组测试）

- [ ] **Step 1: 运行所有组件测试（分组）**

```bash
npm test -- --testPathPattern="Modal|Select|Table" --maxWorkers=1
```

Expected: 所有相关组件测试通过

- [ ] **Step 2: 运行 TypeScript 类型检查**

```bash
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 3: 运行 ESLint 检查**

```bash
npm run lint
```

Expected: 无 ESLint 错误

- [ ] **Step 4: 创建阶段 1 完成文档**

创建文件：`docs/implementation-reports/phase-1-completed.md`

```markdown
# 阶段 1：低风险清理 - 完成报告

## 完成情况

### 删除的组件
- ✅ BaseModal（355 行）
- ✅ Select（旧）（395 行）
- ✅ Table（旧）

### 迁移的文件
- BaseModal: xx 个文件
- Select（旧）: xx 个文件
- Table（旧）: xx 个文件

### 验证结果
- ✅ 所有测试通过
- ✅ 无类型错误
- ✅ 无 ESLint 错误
- ✅ 无功能回归

## 遗留问题
- 无
```

- [ ] **Step 5: 提交阶段 1 完成文档**

```bash
git add docs/implementation-reports/phase-1-completed.md
git commit -m "docs: 阶段 1 完成 - 删除废弃组件"
```

---

## 阶段 2：架构优化（拆分大文件）

### 轮次 2.1：优化 Table.tsx（854 行）（3 个 subagent 并行）

**Subagent 1 任务：分析 Table.tsx 的代码结构**

- [ ] **Step 1: 读取 Table.tsx 文件**

```bash
wc -l frontend/src/shared/ui/components/Table/Table.tsx
# Expected: 854 行
```

- [ ] **Step 2: 分析代码结构**

创建文件：`docs/refactor-analysis/table-refactor-plan.md`

```markdown
# Table.tsx 重构计划

## 当前结构分析

### 主要功能模块
1. 表格渲染逻辑（xx 行）
2. 排序逻辑（xx 行）
3. 分页逻辑（xx 行）
4. 筛选逻辑（xx 行）
5. 工具函数（xx 行）

### 可拆分的部分
1. 排序逻辑 → `useTableSort` hook
2. 分页逻辑 → `useTablePagination` hook
3. 筛选逻辑 → `useTableFilter` hook
4. 工具函数 → `tableUtils.ts`

### 拆分后的文件结构
```
Table/
├── Table.tsx (主组件，< 500 行)
├── hooks/
│   ├── useTableSort.ts
│   ├── useTablePagination.ts
│   └── useTableFilter.ts
├── utils/
│   └── tableUtils.ts
├── types.ts
└── Table.test.tsx
```
```

- [ ] **Step 3: 提交分析文档**

```bash
git add docs/refactor-analysis/table-refactor-plan.md
git commit -m "docs: Table.tsx 重构计划"
```

**Subagent 2 任务：拆分 Table.tsx 的 hooks**

- [ ] **Step 1: 创建 useTableSort hook**

创建文件：`frontend/src/shared/ui/components/Table/hooks/useTableSort.ts`

```typescript
import { useState, useCallback, useMemo } from 'react';

export interface UseTableSortOptions<T> {
  data: T[];
  defaultSortKey?: keyof T;
  defaultSortDirection?: 'asc' | 'desc';
}

export interface UseTableSortResult<T> {
  sortedData: T[];
  sortKey: keyof T | null;
  sortDirection: 'asc' | 'desc';
  handleSort: (key: keyof T) => void;
}

export function useTableSort<T>({
  data,
  defaultSortKey,
  defaultSortDirection = 'asc',
}: UseTableSortOptions<T>): UseTableSortResult<T> {
  const [sortKey, setSortKey] = useState<keyof T | null>(defaultSortKey || null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>(defaultSortDirection);

  const sortedData = useMemo(() => {
    if (!sortKey) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortKey];
      const bValue = b[sortKey];

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortKey, sortDirection]);

  const handleSort = useCallback((key: keyof T) => {
    if (sortKey === key) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  }, [sortKey]);

  return {
    sortedData,
    sortKey,
    sortDirection,
    handleSort,
  };
}
```

- [ ] **Step 2: 创建 useTablePagination hook**

创建文件：`frontend/src/shared/ui/components/Table/hooks/useTablePagination.ts`

```typescript
import { useState, useCallback, useMemo } from 'react';

export interface UseTablePaginationOptions {
  totalItems: number;
  defaultPageSize?: number;
  defaultCurrentPage?: number;
}

export interface UseTablePaginationResult {
  currentPage: number;
  pageSize: number;
  totalPages: number;
  startIndex: number;
  endIndex: number;
  handlePageChange: (page: number) => void;
  handlePageSizeChange: (size: number) => void;
}

export function useTablePagination({
  totalItems,
  defaultPageSize = 10,
  defaultCurrentPage = 1,
}: UseTablePaginationOptions): UseTablePaginationResult {
  const [currentPage, setCurrentPage] = useState(defaultCurrentPage);
  const [pageSize, setPageSize] = useState(defaultPageSize);

  const totalPages = useMemo(() => Math.ceil(totalItems / pageSize), [totalItems, pageSize]);

  const startIndex = useMemo(() => (currentPage - 1) * pageSize, [currentPage, pageSize]);
  const endIndex = useMemo(() => Math.min(startIndex + pageSize, totalItems), [startIndex, pageSize, totalItems]);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  }, [totalPages]);

  const handlePageSizeChange = useCallback((size: number) => {
    setPageSize(size);
    setCurrentPage(1);
  }, []);

  return {
    currentPage,
    pageSize,
    totalPages,
    startIndex,
    endIndex,
    handlePageChange,
    handlePageSizeChange,
  };
}
```

- [ ] **Step 3: 提交 hooks**

```bash
git add frontend/src/shared/ui/components/Table/hooks/
git commit -m "refactor: 拆分 Table hooks - useTableSort 和 useTablePagination"
```

**Subagent 3 任务：拆分 Table.tsx 的工具函数**

- [ ] **Step 1: 创建 tableUtils.ts**

创建文件：`frontend/src/shared/ui/components/Table/utils/tableUtils.ts`

```typescript
/**
 * 格式化表格数据
 */
export function formatTableData<T>(data: T[]): T[] {
  return data.map(item => ({
    ...item,
    // 添加格式化逻辑
  }));
}

/**
 * 过滤表格数据
 */
export function filterTableData<T>(
  data: T[],
  filters: Record<string, any>
): T[] {
  return data.filter(item => {
    return Object.entries(filters).every(([key, value]) => {
      if (!value) return true;
      return item[key] === value;
    });
  });
}

/**
 * 计算表格列宽
 */
export function calculateColumnWidths(
  columns: Array<{ key: string; width?: number }>
): Record<string, number> {
  const totalWidth = columns.reduce((sum, col) => sum + (col.width || 0), 0);
  const remainingWidth = 100 - totalWidth;
  const autoColumns = columns.filter(col => !col.width);

  return columns.reduce((widths, col) => {
    widths[col.key] = col.width || remainingWidth / autoColumns.length;
    return widths;
  }, {} as Record<string, number>);
}
```

- [ ] **Step 2: 创建 types.ts**

创建文件：`frontend/src/shared/ui/components/Table/types.ts`

```typescript
export interface TableColumn<T = any> {
  key: string;
  title: string;
  width?: number;
  sortable?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
}

export interface TableProps<T = any> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: boolean;
  pageSize?: number;
  sortable?: boolean;
  onRowClick?: (record: T, index: number) => void;
}

export interface TableState {
  currentPage: number;
  pageSize: number;
  sortKey: string | null;
  sortDirection: 'asc' | 'desc';
  filters: Record<string, any>;
}
```

- [ ] **Step 3: 提交工具函数和类型**

```bash
git add frontend/src/shared/ui/components/Table/utils/ frontend/src/shared/ui/components/Table/types.ts
git commit -m "refactor: 拆分 Table 工具函数和类型定义"
```

---

### 轮次 2.2：重构 Table.tsx 主文件（使用拆分后的模块）

- [ ] **Step 1: 重构 Table.tsx 主文件**

修改文件：`frontend/src/shared/ui/components/Table/Table.tsx`

```typescript
import React from 'react';
import { useTableSort } from './hooks/useTableSort';
import { useTablePagination } from './hooks/useTablePagination';
import { filterTableData, calculateColumnWidths } from './utils/tableUtils';
import type { TableProps, TableColumn } from './types';

export const Table = React.memo(function Table<T>({
  data,
  columns,
  loading = false,
  pagination = true,
  pageSize = 10,
  sortable = false,
  onRowClick,
}: TableProps<T>) {
  // 使用拆分后的 hooks
  const { sortedData, sortKey, sortDirection, handleSort } = useTableSort({
    data,
    defaultSortDirection: 'asc',
  });

  const {
    currentPage,
    pageSize: currentPageSize,
    totalPages,
    startIndex,
    endIndex,
    handlePageChange,
    handlePageSizeChange,
  } = useTablePagination({
    totalItems: sortedData.length,
    defaultPageSize: pageSize,
  });

  // 计算列宽
  const columnWidths = calculateColumnWidths(columns);

  // 获取当前页数据
  const currentPageData = sortedData.slice(startIndex, endIndex);

  // 渲染逻辑...
  return (
    <div className="table-container">
      {/* 表格渲染代码 */}
    </div>
  );
});
```

- [ ] **Step 2: 验证文件行数**

```bash
wc -l frontend/src/shared/ui/components/Table/Table.tsx
# Expected: < 500 行
```

- [ ] **Step 3: 提交重构**

```bash
git add frontend/src/shared/ui/components/Table/Table.tsx
git commit -m "refactor: 重构 Table.tsx 主文件 - 使用拆分后的模块"
```

---

### 轮次 2.3：优化 Select.tsx（590 行）（3 个 subagent 并行）

**Subagent 1 任务：分析 Select.tsx 的代码结构**

- [ ] **Step 1: 读取 Select.tsx 文件**

```bash
wc -l frontend/src/shared/ui/components/Select/Select.tsx
# Expected: 590 行
```

- [ ] **Step 2: 分析代码结构**

创建文件：`docs/refactor-analysis/select-refactor-plan.md`

```markdown
# Select.tsx 重构计划

## 当前结构分析

### 主要功能模块
1. 选项渲染逻辑（xx 行）
2. 搜索逻辑（xx 行）
3. 多选逻辑（xx 行）
4. 工具函数（xx 行）

### 可拆分的部分
1. 搜索逻辑 → `useSelectSearch` hook
2. 多选逻辑 → `useSelectMultiple` hook
3. 工具函数 → `selectUtils.ts`

### 拆分后的文件结构
```
Select/
├── Select.tsx (主组件，< 500 行)
├── hooks/
│   ├── useSelectSearch.ts
│   └── useSelectMultiple.ts
├── utils/
│   └── selectUtils.ts
├── types.ts
└── Select.test.tsx
```
```

- [ ] **Step 3: 提交分析文档**

```bash
git add docs/refactor-analysis/select-refactor-plan.md
git commit -m "docs: Select.tsx 重构计划"
```

**Subagent 2 任务：拆分 Select.tsx 的 hooks**

- [ ] **Step 1: 创建 useSelectSearch hook**

创建文件：`frontend/src/shared/ui/components/Select/hooks/useSelectSearch.ts`

```typescript
import { useState, useCallback, useMemo } from 'react';

export interface UseSelectSearchOptions<T> {
  options: T[];
  filterOption?: (option: T, searchValue: string) => boolean;
}

export interface UseSelectSearchResult<T> {
  searchValue: string;
  filteredOptions: T[];
  handleSearch: (value: string) => void;
  clearSearch: () => void;
}

export function useSelectSearch<T>({
  options,
  filterOption,
}: UseSelectSearchOptions<T>): UseSelectSearchResult<T> {
  const [searchValue, setSearchValue] = useState('');

  const filteredOptions = useMemo(() => {
    if (!searchValue) return options;

    return options.filter(option => {
      if (filterOption) {
        return filterOption(option, searchValue);
      }

      // 默认过滤逻辑
      const label = (option as any).label || '';
      return label.toLowerCase().includes(searchValue.toLowerCase());
    });
  }, [options, searchValue, filterOption]);

  const handleSearch = useCallback((value: string) => {
    setSearchValue(value);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchValue('');
  }, []);

  return {
    searchValue,
    filteredOptions,
    handleSearch,
    clearSearch,
  };
}
```

- [ ] **Step 2: 创建 useSelectMultiple hook**

创建文件：`frontend/src/shared/ui/components/Select/hooks/useSelectMultiple.ts`

```typescript
import { useState, useCallback } from 'react';

export interface UseSelectMultipleOptions<T> {
  value?: T[];
  onChange?: (value: T[]) => void;
}

export interface UseSelectMultipleResult<T> {
  selectedValues: T[];
  isSelected: (value: T) => boolean;
  handleSelect: (value: T) => void;
  handleDeselect: (value: T) => void;
  handleClear: () => void;
}

export function useSelectMultiple<T>({
  value = [],
  onChange,
}: UseSelectMultipleOptions<T>): UseSelectMultipleResult<T> {
  const [selectedValues, setSelectedValues] = useState<T[]>(value);

  const isSelected = useCallback(
    (val: T) => selectedValues.includes(val),
    [selectedValues]
  );

  const handleSelect = useCallback(
    (val: T) => {
      const newValues = [...selectedValues, val];
      setSelectedValues(newValues);
      onChange?.(newValues);
    },
    [selectedValues, onChange]
  );

  const handleDeselect = useCallback(
    (val: T) => {
      const newValues = selectedValues.filter(v => v !== val);
      setSelectedValues(newValues);
      onChange?.(newValues);
    },
    [selectedValues, onChange]
  );

  const handleClear = useCallback(() => {
    setSelectedValues([]);
    onChange?.([]);
  }, [onChange]);

  return {
    selectedValues,
    isSelected,
    handleSelect,
    handleDeselect,
    handleClear,
  };
}
```

- [ ] **Step 3: 提交 hooks**

```bash
git add frontend/src/shared/ui/components/Select/hooks/
git commit -m "refactor: 拆分 Select hooks - useSelectSearch 和 useSelectMultiple"
```

**Subagent 3 任务：拆分 Select.tsx 的工具函数**

- [ ] **Step 1: 创建 selectUtils.ts**

创建文件：`frontend/src/shared/ui/components/Select/utils/selectUtils.ts`

```typescript
/**
 * 格式化选项数据
 */
export function formatOptions<T>(options: T[]): T[] {
  return options.map(option => ({
    ...option,
    // 添加格式化逻辑
  }));
}

/**
 * 过滤选项
 */
export function filterOptions<T>(
  options: T[],
  searchValue: string,
  filterOption?: (option: T, searchValue: string) => boolean
): T[] {
  if (!searchValue) return options;

  return options.filter(option => {
    if (filterOption) {
      return filterOption(option, searchValue);
    }

    const label = (option as any).label || '';
    return label.toLowerCase().includes(searchValue.toLowerCase());
  });
}

/**
 * 高亮搜索关键词
 */
export function highlightSearchMatch(text: string, searchValue: string): string {
  if (!searchValue) return text;

  const regex = new RegExp(`(${searchValue})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}
```

- [ ] **Step 2: 创建 types.ts**

创建文件：`frontend/src/shared/ui/components/Select/types.ts`

```typescript
export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  [key: string]: any;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string | number | (string | number)[];
  onChange?: (value: string | number | (string | number)[]) => void;
  placeholder?: string;
  disabled?: boolean;
  loading?: boolean;
  multiple?: boolean;
  searchable?: boolean;
  clearable?: boolean;
}
```

- [ ] **Step 3: 提交工具函数和类型**

```bash
git add frontend/src/shared/ui/components/Select/utils/ frontend/src/shared/ui/components/Select/types.ts
git commit -m "refactor: 拆分 Select 工具函数和类型定义"
```

---

### 轮次 2.4：优化 Form.test.tsx（1095 行）（3 个 subagent 并行）

**Subagent 1 任务：分析 Form.test.tsx 的代码结构**

- [ ] **Step 1: 读取 Form.test.tsx 文件**

```bash
wc -l frontend/src/shared/ui/components/Form/Form.test.tsx
# Expected: 1095 行
```

- [ ] **Step 2: 分析测试代码结构**

创建文件：`docs/refactor-analysis/form-test-refactor-plan.md`

```markdown
# Form.test.tsx 重构计划

## 当前结构分析

### 测试分组
1. 基础渲染测试（xx 行）
2. 表单验证测试（xx 行）
3. 表单提交测试（xx 行）
4. 字段交互测试（xx 行）

### 优化策略
遵循"1个组件1个测试文件"原则，优化内部代码组织：
1. 提取测试辅助函数
2. 优化测试分组结构
3. 提取测试数据工厂

### 优化后的文件结构
```
Form/
├── Form.test.tsx (优化后的测试文件，< 1200 行)
├── __tests__/
│   ├── testHelpers.ts (测试辅助函数)
│   └── testData.ts (测试数据工厂)
```
```

- [ ] **Step 3: 提交分析文档**

```bash
git add docs/refactor-analysis/form-test-refactor-plan.md
git commit -m "docs: Form.test.tsx 重构计划"
```

**Subagent 2 任务：提取测试辅助函数**

- [ ] **Step 1: 创建 testHelpers.ts**

创建文件：`frontend/src/shared/ui/components/Form/__tests__/testHelpers.ts`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactElement } from 'react';

/**
 * 渲染表单组件
 */
export function renderForm(ui: ReactElement) {
  return {
    ...render(ui),
    user: userEvent.setup(),
  };
}

/**
 * 填写表单字段
 */
export async function fillFormField(
  user: ReturnType<typeof userEvent.setup>,
  label: string,
  value: string
) {
  const input = screen.getByLabelText(label);
  await user.clear(input);
  await user.type(input, value);
}

/**
 * 提交表单
 */
export async function submitForm(user: ReturnType<typeof userEvent.setup>) {
  const submitButton = screen.getByRole('button', { name: /submit/i });
  await user.click(submitButton);
}

/**
 * 验证错误消息
 */
export function expectErrorMessage(message: string) {
  expect(screen.getByText(message)).toBeInTheDocument();
}

/**
 * 验证字段值
 */
export function expectFieldValue(label: string, value: string) {
  const input = screen.getByLabelText(label);
  expect(input).toHaveValue(value);
}
```

- [ ] **Step 2: 创建 testData.ts**

创建文件：`frontend/src/shared/ui/components/Form/__tests__/testData.ts`

```typescript
/**
 * 表单测试数据工厂
 */
export const createFormData = (overrides = {}) => ({
  username: 'testuser',
  email: 'test@example.com',
  password: 'Test@123456',
  ...overrides,
});

/**
 * 无效的表单数据
 */
export const invalidFormData = {
  emptyUsername: { username: '' },
  invalidEmail: { email: 'invalid-email' },
  shortPassword: { password: '123' },
};

/**
 * 表单字段配置
 */
export const formFields = [
  {
    name: 'username',
    label: 'Username',
    type: 'text',
    required: true,
    minLength: 3,
    maxLength: 20,
  },
  {
    name: 'email',
    label: 'Email',
    type: 'email',
    required: true,
  },
  {
    name: 'password',
    label: 'Password',
    type: 'password',
    required: true,
    minLength: 8,
  },
];
```

- [ ] **Step 3: 提交测试辅助函数**

```bash
git add frontend/src/shared/ui/components/Form/__tests__/
git commit -m "refactor: 提取 Form 测试辅助函数和数据工厂"
```

**Subagent 3 任务：优化 Form.test.tsx 的代码组织**

- [ ] **Step 1: 重构 Form.test.tsx**

修改文件：`frontend/src/shared/ui/components/Form/Form.test.tsx`

```typescript
import { renderForm, fillFormField, submitForm, expectErrorMessage, expectFieldValue } from './__tests__/testHelpers';
import { createFormData, invalidFormData, formFields } from './__tests__/testData';
import { Form } from './Form';

describe('Form Component', () => {
  // ==================== 基础渲染测试 ====================
  describe('Rendering', () => {
    it('should render form fields correctly', () => {
      // ...
    });

    it('should render submit button', () => {
      // ...
    });
  });

  // ==================== 表单验证测试 ====================
  describe('Validation', () => {
    it('should show error for empty username', async () => {
      // ...
    });

    it('should show error for invalid email', async () => {
      // ...
    });
  });

  // ==================== 表单提交测试 ====================
  describe('Submission', () => {
    it('should submit valid form data', async () => {
      // ...
    });

    it('should not submit invalid form', async () => {
      // ...
    });
  });

  // ==================== 字段交互测试 ====================
  describe('Field Interactions', () => {
    it('should update field value on change', async () => {
      // ...
    });

    it('should clear field on reset', async () => {
      // ...
    });
  });
});
```

- [ ] **Step 2: 验证文件行数**

```bash
wc -l frontend/src/shared/ui/components/Form/Form.test.tsx
# Expected: < 1200 行
```

- [ ] **Step 3: 提交重构**

```bash
git add frontend/src/shared/ui/components/Form/Form.test.tsx
git commit -m "refactor: 优化 Form.test.tsx 代码组织 - 使用辅助函数和清晰的测试分组"
```

---

### 轮次 2.5：阶段 2 最终验证（分组测试）

- [ ] **Step 1: 运行所有重构组件的测试（分组）**

```bash
npm test -- --testPathPattern="Table|Select|Form" --maxWorkers=1
```

Expected: 所有相关组件测试通过

- [ ] **Step 2: 运行 TypeScript 类型检查**

```bash
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 3: 验证文件行数**

```bash
wc -l frontend/src/shared/ui/components/Table/Table.tsx
wc -l frontend/src/shared/ui/components/Select/Select.tsx
wc -l frontend/src/shared/ui/components/Form/Form.test.tsx
# Expected: 所有文件 < 500 行（组件）或 < 1200 行（测试）
```

- [ ] **Step 4: 创建阶段 2 完成文档**

创建文件：`docs/implementation-reports/phase-2-completed.md`

```markdown
# 阶段 2：架构优化 - 完成报告

## 完成情况

### 优化的大文件
- ✅ Table.tsx（854 行 → < 500 行）
- ✅ Select.tsx（590 行 → < 500 行）
- ✅ Form.test.tsx（1095 行 → < 1200 行）

### 拆分的模块
- Table: 2 个 hooks + 1 个 utils + types
- Select: 2 个 hooks + 1 个 utils + types
- Form: 测试辅助函数 + 测试数据工厂

### 验证结果
- ✅ 所有测试通过
- ✅ 无类型错误
- ✅ 文件行数符合标准
- ✅ 无功能回归

## 遗留问题
- 无
```

- [ ] **Step 5: 提交阶段 2 完成文档**

```bash
git add docs/implementation-reports/phase-2-completed.md
git commit -m "docs: 阶段 2 完成 - 架构优化"
```

---

## 阶段 3：性能优化

### 轮次 3.1：为所有组件添加 React.memo（3 个 subagent 并行）

**Subagent 1 任务：扫描未使用 React.memo 的组件**

- [ ] **Step 1: 查找所有组件文件**

```bash
find frontend/src/shared/ui -name "*.tsx" -type f | grep -v test | grep -v ".d.ts" > /tmp/all-components.txt
cat /tmp/all-components.txt
```

Expected: 列出所有组件文件

- [ ] **Step 2: 检查哪些组件未使用 React.memo**

```bash
for file in $(cat /tmp/all-components.txt); do
  if ! grep -q "React.memo" "$file"; then
    echo "$file"
  fi
done > /tmp/components-without-memo.txt
cat /tmp/components-without-memo.txt
```

Expected: 列出未使用 React.memo 的组件

- [ ] **Step 3: 提交扫描结果**

```bash
git add /tmp/components-without-memo.txt
git commit -m "docs: 记录未使用 React.memo 的组件清单"
```

**Subagent 2 任务：为组件添加 React.memo**

- [ ] **Step 1: 为每个未使用 React.memo 的组件添加优化**

对每个组件文件：

```typescript
// 优化前
export function MyComponent(props: MyComponentProps) {
  // ...
}

// 优化后
export const MyComponent = React.memo(function MyComponent(props: MyComponentProps) {
  // ...
});
```

- [ ] **Step 2: 验证优化**

```bash
# 验证所有组件都使用了 React.memo
for file in $(cat /tmp/components-without-memo.txt); do
  if grep -q "React.memo" "$file"; then
    echo "✅ $file"
  else
    echo "❌ $file"
  fi
done
```

Expected: 所有组件都显示 ✅

- [ ] **Step 3: 提交优化**

```bash
git add .
git commit -m "perf: 为所有组件添加 React.memo 优化"
```

**Subagent 3 任务：为事件处理器添加 useCallback**

- [ ] **Step 1: 扫描需要优化的组件**

```bash
# 查找包含事件处理器的组件
grep -r "onClick\|onChange\|onSubmit" frontend/src/shared/ui --include="*.tsx" | grep -v test | cut -d: -f1 | sort -u > /tmp/components-with-handlers.txt
cat /tmp/components-with-handlers.txt
```

Expected: 列出包含事件处理器的组件

- [ ] **Step 2: 为每个组件添加 useCallback**

对每个组件文件：

```typescript
import { useCallback } from 'react';

// 优化前
function MyComponent({ onClick }: Props) {
  const handleClick = () => {
    onClick();
  };
}

// 优化后
function MyComponent({ onClick }: Props) {
  const handleClick = useCallback(() => {
    onClick();
  }, [onClick]);
}
```

- [ ] **Step 3: 提交优化**

```bash
git add .
git commit -m "perf: 为所有事件处理器添加 useCallback 优化"
```

---

### 轮次 3.2：为计算属性添加 useMemo（3 个 subagent 并行）

**Subagent 1 任务：扫描需要优化的计算属性**

- [ ] **Step 1: 查找包含计算属性的组件**

```bash
# 查找包含复杂计算的组件
grep -r "filter\|map\|reduce\|sort" frontend/src/shared/ui --include="*.tsx" | grep -v test | cut -d: -f1 | sort -u > /tmp/components-with-computations.txt
cat /tmp/components-with-computations.txt
```

Expected: 列出包含计算属性的组件

- [ ] **Step 2: 分析需要优化的计算**

创建文件：`docs/performance-analysis/usememo-optimization-plan.md`

```markdown
# useMemo 优化计划

## 需要优化的组件

| 组件 | 计算属性 | 优化方式 |
|------|---------|---------|
| Table | sortedData | useMemo |
| Select | filteredOptions | useMemo |
| ... | ... | ... |
```

- [ ] **Step 3: 提交分析文档**

```bash
git add docs/performance-analysis/usememo-optimization-plan.md
git commit -m "docs: useMemo 优化计划"
```

**Subagent 2 任务：为计算属性添加 useMemo**

- [ ] **Step 1: 为每个组件添加 useMemo**

对每个组件文件：

```typescript
import { useMemo } from 'react';

// 优化前
function MyComponent({ data }: Props) {
  const filteredData = data.filter(item => item.active);
  const sortedData = filteredData.sort((a, b) => a.name.localeCompare(b.name));
}

// 优化后
function MyComponent({ data }: Props) {
  const filteredData = useMemo(() => data.filter(item => item.active), [data]);
  const sortedData = useMemo(() => filteredData.sort((a, b) => a.name.localeCompare(b.name)), [filteredData]);
}
```

- [ ] **Step 2: 验证优化**

```bash
# 验证所有计算属性都使用了 useMemo
for file in $(cat /tmp/components-with-computations.txt); do
  if grep -q "useMemo" "$file"; then
    echo "✅ $file"
  else
    echo "❌ $file"
  fi
done
```

Expected: 所有组件都显示 ✅

- [ ] **Step 3: 提交优化**

```bash
git add .
git commit -m "perf: 为所有计算属性添加 useMemo 优化"
```

**Subagent 3 任务：性能测试验证**

- [ ] **Step 1: 运行性能测试（分组）**

```bash
npm test -- --testPathPattern="performance" --maxWorkers=1
```

Expected: 性能测试通过

- [ ] **Step 2: 运行所有组件测试（分组）**

```bash
npm test -- --testPathPattern="shared/ui" --maxWorkers=1
```

Expected: 所有组件测试通过

- [ ] **Step 3: 提交验证结果**

```bash
git add .
git commit -m "test: 验证性能优化后的功能完整性"
```

---

### 轮次 3.3：阶段 3 最终验证（分组测试）

- [ ] **Step 1: 运行所有性能测试（分组）**

```bash
npm test -- --testPathPattern="performance" --maxWorkers=1
```

Expected: 所有性能测试通过

- [ ] **Step 2: 运行 TypeScript 类型检查**

```bash
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 3: 验证性能优化统计**

```bash
# 统计 React.memo 使用情况
grep -r "React.memo" frontend/src/shared/ui --include="*.tsx" | wc -l
# Expected: > 67 处

# 统计 useCallback 使用情况
grep -r "useCallback" frontend/src/shared/ui --include="*.tsx" | wc -l
# Expected: > 之前数量

# 统计 useMemo 使用情况
grep -r "useMemo" frontend/src/shared/ui --include="*.tsx" | wc -l
# Expected: > 之前数量
```

- [ ] **Step 4: 创建阶段 3 完成文档**

创建文件：`docs/implementation-reports/phase-3-completed.md`

```markdown
# 阶段 3：性能优化 - 完成报告

## 完成情况

### 性能优化统计
- ✅ React.memo 使用：xx 处（新增 xx 处）
- ✅ useCallback 使用：xx 处（新增 xx 处）
- ✅ useMemo 使用：xx 处（新增 xx 处）

### 优化的组件
- 所有组件都使用了 React.memo
- 所有事件处理器都使用了 useCallback
- 所有计算属性都使用了 useMemo

### 验证结果
- ✅ 所有性能测试通过
- ✅ 无类型错误
- ✅ 性能无下降
- ✅ 无功能回归

## 遗留问题
- 无
```

- [ ] **Step 5: 提交阶段 3 完成文档**

```bash
git add docs/implementation-reports/phase-3-completed.md
git commit -m "docs: 阶段 3 完成 - 性能优化"
```

---

## 阶段 4：测试完善

### 轮次 4.1：提升测试覆盖率（3 个 subagent 并行）

**Subagent 1 任务：扫描测试覆盖率**

- [ ] **Step 1: 生成测试覆盖率报告（分组）**

```bash
npm test -- --testPathPattern="shared/ui" --coverage --coverageReporters=html --maxWorkers=1
```

Expected: 生成覆盖率报告

- [ ] **Step 2: 查看覆盖率报告**

```bash
open coverage/index.html
```

Expected: 查看详细的覆盖率数据

- [ ] **Step 3: 记录覆盖率数据**

创建文件：`docs/test-coverage/coverage-analysis.md`

```markdown
# 测试覆盖率分析

## 当前覆盖率

| 组件 | 行覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|---------|-----------|-----------|
| Table | xx% | xx% | xx% |
| Select | xx% | xx% | xx% |
| ... | ... | ... | ... |

## 需要提升覆盖率的组件
- 组件 A：当前 xx%，目标 80%
- 组件 B：当前 xx%，目标 80%
- ...
```

- [ ] **Step 4: 提交分析文档**

```bash
git add docs/test-coverage/coverage-analysis.md
git commit -m "docs: 测试覆盖率分析"
```

**Subagent 2 任务：为覆盖率不足的组件补充测试**

- [ ] **Step 1: 为每个覆盖率不足的组件补充测试**

对每个组件：

```typescript
// 补充缺失的测试用例
describe('ComponentName', () => {
  // 已有测试...

  // 新增测试：边界情况
  it('should handle edge case', () => {
    // ...
  });

  // 新增测试：错误情况
  it('should handle error case', () => {
    // ...
  });

  // 新增测试：用户交互
  it('should handle user interaction', () => {
    // ...
  });
});
```

- [ ] **Step 2: 验证覆盖率提升**

```bash
npm test -- --testPathPattern="ComponentName" --coverage --maxWorkers=1
```

Expected: 覆盖率 ≥ 80%

- [ ] **Step 3: 提交测试补充**

```bash
git add .
git commit -m "test: 补充测试用例 - 提升覆盖率到 80%"
```

**Subagent 3 任务：为核心组件添加集成测试**

- [ ] **Step 1: 为核心组件创建集成测试**

创建文件：`frontend/src/shared/ui/components/__tests__/TableForm.integration.test.tsx`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Table } from '../Table';
import { Form } from '../Form';

describe('Table + Form Integration', () => {
  it('should update table when form is submitted', async () => {
    const user = userEvent.setup();
    
    render(
      <div>
        <Form onSubmit={handleAddRow} />
        <Table data={tableData} />
      </div>
    );

    // 填写表单
    await user.type(screen.getByLabelText('Name'), 'New Item');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    // 验证表格更新
    await waitFor(() => {
      expect(screen.getByText('New Item')).toBeInTheDocument();
    });
  });
});
```

- [ ] **Step 2: 运行集成测试（分组）**

```bash
npm test -- --testPathPattern="integration" --maxWorkers=1
```

Expected: 所有集成测试通过

- [ ] **Step 3: 提交集成测试**

```bash
git add .
git commit -m "test: 为核心组件添加集成测试"
```

---

### 轮次 4.2：阶段 4 最终验证（分组测试）

- [ ] **Step 1: 运行所有测试（分组）**

```bash
npm test -- --testPathPattern="shared/ui" --maxWorkers=1
```

Expected: 所有测试通过

- [ ] **Step 2: 验证测试覆盖率**

```bash
npm test -- --testPathPattern="shared/ui" --coverage --maxWorkers=1
```

Expected: 覆盖率 ≥ 80%

- [ ] **Step 3: 运行 TypeScript 类型检查**

```bash
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 4: 创建阶段 4 完成文档**

创建文件：`docs/implementation-reports/phase-4-completed.md`

```markdown
# 阶段 4：测试完善 - 完成报告

## 完成情况

### 测试覆盖率
- ✅ 总体覆盖率：xx%（目标 ≥ 80%）
- ✅ 核心组件覆盖率：xx%

### 新增测试
- 单元测试：xx 个
- 集成测试：xx 个

### 验证结果
- ✅ 所有测试通过
- ✅ 覆盖率达标
- ✅ 无类型错误
- ✅ 无功能回归

## 遗留问题
- 无
```

- [ ] **Step 5: 提交阶段 4 完成文档**

```bash
git add docs/implementation-reports/phase-4-completed.md
git commit -m "docs: 阶段 4 完成 - 测试完善"
```

---

## 最终验收：全量组件扫描（3 个 subagent 并行）

### 轮次 Final：查漏补缺扫描

**Subagent 1 任务：扫描组件目录结构和文件大小**

- [ ] **Step 1: 扫描所有组件目录**

```bash
find frontend/src/shared/ui -name "*.tsx" -type f | grep -v test | grep -v ".d.ts" | xargs wc -l | sort -rn > /tmp/component-sizes.txt
cat /tmp/component-sizes.txt
```

Expected: 所有组件文件 < 500 行

- [ ] **Step 2: 扫描测试文件**

```bash
find frontend/src/shared/ui -name "*.test.tsx" -type f | xargs wc -l | sort -rn > /tmp/test-sizes.txt
cat /tmp/test-sizes.txt
```

Expected: 所有测试文件 < 1200 行

- [ ] **Step 3: 生成扫描报告**

创建文件：`docs/final-scan/component-structure-scan.md`

```markdown
# 组件结构扫描报告

## 组件文件大小统计

| 组件 | 行数 | 状态 |
|------|------|------|
| Table.tsx | xxx | ✅ < 500 行 |
| Select.tsx | xxx | ✅ < 500 行 |
| ... | ... | ... |

## 测试文件大小统计

| 测试文件 | 行数 | 状态 |
|---------|------|------|
| Form.test.tsx | xxx | ✅ < 1200 行 |
| ... | ... | ... |

## 发现的问题
- 无
```

- [ ] **Step 4: 提交扫描报告**

```bash
git add docs/final-scan/component-structure-scan.md
git commit -m "docs: 最终扫描 - 组件结构"
```

**Subagent 2 任务：扫描性能优化情况**

- [ ] **Step 1: 扫描 React.memo 使用情况**

```bash
grep -r "React.memo" frontend/src/shared/ui --include="*.tsx" | wc -l > /tmp/memo-count.txt
cat /tmp/memo-count.txt
```

Expected: 所有组件都使用了 React.memo

- [ ] **Step 2: 扫描 useCallback 使用情况**

```bash
grep -r "useCallback" frontend/src/shared/ui --include="*.tsx" | wc -l > /tmp/callback-count.txt
cat /tmp/callback-count.txt
```

Expected: 所有事件处理器都使用了 useCallback

- [ ] **Step 3: 扫描 useMemo 使用情况**

```bash
grep -r "useMemo" frontend/src/shared/ui --include="*.tsx" | wc -l > /tmp/memo-count.txt
cat /tmp/memo-count.txt
```

Expected: 所有计算属性都使用了 useMemo

- [ ] **Step 4: 生成扫描报告**

创建文件：`docs/final-scan/performance-optimization-scan.md`

```markdown
# 性能优化扫描报告

## React.memo 使用统计

- 总使用次数：xx 处
- 状态：✅ 所有组件已优化

## useCallback 使用统计

- 总使用次数：xx 处
- 状态：✅ 所有事件处理器已优化

## useMemo 使用统计

- 总使用次数：xx 处
- 状态：✅ 所有计算属性已优化

## 发现的问题
- 无
```

- [ ] **Step 5: 提交扫描报告**

```bash
git add docs/final-scan/performance-optimization-scan.md
git commit -m "docs: 最终扫描 - 性能优化"
```

**Subagent 3 任务：扫描测试覆盖率和质量**

- [ ] **Step 1: 生成测试覆盖率报告（分组）**

```bash
npm test -- --testPathPattern="shared/ui" --coverage --coverageReporters=html --maxWorkers=1
```

Expected: 覆盖率 ≥ 80%

- [ ] **Step 2: 检查测试文件组织**

```bash
# 检查是否所有组件都有对应的测试文件
find frontend/src/shared/ui -name "*.tsx" -type f | grep -v test | grep -v ".d.ts" | while read file; do
  testFile="${file%.tsx}.test.tsx"
  if [ ! -f "$testFile" ]; then
    echo "Missing test: $testFile"
  fi
done > /tmp/missing-tests.txt
cat /tmp/missing-tests.txt
```

Expected: 无缺失的测试文件

- [ ] **Step 3: 生成扫描报告**

创建文件：`docs/final-scan/test-coverage-scan.md`

```markdown
# 测试覆盖率扫描报告

## 覆盖率统计

- 总体覆盖率：xx%
- 状态：✅ 达标（≥ 80%）

## 测试文件完整性

- 组件总数：xx 个
- 有测试的组件：xx 个
- 缺失测试：xx 个
- 状态：✅ 所有组件都有测试

## 测试文件大小

| 测试文件 | 行数 | 状态 |
|---------|------|------|
| Form.test.tsx | xxx | ✅ < 1200 行 |
| ... | ... | ... |

## 发现的问题
- 无
```

- [ ] **Step 4: 提交扫描报告**

```bash
git add docs/final-scan/test-coverage-scan.md
git commit -m "docs: 最终扫描 - 测试覆盖率"
```

---

## 创建实施完成文档

- [ ] **Step 1: 创建实施完成文档**

创建文件：`docs/implementation-reports/2026-03-21-component-library-optimization-completed.md`

```markdown
# 组件库优化实施完成报告

## 1. 实施概览

- **实施时间**：2026-03-21
- **参与人员**：Aone Copilot
- **总耗时**：约 4 小时

## 2. 完成情况汇总

- ✅ **已完成任务**：所有 4 个阶段
- ⏳ **进行中任务**：0 个
- ❌ **未完成任务**：0 个
- 🔄 **需要后续跟进**：0 个

## 3. 各阶段完成情况

### 阶段 1：低风险清理

- **完成情况**：100%
- **主要成果**：
  - 删除了 BaseModal、Select（旧）、Table（旧）等 3 个废弃组件
  - 更新了 xx 个文件的导入路径
  - 所有测试通过

### 阶段 2：架构优化

- **完成情况**：100%
- **主要成果**：
  - 优化了 Table.tsx、Select.tsx 等 xx 个大文件
  - 重构了 Form.test.tsx 等测试文件的代码组织
  - 统一了组件目录结构

### 阶段 3：性能优化

- **完成情况**：100%
- **主要成果**：
  - 为 xx 个组件添加了 React.memo
  - 为 xx 个事件处理器添加了 useCallback
  - 为 xx 个计算属性添加了 useMemo

### 阶段 4：测试完善

- **完成情况**：100%
- **主要成果**：
  - 测试覆盖率从 xx% 提升到 xx%
  - 新增了 xx 个单元测试
  - 新增了 xx 个集成测试

## 4. 遇到的问题和解决方案

| 问题 | 影响 | 解决方案 | 状态 |
|------|------|---------|------|
| 无 | - | - | - |

## 5. 性能改进数据

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 平均渲染时间 | xx ms | xx ms | xx% |
| 测试覆盖率 | xx% | xx% | +xx% |
| 组件文件平均行数 | xx 行 | xx 行 | -xx% |

## 6. 最终扫描结果

### 组件结构扫描
- ✅ 所有组件文件 < 500 行
- ✅ 所有测试文件 < 1200 行
- ✅ 无残留废弃组件

### 性能优化扫描
- ✅ 所有组件使用 React.memo
- ✅ 所有事件处理器使用 useCallback
- ✅ 所有计算属性使用 useMemo

### 测试覆盖率扫描
- ✅ 总体覆盖率 ≥ 80%
- ✅ 所有组件都有对应测试
- ✅ 测试文件组织良好

## 7. 后续建议

- 建议 1：定期检查组件文件大小，避免文件过大
- 建议 2：持续监控测试覆盖率，保持 ≥ 80%
- 建议 3：定期审查性能优化效果，确保性能不下降

## 8. 附录

- 完整的任务清单
- 详细的测试报告
- 性能对比数据
```

- [ ] **Step 2: 提交实施完成文档**

```bash
git add docs/implementation-reports/2026-03-21-component-library-optimization-completed.md
git commit -m "docs: 组件库优化实施完成报告"
```

- [ ] **Step 3: 推送到 GitHub**

```bash
git push origin main
```

Expected: 成功推送到 GitHub 远程仓库

---

## 计划完成

**Plan complete and saved to `docs/superpowers/plans/2026-03-21-component-library-optimization.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
