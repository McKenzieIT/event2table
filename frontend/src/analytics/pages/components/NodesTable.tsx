import { Button } from "@shared/ui";
import Table from "@shared/ui/components/Table";
import type { TableColumn } from "@shared/ui/components/Table";
import React from "react";
import { Link } from "react-router-dom";

/**
 * 节点数据类型
 */
interface NodeData {
  id: string;
  [key: string]: unknown;
}

/**
 * 节点表格组件
 * 展示事件节点列表，支持分页和排序
 * 
 * 注意：此组件接收 TanStack Table 实例，用于高级表格功能
 * 如果只需要简单展示数据，可以使用 data + columns props
 */
function NodesTable({
  table,
  isLoading,
  empty,
}: {
  table: any;
  isLoading: boolean;
  empty: boolean;
}) {
  if (isLoading) {
    return (
      <div className="glass-card text-center p-5">
        <div className="spinner-border" role="status"></div>
        <p className="mt-3 text-muted">加载事件节点中...</p>
      </div>
    );
  }

  if (empty) {
    return (
      <div className="glass-card text-center p-5">
        <i className="bi bi-diagram-3 display-4 text-muted d-block mb-3"></i>
        <h3 className="mt-3 text-muted">暂无事件节点</h3>
        <p className="text-muted">您还没有创建任何事件节点</p>
        <Link to="/event-node-builder">
          <Button variant="primary">
            创建第一个节点
          </Button>
        </Link>
      </div>
    );
  }

  // 从 TanStack Table 实例提取数据和列定义
  const data = table.getRowModel().rows.map((row: any) => {
    const rowData: Record<string, unknown> = { id: row.id };
    row.getVisibleCells().forEach((cell: any) => {
      rowData[cell.column.id] = cell.getValue();
    });
    return rowData;
  });

  const columns: TableColumn<NodeData>[] = table.getAllColumns().map((column: any) => ({
    id: column.id,
    header: column.columnDef.header,
    accessorKey: column.id,
    size: column.getSize(),
    cell: (info: { getValue: () => unknown; row: { id: string } }) => {
      const cellDef = column.columnDef.cell;
      if (cellDef instanceof Function) {
        // 对于函数类型的 cell，需要从原始 table 实例渲染
        const row = table.getRowModel().rows.find((r: any) => r.id === info.row.id);
        if (row) {
          const cell = row.getVisibleCells().find((c: any) => c.column.id === column.id);
          if (cell) {
            return cellDef(cell.getContext());
          }
        }
      }
      return String(info.getValue() ?? '');
    },
  }));

  return (
    <div className="glass-card">
      <div className="table-responsive">
        <Table
          data={data}
          columns={columns}
          variant="bordered"
          size="md"
          striped
          hoverable
          pagination={false}
        />
      </div>

      {/* 分页 */}
      <div className="d-flex justify-content-between align-items-center p-3 border-top">
        <span className="text-muted">
          共 {table.getFilteredRowModel().rows.length} 条记录
        </span>
        <div className="d-flex gap-2">
          <Button
            variant="outline-secondary"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
          >
            首页
          </Button>
          <Button
            variant="outline-secondary"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            上一页
          </Button>
          <span className="btn btn-light disabled">
            {table.getState().pagination.pageIndex + 1} / {table.getPageCount()}
          </span>
          <Button
            variant="outline-secondary"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            下一页
          </Button>
          <Button
            variant="outline-secondary"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
          >
            末页
          </Button>
        </div>
      </div>
    </div>
  );
}

export default React.memo(NodesTable);
