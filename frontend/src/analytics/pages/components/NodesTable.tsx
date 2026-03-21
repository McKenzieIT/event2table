import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@shared/ui";
import Table from "@shared/ui/components/Table";

/**
 * 节点表格组件
 * 展示事件节点列表，支持分页和排序
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

  return (
    <div className="glass-card">
      <div className="table-responsive">
        <Table variant="bordered" size="md" striped hoverable>
          <Table.Header>
            {table.getHeaderGroups().map((headerGroup: any) => (
              <Table.Row key={headerGroup.id}>
                {headerGroup.headers.map((header: any) => (
                  <Table.Head key={header.id} style={{ width: header.getSize() }}>
                    {header.isPlaceholder ? null : (
                      <div
                        className={
                          header.column.getCanSort()
                            ? "cursor-pointer user-select-none"
                            : ""
                        }
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {header.column.columnDef.header instanceof Function
                          ? header.column.columnDef.header(header.getContext())
                          : header.column.columnDef.header.toString()}
                        {header.column.getIsSorted() && (
                          <i
                            className={`bi bi-arrow-${header.column.getIsSorted() === "asc" ? "up" : "down"} ms-1`}
                          ></i>
                        )}
                      </div>
                    )}
                  </Table.Head>
                ))}
              </Table.Row>
            ))}
          </Table.Header>
          <Table.Body>
            {table.getRowModel().rows.map((row: any) => (
              <Table.Row key={row.id}>
                {row.getVisibleCells().map((cell: any) => (
                  <Table.Cell key={cell.id}>
                    {cell.column.columnDef.cell instanceof Function
                      ? cell.column.columnDef.cell(cell.getContext())
                      : String(cell.column.columnDef.cell)}
                  </Table.Cell>
                ))}
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
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
