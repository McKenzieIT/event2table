/**
 * Table Component Examples
 * 
 * 展示 Table 组件的各种用法
 */

import { Table, type TableColumn } from '@shared/ui';
import React, { useState } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
  age: number;
  status: 'active' | 'inactive';
  role: string;
  createdAt: string;
}

const basicColumns: TableColumn<User>[] = [
  { accessorKey: 'id', header: 'ID', width: 80 },
  { accessorKey: 'name', header: '姓名', width: 150 },
  { accessorKey: 'email', header: '邮箱', width: 200 },
  { accessorKey: 'age', header: '年龄', width: 100 },
  { accessorKey: 'status', header: '状态', width: 100 },
];

const sampleUsers: User[] = [
  { id: 1, name: '张三', email: 'zhangsan@example.com', age: 28, status: 'active', role: '开发者', createdAt: '2024-01-15' },
  { id: 2, name: '李四', email: 'lisi@example.com', age: 32, status: 'active', role: '设计师', createdAt: '2024-02-20' },
  { id: 3, name: '王五', email: 'wangwu@example.com', age: 25, status: 'inactive', role: '产品经理', createdAt: '2024-03-10' },
  { id: 4, name: '赵六', email: 'zhaoliu@example.com', age: 30, status: 'active', role: '测试工程师', createdAt: '2024-04-05' },
  { id: 5, name: '钱七', email: 'qianqi@example.com', age: 27, status: 'active', role: '运维工程师', createdAt: '2024-05-12' },
];

const largeDataset: User[] = Array.from({ length: 100 }, (_, i) => ({
  id: i + 1,
  name: `用户${i + 1}`,
  email: `user${i + 1}@example.com`,
  age: 20 + (i % 30),
  status: i % 3 === 0 ? 'inactive' : 'active',
  role: ['开发者', '设计师', '产品经理', '测试工程师', '运维工程师'][i % 5],
  createdAt: new Date(2024, 0, 1 + i).toISOString().split('T')[0],
}));

export function TableBasicExample() {
  return (
    <div className="example-section">
      <h3>基础用法</h3>
      <Table
        data={sampleUsers}
        columns={basicColumns}
        pagination={false}
      />
    </div>
  );
}

export function TablePaginationExample() {
  return (
    <div className="example-section">
      <h3>分页表格</h3>
      <Table
        data={largeDataset}
        columns={basicColumns}
        pagination={true}
        pageSize={10}
        pageSizeOptions={[5, 10, 20, 50]}
      />
    </div>
  );
}

export function TableSortingExample() {
  return (
    <div className="example-section">
      <h3>可排序表格</h3>
      <Table
        data={largeDataset}
        columns={basicColumns}
        sortable={true}
        pagination={true}
        pageSize={10}
      />
    </div>
  );
}

export function TableSelectableExample() {
  const [selectedRows, setSelectedRows] = useState<User[]>([]);

  const handleSelectionChange = (rows: object[]) => {
    setSelectedRows(rows as User[]);
  };

  return (
    <div className="example-section">
      <h3>可选择的表格</h3>
      <Table
        data={sampleUsers}
        columns={basicColumns}
        selectable={true}
        onSelectionChange={handleSelectionChange}
        pagination={false}
      />
      <div className="selected-info">
        <strong>已选择 {selectedRows.length} 行</strong>
        {selectedRows.length > 0 && (
          <div className="selected-details">
            {selectedRows.map(row => row.name).join(', ')}
          </div>
        )}
      </div>
    </div>
  );
}

export function TableVirtualScrollExample() {
  return (
    <div className="example-section">
      <h3>虚拟滚动（大数据量）</h3>
      <Table
        data={largeDataset}
        columns={basicColumns}
        virtual={true}
        maxHeight={400}
        pagination={false}
      />
      <div className="table-info">
        共 {largeDataset.length} 条数据，使用虚拟滚动优化性能
      </div>
    </div>
  );
}

export function TableCustomCellExample() {
  const customColumns: TableColumn<User>[] = [
    { accessorKey: 'id', header: 'ID', width: 80 },
    { accessorKey: 'name', header: '姓名', width: 150 },
    { 
      accessorKey: 'status', 
      header: '状态', 
      width: 120,
      cellRenderer: ({ value }: { value: string }) => (
        <span className={`status-badge status-${value}`}>
          {value === 'active' ? '活跃' : '非活跃'}
        </span>
      )
    },
    { 
      accessorKey: 'role', 
      header: '角色', 
      width: 150,
      cellRenderer: ({ value }) => (
        <span className="role-badge">{value}</span>
      )
    },
    { accessorKey: 'createdAt', header: '创建时间', width: 150 },
  ];

  return (
    <div className="example-section">
      <h3>自定义单元格渲染</h3>
      <Table
        data={sampleUsers}
        columns={customColumns}
        pagination={false}
      />
    </div>
  );
}

