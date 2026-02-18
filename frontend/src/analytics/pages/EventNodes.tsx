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
import { Link, useSearchParams, useOutletContext, useNavigate } from "react-router-dom";
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
import { ConfirmDialog } from "@shared/ui/ConfirmDialog/ConfirmDialog";
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
      <i className="bi bi-controller display-4 text-primary mb-3 d-block"></i>
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
 * 统计卡片组件 - 使用metric-card系统
 */
function StatisticsCards({ stats }: { stats: EventNodeStats | null }) {
  if (!stats) {
    return (
      <div className="stats-grid">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="metric-card skeleton-card">
            <div className="skeleton-icon"></div>
            <div className="skeleton-content">
              <div className="skeleton-number"></div>
              <div className="skeleton-text"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="stats-grid">
      {/* 总节点数 */}
      <div className="metric-card metric-card--cyan">
        <div className="metric-card__icon metric-card__icon--cyan">
          <i className="bi bi-diagram-3-fill"></i>
        </div>
        <div className="metric-card__value">{stats.total_nodes}</div>
        <div className="metric-card__label">事件节点总数</div>
      </div>

      {/* 关联事件数 */}
      <div className="metric-card metric-card--violet">
        <div className="metric-card__icon metric-card__icon--violet">
          <i className="bi bi-box-seam-fill"></i>
        </div>
        <div className="metric-card__value">{stats.unique_events}</div>
        <div className="metric-card__label">关联事件数</div>
      </div>

      {/* 平均字段数 */}
      <div className="metric-card metric-card--warning">
        <div className="metric-card__icon metric-card__icon--warning">
          <i className="bi bi-list-ul"></i>
        </div>
        <div className="metric-card__value">{stats.avg_fields.toFixed(1)}</div>
        <div className="metric-card__label">平均字段数</div>
      </div>

      {/* 今日修改 */}
      <div className="metric-card metric-card--success">
        <div className="metric-card__icon metric-card__icon--success">
          <i className="bi bi-clock-history"></i>
        </div>
        <div className="metric-card__value">{stats.today_modified || 0}</div>
        <div className="metric-card__label">今日修改</div>
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
    <div className="glass-card filter-bar">
      <div className="filter-bar__main">
        {/* 基础搜索 */}
        <div className="search-input-wrapper">
          <i className="bi bi-search search-icon"></i>
          <input
            type="text"
            className="input-cyber"
            placeholder="搜索节点名称、别名..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
        </div>

        {/* 右侧操作区 */}
        <div className="filter-actions">
          {selectedCount > 0 && (
            <div className="bulk-actions">
              <span className="selection-count">
                已选择 <strong>{selectedCount}</strong> 个节点
              </span>
              <Button variant="outline-danger" onClick={onBulkDelete}>
                <i className="bi bi-trash me-2"></i>
                批量删除
              </Button>
            </div>
          )}
          <Button
            variant={showAdvanced ? "primary" : "outline-primary"}
            onClick={onToggleAdvanced}
          >
            <i className="bi bi-funnel me-2"></i>
            高级筛选
            {showAdvanced ? <i className="bi bi-chevron-up ms-2"></i> : <i className="bi bi-chevron-down ms-2"></i>}
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
  const navigate = useNavigate();
  const [confirmState, setConfirmState] = useState({ open: false, onConfirm: () => {}, title: '', message: '' });

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

  // 更新筛选条件（仅更新本地状态）
  const updateFilters = useCallback(
    (updates: Partial<EventNodeFilters>) => {
      setFilters((prevFilters) => ({ ...prevFilters, ...updates }));
    },
    []
  );

  // URL同步：将filters变化同步到URL参数（独立useEffect）
  useEffect(() => {
    const params: Record<string, string> = {};
    if (filters.keyword) params.q = filters.keyword;
    if (filters.todayModified) params.today = "true";
    if (filters.eventId) params.event = filters.eventId;
    if (filters.fieldCountMin) params.field_min = filters.fieldCountMin;
    if (filters.fieldCountMax) params.field_max = filters.fieldCountMax;

    setSearchParams(params);
  }, [filters, setSearchParams]);

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
        navigate(`/event-node-builder?node_id=${nodeId}`);
      }
    },
    onCopy: async (nodeId) => {
      const newName = prompt("请输入新节点名称:");
      if (newName) {
        try {
          await eventNodesApi.copy(nodeId, newName);
          queryClient.invalidateQueries({ queryKey: ["event-nodes"] });
          success("复制成功");
        } catch (error) {
          toastError("复制失败");
        }
      }
    },
    onDelete: (nodeId) => {
      setConfirmState({
        open: true,
        title: '确认删除',
        message: '确定要删除这个节点吗？',
        onConfirm: () => {
          setConfirmState(s => ({ ...s, open: false }));
          deleteMutation.mutate(nodeId);
        }
      });
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
      queryClient.invalidateQueries({ queryKey: ["event-nodes-stats"] });
      success("删除成功");
    },
  });

  // 批量删除mutation
  const bulkDeleteMutation = useMutation({
    mutationFn: (ids: number[]) => eventNodesApi.bulkDelete(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["event-nodes"] });
      queryClient.invalidateQueries({ queryKey: ["event-nodes-stats"] });
      clearSelection();
      success("批量删除成功");
    },
  });

  // 错误处理
  if (isError) {
    return (
      <ErrorFallback
        error={error as Error}
        resetErrorBoundary={() => {
          queryClient.invalidateQueries({ queryKey: ["event-nodes"] });
          queryClient.invalidateQueries({ queryKey: ["event-nodes-stats"] });
        }}
      />
    );
  }

  return (
    <ErrorBoundary>
      <div className="event-nodes-page" data-testid="event-nodes-page">
        {/* 页面头部 - 优雅两栏布局 */}
        <div className="page-header" data-testid="event-nodes-header">
          <div className="page-header-content">
            <div className="d-flex align-items-center gap-4 mb-2">
              <div className="hero-icon-box">
                <i className="bi bi-diagram-3"></i>
              </div>
              <div>
                <h1 className="page-header-title">事件节点管理</h1>
                <p className="page-header-description">
                  管理和配置事件节点，批量导出HQL
                </p>
              </div>
            </div>
          </div>
          <div className="page-header-actions">
            <Link to="/event-node-builder" style={{ textDecoration: 'none' }}>
              <Button
                variant="primary"
                className="me-3"
                data-testid="new-node-button"
              >
                <i className="bi bi-plus-lg me-2"></i>
                新建节点
              </Button>
            </Link>
            <Button
              variant="outline-primary"
              onClick={() => {
                success("批量导出功能开发中...");
              }}
              data-testid="bulk-export-button"
            >
              <i className="bi bi-download me-2"></i>
              批量导出HQL
            </Button>
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
            setConfirmState({
              open: true,
              title: '确认批量删除',
              message: `确定要删除选中的 ${selectedCount} 个节点吗？`,
              onConfirm: () => {
                setConfirmState(s => ({ ...s, open: false }));
                bulkDeleteMutation.mutate(selectedIds);
              }
            });
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
          onUpdate={() => queryClient.invalidateQueries({ queryKey: ["event-nodes"] })}
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

        <ConfirmDialog
          open={confirmState.open}
          title={confirmState.title}
          message={confirmState.message}
          confirmText="删除"
          cancelText="取消"
          variant="danger"
          onConfirm={confirmState.onConfirm}
          onCancel={() => setConfirmState(s => ({ ...s, open: false }))}
        />
      </div>
    </ErrorBoundary>
  );
}

export default EventNodes;
