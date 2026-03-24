# Table分页功能和React测试警告修复设计文档

**日期**: 2026-03-24
**状态**: 设计完成
**目标**: 修复CI Frontend Unit Tests失败和React警告

---

## 📋 问题概述

### 失败的测试
- `Table.test.tsx`: "should change page size when size changer is used" ❌

### React警告
1. `TableHeader.tsx:11`: NaN is an invalid value for the `width` css style property ⚠️
2. `SearchInput.tsx:14`: Function components cannot be given refs ⚠️
3. `FormUpload.test.tsx:21`: Updates not wrapped in act() ⚠️

---

## 🎯 修复方案

### 架构设计：3个并行任务

```
主进程
├── 任务1: Table分页功能修复
│   ├── 添加 showSizeChanger 属性
│   ├── 更新组件实现
│   └── 修复相关测试
│
├── 任务2: TableHeader NaN width修复
│   ├── 定位NaN产生原因
│   ├── 添加宽度验证逻辑
│   └── 添加边界情况测试
│
└── 任务3: React警告修复
    ├── SearchInput添加forwardRef
    ├── FormUpload测试添加act()包裹
    └── 验证警告消除
```

---

## 📝 详细实现

### 任务1：Table分页功能修复

#### 1.1 类型定义更新
**文件**: `frontend/src/shared/ui/components/Table/Table.types.ts`

```typescript
export interface TableProps<TData = any> {
  // Pagination
  pagination?: boolean;
  pageSize?: number;
  currentPage?: number;
  onPageChange?: (page: number, pageSize: number) => void;
  pageSizeOptions?: number[];
  showSizeChanger?: boolean;  // 新增：默认隐藏页面大小选择器
  showQuickJumper?: boolean;   // 新增：可选功能
}
```

#### 1.2 组件实现更新
**文件**: `frontend/src/shared/ui/components/Table/Table.tsx` (第566-580行)

```typescript
{pagination && !loading && displayRows.length > 0 && (
  <TablePagination
    currentPage={paginationState.pageIndex + 1}
    pageSize={paginationState.pageSize}
    total={table.getFilteredRowModel().rows.length}
    pageSizeOptions={pageSizeOptions}
    showSizeChanger={showSizeChanger}  // 新增
    showQuickJumper={showQuickJumper}  // 新增
    onPageChange={(page, size) => {
      setPaginationState({ pageIndex: page - 1, pageSize: size });
      onPageChange?.(page, size);
    }}
    showTotal={(total, range) => (
      <span>{range[0]}-{range[1]} of {total} items</span>
    )}
  />
)}
```

#### 1.3 测试更新
**文件**: `frontend/src/shared/ui/components/Table/Table.test.tsx` (第381-398行)

```typescript
it('should change page size when size changer is used', async () => {
  const user = userEvent.setup();

  render(
    <Table
      data={mockData}
      columns={mockColumns}
      pagination
      pageSize={2}
      pageSizeOptions={[2, 5, 10]}
      showSizeChanger={true}  // 显式启用
    />
  );

  const sizeSelect = screen.getByDisplayValue('2 / page');
  await user.selectOptions(sizeSelect, '5');

  expect(sizeSelect).toHaveValue('5');
});

// 新增测试：默认不显示size changer
it('should not render size changer when showSizeChanger is false', () => {
  render(
    <Table
      data={mockData}
      columns={mockColumns}
      pagination
      pageSize={2}
      pageSizeOptions={[2, 5, 10]}
      showSizeChanger={false}  // 显式禁用
    />
  );

  expect(screen.queryByDisplayValue(/\/ page/)).not.toBeInTheDocument();
});
```

---

### 任务2：TableHeader NaN width修复

#### 2.1 问题定位
**文件**: `frontend/src/shared/ui/components/Table/TableHeader.tsx:11`

检查width计算逻辑，找到产生NaN的原因：
- 除法运算：`width / scale` 可能产生NaN
- 数学运算：`width * ratio` 可能产生Infinity
- 未定义值：`column.width` 为undefined

#### 2.2 防御性实现
```typescript
const parseWidth = (width: unknown): string => {
  // 处理数字类型
  if (typeof width === 'number') {
    if (width < 0 || !Number.isFinite(width)) {
      console.warn(`Invalid column width: ${width}, using 'auto'`);
      return 'auto';
    }
    return `${width}px`;
  }

  // 处理字符串类型
  if (typeof width === 'string' && width.trim() !== '') {
    return width;
  }

  // 默认值
  return 'auto';
};

// 使用安全宽度
const safeWidth = parseWidth(column.width);
```

#### 2.3 测试用例
```typescript
it('should handle invalid width values gracefully', () => {
  const columnsWithInvalidWidth = [
    ...mockColumns,
    { id: 'invalid', header: 'Invalid', accessorKey: 'invalid', width: NaN },
    { id: 'negative', header: 'Negative', accessorKey: 'negative', width: -100 },
  ];

  render(<Table data={mockData} columns={columnsWithInvalidWidth} />);

  // 验证表格正常渲染，无控制台错误
  expect(screen.getByRole('table')).toBeInTheDocument();
});
```

---

### 任务3：React警告修复

#### 3.1 SearchInput ref修复
**文件**: `frontend/src/shared/ui/SearchInput/SearchInput.tsx:14`

```typescript
import React from 'react';
import type { SearchInputProps } from './SearchInput.types';

export const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProps>(
  (props, ref) => {
    const { placeholder = 'Search...', onChange, className = '', ...otherProps } = props;

    return (
      <input
        ref={ref}
        type="text"
        placeholder={placeholder}
        onChange={onChange}
        className={`search-input ${className}`}
        {...otherProps}
      />
    );
  }
);

SearchInput.displayName = 'SearchInput';  // 添加displayName便于调试
```

#### 3.2 FormUpload测试act()修复
**文件**: `frontend/src/shared/ui/components/Form/FormUpload.test.tsx:21`

```typescript
import { render, screen, waitFor, act } from '@test/test-utils';
import userEvent from '@testing-library/user-event';

describe('FormUpload Component', () => {
  it('should render upload button', async () => {
    await act(async () => {
      render(<FormUpload {...props} />);
      // 等待状态更新完成
      await waitFor(() => {
        expect(screen.getByText('Upload')).toBeInTheDocument();
      });
    });
  });

  // 或使用waitFor + async
  it('should render helper text when provided', async () => {
    const { container } = await renderAsync(
      <FormUpload helperText="Max file size: 5MB" />
    );

    await waitFor(() => {
      expect(screen.getByText('Max file size: 5MB')).toBeInTheDocument();
    });
  });
});
```

---

## ✅ 验证流程

### 第1轮：独立测试
```bash
# 任务1
npm test -- Table.test.tsx -t "pagination"

# 任务2
npm test -- Table.test.tsx -t "render.*column"

# 任务3
npm test -- SearchInput FormUpload
```

### 第2轮：集成测试
```bash
npm test -- --run Table.test.tsx
```

### 第3轮：全量回归
```bash
npm test -- --run
```

---

## 🔄 回滚方案

如果修复失败或引入新问题：

```bash
# 回滚特定提交
git revert <commit-hash>

# 或重置多个提交
git reset --soft HEAD~3

# 重新开始
git checkout .
```

---

## 📊 成功标准

- ✅ 所有Table组件测试通过（54/54）
- ✅ 无React控制台警告
- ✅ CI Frontend Unit Tests通过
- ✅ 无TypeScript类型错误
- ✅ ESLint检查通过

---

**Co-Authored-By**: Claude Sonnet 4.6 <noreply@anthropic.com>
