/**
 * 事件节点表格列定义
 * Event Nodes Table Column Definitions
 */

import { createColumnHelper } from '@tanstack/react-table';
import type { EventNode } from '@shared/types/eventNodes';
import type { EventNodesColumnDef } from '@shared/hooks/useEventNodesTable';

const columnHelper = createColumnHelper<EventNode>();

/**
 * 创建事件节点表格列定义
 *
 * @param callbacks - 操作回调函数
 * @returns 列定义数组
 */
export function createEventNodesColumns(callbacks: {
  onViewHql: (nodeId: number) => void;
  onQuickEdit: (nodeId: number) => void;
  onEditInBuilder: (nodeId: number) => void;
  onCopy: (nodeId: number) => void;
  onDelete: (nodeId: number) => void;
  onViewFields: (nodeId: number) => void;
}): EventNodesColumnDef[] {
  return [
    // 选择列
    columnHelper.display({
      id: 'select',
      header: ({ table }) => (
        <input
          type="checkbox"
          className="form-check-input"
          checked={table.getIsAllRowsSelected()}
          onChange={table.getToggleAllRowsSelectedHandler()}
          aria-label="全选所有节点"
        />
      ),
      cell: ({ row }) => (
        <input
          type="checkbox"
          className="form-check-input"
          checked={row.getIsSelected()}
          onChange={row.getToggleSelectedHandler()}
          aria-label={`选择节点 ${row.original.name_en || row.original.name_cn}`}
        />
      ),
      enableSorting: false,
      enableHiding: false,
      size: 50,
    }),

    // 节点名称（英文）
    columnHelper.accessor('name_en', {
      id: 'name_en',
      header: '节点名称',
      cell: info => (
        <code className="text-primary" style={{ fontSize: '0.9em' }}>
          {info.getValue()}
        </code>
      ),
      size: 200,
    }),

    // 中文名称
    columnHelper.accessor('name_cn', {
      id: 'name_cn',
      header: '中文名称',
      size: 180,
    }),

    // 关联事件
    columnHelper.accessor(
      row => `${row.event_name || '未关联'} (${row.event_name_cn || '-'})`,
      {
        id: 'event',
        header: '关联事件',
        size: 250,
      }
    ),

    // 字段数
    columnHelper.accessor('field_count', {
      id: 'field_count',
      header: '字段数',
      cell: info => (
        <button
          className="btn btn-sm btn-link p-0 text-decoration-none"
          onClick={() => callbacks.onViewFields(info.row.original.id)}
        >
          <i className="bi bi-list-check me-1"></i>
          {info.getValue()}
        </button>
      ),
      size: 100,
    }),

    // 创建时间
    columnHelper.accessor('created_at', {
      id: 'created_at',
      header: '创建时间',
      cell: info => {
        const date = new Date(info.getValue());
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        });
      },
      size: 160,
    }),

    // 操作列
    columnHelper.display({
      id: 'actions',
      header: '操作',
      cell: ({ row }) => (
        <div className="dropdown">
          <button
            className="btn btn-sm btn-light dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <i className="bi bi-three-dots-vertical"></i>
          </button>
          <ul className="dropdown-menu">
            <li>
              <button
                className="dropdown-item"
                onClick={() => callbacks.onViewHql(row.original.id)}
              >
                <i className="bi bi-code me-2 text-primary"></i>
                查看HQL
              </button>
            </li>
            <li>
              <button
                className="dropdown-item"
                onClick={() => callbacks.onViewFields(row.original.id)}
              >
                <i className="bi bi-list-check me-2 text-info"></i>
                字段列表
              </button>
            </li>
            <li>
              <button
                className="dropdown-item"
                onClick={() => callbacks.onQuickEdit(row.original.id)}
              >
                <i className="bi bi-pencil me-2 text-warning"></i>
                快速编辑
              </button>
            </li>
            <li>
              <button
                className="dropdown-item"
                onClick={() => callbacks.onEditInBuilder(row.original.id)}
              >
                <i className="bi bi-diagram-3 me-2 text-success"></i>
                构建器编辑
              </button>
            </li>
            <li>
              <button
                className="dropdown-item"
                onClick={() => callbacks.onCopy(row.original.id)}
              >
                <i className="bi bi-copy me-2"></i>
                复制配置
              </button>
            </li>
            <li><hr className="dropdown-divider" /></li>
            <li>
              <button
                className="dropdown-item text-danger"
                onClick={() => callbacks.onDelete(row.original.id)}
              >
                <i className="bi bi-trash me-2"></i>
                删除
              </button>
            </li>
          </ul>
        </div>
      ),
      enableSorting: false,
      size: 80,
    }),
  ];
}
