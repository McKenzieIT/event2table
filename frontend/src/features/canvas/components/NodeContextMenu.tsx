// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React from "react";
import "./NodeContextMenu.css";
import type { NodeContextMenuProps, CanvasNode } from "./types";

/**
 * 节点右键上下文菜单
 * 显示"查看详情"、"编辑配置"、"删除节点"等选项
 */
export default function NodeContextMenu({
  position,
  node,
  onClose,
  onViewDetail,
  onEdit,
  onDelete,
}: NodeContextMenuProps): React.JSX.Element {
  const isEventNode = node.type === "event";
  const hasConfigId = isEventNode && (node.data as any).configId;

  return (
    <div
      className="node-context-menu"
      style={{ left: position.x, top: position.y }}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="context-menu-header">
        <span className="node-icon">{(node.data as any).icon || "⚙️"}</span>
        <span className="node-label">{node.data.label}</span>
      </div>

      <div className="context-menu-divider"></div>

      <button className="context-menu-item" onClick={() => onViewDetail(node as CanvasNode)}>
        <span className="menu-icon">👁️</span>
        查看详情
      </button>

      {hasConfigId && onEdit && (
        <button className="context-menu-item" onClick={() => onEdit(node as CanvasNode)}>
          <span className="menu-icon">✏️</span>
          编辑配置
        </button>
      )}

      <button
        className="context-menu-item danger"
        onClick={() => onDelete(node as CanvasNode)}
      >
        <span className="menu-icon">🗑️</span>
        删除节点
      </button>
    </div>
  );
}
