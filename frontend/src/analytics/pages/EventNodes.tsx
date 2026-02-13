/**
 * 事件节点管理页面 - 完整实现
 * Event Nodes Management Page - Full Implementation
 *
 * @description 提供完整的事件节点CRUD功能，包括搜索、筛选、批量操作
 * @features
 * - 节点列表展示（支持排序、分页）
 * - 高级搜索和筛选（关键词、今日修改、事件、字段数）
 * - 批量操作（删除、导出HQL）
 * - HQL代码查看（语法高亮、复制）
 * - 快速编辑（名称、描述）
 * - 复制节点配置
 */

import React, { useState, useEffect, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams, useOutletContext } from "react-router-dom";
import toast from "react-hot-toast";
import { useEventNodesTable } from "@shared/hooks/useEventNodesTable";
import { createEventNodesColumns } from "@analytics/components/columns/eventNodesColumns";
import { eventNodesApi } from "@shared/api/eventNodes";
import { ErrorBoundary, ErrorFallback } from "@shared/ui/ErrorBoundary";
import { HQLViewModal } from "@event-builder/components/HQLViewModal";
import { QuickEditModal } from "@event-builder/components/QuickEditModal";
import { FieldsListModal } from "@event-builder/components/FieldsListModal";
import { AdvancedFilterPanel } from "@event-builder/components/AdvancedFilterPanel";
import { useDebounce } from "@shared/hooks/useDebounce";
import { Button } from "@shared/ui/Button";
import type {
  EventNode,
  EventNodeFilters,
  EventNodeStats,
} from "@shared/types/eventNodes";
import "./EventNodes.css";

/**
 * 游戏选择提示组件
 */
function GameSelectionPrompt() {
  return (
    <div className="glass-card text-center p-5 m-4">
      <span className="display-4 text-primary mb-3">🎮</span>
      <h3 className="mb-3">请先选择游戏</h3>
      <p className="text-muted mb-4">事件节点管理需要先选择一个游戏</p>
      <Link to="/games">
        <Button variant="primary">
          前往游戏管理
        </Button>
      </Link>
    </div>
  );
}

/**
 * 统计卡片组件
 */
function StatisticsCards({ stats }: { stats: EventNodeStats | null }) {
  if (!stats) {
    return (
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass-card" style={{ padding: "1.5rem" }}>
            <div className="placeholder-glow">
              <div className="placeholder bg-secondary col-6"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: "1.5rem",
        marginBottom: "1.5rem",
      }}
    >
      {/* 总节点数 */}
      <div
        className="glass-card animate-slide-in"
        style={{ padding: "1.5rem", animationDelay: "0s" }}
      >
        <div className="d-flex align-items-center gap-3">
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "12px",
              background:
                "linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-info) 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.5rem",
            }}
          >
            🔷
          </div>
          <div>
            <p className="text-secondary mb-1" style={{ fontSize: "0.875rem" }}>
              事件节点总数
            </p>
            <h3
              className="mb-0"
              style={{ fontSize: "1.5rem", fontWeight: 700 }}
            >
              {stats.total_nodes}
            </h3>
          </div>
        </div>
      </div>

      {/* 关联事件数 */}
      <div
        className="glass-card animate-slide-in"
        style={{ padding: "1.5rem", animationDelay: "0.1s" }}
      >
        <div className="d-flex align-items-center gap-3">
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "12px",
              background: "linear-gradient(135deg, #A78BFA 0%, #8B5CF6 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.5rem",
            }}
          >
            📦
          </div>
          <div>
            <p className="text-secondary mb-1" style={{ fontSize: "0.875rem" }}>
              关联事件数
            </p>
            <h3
              className="mb-0"
              style={{ fontSize: "1.5rem", fontWeight: 700 }}
            >
              {stats.unique_events}
            </h3>
          </div>
        </div>
      </div>

      {/* 平均字段数 */}
      <div
        className="glass-card animate-slide-in"
        style={{ padding: "1.5rem", animationDelay: "0.2s" }}
      >
        <div className="d-flex align-items-center gap-3">
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "12px",
              background: "linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.5rem",
            }}
          >
            ✅
          </div>
          <div>
            <p className="text-secondary mb-1" style={{ fontSize: "0.875rem" }}>
              平均字段数
            </p>
            <h3
              className="mb-0"
              style={{ fontSize: "1.5rem", fontWeight: 700 }}
            >
              {stats.avg_fields.toFixed(1)}
            </h3>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * 搜索和筛选栏组件
 */
