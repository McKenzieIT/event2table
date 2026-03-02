// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { useState, useEffect, useCallback } from "react";
import { SearchInput, EmptyState } from '@shared/ui';
import { FlowNode } from '../../types';
import "./NodeSelector.css";

/**
 * 节点选择器组件 Props 接口
 */
interface NodeSelectorProps {
  /** 可选节点列表 */
  nodes: FlowNode[];
  /** 节点选择回调 */
  onSelect: (node: FlowNode) => void;
  /** 已选择的节点ID */
  selectedId?: string;
  /** 过滤的节点类型 */
  filterType?: string;
}

/**
 * 节点数据结构
 */
interface NodeData {
  label: string;
  eventName?: string;
  [key: string]: unknown;
}

/**
 * 节点选择器组件
 * 用于在连接提示模态框中选择目标节点
 *
 * @example
 * ```tsx
 * <NodeSelector
 *   nodes={nodes}
 *   onSelect={handleNodeSelect}
 *   selectedId={selectedNodeId}
 *   filterType="output"
 * />
 * ```
 */
const NodeSelector: React.FC<NodeSelectorProps> = ({
  nodes,
  onSelect,
  selectedId,
  filterType,
}) => {
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [filteredNodes, setFilteredNodes] = useState<FlowNode[]>([]);

  // 过滤节点
  useEffect(() => {
    let filtered = [...nodes];

    // 按类型过滤
    if (filterType) {
      filtered = filtered.filter((node) => node.type === filterType);
    }

    // 按搜索词过滤
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (node) => {
          const nodeData = node.data as NodeData;
          return (
            nodeData.label?.toLowerCase().includes(term) ||
            (nodeData.eventName &&
              nodeData.eventName.toLowerCase().includes(term))
          );
        }
      );
    }

    setFilteredNodes(filtered);
  }, [nodes, searchTerm, filterType]);

  // 生成节点类型的图标
  const getNodeIcon = (nodeType: string): string => {
    const icons: Record<string, string> = {
      event: "🎮",
      union_all: "🔀",
      join: "🔗",
      output: "📤",
    };
    return icons[nodeType] || "📦";
  };

  // 生成节点类型的中文名称
  const getNodeTypeName = (nodeType: string): string => {
    const names: Record<string, string> = {
      event: "事件节点",
      union_all: "UNION ALL",
      join: "JOIN",
      output: "输出节点",
    };
    return names[nodeType] || "未知类型";
  };

  // 处理节点选择
  const handleNodeSelect = useCallback(
    (node: FlowNode) => {
      if (onSelect) {
        onSelect(node);
      }
    },
    [onSelect],
  );

  // 清除搜索
  const handleClearSearch = useCallback(() => {
    setSearchTerm('');
  }, []);

  return (
    <div className="node-selector">
      <div className="search-container">
        <SearchInput
          placeholder="搜索节点名称..."
          value={searchTerm}
          onChange={(value: string) => setSearchTerm(value)}
        />
        {searchTerm && (
          <button
            className="clear-button"
            onClick={handleClearSearch}
            title="清除搜索"
            type="button"
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
          filteredNodes.map((node) => {
            const nodeData = node.data as NodeData;
            return (
              <div
                key={node.id}
                className={`node-item ${selectedId === node.id ? "selected" : ""}`}
                onClick={() => handleNodeSelect(node)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleNodeSelect(node);
                  }
                }}
                aria-pressed={selectedId === node.id}
              >
                <div className="node-content">
                  <span className="node-icon">{getNodeIcon(node.type)}</span>
                  <div className="node-info">
                    <span className="node-label">{nodeData.label}</span>
                    {nodeData.eventName && (
                      <span className="node-sublabel">{nodeData.eventName}</span>
                    )}
                  </div>
                </div>
                <div className="node-type">{getNodeTypeName(node.type)}</div>
                {selectedId === node.id && <span className="checkmark">✓</span>}
              </div>
            );
          })
        )}
      </div>

      {filteredNodes.length > 0 && (
        <div className="node-count">共 {filteredNodes.length} 个节点</div>
      )}
    </div>
  );
};

export default NodeSelector;