export function TableEditableExample() {
  const [data, setData] = useState<User[]>(sampleUsers);

  const handleEdit = (row: object, columnId: string, value: unknown) => {
    const userRow = row as User;
    setData(prev => prev.map(item => 
      item.id === userRow.id ? { ...item, [columnId]: value } : item
    ));
  };

  const editableColumns: TableColumn<User>[] = [
    { accessorKey: 'id', header: 'ID', width: 80, editable: false },
    { accessorKey: 'name', header: '姓名', width: 150, editable: true },
    { accessorKey: 'email', header: '邮箱', width: 200, editable: true },
    { accessorKey: 'age', header: '年龄', width: 100, editable: true },
    { accessorKey: 'status', header: '状态', width: 100, editable: true },
  ];

  return (
    <div className="example-section">
      <h3>可编辑表格</h3>
      <p className="example-hint">双击单元格进行编辑</p>
      <Table
        data={data}
        columns={editableColumns}
        editable={true}
        onEdit={handleEdit}
        pagination={false}
      />
    </div>
  );
}

export function TableVariantExample() {
  return (
    <div className="example-section">
      <h3>不同变体</h3>
      <div className="table-variants">
        <div className="variant-item">
          <h4>默认样式</h4>
          <Table
            data={sampleUsers.slice(0, 3)}
            columns={basicColumns}
            variant="default"
            pagination={false}
          />
        </div>
        <div className="variant-item">
          <h4>紧凑样式</h4>
          <Table
            data={sampleUsers.slice(0, 3)}
            columns={basicColumns}
            variant="compact"
            size="sm"
            pagination={false}
          />
        </div>
      </div>
    </div>
  );
}

export function TableLoadingExample() {
  const [loading, setLoading] = useState(false);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <div className="example-section">
      <h3>加载状态</h3>
      <div className="loading-controls">
        <button onClick={handleRefresh}>刷新数据</button>
      </div>
      <Table
        data={sampleUsers}
        columns={basicColumns}
        loading={loading}
        pagination={false}
      />
    </div>
  );
}

export function TableBestPractices() {
  return (
    <div className="example-section">
      <h3>最佳实践</h3>
      <div className="best-practices">
        <div className="practice-item">
          <h4>1. 小数据集禁用分页</h4>
          <Table
            data={sampleUsers}
            columns={basicColumns}
            pagination={false}
          />
        </div>
        <div className="practice-item">
          <h4>2. 大数据集使用虚拟滚动</h4>
          <Table
            data={largeDataset}
            columns={basicColumns}
            virtual={true}
            maxHeight={300}
            pagination={false}
          />
        </div>
        <div className="practice-item">
          <h4>3. 提供合适的分页选项</h4>
          <Table
            data={largeDataset}
            columns={basicColumns}
            pagination={true}
            pageSize={10}
            pageSizeOptions={[5, 10, 20, 50]}
          />
        </div>
        <div className="practice-item">
          <h4>4. 使用自定义渲染增强可读性</h4>
          <Table
            data={sampleUsers}
            columns={[
              { accessorKey: 'name', header: '姓名' },
              { 
                accessorKey: 'status', 
                header: '状态',
                cellRenderer: ({ value }) => (
                  <span className={`status-badge status-${value}`}>
                    {value === 'active' ? '活跃' : '非活跃'}
                  </span>
                )
              },
            ]}
            pagination={false}
          />
        </div>
        <div className="practice-item">
          <h4>5. 需要选择时启用行选择</h4>
          <Table
            data={sampleUsers}
            columns={basicColumns}
            selectable={true}
            pagination={false}
          />
        </div>
      </div>
    </div>
  );
}

export default function TableExamples() {
  return (
    <div className="examples-container">
      <h2>Table 组件示例</h2>
      <TableBasicExample />
      <TablePaginationExample />
      <TableSortingExample />
      <TableSelectableExample />
      <TableVirtualScrollExample />
      <TableCustomCellExample />
      <TableEditableExample />
      <TableVariantExample />
      <TableLoadingExample />
      <TableBestPractices />
    </div>
  );
}