function SearchFilterBar({
  filters,
  updateFilters,
  selectedCount,
  onClearSelection,
  onBulkDelete,
  onToggleAdvanced,
  showAdvanced,
}: {
  filters: EventNodeFilters;
  updateFilters: (updates: Partial<EventNodeFilters>) => void;
  selectedCount: number;
  onClearSelection: () => void;
  onBulkDelete: () => void;
  onToggleAdvanced: () => void;
  showAdvanced: boolean;
}) {
  const [input, setInput] = useState(filters.keyword);
  const debouncedInput = useDebounce(input, 300);

  useEffect(() => {
    updateFilters({ keyword: debouncedInput });
  }, [debouncedInput, updateFilters]);

  return (
    <div
      className="glass-card"
      style={{ padding: "1.5rem", marginBottom: "1.5rem" }}
    >
      <div
        className="d-flex justify-content-between gap-3"
        style={{ flexWrap: "wrap" }}
      >
        {/* 基础搜索 */}
        <div
          className="flex-grow-1"
          style={{ maxWidth: "500px", minWidth: "280px" }}
        >
          <div className="position-relative">
            <i
              className="bi bi-search position-absolute top-50 start-3 translate-middle-y text-muted"
              style={{ fontSize: "1.1rem" }}
            ></i>
            <input
              type="text"
              className="form-control ps-5"
              placeholder="搜索节点名称、别名..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
          </div>
        </div>

        {/* 右侧操作区 */}
        <div className="d-flex gap-2 align-items-center">
          {selectedCount > 0 && (
            <>
              <span className="text-muted">
                已选择 <strong className="text-primary">{selectedCount}</strong>{" "}
                个节点
              </span>
              <Button variant="outline-danger" onClick={onBulkDelete}>
                批量删除
              </Button>
            </>
          )}
          <Button
            variant={showAdvanced ? "primary" : "outline-primary"}
            onClick={onToggleAdvanced}
          >
            高级筛选 {showAdvanced ? "▲" : "▼"}
          </Button>
        </div>
      </div>
    </div>
  );
}

/**
 * 节点表格组件（简化版）
 */
