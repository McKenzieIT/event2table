// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React, { useCallback, memo } from "react";
import { useReactFlow } from "reactflow";
import { Button, useToast } from "@shared/ui";
import ConfirmDialog from "@shared/ui/ConfirmDialog/ConfirmDialog";
import "./Toolbar.css";
import type { ToolbarProps, GameData } from "./types";

function Toolbar({ gameData, onExecute, onLocateNodes }: ToolbarProps): React.JSX.Element {
  const { getNodes, getEdges, setNodes, setEdges } = useReactFlow();
  const { success: toastSuccess, error: toastError, warning: toastWarning } = useToast();
  const [confirmState, setConfirmState] = React.useState<{
    open: boolean;
    onConfirm: () => void;
    title: string;
    message: string;
  }>({ open: false, onConfirm: () => {}, title: '', message: '' });

  // 删除选中的节点
  const deleteSelected = useCallback(() => {
    const selectedNodes = getNodes().filter((node) => node.selected);
    if (selectedNodes.length === 0) {
      toastWarning("请先选择要删除的节点");
      return;
    }

    setConfirmState({
      open: true,
      title: '确认删除节点',
      message: `确定要删除 ${selectedNodes.length} 个节点吗？`,
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        const selectedIds = new Set(selectedNodes.map((n) => n.id));
        setNodes((nodes) => nodes.filter((n) => !selectedIds.has(n.id)));
        setEdges((edges) =>
          edges.filter(
            (e) => !selectedIds.has(e.source) && !selectedIds.has(e.target),
          ),
        );
      }
    });
  }, [getNodes, setNodes, setEdges, toastWarning]);

  // 清空画布
  const clearCanvas = useCallback(() => {
    setConfirmState({
      open: true,
      title: '确认清空画布',
      message: '确定要清空画布吗？此操作不可撤销。',
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        setNodes([]);
        setEdges([]);
      }
    });
  }, [setNodes, setEdges]);

  // 保存流程
  const saveFlow = useCallback(async () => {
    const nodes = getNodes();
    const edges = getEdges();

    if (nodes.length === 0) {
      toastWarning("画布为空，无法保存");
      return;
    }

    const flowName = prompt("请输入流程名称：");
    if (!flowName) return;

    const flowData = {
      name: flowName,
      game_id: gameData.id,
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type,
        position: n.position,
        data: n.data,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle,
        targetHandle: e.targetHandle,
      })),
    };

    try {
      // 🔧 v1.0.26.1: 修改API路径和数据格式以适配后端Flow API
      // Flow API需要output_config，我们添加默认值
      const response = await fetch("/api/flows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          flow_name: flowName,
          flow_graph: {
            nodes: flowData.nodes.map((n) => ({
              node_id: n.id,
              node_type: n.type,
              config_ref: n.data?.configId || null,
            })),
            connections: flowData.edges.map((e) => ({
              id: e.id,
              source_node: e.source,
              target_node: e.target,
              connection_type: "union_all",
            })),
            output_config: {
              table_name: `v_dwd_${gameData.gid}_${Date.now()}`,
              database: "ieu_cdm",
            },
          },
          description: `画布流程: ${nodes.length}节点, ${edges.length}连接`,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      if (result.success || result.data) {
        toastSuccess(`结果 "${flowName}" 保存成功！`);
      } else {
        toastError(`保存失败: ${result.message || result.error}`);
      }
    } catch (error) {
      toastError(`保存失败: ${(error as any).message}`);
    }
  }, [getNodes, getEdges, gameData, toastWarning, toastSuccess, toastError]);

  // ⚡ PERF: 降级到旧API的HQL生成（移到前面以避免TDZ错误）
  const generateFallbackHQL = useCallback(async () => {
    const nodes = getNodes();
    const edges = getEdges();

    if (nodes.length === 0) {
      toastWarning("画布为空，无法生成HQL");
      return;
    }

    const flowData = {
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type,
        position: n.position,
        data: n.data,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
    };

    try {
      const response = await fetch("/canvas/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(flowData),
      });

      const result = await response.json();
      if (result.success) {
        // 显示HQL结果
        const hqlWindow = window.open("", "_blank", "width=800,height=600");
        if (hqlWindow) {
          const doc = hqlWindow.document;
          doc.open();
          doc.write(`
            <html>
              <head>
                <title>HQL生成结果</title>
                <style>
                  body { font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                  pre { background: #2d2d2d; padding: 20px; border-radius: 8px; overflow-x: auto; }
                  h1 { color: #4ec9b0; }
                </style>
              </head>
              <body>
                <h1>HQL生成成功</h1>
                <pre></pre>
              </body>
            </html>
          `);
          const preElement = doc.querySelector('pre');
          if (preElement) {
            preElement.textContent = result.data.hql || '无HQL内容';
          }
          doc.close();
        }
      } else {
        toastError(`生成失败: ${result.message}`);
      }
    } catch (error) {
      toastError("生成失败，请检查网络连接");
    }
  }, [getNodes, getEdges, toastWarning, toastError]);

  // 生成HQL（使用新执行引擎）
  const generateHQL = useCallback(() => {
    if (onExecute) {
      // 使用新执行引擎
      onExecute();
    } else {
      // 降级到旧API
      generateFallbackHQL();
    }
  }, [onExecute, generateFallbackHQL]);

  // 适应视图
  const fitView = useCallback(() => {
    // ReactFlow的Controls组件已包含此功能
  }, []);

  return (
    <div className="canvas-toolbar">
      <div className="toolbar-group">
        <Button
          onClick={clearCanvas}
          variant="danger"
          size="sm"
          className="toolbar-btn"
          title="清空画布"
        >
          🗑️ 清空
        </Button>
        <Button
          onClick={deleteSelected}
          variant="warning"
          size="sm"
          className="toolbar-btn"
          title="删除选中的节点"
        >
          ❌ 删除
        </Button>
      </div>

      <div className="toolbar-group">
        <Button
          onClick={saveFlow}
          variant="primary"
          size="sm"
          className="toolbar-btn"
          title="保存结果（画布配置+HQL）"
        >
          💾 保存结果
        </Button>
        <Button
          onClick={generateHQL}
          variant="success"
          size="sm"
          className="toolbar-btn"
          title="生成HQL"
        >
          ⚡ 生成HQL
        </Button>
      </div>

      <div className="toolbar-group">
        <Button
          onClick={onLocateNodes}
          variant="outline-primary"
          size="sm"
          className="toolbar-btn"
          title="定位节点 - 在Console显示节点信息并高亮显示"
        >
          🔍 定位节点
        </Button>
      </div>

      <div className="toolbar-info">
        <span>节点: {getNodes().length}</span>
        <span>连接: {getEdges().length}</span>
      </div>

      <ConfirmDialog
        open={confirmState.open}
        title={confirmState.title}
        message={confirmState.message}
        confirmText="确认"
        cancelText="取消"
        variant="danger"
        onConfirm={confirmState.onConfirm}
        onCancel={() => setConfirmState(s => ({ ...s, open: false }))}
      />
    </div>
  );
}

// ⚡ PERF: 使用 React.memo 优化渲染性能
const ToolbarMemo = memo(Toolbar);
export default ToolbarMemo;
