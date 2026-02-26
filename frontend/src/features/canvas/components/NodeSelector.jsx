import React, { useState, useEffect, useCallback } from "react";
import { SearchInput, EmptyState } from '@shared/ui';
import "./NodeSelector.css";

/**
 * 节点选择器组件
 * 用于在连接提示模态框中选择目标节点
 *
 * @param {Array} nodes - 可选节点列表
 * @param {Function} onSelect - 节点选择回调
 * @param {string} selectedId - 已选择的节点ID
 * @param {string} filterType - 过滤的节点类型
 *
 * @example
 * <NodeSelector
 *   nodes={nodes}
 *   onSelect={handleNodeSelect}
 *   selectedId={selectedNodeId}
 *   filterType="output"
 * />
 */
export default function NodeSelector({
  nodes,
  onSelect,
  selectedId,
  filterType,
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredNodes, setFilteredNodes] = useState([]);

  // 过滤节点
  useEffect(() => {
    let filtered = nodes;

    // 按类型过滤
    if (filterType) {
      filtered = filtered.filter((node) => node.type === filterType);
    }

    // 按搜索词过滤
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (node) =>
          node.data.label.toLowerCase().includes(term) ||
          (node.data.eventName &&
            node.data.eventName.toLowerCase().includes(term)),
      );
    }

    setFilteredNodes(filtered);
  }, [nodes, searchTerm, filterType]);

  // 生成节点类型的图标
  const getNodeIcon = (nodeType) => {
    const icons = {
      event: "🎮",
      union_all: "🔀",
      join: "🔗",
      output: "📤",
    };
    return icons[nodeType] || "📦";
  };

  // 生成节点类型的中文名称
  const getNodeTypeName = (nodeType) => {
    const names = {
      event: "事件节点",
      union_all: "UNION ALL",
      join: "JOIN",
      output: "输出节点",
    };
    return names[nodeType] || "未知类型";
  };

  // 处理节点选择
  const handleNodeSelect = useCallback(
    (node) => {
      if (onSelect) {
        onSelect(node);
      }
    },
    [onSelect],
  );

  // 清除搜索
  const handleClearSearch = () => {
    setSearchTerm('');
  };

  return (
    <div className="node-selector">
      <div className="search-container">
        <SearchInput
          placeholder="搜索节点名称..."
          value={searchTerm}
          onChange={(value) => setSearchTerm(value)}
        />
        {searchTerm && (
          <button
            className="clear-button"
            onClick={handleClearSearch}
            title="清除搜索"
          >
            ×
          </button>
        )}
      </div>

      <div className="node-list">
        {filteredNodes.length === 0 ? (
          <EmptyState
            icon={<i className="bi bi-diagram-3" style={{ fontSize: '32px' }} />}
            title={searchTerm ? "没有找到匹配的节点" : "没有可选择的节点"}
          />
        ) : (
          filteredNodes.map((node) => (
            <div
              key={node.id}
              className={`node-item ${selectedId === node.id ? "selected" : ""}`}
              onClick={() => handleNodeSelect(node)}
            >
              <div className="node-content">
                <span className="node-icon">{getNodeIcon(node.type)}</span>
                <div className="node-info">
                  <span className="node-label">{node.data.label}</span>
                  {node.data.eventName && (
                    <span className="node-sublabel">{node.data.eventName}</span>
                  )}
                </div>
              </div>
              <div className="node-type">{getNodeTypeName(node.type)}</div>
              {selectedId === node.id && <span className="checkmark">✓</span>}
            </div>
          ))
        )}
      </div>

      {filteredNodes.length > 0 && (
        <div className="node-count">共 {filteredNodes.length} 个节点</div>
      )}
    </div>
  );
}
