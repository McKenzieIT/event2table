import React from "react";
import "./NodeContextMenu.css";

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
}) {
  const isEventNode = node.type === "event";
  const hasConfigId = isEventNode && node.data.configId;

  return (
    <div
      className="node-context-menu"
      style={{ left: position.x, top: position.y }}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="context-menu-header">
        <span className="node-icon">{node.data.icon || "⚙️"}</span>
        <span className="node-label">{node.data.label}</span>
      </div>

      <div className="context-menu-divider"></div>

      <button className="context-menu-item" onClick={() => onViewDetail(node)}>
        <span className="menu-icon">👁️</span>
        查看详情
      </button>

      {hasConfigId && (
        <button className="context-menu-item" onClick={() => onEdit(node)}>
          <span className="menu-icon">✏️</span>
          编辑配置
        </button>
      )}

      <button
        className="context-menu-item danger"
        onClick={() => onDelete(node)}
      >
        <span className="menu-icon">🗑️</span>
        删除节点
      </button>
    </div>
  );
}
