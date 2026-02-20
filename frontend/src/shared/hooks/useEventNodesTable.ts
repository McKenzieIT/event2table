// @ts-nocheck - TypeScript检查暂禁用
/**
 * 事件节点表格Hook
 * Event Nodes Table Hook
 *
 * 使用TanStack Table管理事件节点表格状态
 */

import { useState, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  createColumnHelper,
  SortingState,
  ColumnFiltersState,
} from '@tanstack/react-table';
import type { EventNode } from '@shared/types/eventNodes';

/**
 * 列定义类型
 */
export type EventNodesColumnDef = ReturnType<typeof createColumnHelper<EventNode>>['_inferColumnDef'];

/**
 * 事件节点表格Hook
 *
 * @param data - 事件节点数据
 * @param columns - 列定义
 * @returns 表格实例和辅助方法
 */
export function useEventNodesTable(
  data: EventNode[],
  columns: EventNodesColumnDef[]
) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'created_at', desc: true },
  ]);
  const [rowSelection, setRowSelection] = useState({});

  // 初始化表格
  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      rowSelection,
    },
    onSortingChange: setSorting,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    enableRowSelection: true,
    meta: {
      // 存储额外的meta信息
      updateData: (rowIndex: number, columnId: string, value: unknown) => {
        // TODO: 实现数据更新逻辑
        console.log('updateData called:', rowIndex, columnId, value);
      },
    },
  });

  // 计算选中的行
  const selectedRows = useMemo(() => {
    return table.getFilteredSelectedRowModel().flatRows;
  }, [table]);

  // 选中的节点ID列表
  const selectedIds = useMemo(() => {
    return selectedRows.map(row => row.original.id);
  }, [selectedRows]);

  // 选中数量
  const selectedCount = selectedRows.length;

  // 是否全选
  const isAllRowsSelected = table.getIsAllRowsSelected();
  const isSomeRowsSelected = table.getIsSomeRowsSelected();

  // 全选/取消全选
  const toggleAllRowsSelected = () => {
    table.toggleAllRowsSelected(!isAllRowsSelected);
  };

  // 清除选择
  const clearSelection = () => {
    table.resetRowSelection();
  };

  return {
    table,
    selectedRows,
    selectedIds,
    selectedCount,
    isAllRowsSelected,
    isSomeRowsSelected,
    toggleAllRowsSelected,
    clearSelection,
    sorting,
  };
}