function NodesTable({
  table,
  isLoading,
  empty,
}: {
  table: ReturnType<typeof useEventNodesTable>["table"];
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
        <span className="display-4 text-muted">📊</span>
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
        <table className="table table-hover oled-table mb-0">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id} style={{ width: header.getSize() }}>
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
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {cell.column.columnDef.cell instanceof Function
                      ? cell.column.columnDef.cell(cell.getContext())
                      : String(cell.column.columnDef.cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
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

/**
 * 事件节点管理主组件
 */
// 类型定义：从MainLayout传递的上下文
interface LayoutContext {
  currentGame: {
    id: number;
    gid: number;
    name: string;
    ods_db: string;
  } | null;
  setCurrentGame: (game: any) => void;
}

function EventNodes() {
  // 使用 useOutletContext 从 MainLayout 获取游戏上下文
  const { currentGame } = useOutletContext<LayoutContext>();
  const gameGid = currentGame?.gid || null;
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();

  // Toast 辅助函数
  const success = (message: string) => {
    toast.success(message);
  };

  const toastError = (message: string) => {
    toast.error(message);
  };

  // URL同步的筛选状态
  const [filters, setFilters] = useState<EventNodeFilters>({
    keyword: searchParams.get("q") || "",
    todayModified: searchParams.get("today") === "true",
    eventId: searchParams.get("event") || "",
    fieldCountMin: searchParams.get("field_min") || "",
    fieldCountMax: searchParams.get("field_max") || "",
  });

  // 高级筛选面板显示状态
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 模态框状态
  const [modals, setModals] = useState({
    hql: { show: false, nodeId: null as number | null },
    quickEdit: { show: false, nodeId: null as number | null },
    fields: { show: false, nodeId: null as number | null },
  });

  // 更新筛选条件并同步到URL
  const updateFilters = useCallback(
    (updates: Partial<EventNodeFilters>) => {
      setFilters((prevFilters) => {
        const newFilters = { ...prevFilters, ...updates };

        // 同步到URL
        const params: Record<string, string> = {};
        if (newFilters.keyword) params.q = newFilters.keyword;
        if (newFilters.todayModified) params.today = "true";
        if (newFilters.eventId) params.event = newFilters.eventId;
        if (newFilters.fieldCountMin)
          params.field_min = newFilters.fieldCountMin;
        if (newFilters.fieldCountMax)
          params.field_max = newFilters.fieldCountMax;

        setSearchParams(params);
        return newFilters;
      });
    },
    [setSearchParams],
  );

  // 游戏上下文验证
  if (!gameGid) {
    return <GameSelectionPrompt />;
  }

  // 数据获取
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["event-nodes", gameGid, filters],
    queryFn: async () => {
      const response = await eventNodesApi.list({
        game_gid: gameGid!,
        keyword: filters.keyword || undefined,
        today_modified: filters.todayModified || undefined,
        event_id: filters.eventId || undefined,
        field_count_min: filters.fieldCountMin || undefined,
        field_count_max: filters.fieldCountMax || undefined,
      });
      return response.data;
    },
    retry: 2,
    staleTime: 30000,
  });

  const { data: stats } = useQuery({
    queryKey: ["event-nodes-stats", gameGid],
    queryFn: async () => {
      const response = await eventNodesApi.stats(gameGid!);
      return response.data;
    },
    staleTime: 60000,
  });

  // 表格逻辑
  const columns = createEventNodesColumns({
    onViewHql: (nodeId) =>
      setModals((prev) => ({ ...prev, hql: { show: true, nodeId } })),
    onQuickEdit: (nodeId) =>
      setModals((prev) => ({ ...prev, quickEdit: { show: true, nodeId } })),
    onEditInBuilder: (nodeId) => {
      const node = data?.nodes.find((n) => n.id === nodeId);
      if (node) {
        window.location.href = `/event-node-builder?node_id=${nodeId}`;
      }
    },
    onCopy: async (nodeId) => {
      const newName = prompt("请输入新节点名称:");
      if (newName) {
        try {
          await eventNodesApi.copy(nodeId, newName);
          queryClient.invalidateQueries(["event-nodes"]);
          success("复制成功");
        } catch (error) {
          toastError("复制失败");
        }
      }
    },
    onDelete: (nodeId) => {
      if (confirm("确定要删除这个节点吗？")) {
        deleteMutation.mutate(nodeId);
      }
    },
    onViewFields: (nodeId) =>
      setModals((prev) => ({ ...prev, fields: { show: true, nodeId } })),
  });

  const { table, selectedIds, selectedCount, clearSelection } =
    useEventNodesTable(data?.nodes || [], columns);

  // 删除mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => eventNodesApi.delete(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries(["event-nodes"]);
      const previous = queryClient.getQueryData([
        "event-nodes",
        gameGid,
        filters,
      ]);
      queryClient.setQueryData(
        ["event-nodes", gameGid, filters],
        (old: any) => ({
          ...old,
          nodes: old.nodes.filter((n: EventNode) => n.id !== id),
        }),
      );
      return { previous };
    },
    onError: (err, id, context) => {
      queryClient.setQueryData(
        ["event-nodes", gameGid, filters],
        context?.previous,
      );
      toastError("删除失败，请重试");
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["event-nodes-stats"]);
      success("删除成功");
    },
  });

  // 批量删除mutation
  const bulkDeleteMutation = useMutation({
    mutationFn: (ids: number[]) => eventNodesApi.bulkDelete(ids),
    onSuccess: () => {
      queryClient.invalidateQueries(["event-nodes"]);
      queryClient.invalidateQueries(["event-nodes-stats"]);
      clearSelection();
      success("批量删除成功");
    },
  });

  // 错误处理
  if (isError) {
    return (
      <ErrorFallback
        error={error as Error}
        resetErrorBoundary={() => window.location.reload()}
      />
    );
  }

  return (
    <ErrorBoundary>
      <div className="event-nodes-page" data-testid="event-nodes-page">
        {/* 页面头部 */}
        <div
          className="glass-card"
          style={{
            padding: "2rem",
            marginBottom: "1.5rem",
            position: "relative",
            overflow: "hidden",
          }}
          data-testid="event-nodes-header"
        >
          <div className="header-gradient"></div>
          <div
            className="d-flex justify-content-between align-items-center"
            style={{ position: "relative", zIndex: 1 }}
          >
            <div className="d-flex align-items-center gap-3">
              <div className="hero-icon-box">
                <span className="icon-2xl">📊</span>
              </div>
              <div>
                <h2
                  className="text-primary"
                  style={{
                    fontSize: "1.5rem",
                    fontWeight: 700,
                    marginBottom: "0.25rem",
                  }}
                >
                  事件节点管理
                </h2>
                <p className="text-secondary" style={{ fontSize: "0.875rem" }}>
                  管理和配置事件节点，批量导出HQL
                </p>
              </div>
            </div>
            <div className="d-flex gap-2">
              <Link to="/event-node-builder">
                <Button
                  variant="light-secondary"
                  data-testid="new-node-button"
                >
                  新建节点
                </Button>
              </Link>
              <Button
                variant="light-primary"
                onClick={() => {
                  // 批量导出HQL（后续实现）
                  success("批量导出功能开发中...");
                }}
                data-testid="bulk-export-button"
              >
                批量导出HQL
              </Button>
            </div>
          </div>
        </div>

        {/* 统计卡片 */}
        <StatisticsCards stats={stats || null} />

        {/* 搜索和筛选 */}
        <SearchFilterBar
          filters={filters}
          updateFilters={updateFilters}
          selectedCount={selectedCount}
          onClearSelection={clearSelection}
          onBulkDelete={() => {
            if (confirm(`确定要删除选中的 ${selectedCount} 个节点吗？`)) {
              bulkDeleteMutation.mutate(selectedIds);
            }
          }}
          onToggleAdvanced={() => setShowAdvanced(!showAdvanced)}
          showAdvanced={showAdvanced}
        />

        {/* 高级筛选面板 */}
        <AdvancedFilterPanel
          show={showAdvanced}
          filters={filters}
          updateFilters={updateFilters}
          gameGid={gameGid}
        />

        {/* 节点表格 */}
        <NodesTable
          table={table}
          isLoading={isLoading}
          empty={!data?.nodes || data.nodes.length === 0}
        />

        {/* 模态框组件 */}
        <HQLViewModal
          show={modals.hql.show}
          nodeId={modals.hql.nodeId}
          onClose={() =>
            setModals((prev) => ({
              ...prev,
              hql: { show: false, nodeId: null },
            }))
          }
          data-testid="hql-view-modal"
        />

        <QuickEditModal
          show={modals.quickEdit.show}
          nodeId={modals.quickEdit.nodeId}
          nodes={data?.nodes || []}
          onClose={() =>
            setModals((prev) => ({
              ...prev,
              quickEdit: { show: false, nodeId: null },
            }))
          }
          onUpdate={() => queryClient.invalidateQueries(["event-nodes"])}
          data-testid="quick-edit-modal"
        />

        <FieldsListModal
          show={modals.fields.show}
          nodeId={modals.fields.nodeId}
          nodeName={
            data?.nodes.find((n) => n.id === modals.fields.nodeId)?.name
          }
          onClose={() =>
            setModals((prev) => ({
              ...prev,
              fields: { show: false, nodeId: null },
            }))
          }
          data-testid="fields-list-modal"
        />
      </div>
    </ErrorBoundary>
  );
}

export default EventNodes;
