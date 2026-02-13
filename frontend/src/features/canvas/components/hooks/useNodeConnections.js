import { useState, useCallback } from "react";

/**
 * 节点连接管理 Hook
 * 管理节点间的连接关系和连接逻辑
 *
 * @param {Array} nodes - 节点列表
 * @param {Array} edges - 边列表
 * @param {Function} onEdgesChange - 边变更回调
 * @param {Function} addEdge - 添加边的函数
 *
 * @returns {Object} 连接管理相关的函数和状态
 *   - connections: 当前连接关系
 *   - canConnect: 检查是否可以连接
 *   - suggestConnections: 建议可能的连接
 *   - findSourceNodes: 查找源节点
 *   - findTargetNodes: 查找目标节点
 *   - validateConnection: 验证连接的有效性
 */
export function useNodeConnections(nodes, edges, onEdgesChange, addEdge) {
  const [connections, setConnections] = useState([]);

  // 检查两个节点是否可以连接
  const canConnect = useCallback(
    (sourceNode, targetNode) => {
      if (!sourceNode || !targetNode) return false;
      if (sourceNode.id === targetNode.id) return false; // 不能连接自己

      // 检查是否已存在连接
      const existingConnection = edges.find(
        (edge) =>
          edge.source === sourceNode.id && edge.target === targetNode.id,
      );
      if (existingConnection) return false;

      // 检查节点类型兼容性
      const typeRules = {
        event: ["union_all", "join", "output"],
        union_all: ["join", "output"],
        join: ["output"],
        output: [], // 输出节点不能作为源节点
      };

      const allowedTypes = typeRules[sourceNode.type] || [];
      return allowedTypes.includes(targetNode.type);
    },
    [edges],
  );

  // 验证连接的有效性
  const validateConnection = useCallback(
    (connection) => {
      const sourceNode = nodes.find((n) => n.id === connection.source);
      const targetNode = nodes.find((n) => n.id === connection.target);

      if (!sourceNode || !targetNode) {
        return { valid: false, error: "节点不存在" };
      }

      if (!canConnect(sourceNode, targetNode)) {
        return { valid: false, error: "连接规则不允许" };
      }

      return { valid: true };
    },
    [nodes, canConnect],
  );

  // 建议可能的连接
  const suggestConnections = useCallback(
    (nodeId) => {
      const suggestions = [];
      const node = nodes.find((n) => n.id === nodeId);

      if (!node) return suggestions;

      // 查找可以作为目标的节点
      nodes.forEach((targetNode) => {
        if (targetNode.id !== nodeId && canConnect(node, targetNode)) {
          suggestions.push({
            source: node.id,
            target: targetNode.id,
            sourceLabel: node.data.label,
            targetLabel: targetNode.data.label,
            type: targetNode.type,
          });
        }
      });

      return suggestions;
    },
    [nodes, canConnect],
  );

  // 查找所有源节点（可以连接到给定节点的节点）
  const findSourceNodes = useCallback(
    (targetId) => {
      return nodes.filter((node) => {
        if (node.id === targetId) return false;
        return canConnect(
          node,
          nodes.find((n) => n.id === targetId),
        );
      });
    },
    [nodes, canConnect],
  );

  // 查找所有目标节点（可以从给定节点连接到的节点）
  const findTargetNodes = useCallback(
    (sourceId) => {
      return nodes.filter((node) => {
        if (node.id === sourceId) return false;
        return canConnect(
          nodes.find((n) => n.id === sourceId),
          node,
        );
      });
    },
    [nodes, canConnect],
  );

  // 创建连接
  const createConnection = useCallback(
    (sourceId, targetId) => {
      const connection = { source: sourceId, target: targetId };
      const validation = validateConnection(connection);

      if (!validation.valid) {
        throw new Error(validation.error);
      }

      const newEdge = {
        id: `edge_${Date.now()}`,
        source: sourceId,
        target: targetId,
        type: "smoothstep",
        animated: true,
        style: { stroke: "#667eea", strokeWidth: 2 },
        label: "",
      };

      addEdge(newEdge, edges);
      return newEdge;
    },
    [validateConnection, addEdge, edges],
  );

  // 删除连接
  // Note: setEdges should be passed as a parameter or use onEdgesChange
  const removeConnection = useCallback(
    (edgeId) => {
      // Use onEdgesChange to remove the edge
      const edgeToRemove = edges.find((edge) => edge.id === edgeId);
      if (edgeToRemove && onEdgesChange) {
        onEdgesChange([{ type: "remove", id: edgeId }]);
      }
    },
    [edges, onEdgesChange],
  );

  // 获取节点的入度（连接到该节点的数量）
  const getNodeInDegree = useCallback(
    (nodeId) => {
      return edges.filter((edge) => edge.target === nodeId).length;
    },
    [edges],
  );

  // 获取节点的出度（从该节点连接出的数量）
  const getNodeOutDegree = useCallback(
    (nodeId) => {
      return edges.filter((edge) => edge.source === nodeId).length;
    },
    [edges],
  );

  // 获取节点的连接状态
  const getNodeConnections = useCallback(
    (nodeId) => {
      return {
        incoming: edges.filter((edge) => edge.target === nodeId),
        outgoing: edges.filter((edge) => edge.source === nodeId),
        inDegree: getNodeInDegree(nodeId),
        outDegree: getNodeOutDegree(nodeId),
      };
    },
    [edges, getNodeInDegree, getNodeOutDegree],
  );

  // 检查节点是否为源节点（只有输出）
  const isSourceNode = useCallback(
    (nodeId) => {
      const connections = getNodeConnections(nodeId);
      return (
        connections.incoming.length === 0 && connections.outgoing.length > 0
      );
    },
    [getNodeConnections],
  );

  // 检查节点是否为中间节点（有输入也有输出）
  const isIntermediateNode = useCallback(
    (nodeId) => {
      const connections = getNodeConnections(nodeId);
      return connections.incoming.length > 0 && connections.outgoing.length > 0;
    },
    [getNodeConnections],
  );

  // 检查节点是否为终端节点（只有输入）
  const isTerminalNode = useCallback(
    (nodeId) => {
      const connections = getNodeConnections(nodeId);
      return (
        connections.incoming.length > 0 && connections.outgoing.length === 0
      );
    },
    [getNodeConnections],
  );

  return {
    connections,
    canConnect,
    validateConnection,
    suggestConnections,
    findSourceNodes,
    findTargetNodes,
    createConnection,
    removeConnection,
    getNodeConnections,
    getNodeInDegree,
    getNodeOutDegree,
    isSourceNode,
    isIntermediateNode,
    isTerminalNode,
  };
}
